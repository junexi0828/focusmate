"""User Settings API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.core.exceptions import UnauthorizedException, ValidationException
from app.domain.settings.schemas import (
    EmailChangeRequest,
    PasswordChangeRequest,
    UserSettingsResponse,
    UserSettingsUpdate,
)
from app.domain.settings.service import UserSettingsService
from app.infrastructure.database.session import DatabaseSession
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.user_settings_repository import (
    UserSettingsRepository,
)


router = APIRouter(prefix="/settings", tags=["settings"])


# Dependency Injection
def get_user_repository(db: DatabaseSession) -> UserRepository:
    """Get user repository."""
    return UserRepository(db)


def get_settings_repository(db: DatabaseSession) -> UserSettingsRepository:
    """Get user settings repository."""
    return UserSettingsRepository(db)


def get_settings_service(
    settings_repo: Annotated[
        UserSettingsRepository, Depends(get_settings_repository)
    ],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserSettingsService:
    """Get user settings service."""
    return UserSettingsService(settings_repo, user_repo)


# Endpoints
@router.get("/", response_model=UserSettingsResponse)
async def get_my_settings(
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[UserSettingsService, Depends(get_settings_service)],
) -> UserSettingsResponse:
    """Get current user's settings.

    Args:
        current_user: Current authenticated user
        service: User settings service

    Returns:
        User settings
    """
    user_id = current_user["id"]
    return await service.get_settings(user_id)


@router.put("/", response_model=UserSettingsResponse)
async def update_my_settings(
    data: UserSettingsUpdate,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[UserSettingsService, Depends(get_settings_service)],
) -> UserSettingsResponse:
    """Update current user's settings.

    Args:
        data: Settings update data
        current_user: Current authenticated user
        service: User settings service

    Returns:
        Updated user settings
    """
    user_id = current_user["id"]
    return await service.update_settings(user_id, data)


@router.post("/password", status_code=status.HTTP_200_OK)
async def change_password(
    data: PasswordChangeRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[UserSettingsService, Depends(get_settings_service)],
) -> dict:
    """Change current user's password.

    Args:
        data: Password change data
        current_user: Current authenticated user
        service: User settings service

    Returns:
        Success message

    Raises:
        HTTPException: If current password is incorrect
    """
    user_id = current_user["id"]
    try:
        await service.change_password(user_id, data)
        return {"message": "Password changed successfully"}
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message)


@router.post("/email", status_code=status.HTTP_200_OK)
async def change_email(
    data: EmailChangeRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[UserSettingsService, Depends(get_settings_service)],
) -> dict:
    """Change current user's email.

    Args:
        data: Email change data
        current_user: Current authenticated user
        service: User settings service

    Returns:
        Success message

    Raises:
        HTTPException: If password is incorrect or email already exists
    """
    user_id = current_user["id"]
    try:
        await service.change_email(user_id, data)
        return {
            "message": "Email changed successfully. Please verify your new email address."
        }
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message)
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
