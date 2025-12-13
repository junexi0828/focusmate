"""Authentication and User Profile API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.exceptions import UnauthorizedException, ValidationException
from app.domain.user.schemas import TokenResponse, UserLogin, UserProfileUpdate, UserRegister, UserResponse
from app.domain.user.service import UserService
from app.infrastructure.database.session import DatabaseSession
from app.infrastructure.repositories.user_repository import UserRepository

router = APIRouter(prefix="/auth", tags=["auth"])


def get_user_repository(db: DatabaseSession) -> UserRepository:
    """Get user repository."""
    return UserRepository(db)


def get_user_service(repo: Annotated[UserRepository, Depends(get_user_repository)]) -> UserService:
    """Get user service."""
    return UserService(repo)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserRegister,
    service: Annotated[UserService, Depends(get_user_service)],
) -> TokenResponse:
    """Register a new user."""
    try:
        return await service.register(data)
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again later.",
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserLogin,
    service: Annotated[UserService, Depends(get_user_service)],
) -> TokenResponse:
    """Login user and return JWT token."""
    try:
        return await service.login(data)
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Login error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again later.",
        )


@router.get("/profile/{user_id}", response_model=UserResponse)
async def get_profile(
    user_id: str,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    """Get user profile by ID.

    Args:
        user_id: User identifier
        service: User service

    Returns:
        User profile with stats

    Raises:
        HTTPException: If user not found
    """
    try:
        return await service.get_profile(user_id)
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.put("/profile/{user_id}", response_model=UserResponse)
async def update_profile(
    user_id: str,
    data: UserProfileUpdate,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    """Update user profile.

    Args:
        user_id: User identifier
        data: Profile updates (username, bio)
        service: User service

    Returns:
        Updated user profile

    Raises:
        HTTPException: If user not found
    """
    try:
        return await service.update_profile(user_id, data)
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
