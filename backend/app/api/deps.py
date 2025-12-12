"""API dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.domain.room.service import RoomService
from app.infrastructure.database.session import get_db
from app.infrastructure.repositories.room_repository import RoomRepository
from app.infrastructure.repositories.timer_repository import TimerRepository
from app.infrastructure.repositories.user_repository import UserRepository

DatabaseSession = Annotated[AsyncSession, Depends(get_db)]

security = HTTPBearer()


async def get_current_user(
    db: DatabaseSession,
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Get current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer token credentials
        db: Database session (injected via dependency)

    Returns:
        User dictionary with id, email, username

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials

    try:
        # Decode JWT token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials: missing user ID",
            )
    except JWTError as e:
        # Log the actual error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"JWT decode error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
        )

    # Get user from database
    # db is injected via DatabaseSession dependency
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated",
        )
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "is_admin": user.is_admin,
    }


def get_room_repository(db: DatabaseSession) -> RoomRepository:
    """Get room repository."""
    return RoomRepository(db)


def get_timer_repository(db: DatabaseSession) -> TimerRepository:
    """Get timer repository."""
    return TimerRepository(db)


def get_room_service(repo: Annotated[RoomRepository, Depends(get_room_repository)]) -> RoomService:
    """Get room service."""
    return RoomService(repo)
