"""Pydantic v2 schemas for the User domain."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from app.core.constants import UserLevel


class UserCreate(BaseModel):
    """Schema for registering a new user account.

    The ``password`` field is validated to enforce a minimum length of
    8 characters.  It is **never** included in any response schema.
    """

    model_config = ConfigDict(from_attributes=True)

    name: str
    email: EmailStr
    password: str
    skills: list[str] = []
    interests: list[str] = []
    level: UserLevel

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        """Enforce a minimum password length of 8 characters."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        return v


class UserUpdate(BaseModel):
    """Schema for updating an existing user's profile.

    All fields are optional; only the supplied fields will be applied.
    The ``hashed_password`` is **never** updated through this schema.
    """

    model_config = ConfigDict(from_attributes=True)

    name: str | None = None
    email: EmailStr | None = None
    skills: list[str] | None = None
    interests: list[str] | None = None
    level: UserLevel | None = None


class UserRead(BaseModel):
    """Schema returned to API clients representing a user's public profile.

    Critically, ``hashed_password`` is **excluded** and will never appear
    in any serialised response.
    """

    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    name: str
    email: str
    skills: list[str]
    interests: list[str]
    level: UserLevel
    created_at: datetime


class UserLogin(BaseModel):
    """Schema for the login request body."""

    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema returned after a successful authentication.

    Contains the JWT access token, its type (always ``"bearer"``), and a
    fully populated :class:`UserRead` payload for immediate use by the
    frontend.
    """

    model_config = ConfigDict(from_attributes=True)

    access_token: str
    token_type: str = "bearer"
    user: UserRead
