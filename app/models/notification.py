"""Notification model definition."""
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLEnum

from database.base import Base
from app.core.constants import NotificationStatus

if TYPE_CHECKING:
    from app.models.opportunity import Opportunity

class Notification(Base):
    """
    Represents an alert sent to a user regarding an opportunity.
    """
    __tablename__ = "notifications"

    notification_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.user_id"), nullable=False)
    opportunity_id: Mapped[str] = mapped_column(String(36), ForeignKey("opportunities.id"), nullable=False)
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="unread", nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationship: eagerly join the linked opportunity
    opportunity: Mapped["Opportunity"] = relationship("Opportunity", lazy="joined")

    __table_args__ = (
        Index('ix_notifications_user_id_status', 'user_id', 'status'),
    )
