
from app.repositories.recommendation_repository import RecommendationRepository

class RecommendationService:
    def __init__(self, repo: RecommendationRepository):
        self.repo = repo

    async def get_recommendations(self, user_id: str, top_n: int = 10):
        """Get top recommended opportunities for a user."""
        return await self.repo.get_top_n(user_id=user_id, n=top_n)

    async def store_recommendations(self, user_id: str, scored_opps: list[dict]) -> int:
        """Store scored opportunities as recommendations for a user."""
        count = 0
        for item in scored_opps:
            await self.repo.upsert(
                user_id=user_id,
                opportunity_id=item.get('opportunity_id') or item.get('id'),
                score=item.get('score') or item.get('final_score', 0.0),
                match_reasons=item.get('match_reasons', [])
            )
            count += 1
        return count

    async def refresh_recommendations(self, user_id: str, scored_opps: list[dict]) -> int:
        """Clear old recommendations and store new ones."""
        await self.repo.delete_by_user(user_id)
        return await self.store_recommendations(user_id, scored_opps)

    async def get_average_score(self, user_id: str) -> float | None:
        """Get the average recommendation score for a given user."""
        return await self.repo.get_average_score(user_id)
