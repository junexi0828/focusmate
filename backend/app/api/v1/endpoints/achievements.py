"""Achievement API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.exceptions import ValidationException
from app.domain.achievement.schemas import (
    AchievementCreate,
    AchievementProgressResponse,
    AchievementResponse,
    UserAchievementResponse,
)
from app.domain.achievement.service import AchievementService
from app.infrastructure.database.session import DatabaseSession
from app.infrastructure.repositories.achievement_repository import (
    AchievementRepository,
    UserAchievementRepository,
)
from app.infrastructure.repositories.community_repository import PostRepository
from app.infrastructure.repositories.session_history_repository import SessionHistoryRepository
from app.infrastructure.repositories.user_repository import UserRepository


router = APIRouter(prefix="/achievements", tags=["achievements"])


# Dependency Injection
def get_achievement_repository(db: DatabaseSession) -> AchievementRepository:
    """Get achievement repository."""
    return AchievementRepository(db)


def get_user_achievement_repository(db: DatabaseSession) -> UserAchievementRepository:
    """Get user achievement repository."""
    return UserAchievementRepository(db)


def get_user_repository(db: DatabaseSession) -> UserRepository:
    """Get user repository."""
    return UserRepository(db)


def get_post_repository(db: DatabaseSession) -> PostRepository:
    """Get post repository."""
    return PostRepository(db)


def get_session_history_repository(db: DatabaseSession) -> SessionHistoryRepository:
    """Get session history repository."""
    return SessionHistoryRepository(db)


def get_achievement_service(
    achievement_repo: Annotated[AchievementRepository, Depends(get_achievement_repository)],
    user_achievement_repo: Annotated[UserAchievementRepository, Depends(get_user_achievement_repository)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    post_repo: Annotated[PostRepository, Depends(get_post_repository)],
    session_repo: Annotated[SessionHistoryRepository, Depends(get_session_history_repository)],
) -> AchievementService:
    """Get achievement service."""
    return AchievementService(achievement_repo, user_achievement_repo, user_repo, post_repo, session_repo)


# Endpoints
@router.post("/", response_model=AchievementResponse, status_code=status.HTTP_201_CREATED)
async def create_achievement(
    data: AchievementCreate,
    service: Annotated[AchievementService, Depends(get_achievement_service)],
) -> AchievementResponse:
    """Create a new achievement definition.

    Args:
        data: Achievement details
        service: Achievement service

    Returns:
        Created achievement

    Raises:
        HTTPException: If achievement name already exists
    """
    try:
        return await service.create_achievement(data)
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.get("/", response_model=list[AchievementResponse])
async def get_all_achievements(
    service: Annotated[AchievementService, Depends(get_achievement_service)],
) -> list[AchievementResponse]:
    """Get all active achievements.

    Args:
        service: Achievement service

    Returns:
        List of all active achievements
    """
    return await service.get_all_achievements()


@router.get("/category/{category}", response_model=list[AchievementResponse])
async def get_achievements_by_category(
    category: str,
    service: Annotated[AchievementService, Depends(get_achievement_service)],
) -> list[AchievementResponse]:
    """Get achievements by category.

    Args:
        category: Achievement category (sessions, time, streak, social)
        service: Achievement service

    Returns:
        List of achievements in the category

    Raises:
        HTTPException: If category is invalid
    """
    valid_categories = ["sessions", "time", "streak", "social"]
    if category not in valid_categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
        )

    return await service.get_achievements_by_category(category)


@router.get("/user/{user_id}", response_model=list[UserAchievementResponse])
async def get_user_achievements(
    user_id: str,
    service: Annotated[AchievementService, Depends(get_achievement_service)],
) -> list[UserAchievementResponse]:
    """Get all unlocked achievements for a user.

    Args:
        user_id: User identifier
        service: Achievement service

    Returns:
        List of user's unlocked achievements
    """
    return await service.get_user_achievements(user_id)


@router.get("/user/{user_id}/progress", response_model=list[AchievementProgressResponse])
async def get_user_achievement_progress(
    user_id: str,
    service: Annotated[AchievementService, Depends(get_achievement_service)],
) -> list[AchievementProgressResponse]:
    """Get achievement progress for a user across all achievements.

    Args:
        user_id: User identifier
        service: Achievement service

    Returns:
        List of achievements with progress and unlock status
    """
    return await service.get_user_achievement_progress(user_id)


@router.post("/user/{user_id}/check", response_model=list[UserAchievementResponse])
async def check_and_unlock_achievements(
    user_id: str,
    service: Annotated[AchievementService, Depends(get_achievement_service)],
) -> list[UserAchievementResponse]:
    """Check user progress and unlock any newly achieved achievements.

    This endpoint should be called after significant user actions
    (completing sessions, posting in community, etc.)

    Args:
        user_id: User identifier
        service: Achievement service

    Returns:
        List of newly unlocked achievements (empty if none)
    """
    return await service.check_and_unlock_achievements(user_id)
