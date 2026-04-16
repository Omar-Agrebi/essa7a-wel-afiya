"""Security utilities for password hashing and JWT token management."""
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status

from app.core.config import settings

# ---------------------------------------------------------------------------
# Password hashing context — bcrypt scheme
# ---------------------------------------------------------------------------
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT algorithm
_ALGORITHM = "HS256"
_DEFAULT_EXPIRY_HOURS = 24


def hash_password(plain: str) -> str:
    """Hash a plain-text password using bcrypt.

    Args:
        plain: The raw password string provided by the user.

    Returns:
        The bcrypt-hashed representation of the password.
    """
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain-text password against a stored bcrypt hash.

    Args:
        plain:  The raw password provided at login.
        hashed: The stored hashed password retrieved from the database.

    Returns:
        True if the password matches the hash, False otherwise.
    """
    return _pwd_context.verify(plain, hashed)


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token.

    The token payload will always contain:
    - ``sub``: the user_id (cast to string)
    - ``exp``: the expiry timestamp (UTC)

    Any additional keys supplied in *data* are merged into the payload.

    Args:
        data:          A dict containing at minimum ``{"sub": <user_id>}``.
        expires_delta: Custom expiry duration. Defaults to 24 hours.

    Returns:
        A signed JWT string.
    """
    payload = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta is not None else timedelta(hours=_DEFAULT_EXPIRY_HOURS)
    )
    payload["exp"] = expire
    # Ensure sub is always a plain string (UUID-safe)
    if "sub" in payload:
        payload["sub"] = str(payload["sub"])

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and verify a JWT access token.

    Args:
        token: The raw Bearer JWT string to decode.

    Returns:
        The decoded payload as a dict.

    Raises:
        HTTPException 401: If the token is expired, malformed, or the
                           ``sub`` claim is missing.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[_ALGORITHM])
        subject: str | None = payload.get("sub")
        if subject is None:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception
