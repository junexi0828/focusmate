"""Security utilities (JWT, password hashing).

Provides authentication and cryptography functions.
"""


from typing import Any, Dict, Optional
from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings
from datetime import UTC, datetime, timedelta


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """Create JWT access token.

    Args:
        data: Token payload
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password

    Returns:
        True if password matches
    """
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Hash password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def decode_jwt_token(token: str) -> dict[str, Any]:
    """Decode JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        jwt.JWTError: If token is invalid
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def create_refresh_token(user_id: str, token_id: str, family_id: str) -> str:
    """Create JWT refresh token.

    Args:
        user_id: User identifier
        token_id: Unique token identifier (jti claim)
        family_id: Token family identifier

    Returns:
        Encoded JWT refresh token
    """
    now = datetime.now(UTC)
    expires_at = now + timedelta(days=7)
    absolute_expires_at = now + timedelta(days=30)

    payload = {
        "sub": user_id,
        "jti": token_id,
        "token_type": "refresh",
        "family_id": family_id,
        "exp": int(expires_at.timestamp()),
        "absolute_exp": int(absolute_expires_at.timestamp()),
        "iat": int(now.timestamp())
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def validate_refresh_token(token: str) -> dict[str, Any]:
    """Validate refresh token and check critical claims.

    Args:
        token: JWT refresh token

    Returns:
        Decoded payload

    Raises:
        ValueError: If token type is invalid or absolute expiry exceeded
        jwt.JWTError: If token signature is invalid
    """
    payload = decode_jwt_token(token)

    # CRITICAL: Enforce token type
    if payload.get("token_type") != "refresh":
        raise ValueError("Invalid token type")

    # CRITICAL: Check absolute expiry
    absolute_exp = payload.get("absolute_exp")
    if not absolute_exp or datetime.fromtimestamp(absolute_exp, UTC) < datetime.now(UTC):
        raise ValueError("Absolute expiry exceeded - re-login required")

    return payload
