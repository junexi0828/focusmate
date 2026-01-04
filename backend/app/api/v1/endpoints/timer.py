"""Timer API endpoints."""


from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import DatabaseSession, get_current_user_required, get_room_repository, get_timer_repository
from app.core.exceptions import (
    InvalidTimerStateException,
    RoomNotFoundException,
    TimerNotFoundException,
)
from app.domain.timer.schemas import TimerStateResponse
from app.domain.timer.service import TimerService
from app.infrastructure.repositories.room_repository import RoomRepository
from app.infrastructure.repositories.timer_repository import TimerRepository


router = APIRouter(prefix="/timer", tags=["timer"])


def get_timer_service(
    timer_repo: Annotated[TimerRepository, Depends(get_timer_repository)],
    room_repo: Annotated[RoomRepository, Depends(get_room_repository)],
) -> TimerService:
    """Get timer service."""
    return TimerService(timer_repo, room_repo)


@router.get("/{room_id}", response_model=TimerStateResponse)
async def get_timer_state(
    room_id: str,
    service: Annotated[TimerService, Depends(get_timer_service)],
) -> TimerStateResponse:
    """Get current timer state for a room.

    Returns real-time calculated state including remaining seconds.
    """
    try:
        return await service.get_or_create_timer(room_id)
    except RoomNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e


@router.post("/{room_id}/start", response_model=TimerStateResponse)
async def start_timer(
    room_id: str,
    service: Annotated[TimerService, Depends(get_timer_service)],
) -> TimerStateResponse:
    """Start the timer.

    Transitions from IDLE or PAUSED to RUNNING.
    """
    try:
        return await service.start_timer(room_id)
    except TimerNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    except InvalidTimerStateException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message) from e


@router.post("/{room_id}/pause", response_model=TimerStateResponse)
async def pause_timer(
    room_id: str,
    service: Annotated[TimerService, Depends(get_timer_service)],
) -> TimerStateResponse:
    """Pause the timer.

    Transitions from RUNNING to PAUSED, saving remaining time.
    """
    try:
        return await service.pause_timer(room_id)
    except TimerNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    except InvalidTimerStateException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message) from e


@router.post("/{room_id}/resume", response_model=TimerStateResponse)
async def resume_timer(
    room_id: str,
    service: Annotated[TimerService, Depends(get_timer_service)],
) -> TimerStateResponse:
    """Resume the paused timer.

    Transitions from PAUSED to RUNNING, continuing from remaining time.
    """
    try:
        return await service.resume_timer(room_id)
    except TimerNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    except InvalidTimerStateException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message) from e


@router.post("/{room_id}/reset", response_model=TimerStateResponse)
async def reset_timer(
    room_id: str,
    service: Annotated[TimerService, Depends(get_timer_service)],
) -> TimerStateResponse:
    """Reset the timer to initial state.

    Returns timer to IDLE state with full duration.
    """
    try:
        return await service.reset_timer(room_id)
    except (TimerNotFoundException, RoomNotFoundException) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e


@router.post("/{room_id}/complete", response_model=TimerStateResponse)
async def complete_phase(
    room_id: str,
    current_user: Annotated[dict, Depends(get_current_user_required)],
    service: Annotated[TimerService, Depends(get_timer_service)],
    db: DatabaseSession,
) -> TimerStateResponse:
    """Complete current phase and transition to next phase.

    Transitions from WORK → BREAK or BREAK → WORK.
    Auto-starts break if auto_start_break is enabled.
    Automatically records session to session_history when work phase completes.
    """
    try:
        timer_response = await service.complete_phase(room_id)

        # ✅ 자동 세션 기록: WORK 단계 완료 시 세션 기록
        if timer_response.phase == "break":  # WORK → BREAK 전환 시
            from app.domain.stats.service import StatsService
            from app.infrastructure.repositories.session_history_repository import SessionHistoryRepository

            # ✅ 최적화: JOIN을 사용하여 단일 쿼리로 timer와 room 조회
            result = await service.timer_repo.get_with_room_by_room_id(room_id)

            if result:
                timer, room = result
                # 세션 기록
                session_repo = SessionHistoryRepository(db)
                stats_service = StatsService(session_repo, db)

                try:
                    await stats_service.record_session(
                        user_id=current_user["id"],
                        room_id=room_id,
                        session_type="work",
                        duration_minutes=room.work_duration,
                    )
                except Exception as e:
                    # 세션 기록 실패해도 타이머 완료는 성공으로 처리
                    import logging
                    logging.warning(f"Failed to record session after timer completion: {e}")


        return timer_response
    except TimerNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    except RoomNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    except InvalidTimerStateException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message) from e
