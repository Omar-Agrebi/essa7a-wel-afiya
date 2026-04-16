"""FastAPI dependency for resolving the currently authenticated user."""
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.models.user import User
from app.repositories.user_repository import UserRepository
from database.session import get_db

# The tokenUrl must match the login endpoint path so that FastAPI's
# interactive Swagger docs can obtain tokens automatically.
_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


async def get_current_user(
    token: str = Depends(_oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """FastAPI dependency that resolves the authenticated user from a JWT.

    Decodes the Bearer token, extracts the ``sub`` claim (user UUID),
    and loads the corresponding user from the database.

    Args:
        token: The raw JWT Bearer string extracted from the Authorization
               header by :class:`OAuth2PasswordBearer`.
        db:    An async SQLAlchemy session provided by :func:`get_db`.

    Returns:
        The authenticated :class:`User` ORM object.

    Raises:
        HTTPException 401: When the token is invalid, expired, or the
                           referenced user no longer exists in the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode and verify the token — raises 401 internally on failure.
    payload = security.decode_token(token)

    user_id_str: str | None = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    try:
        user_id = UUID(user_id_str)
    except (ValueError, AttributeError):
        raise credentials_exception

    # Load the user from DB to confirm they still exist.
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if user is None:
        raise credentials_exception

    return user
