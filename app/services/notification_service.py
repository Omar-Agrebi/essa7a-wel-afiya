
from fastapi import HTTPException, status
from app.repositories.notification_repository import NotificationRepository

class NotificationService:
    def __init__(self, repo: NotificationRepository):
        self.repo = repo

    async def get_user_notifications(self, user_id: str):
        """Get all notifications for a specific user."""
        return await self.repo.get_by_user(user_id)

    async def get_unread(self, user_id: str):
        """Get only unread notifications for a user."""
        return await self.repo.get_unread(user_id)

    async def count_unread(self, user_id: str) -> int:
        """Count the number of unread notifications for a user."""
        return await self.repo.count_unread(user_id)

    async def mark_read(self, notification_id: str):
        """Mark a single notification as read."""
        notification = await self.repo.get_by_id(notification_id)
        if not notification:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
        return await self.repo.mark_as_read(notification_id)

    async def mark_all_read(self, user_id: str) -> int:
        """Mark all of a user's notifications as read."""
        return await self.repo.mark_all_read(user_id)

    async def create_notification(self, user_id: str, opportunity_id: str, message: str):
        """Create a new notification for a targeted opportunity and user."""
        return await self.repo.create({
            "user_id": user_id,
            "opportunity_id": opportunity_id,
            "message": message,
            "status": "unread",
        })
