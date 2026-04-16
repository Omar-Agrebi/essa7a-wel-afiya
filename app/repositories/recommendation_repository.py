"""Recommendation repository."""
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func

from app.repositories.base_repository import BaseRepository
from app.models.recommendation import Recommendation

class RecommendationRepository(BaseRepository[Recommendation]):
    """
    Repository for Recommendation specific database operations.
    """
    def __init__(self, session: AsyncSession):
        """Initializes the repository with the Recommendation model."""
        super().__init__(session, Recommendation)

    async def get_by_user(self, user_id: UUID) -> list[Recommendation]:
        """
        Retrieves all recommendations for a specific user, ordered by score descending.
        Relationships like opportunity are loaded efficiently via joined load (default on model).
        """
        try:
            stmt = select(Recommendation).where(
                Recommendation.user_id == user_id
            ).order_by(Recommendation.score.desc())
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise e

    async def get_top_n(self, user_id: UUID, n: int) -> list[Recommendation]:
        """
        Retrieves the top N recommendations for a user by score descending.
        """
        try:
            stmt = select(Recommendation).where(
                Recommendation.user_id == user_id
            ).order_by(Recommendation.score.desc()).limit(n)
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise e

    async def upsert(
        self, 
        user_id: UUID, 
        opportunity_id: UUID, 
        score: float, 
        match_reasons: list[str]
    ) -> Recommendation:
        """
        Upserts a recommendation for a user and an opportunity.
        If the pair exists, updates score and match_reasons.
        If it's new, inserts it.
        """
        try:
            stmt = select(Recommendation).where(
                Recommendation.user_id == user_id,
                Recommendation.opportunity_id == opportunity_id
            )
            result = await self.session.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                existing.score = score
                existing.match_reasons = match_reasons
                await self.session.commit()
                await self.session.refresh(existing)
                return existing
            else:
                db_obj = Recommendation(
                    user_id=user_id,
                    opportunity_id=opportunity_id,
                    score=score,
                    match_reasons=match_reasons
                )
                self.session.add(db_obj)
                await self.session.commit()
                await self.session.refresh(db_obj)
                return db_obj
        except Exception as e:
            await self.session.rollback()
            raise e

    async def delete_by_user(self, user_id: UUID) -> int:
        """
        Deletes all recommendations for a specific user.
        Returns the number of deleted records.
        """
        try:
            stmt = delete(Recommendation).where(Recommendation.user_id == user_id)
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.rowcount
        except Exception as e:
            await self.session.rollback()
            raise e

    async def get_average_score(self, user_id: UUID) -> float | None:
        """
        Computes the average score of all recommendations for a given user.
        """
        try:
            stmt = select(func.avg(Recommendation.score)).where(Recommendation.user_id == user_id)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            raise e
