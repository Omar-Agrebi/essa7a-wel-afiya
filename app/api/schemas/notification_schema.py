"""Pydantic v2 schemas for the Notification domain."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.api.schemas.opportunity_schema import OpportunityRead
from app.core.constants import NotificationStatus


class NotificationRead(BaseModel):
    """Schema returned to clients for a single notification.

    Includes the full :class:`OpportunityRead` payload so the frontend
    can render opportunity details without a second request.
    """

    model_config = ConfigDict(from_attributes=True)

    notification_id: UUID
    message: str
    status: NotificationStatus
    timestamp: datetime
    opportunity: OpportunityRead


class NotificationStatusUpdate(BaseModel):
    """Schema accepted when a caller updates the status of a notification.

    Used by the ``PUT /notifications/{id}/read`` endpoint to transition
    a notification between ``unread``, ``read``, or ``dismissed`` states.
    """

    model_config = ConfigDict(from_attributes=True)

    status: NotificationStatus
