from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.core.constants import UserLevel

class UserCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    email: EmailStr
    password: str = Field(min_length=8)
    skills: list[str] = []
    interests: list[str] = []
    level: UserLevel

class UserUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str | None = None
    email: EmailStr | None = None
    skills: list[str] | None = None
    interests: list[str] | None = None
    level: UserLevel | None = None

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: str
    name: str
    email: str
    skills: list[str]
    interests: list[str]
    level: str
    created_at: datetime

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    access_token: str
    token_type: str = "bearer"
    user: UserRead
