from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from app.api.schemas.notification_schema import NotificationRead
from app.services.notification_service import NotificationService
from app.repositories.notification_repository import NotificationRepository
from app.database.session import get_db
from app.api.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/notifications", tags=["notifications"])

def get_notification_service(db: AsyncSession = Depends(get_db)) -> NotificationService:
    """Service factory for NotificationService."""
    return NotificationService(NotificationRepository(db))

@router.get("/", response_model=List[NotificationRead])
async def get_all_notifications(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    """Get all notifications for the active user."""
    return await service.get_user_notifications(current_user.user_id)

@router.get("/unread", response_model=List[NotificationRead])
async def get_unread_notifications(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    """Get only unread notifications for a user."""
    return await service.get_unread(current_user.user_id)

@router.get("/unread/count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    """Count the number of unread notifications for a user."""
    count = await service.count_unread(current_user.user_id)
    return {"count": count}

@router.put("/{notification_id}/read", response_model=NotificationRead)
async def mark_notification_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    """Mark a single notification as read."""
    # Note: Service layer handles the 404 Exception inside mark_read.
    return await service.mark_read(notification_id)

@router.put("/read-all")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    """Mark all of a user's notifications as read."""
    updated_count = await service.mark_all_read(current_user.user_id)
    return {"updated": updated_count}
