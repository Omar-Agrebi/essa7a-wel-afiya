"""Notification repository."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func

from app.repositories.base_repository import BaseRepository
from app.models.notification import Notification
from app.core.constants import NotificationStatus

class NotificationRepository(BaseRepository[Notification]):
    """
    Repository for Notification specific database operations.
    """
    def __init__(self, session: AsyncSession):
        """Initializes the repository with the Notification model."""
        super().__init__(session, Notification)

    async def get_by_user(self, user_id: str) -> list[Notification]:
        """
        Retrieves all notifications for a specific user, ordered by timestamp descending.
        """
        try:
            stmt = select(Notification).where(
                Notification.user_id == user_id
            ).order_by(Notification.timestamp.desc())
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise e

    async def get_unread(self, user_id: str) -> list[Notification]:
        """
        Retrieves unread notifications for a user, ordered by timestamp descending.
        """
        try:
            stmt = select(Notification).where(
                Notification.user_id == user_id,
                Notification.status == 'unread'
            ).order_by(Notification.timestamp.desc())
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise e

    async def mark_as_read(self, notification_id: str) -> Notification | None:
        """
        Marks a specific notification as read.
        """
        try:
            notification = await self.get_by_id(notification_id)
            if not notification:
                return None
            notification.status = NotificationStatus.read
            await self.session.commit()
            await self.session.refresh(notification)
            return notification
        except Exception as e:
            await self.session.rollback()
            raise e

    async def mark_all_read(self, user_id: str) -> int:
        """
        Marks all unread notifications for a user as read.
        Returns the number of updated records.
        """
        try:
            stmt = update(Notification).where(
                Notification.user_id == user_id,
                Notification.status == 'unread'
            ).values(status='read')
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.rowcount
        except Exception as e:
            await self.session.rollback()
            raise e

    async def count_unread(self, user_id: str) -> int:
        """
        Counts the number of unread notifications for a user.
        """
        try:
            stmt = select(func.count()).select_from(Notification).where(
                Notification.user_id == user_id,
                Notification.status == 'unread'
            )
            result = await self.session.execute(stmt)
            return result.scalar_one()
        except Exception as e:
            raise e
