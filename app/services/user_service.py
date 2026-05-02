
from fastapi import HTTPException, status
from app.repositories.user_repository import UserRepository
from app.api.schemas.user_schema import UserCreate, UserUpdate
from app.core.security import hash_password, verify_password, create_access_token as generate_access_token

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def register_user(self, data: UserCreate):
        """Register a new user."""
        existing_user = await self.repo.get_by_email(data.email)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        
        user_dict = data.model_dump()
        hashed_password = hash_password(user_dict.pop("password"))
        user_dict["hashed_password"] = hashed_password
        return await self.repo.create(user_dict)

    async def get_user(self, user_id: str):
        """Get user details by ID."""
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    async def get_user_by_email(self, email: str):
        """Get user details by email."""
        return await self.repo.get_by_email(email)

    async def update_profile(self, user_id: str, data: UserUpdate):
        """Update a user's profile."""
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return await self.repo.update(user_id, data.model_dump(exclude_unset=True))

    async def update_skills(self, user_id: str, skills: list[str]):
        """Update a user's skills explicitly."""
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return await self.repo.update_skills(user_id, skills)

    async def authenticate_user(self, email: str, password: str):
        """Authenticate a user and return the user object if successful."""
        user = await self.repo.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def create_access_token(self, user_id: str) -> str:
        """Create a JWT access token for the given user ID."""
        return generate_access_token(str(user_id))

    async def get_all_users(self):
        """Get all users, typically used by recommendation pipeline."""
        return await self.repo.get_all()
