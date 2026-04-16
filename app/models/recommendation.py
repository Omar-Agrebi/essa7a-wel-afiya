"""Recommendation model definition."""
import uuid
from sqlalchemy import Float, ForeignKey, UniqueConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime, timezone
from sqlalchemy import DateTime

from database.base import Base
from app.models.user import User
from app.models.opportunity import Opportunity

class Recommendation(Base):
    """
    Represents a matching recommendation of an opportunity for a given user.
    """
    __tablename__ = "recommendations"

    recommendation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False
    )
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("opportunities.id"), nullable=False
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)
    match_reasons: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint("user_id", "opportunity_id", name="uix_user_opportunity"),
    )

    user: Mapped["User"] = relationship()
    opportunity: Mapped["Opportunity"] = relationship(lazy="joined")
