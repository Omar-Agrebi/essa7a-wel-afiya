"""Opportunity model definition."""
import uuid
from datetime import date
from sqlalchemy import String, Text, Enum as SQLEnum, Integer, Date
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, ARRAY

from database.base import Base, TimestampMixin
from app.core.constants import OpportunityType, OpportunityCategory

class Opportunity(Base, TimestampMixin):
    """
    Represents an actionable opportunity (internship, scholarship, project, course, postdoc).
    """
    __tablename__ = "opportunities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    type: Mapped[OpportunityType] = mapped_column(
        SQLEnum(OpportunityType, name="opportunitytype_enum"), nullable=False, index=True
    )
    category: Mapped[OpportunityCategory] = mapped_column(
        SQLEnum(OpportunityCategory, name="opportunitycategory_enum"), nullable=False, index=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    skills_required: Mapped[list[str] | None] = mapped_column(
        ARRAY(String), nullable=True, default=list
    )
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    eligibility: Mapped[str | None] = mapped_column(String(500), nullable=True)
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    source: Mapped[str] = mapped_column(String(200), nullable=False)
    url: Mapped[str] = mapped_column(String(1000), unique=True, nullable=False)
    cluster_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    cluster_label: Mapped[str | None] = mapped_column(String(200), nullable=True)
