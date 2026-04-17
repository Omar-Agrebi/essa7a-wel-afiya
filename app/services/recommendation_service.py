from uuid import UUID
from app.repositories.recommendation_repository import RecommendationRepository

class RecommendationService:
    def __init__(self, repo: RecommendationRepository):
        self.repo = repo

    async def get_recommendations(self, user_id: UUID, top_n: int = 10):
        """Get top recommended opportunities for a user."""
        return await self.repo.get_recommendations(user_id=user_id, top_n=top_n)

    async def store_recommendations(self, user_id: UUID, scored_opps: list[dict]) -> int:
        """Store scored opportunities as recommendations for a user."""
        count = 0
        for item in scored_opps:
            await self.repo.upsert(
                user_id=user_id,
                opportunity_id=item['opportunity_id'],
                score=item['score'],
                match_reasons=item['match_reasons']
            )
            count += 1
        return count

    async def refresh_recommendations(self, user_id: UUID, scored_opps: list[dict]) -> int:
        """Clear old recommendations and store new ones."""
        await self.repo.delete_by_user(user_id)
        return await self.store_recommendations(user_id, scored_opps)

    async def get_average_score(self, user_id: UUID) -> float | None:
        """Get the average recommendation score for a given user."""
        return await self.repo.get_average_score(user_id)
