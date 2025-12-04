"""Stats API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.core.exceptions import UnauthorizedException
from app.domain.stats.service import StatsService
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
    sessions: list[dict]


# Dependency Injection
# Note: DatabaseSession is Annotated[AsyncSession, Depends(get_db)]
# This is FastAPI's recommended pattern. Type checkers may show warnings,
# but this is correct at runtime - FastAPI extracts Depends() automatically.
def get_session_history_repository(db: DatabaseSession) -> SessionHistoryRepository:  # type: ignore[valid-type]
    """Get session history repository."""
    return SessionHistoryRepository(db)


def get_stats_service(
    repo: Annotated[SessionHistoryRepository, Depends(get_session_history_repository)],
) -> StatsService:
    """Get stats service."""
    return StatsService(repo)


# Endpoints
@router.post(
    "/session",
    response_model=SessionRecordResponse,
    status_code=status.HTTP_201_CREATED,
)
async def record_session(
    data: SessionRecordRequest,
    service: Annotated[StatsService, Depends(get_stats_service)],
) -> SessionRecordResponse:
    """Record a completed pomodoro session.

    Args:
        data: Session details (user_id, room_id, session_type, duration_minutes)
        service: Stats service

    Returns:
        Session record confirmation with session_id
    """
    result = await service.record_session(
        user_id=data.user_id,
        room_id=data.room_id,
        session_type=data.session_type,
        duration_minutes=data.duration_minutes,
    )
    return SessionRecordResponse(**result)


@router.get("/user/{user_id}", response_model=UserStatsResponse)
async def get_user_stats(
    user_id: str,
    service: Annotated[StatsService, Depends(get_stats_service)],
    days: int = Query(7, ge=1, le=365),
) -> UserStatsResponse:
    """Get user statistics for the last N days.

    Args:
        user_id: User identifier
        days: Number of days to look back (default: 7)
        service: Stats service

    Returns:
        User statistics including total focus time, sessions, and session history

    Raises:
        HTTPException: If user not found or invalid parameters
    """
    try:
        stats = await service.get_user_stats(user_id, days)
        return UserStatsResponse(**stats)
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
