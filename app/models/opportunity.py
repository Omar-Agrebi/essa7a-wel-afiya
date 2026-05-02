"""Opportunity model definition."""
import uuid
import json
from datetime import date
from sqlalchemy import String, Text, Enum as SQLEnum, Integer, Date, TypeDecorator
from sqlalchemy.orm import Mapped, mapped_column
from database.base import Base, TimestampMixin
from app.core.constants import OpportunityType, OpportunityCategory

# SQLite-compatible JSON array type
class JSONList(TypeDecorator):
    impl = Text
    cache_ok = True
    def process_bind_param(self, value, dialect):
        if value is None: return "[]"
        if isinstance(value, str): return value
        return json.dumps(value)
    def process_result_value(self, value, dialect):
        if not value: return []
        try: return json.loads(value)
        except: return []

class Opportunity(Base, TimestampMixin):
    """
    Represents an actionable opportunity (internship, scholarship, project, course, postdoc).
    """
    __tablename__ = "opportunities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    skills_required: Mapped[list] = mapped_column(JSONList, nullable=True, default=list)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    eligibility: Mapped[str | None] = mapped_column(String(500), nullable=True)
    deadline: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    source: Mapped[str] = mapped_column(String(200), nullable=False)
    url: Mapped[str] = mapped_column(String(1000), unique=True, nullable=False)
    cluster_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    cluster_label: Mapped[str | None] = mapped_column(String(200), nullable=True)
