"""Business logic service for the User domain."""
from uuid import UUID
from datetime import timedelta

from fastapi import HTTPException, status

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.api.schemas.user_schema import UserCreate, UserUpdate
from app.core import security


class UserService:
    """Service layer for all user-related business operations.

    Handles registration, authentication, profile management, and token
    issuance.  All DB access is delegated to :class:`UserRepository`.
    No SQLAlchemy imports or ML logic appear in this module.
    """

    def __init__(self, repo: UserRepository) -> None:
        """Initialise the service with its repository dependency.

        Args:
            repo: A :class:`UserRepository` instance injected by the FastAPI
                  dependency system or created directly by tests / agents.
        """
        self.repo = repo

    # ------------------------------------------------------------------
    # Registration & authentication
    # ------------------------------------------------------------------

    async def register_user(self, data: UserCreate) -> User:
        """Register a new user account.

        The plain-text password is hashed before persistence.  The raw
        password is never stored.

        Args:
            data: Validated :class:`UserCreate` schema containing name,
                  email, password, skills, interests, and academic level.

        Returns:
            The newly created :class:`User` ORM object.

        Raises:
            HTTPException 409: When a user with the same email already exists.
        """
        existing = await self.repo.get_by_email(data.email)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A user with email '{data.email}' is already registered.",
            )

        user_dict = data.model_dump(exclude={"password"})
        user_dict["hashed_password"] = security.hash_password(data.password)
        return await self.repo.create(user_dict)

    async def authenticate_user(self, email: str, password: str) -> User | None:
        """Verify credentials and return the matching user, or None.

        Args:
            email:    The email address provided at login.
            password: The plain-text password provided at login.

        Returns:
            The :class:`User` ORM object if credentials are valid, else ``None``.
        """
        user = await self.repo.get_by_email(email)
        if user is None:
            return None
        if not security.verify_password(password, user.hashed_password):
            return None
        return user

    def create_access_token(self, user_id: UUID) -> str:
        """Issue a signed JWT access token for the given user.

        Args:
            user_id: The UUID primary key of the authenticated user.

        Returns:
            A signed JWT string with a 24-hour expiry.
        """
        return security.create_access_token(
            data={"sub": str(user_id)},
            expires_delta=timedelta(hours=24),
        )

    # ------------------------------------------------------------------
    # Query methods
    # ------------------------------------------------------------------

    async def get_user(self, user_id: UUID) -> User:
        """Retrieve a user by their primary key.

        Args:
            user_id: The UUID primary key of the user to fetch.

        Returns:
            The matching :class:`User` ORM object.

        Raises:
            HTTPException 404: When no user with the given ID exists.
        """
        user = await self.repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id '{user_id}' not found.",
            )
        return user

    async def get_user_by_email(self, email: str) -> User | None:
        """Retrieve a user by their email address, returning None if absent.

        Args:
            email: The email address to look up.

        Returns:
            The :class:`User` ORM object, or ``None`` if not found.
        """
        return await self.repo.get_by_email(email)

    async def get_all_users(self) -> list[User]:
        """Return all registered users without pagination.

        Used by the pipeline's recommendation stage to iterate over every
        user and compute personalised scores.

        Returns:
            A list of :class:`User` ORM objects ordered by creation date.
        """
        return await self.repo.get_all_users()

    # ------------------------------------------------------------------
    # Mutation methods
    # ------------------------------------------------------------------

    async def update_profile(self, user_id: UUID, data: UserUpdate) -> User:
        """Apply a partial profile update for a user.

        Args:
            user_id: The UUID of the user to update.
            data:    Validated :class:`UserUpdate` schema.  Only non-None
                     fields are applied.

        Returns:
            The updated :class:`User` ORM object.

        Raises:
            HTTPException 404: When no user with the given ID exists.
        """
        # Confirm existence before attempting update.
        await self.get_user(user_id)

        update_data = data.model_dump(exclude_none=True)
        updated = await self.repo.update(user_id, update_data)
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id '{user_id}' not found.",
            )
        return updated

    async def update_skills(self, user_id: UUID, skills: list[str]) -> User:
        """Replace the skill list for a specific user.

        Args:
            user_id: The UUID of the user whose skills are being updated.
            skills:  The new list of skill strings to persist.

        Returns:
            The updated :class:`User` ORM object.

        Raises:
            HTTPException 404: When no user with the given ID exists.
        """
        updated = await self.repo.update_skills(user_id, skills)
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id '{user_id}' not found.",
            )
        return updated
