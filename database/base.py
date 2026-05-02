"""Database declarative base and mixins."""
from datetime import datetime, timezone
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import DateTime

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy declarative models."""
    pass

class TimestampMixin:
    """Mixin to add typical created_at and updated_at columns."""
    
    @declared_attr
    def created_at(cls) -> Mapped[datetime]:
        """Automatically set to the current UTC timestamp on insert."""
        return mapped_column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            nullable=False
        )
        
    @declared_attr
    def updated_at(cls) -> Mapped[datetime]:
        """Automatically set to the current UTC timestamp on insert and update."""
        return mapped_column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            onupdate=lambda: datetime.now(timezone.utc),
            nullable=False
        )
