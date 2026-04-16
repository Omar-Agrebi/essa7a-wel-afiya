"""Business logic service for the Notification domain."""
from uuid import UUID

from fastapi import HTTPException, status

from app.models.notification import Notification
from app.repositories.notification_repository import NotificationRepository


class NotificationService:
    """Service layer for all notification-related business operations.

    Manages creation, retrieval, and status transitions of user
    notifications.  All DB access is delegated to
    :class:`NotificationRepository`.  No ML or SQLAlchemy logic lives here.
    """

    def __init__(self, repo: NotificationRepository) -> None:
        """Initialise the service with its repository dependency.

        Args:
            repo: A :class:`NotificationRepository` instance injected by
                  the FastAPI dependency system or created directly by agents.
        """
        self.repo = repo

    async def get_user_notifications(self, user_id: UUID) -> list[Notification]:
        """Retrieve all notifications for a user, newest first.

        Args:
            user_id: The UUID of the user whose notifications to fetch.

        Returns:
            A list of :class:`Notification` ORM objects ordered by
            timestamp descending.
        """
        return await self.repo.get_by_user(user_id)

    async def get_unread(self, user_id: UUID) -> list[Notification]:
        """Retrieve only unread notifications for a user.

        Args:
            user_id: The UUID of the user to query.

        Returns:
            A list of unread :class:`Notification` ORM objects ordered by
            timestamp descending.
        """
        return await self.repo.get_unread(user_id)

    async def count_unread(self, user_id: UUID) -> int:
        """Return the count of unread notifications for a user.

        Used to populate the unread badge in the frontend navbar.

        Args:
            user_id: The UUID of the user to count for.

        Returns:
            An integer count of unread notifications (may be zero).
        """
        return await self.repo.count_unread(user_id)

    async def mark_read(self, notification_id: UUID) -> Notification:
        """Mark a single notification as read.

        Args:
            notification_id: The UUID of the notification to mark.

        Returns:
            The updated :class:`Notification` ORM object with status ``read``.

        Raises:
            HTTPException 404: When no notification with the given ID exists.
        """
        notification = await self.repo.mark_as_read(notification_id)
        if notification is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notification with id '{notification_id}' not found.",
            )
        return notification

    async def mark_all_read(self, user_id: UUID) -> int:
        """Mark all unread notifications for a user as read.

        Args:
            user_id: The UUID of the user whose notifications to mark.

        Returns:
            The number of notification records that were updated.
        """
        return await self.repo.mark_all_read(user_id)

    async def create_notification(
        self,
        user_id: UUID,
        opportunity_id: UUID,
        message: str,
    ) -> Notification:
        """Create a new dashboard notification linking a user to an opportunity.

        Called by :class:`AgentNotification` after detecting a deadline match.

        Args:
            user_id:        The UUID of the target user.
            opportunity_id: The UUID of the related opportunity.
            message:        The human-readable notification message to display.

        Returns:
            The newly created :class:`Notification` ORM object.
        """
        notification_data = {
            "user_id": user_id,
            "opportunity_id": opportunity_id,
            "message": message,
        }
        return await self.repo.create(notification_data)
