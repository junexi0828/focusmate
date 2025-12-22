"""API dependencies."""

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.domain.room.service import RoomService
from app.infrastructure.database.session import get_db
from app.infrastructure.repositories.room_repository import RoomRepository
from app.infrastructure.repositories.timer_repository import TimerRepository
from app.infrastructure.repositories.user_repository import UserRepository


DatabaseSession = Annotated[AsyncSession, Depends(get_db)]

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: DatabaseSession,
) -> dict | None:
    """Get current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer token credentials (optional)
        db: Database session from dependency injection

    Returns:
        User dictionary with id, email, username, or None if not authenticated

    Raises:
        HTTPException: If token is invalid or user not found (only if credentials provided)
    """
    # If no credentials provided, return None (optional auth)
    if not credentials:
        return None

    token = credentials.credentials

    try:
        # Decode JWT token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        # Invalid token, return None for optional auth
        return None

    # Get user from database using injected session
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user or not user.is_active:
        return None

    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "is_admin": user.is_admin,
    }


async def get_current_user_required(
    current_user: dict | None = Depends(get_current_user),
) -> dict:
    """Get current authenticated user (required).

    Args:
        current_user: User from get_current_user dependency

    Returns:
        User dictionary with id, email, username

    Raises:
        HTTPException: 401 if user is not authenticated
    """
    from fastapi import HTTPException, status

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


def get_room_repository(db: DatabaseSession) -> RoomRepository:
    """Get room repository."""
    return RoomRepository(db)


def get_timer_repository(db: DatabaseSession) -> TimerRepository:
    """Get timer repository."""
    return TimerRepository(db)


def get_room_service(repo: Annotated[RoomRepository, Depends(get_room_repository)]) -> RoomService:
    """Get room service."""
    return RoomService(repo)
