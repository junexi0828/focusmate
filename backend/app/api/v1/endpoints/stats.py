"""Stats API endpoints."""

from datetime import UTC, datetime
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.api.deps import get_current_user
from app.core.exceptions import UnauthorizedException
from app.domain.stats.schemas import (
    ManualSessionCreate,
    ManualSessionResponse,
    UserGoalCreate,
    UserGoalResponse,
)
from app.domain.stats.service import StatsService
from app.infrastructure.database.models.user_stats import ManualSession, UserGoal
from app.infrastructure.database.session import DatabaseSession
from app.infrastructure.repositories.session_history_repository import (
    SessionHistoryRepository,
)


router = APIRouter(prefix="/stats", tags=["stats"])


# Request/Response Schemas
class SessionRecordRequest(BaseModel):
    """Request to record a completed session."""

    user_id: str = Field(..., min_length=1, max_length=36)
    room_id: str = Field(..., min_length=1, max_length=36)
    session_type: str = Field(..., pattern="^(work|break)$")
    duration_minutes: int = Field(..., gt=0, le=120)


class SessionRecordResponse(BaseModel):
    """Response after recording a session."""

    status: str
    session_id: str


class UserStatsResponse(BaseModel):
    """User statistics response."""

    total_focus_time: int
    total_sessions: int
    average_session: int
    sessions: list[
        dict
    ]  # List of session records with session_id, user_id, room_id, session_type, duration_minutes, completed_at


class HourlyPatternResponse(BaseModel):
    """Hourly focus pattern response for radar chart."""

    hourly_focus_time: list[int]  # 24 hours (0-23)
    total_days: int
    peak_hour: int | None = None


class MonthlyComparisonResponse(BaseModel):
    """Monthly comparison response for line chart."""

    monthly_data: list[dict]
    total_months: int


class GoalAchievementResponse(BaseModel):
    """Goal achievement response for progress ring."""

    goal_type: str
    goal_value: int
    current_value: int
    achievement_rate: int  # 0-100
    period: str
    is_achieved: bool
    remaining: int


# Dependency Injection
# Note: DatabaseSession is Annotated[AsyncSession, Depends(get_db)]
# This is FastAPI's recommended pattern. Type checkers may show warnings,
# but this is correct at runtime - FastAPI extracts Depends() automatically.
def get_session_history_repository(db: DatabaseSession) -> SessionHistoryRepository:  # type: ignore[valid-type]
    """Get session history repository."""
    return SessionHistoryRepository(db)


def get_stats_service(
    repo: Annotated[SessionHistoryRepository, Depends(get_session_history_repository)],
    db: DatabaseSession,
) -> StatsService:
    """Get stats service."""
    return StatsService(repo, db)


# Endpoints
@router.post(
    "/session",
    response_model=SessionRecordResponse,
    status_code=status.HTTP_201_CREATED,
)
async def record_session(
    data: SessionRecordRequest,
    service: Annotated[StatsService, Depends(get_stats_service)],
    db: DatabaseSession,
) -> SessionRecordResponse:
    """Record a completed pomodoro session.

    Args:
        data: Session details (user_id, room_id, session_type, duration_minutes)
        service: Stats service
        db: Database session

    Returns:
        Session record confirmation with session_id
    """
    result = await service.record_session(
        user_id=data.user_id,
        room_id=data.room_id,
        session_type=data.session_type,
        duration_minutes=data.duration_minutes,
    )

    # Check and unlock achievements after session completion
    try:
        from app.domain.achievement.service import AchievementService
        from app.infrastructure.repositories.achievement_repository import (
            AchievementRepository,
            UserAchievementRepository,
        )
        from app.infrastructure.repositories.community_repository import PostRepository
        from app.infrastructure.repositories.session_history_repository import (
            SessionHistoryRepository,
        )
        from app.infrastructure.repositories.user_repository import UserRepository

        achievement_repo = AchievementRepository(db)
        user_achievement_repo = UserAchievementRepository(db)
        user_repo = UserRepository(db)
        post_repo = PostRepository(db)
        session_repo = SessionHistoryRepository(db)

        achievement_service = AchievementService(
            achievement_repo,
            user_achievement_repo,
            user_repo,
            post_repo,
            session_repo,
        )

        # Check achievements in background (don't wait for result)
        await achievement_service.check_and_unlock_achievements(data.user_id)
    except Exception as e:
        # Log error but don't fail the session recording
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to check achievements after session: {e}")

    return SessionRecordResponse(**result)


@router.get("/user/{user_id}", response_model=UserStatsResponse)
async def get_user_stats(
    user_id: str,
    service: Annotated[StatsService, Depends(get_stats_service)],
    days: int = Query(7, ge=1, le=365),
    start_date: str | None = Query(
        None, description="Start date (ISO format: YYYY-MM-DD)"
    ),
    end_date: str | None = Query(
        None, description="End date (ISO format: YYYY-MM-DD)"
    ),
) -> UserStatsResponse:
    """Get user statistics for the last N days or date range.

    Args:
        user_id: User identifier
        days: Number of days to look back (default: 7, used if start_date/end_date not provided)
        start_date: Start date for date range filtering (ISO format: YYYY-MM-DD)
        end_date: End date for date range filtering (ISO format: YYYY-MM-DD)
        service: Stats service

    Returns:
        User statistics including total focus time, sessions, and session history

    Raises:
        HTTPException: If user not found or invalid parameters
    """
    try:
        start_dt = None
        end_dt = None

        if start_date and end_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date format. Use ISO format (YYYY-MM-DD)",
                ) from e

        stats = await service.get_user_stats(user_id, days, start_dt, end_dt)
        return UserStatsResponse(**stats)
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve stats: {e!s}",
        ) from e


@router.get("/user/{user_id}/hourly-pattern", response_model=HourlyPatternResponse)
async def get_hourly_pattern(
    user_id: str,
    service: Annotated[StatsService, Depends(get_stats_service)],
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    offset_hours: int = Query(0, ge=-12, le=14, description="Timezone offset in hours"),
) -> HourlyPatternResponse:
    """Get hourly focus pattern for radar chart.

    Args:
        user_id: User identifier
        days: Number of days to analyze (default: 30)
        offset_hours: Timezone offset in hours (default: 0)
        service: Stats service

    Returns:
        Hourly focus time distribution (24 hours: 0-23)

    Raises:
        HTTPException: If user not found or invalid parameters
    """
    try:
        pattern = await service.get_hourly_pattern(user_id, days, offset_hours)
        return HourlyPatternResponse(**pattern)
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve hourly pattern: {e!s}",
        ) from e


@router.get(
    "/user/{user_id}/monthly-comparison", response_model=MonthlyComparisonResponse
)
async def get_monthly_comparison(
    user_id: str,
    service: Annotated[StatsService, Depends(get_stats_service)],
    months: int = Query(6, ge=1, le=24, description="Number of months to compare"),
) -> MonthlyComparisonResponse:
    """Get monthly comparison data for line chart.

    Args:
        user_id: User identifier
        months: Number of months to compare (default: 6)
        service: Stats service

    Returns:
        Monthly statistics for comparison

    Raises:
        HTTPException: If user not found or invalid parameters
    """
    try:
        comparison = await service.get_monthly_comparison(user_id, months)
        return MonthlyComparisonResponse(**comparison)
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve monthly comparison: {e!s}",
        ) from e


@router.get("/user/{user_id}/goal-achievement", response_model=GoalAchievementResponse)
async def get_goal_achievement(
    user_id: str,
    service: Annotated[StatsService, Depends(get_stats_service)],
    goal_type: str = Query(
        ..., pattern="^(focus_time|sessions)$", description="Type of goal"
    ),
    goal_value: int = Query(..., gt=0, description="Target value for the goal"),
    period: str = Query(
        "week", pattern="^(day|week|month)$", description="Time period"
    ),
) -> GoalAchievementResponse:
    """Get goal achievement rate for progress ring.

    Args:
        user_id: User identifier
        goal_type: Type of goal ('focus_time' or 'sessions')
        goal_value: Target value for the goal
        period: Time period ('day', 'week', 'month')
        service: Stats service

    Returns:
        Goal achievement statistics with progress rate

    Raises:
        HTTPException: If user not found or invalid parameters
    """
    try:
        achievement = await service.get_goal_achievement(
            user_id, goal_type, goal_value, period
        )
        return GoalAchievementResponse(**achievement)
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve goal achievement: {e!s}",
        ) from e


# User Goals Endpoints
@router.post(
    "/goals", response_model=UserGoalResponse, status_code=status.HTTP_201_CREATED
)
async def save_user_goal(
    goal_data: UserGoalCreate,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: DatabaseSession,
) -> UserGoalResponse:
    """Save or update user's goals."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    user_id = current_user["id"]

    # Check if user already has goals
    stmt = select(UserGoal).where(UserGoal.user_id == user_id)
    result = await db.execute(stmt)
    existing_goal = result.scalar_one_or_none()

    if existing_goal:
        # Update existing
        existing_goal.daily_goal_minutes = goal_data.daily_goal_minutes
        existing_goal.weekly_goal_sessions = goal_data.weekly_goal_sessions
        await db.commit()
        await db.refresh(existing_goal)
        return UserGoalResponse.model_validate(existing_goal)
    # Create new
    new_goal = UserGoal(
        id=uuid4(),
        user_id=user_id,
        daily_goal_minutes=goal_data.daily_goal_minutes,
        weekly_goal_sessions=goal_data.weekly_goal_sessions,
    )
    db.add(new_goal)
    await db.commit()
    await db.refresh(new_goal)
    return UserGoalResponse.model_validate(new_goal)


@router.get("/goals", response_model=UserGoalResponse)
async def get_user_goal(
    current_user: Annotated[dict, Depends(get_current_user)],
    db: DatabaseSession,
) -> UserGoalResponse:
    """Get user's current goals."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    user_id = current_user["id"]

    stmt = (
        select(UserGoal)
        .where(UserGoal.user_id == user_id)
        .order_by(UserGoal.created_at.desc())
    )
    result = await db.execute(stmt)
    goals = result.scalars().all()

    if not goals:
        # Return default goals if none set
        return UserGoalResponse(
            id=uuid4(),
            user_id=user_id,
            daily_goal_minutes=120,
            weekly_goal_sessions=5,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

    # Use the most recent goal
    goal = goals[0]

    # Optional: If there are duplicates, we could log them or clean them up here
    # For now, we just return the most relevant one to avoid 404s
    return UserGoalResponse.model_validate(goal)


# Manual Session Endpoints
@router.post(
    "/sessions",
    response_model=ManualSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def save_manual_session(
    session_data: ManualSessionCreate,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: DatabaseSession,
) -> ManualSessionResponse:
    """Save a manually logged session."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    user_id = current_user["id"]

    new_session = ManualSession(
        id=uuid4(),
        user_id=user_id,
        duration_minutes=session_data.duration_minutes,
        session_type=session_data.session_type,
        completed_at=session_data.completed_at,
    )

    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)

    return ManualSessionResponse.model_validate(new_session)


@router.get("/sessions", response_model=list[ManualSessionResponse])
async def get_manual_sessions(
    current_user: Annotated[dict, Depends(get_current_user)],
    db: DatabaseSession,
    limit: int = 100,
) -> list[ManualSessionResponse]:
    """Get user's manual sessions."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    user_id = current_user["id"]

    from sqlalchemy import desc

    stmt = (
        select(ManualSession)
        .where(ManualSession.user_id == user_id)
        .order_by(desc(ManualSession.completed_at))
        .limit(limit)
    )
    result = await db.execute(stmt)
    sessions = result.scalars().all()

    return [ManualSessionResponse.model_validate(s) for s in sessions]
