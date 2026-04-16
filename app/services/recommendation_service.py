"""Business logic service for the Recommendation domain."""
from uuid import UUID

from fastapi import HTTPException, status

from app.models.recommendation import Recommendation
from app.repositories.recommendation_repository import RecommendationRepository


class RecommendationService:
    """Service layer for all recommendation-related business operations.

    Handles retrieval, storage, and refresh of personalised opportunity
    recommendations for individual users.  All DB access is delegated to
    :class:`RecommendationRepository`.  No ML logic lives here — scoring
    is performed upstream by :class:`AgentAdvisor`.
    """

    def __init__(self, repo: RecommendationRepository) -> None:
        """Initialise the service with its repository dependency.

        Args:
            repo: A :class:`RecommendationRepository` instance injected by the
                  FastAPI dependency system or created directly by agents.
        """
        self.repo = repo

    async def get_recommendations(
        self,
        user_id: UUID,
        top_n: int = 10,
    ) -> list[Recommendation]:
        """Retrieve the top-N stored recommendations for a user.

        Args:
            user_id: The UUID of the user whose recommendations to fetch.
            top_n:   The maximum number of recommendations to return, ordered
                     by descending score.  Defaults to 10.

        Returns:
            A list of :class:`Recommendation` ORM objects.
        """
        return await self.repo.get_top_n(user_id=user_id, n=top_n)

    async def store_recommendations(
        self,
        user_id: UUID,
        scored_opps: list[dict],
    ) -> int:
        """Persist a list of scored opportunities as recommendations.

        Each element of *scored_opps* must contain at minimum:
        - ``opportunity_id`` (UUID)
        - ``score``          (float)
        - ``match_reasons``  (list[str])

        Existing (user_id, opportunity_id) pairs are updated in-place via
        the repository's upsert method; new pairs are inserted.

        Args:
            user_id:      The UUID of the user these recommendations belong to.
            scored_opps:  A list of dicts produced by the ML recommender.

        Returns:
            The total count of records successfully stored.
        """
        stored = 0
        for item in scored_opps:
            try:
                await self.repo.upsert(
                    user_id=user_id,
                    opportunity_id=item["opportunity_id"],
                    score=item["score"],
                    match_reasons=item.get("match_reasons", []),
                )
                stored += 1
            except Exception:
                # Log silently and continue — partial failures must not abort
                # the entire batch.
                pass
        return stored

    async def refresh_recommendations(
        self,
        user_id: UUID,
        scored_opps: list[dict],
    ) -> int:
        """Delete all existing recommendations for a user, then store fresh ones.

        This is used by the recommendation pipeline stage and by the manual
        /recommendations/refresh endpoint to replace stale data atomically.

        Args:
            user_id:     The UUID of the user to refresh.
            scored_opps: New scored opportunities to persist.

        Returns:
            The count of newly stored recommendation records.
        """
        await self.repo.delete_by_user(user_id)
        return await self.store_recommendations(user_id, scored_opps)

    async def get_average_score(self, user_id: UUID) -> float | None:
        """Compute the average recommendation score for a user.

        Useful for dashboard statistics and monitoring recommendation quality
        over pipeline runs.

        Args:
            user_id: The UUID of the user to compute the average for.

        Returns:
            The average score as a float, or ``None`` if no recommendations
            exist for the user yet.
        """
        return await self.repo.get_average_score(user_id)
