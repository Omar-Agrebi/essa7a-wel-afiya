import uuid
import json
from sqlalchemy import String, Text, TypeDecorator
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum as SQLEnum

from database.base import Base, TimestampMixin
from app.core.constants import UserLevel
from app.models.opportunity import JSONList

class User(Base, TimestampMixin):
    """
    Represents a registered user in the system.
    """
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(300), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(500), nullable=False)
    skills: Mapped[list] = mapped_column(JSONList, default=list)
    interests: Mapped[list] = mapped_column(JSONList, default=list)
    level: Mapped[str] = mapped_column(String(50), nullable=False)
