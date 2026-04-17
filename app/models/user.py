"""User model definition."""
import uuid
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy import Enum as SQLEnum

from database.base import Base, TimestampMixin
from app.core.constants import UserLevel

class User(Base, TimestampMixin):
    """
    Represents a registered user in the system.
    """
    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(300), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(500), nullable=False)
    skills: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    interests: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    level: Mapped[UserLevel] = mapped_column(
        SQLEnum(UserLevel, name="userlevel_enum"), nullable=False
    )
