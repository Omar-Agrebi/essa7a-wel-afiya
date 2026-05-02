"""Recommendation model definition."""
import uuid
from sqlalchemy import Float, ForeignKey, UniqueConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from sqlalchemy import DateTime

from database.base import Base
from app.models.opportunity import JSONList

class Recommendation(Base):
    """
    Represents a matching recommendation of an opportunity for a given user.
    """
    __tablename__ = "recommendations"

    recommendation_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.user_id"), nullable=False)
    opportunity_id: Mapped[str] = mapped_column(String(36), ForeignKey("opportunities.id"), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    match_reasons: Mapped[list] = mapped_column(JSONList, default=list)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint("user_id", "opportunity_id", name="uix_user_opportunity"),
    )

    opportunity: Mapped["Opportunity"] = relationship(lazy="joined")  # type: ignore
