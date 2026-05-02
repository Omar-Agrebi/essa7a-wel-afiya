from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List

from app.api.schemas.user_schema import UserCreate, UserLogin, UserRead, UserUpdate, TokenResponse
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from database.session import get_db
from app.api.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """Service factory for UserService."""
    return UserService(UserRepository(db))

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    """Register a new user."""
    return await service.register_user(data)

@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserLogin,
    service: UserService = Depends(get_user_service)
):
    """Login to obtain a JWT access token."""
    user = await service.authenticate_user(data.email, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = await service.create_access_token(user.user_id)
    return TokenResponse(access_token=access_token, token_type="bearer", user=user)

@router.get("/me", response_model=UserRead)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """Get the currently logged-in user details."""
    return current_user

@router.put("/me", response_model=UserRead)
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """Update profile information for the current user."""
    return await service.update_profile(current_user.user_id, data)

@router.put("/me/skills", response_model=UserRead)
async def update_skills(
    payload: Dict[str, List[str]],
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """Update the skills array for the current user."""
    skills = payload.get("skills", [])
    return await service.update_skills(current_user.user_id, skills)

@router.put("/me/interests", response_model=UserRead)
async def update_interests(
    payload: Dict[str, List[str]],
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """Update the interests array for the current user."""
    interests = payload.get("interests", [])
    data = UserUpdate(interests=interests)
    return await service.update_profile(current_user.user_id, data)
