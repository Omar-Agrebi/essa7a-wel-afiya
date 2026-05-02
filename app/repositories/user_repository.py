"""User repository."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.repositories.base_repository import BaseRepository
from app.models.user import User

class UserRepository(BaseRepository[User]):
    """
    Repository for User specific database operations.
    """
    def __init__(self, session: AsyncSession):
        """Initializes the repository with the User model."""
        super().__init__(session, User)

    async def get_by_email(self, email: str) -> User | None:
        """
        Retrieves a user by their email address.
        """
        try:
            stmt = select(User).where(User.email == email)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            raise e

    async def get_all_users(self) -> list[User]:
        """
        Retrieves all users without pagination.
        Used primarily by the pipeline for batch processing.
        """
        try:
            stmt = select(User).order_by(User.created_at.desc())
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise e

    async def update_skills(self, user_id: str, skills: list[str]) -> User | None:
        """
        Updates the skills array for a given user.
        """
        try:
            user = await self.get_by_id(user_id)
            if not user:
                return None
            user.skills = skills
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except Exception as e:
            await self.session.rollback()
            raise e

    async def update_interests(self, user_id: str, interests: list[str]) -> User | None:
        """
        Updates the interests array for a given user.
        """
        try:
            user = await self.get_by_id(user_id)
            if not user:
                return None
            user.interests = interests
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except Exception as e:
            await self.session.rollback()
            raise e
