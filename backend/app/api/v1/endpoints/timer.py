"""Timer API endpoints."""


from typing import Annotated
import logging
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import (
    DatabaseSession,
    get_current_user_required,
    get_room_repository,
    get_timer_repository,
)
from app.core.exceptions import (
    AppException,
    RoomNotFoundException,
    TimerNotFoundException,
    ConflictException,
    InvalidTimerStateException,
)
from app.domain.timer.schemas import TimerStateResponse, StartTimerRequest
from app.domain.timer.service import TimerService
from app.infrastructure.repositories.room_repository import RoomRepository
from app.infrastructure.repositories.participant_repository import ParticipantRepository
from app.infrastructure.repositories.timer_repository import TimerRepository
from app.infrastructure.websocket.manager import connection_manager
from datetime import UTC, datetime


router = APIRouter(prefix="/timer", tags=["timer"])
logger = logging.getLogger(__name__)


def get_timer_service(
    timer_repo: Annotated[TimerRepository, Depends(get_timer_repository)],
    room_repo: Annotated[RoomRepository, Depends(get_room_repository)],
) -> TimerService:
    """Get timer service."""
    return TimerService(timer_repo, room_repo)


async def ensure_room_access(
    room_id: str,
    user_id: str,
    room_repo: RoomRepository,
    participant_repo: ParticipantRepository,
) -> None:
    """Ensure the user can control the room timer."""
    room = await room_repo.get_by_id(room_id)
    if not room:
        raise RoomNotFoundException(room_id)

    if room.host_id and room.host_id == user_id:
        return

    participant = await participant_repo.get_by_user_and_room(user_id, room_id)
    if not participant or not participant.is_connected:
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException("Not authorized to control this room timer")


async def broadcast_timer_update(room_id: str, timer_state: TimerStateResponse) -> None:
    """Broadcast timer state update to all clients in room via Redis."""
    try:
        from app.infrastructure.redis.pubsub_manager import redis_pubsub_manager
        from uuid import UUID

        await redis_pubsub_manager.publish_event(
            UUID(room_id),
            "timer_update",
            timer_state.model_dump(mode="json")
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to broadcast timer update for room {room_id}: {e}")

async def broadcast_timer_complete(
    room_id: str,
    completed_session_type: str,
    next_session_type: str,
    auto_start: bool,
) -> None:
    """Broadcast timer completion event to all clients in room via Redis."""
    try:
        from app.infrastructure.redis.pubsub_manager import redis_pubsub_manager
        from uuid import UUID

        await redis_pubsub_manager.publish_event(
            UUID(room_id),
            "timer_complete",
            {
                "completed_session_type": completed_session_type,
                "next_session_type": next_session_type,
                "auto_start": auto_start,
            }
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to broadcast timer completion for room {room_id}: {e}")


@router.get("/{room_id}", response_model=TimerStateResponse)
async def get_timer_state(
    room_id: str,
    service: Annotated[TimerService, Depends(get_timer_service)],
    db: DatabaseSession,
) -> TimerStateResponse:
    """Get current timer state for a room.

    Returns real-time calculated state including remaining seconds.
    """
    try:
        return await service.get_timer_state(room_id, db=db)
    except TimerNotFoundException:
        return await service.get_or_create_timer(room_id)


@router.post("/{room_id}/start", response_model=TimerStateResponse)
async def start_timer(
    room_id: str,
    request: StartTimerRequest,
    current_user: Annotated[dict, Depends(get_current_user_required)],
    service: Annotated[TimerService, Depends(get_timer_service)],
    db: DatabaseSession,
) -> TimerStateResponse:
    """Start the timer.

    Transitions from IDLE or PAUSED to RUNNING.
    """
    try:
        await ensure_room_access(
            room_id,
            current_user["id"],
            service.room_repo,
            ParticipantRepository(db),
        )
        timer_state = await service.start_timer(room_id, request.session_type, db=db)
    except RoomNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except TimerNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidTimerStateException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ConflictException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except AppException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Timer start failed: room_id={room_id} user_id={current_user['id']} error={e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "TIMER_INTERNAL_ERROR", "message": "Timer start operation failed"},
        )

    # Broadcast update (non-blocking validation)
    try:
        await broadcast_timer_update(room_id, timer_state)
    except Exception as e:
        # Just log error, don't fail the request since timer is already started
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to broadcast timer update after start for room {room_id}: {e}")

    return timer_state


@router.post("/{room_id}/pause", response_model=TimerStateResponse)
async def pause_timer(
    room_id: str,
    current_user: Annotated[dict, Depends(get_current_user_required)],
    service: Annotated[TimerService, Depends(get_timer_service)],
    db: DatabaseSession,
) -> TimerStateResponse:
    """Pause the timer.

    Transitions from RUNNING to PAUSED, saving remaining time.
    """
    try:
        await ensure_room_access(
            room_id,
            current_user["id"],
            service.room_repo,
            ParticipantRepository(db),
        )
        timer_state = await service.pause_timer(room_id)
        await broadcast_timer_update(room_id, timer_state)
        return timer_state
    except AppException:
        raise
    except Exception as e:
        logger.exception("Timer pause failed: room_id=%s user_id=%s error=%s", room_id, current_user["id"], e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "TIMER_INTERNAL_ERROR", "message": "Timer operation failed"},
        )


@router.post("/{room_id}/resume", response_model=TimerStateResponse)
async def resume_timer(
    room_id: str,
    current_user: Annotated[dict, Depends(get_current_user_required)],
    service: Annotated[TimerService, Depends(get_timer_service)],
    db: DatabaseSession,
) -> TimerStateResponse:
    """Resume the paused timer.

    Transitions from PAUSED to RUNNING, continuing from remaining time.
    """
    try:
        await ensure_room_access(
            room_id,
            current_user["id"],
            service.room_repo,
            ParticipantRepository(db),
        )
        timer_state = await service.resume_timer(room_id)
        await broadcast_timer_update(room_id, timer_state)
        return timer_state
    except AppException:
        raise
    except Exception as e:
        logger.exception("Timer resume failed: room_id=%s user_id=%s error=%s", room_id, current_user["id"], e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "TIMER_INTERNAL_ERROR", "message": "Timer operation failed"},
        )


@router.post("/{room_id}/reset", response_model=TimerStateResponse)
async def reset_timer(
    room_id: str,
    current_user: Annotated[dict, Depends(get_current_user_required)],
    service: Annotated[TimerService, Depends(get_timer_service)],
    db: DatabaseSession,
) -> TimerStateResponse:
    """Reset the timer to initial state.

    If timer was running, partially completed session is recorded.
    Returns timer to IDLE state with full duration.
    """
    try:
        await ensure_room_access(
            room_id,
            current_user["id"],
            service.room_repo,
            ParticipantRepository(db),
        )
        timer_state = await service.reset_timer(room_id, db=db)
        await broadcast_timer_update(room_id, timer_state)
        return timer_state
    except AppException:
        raise
    except Exception as e:
        logger.exception("Timer reset failed: room_id=%s user_id=%s error=%s", room_id, current_user["id"], e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "TIMER_INTERNAL_ERROR", "message": "Timer operation failed"},
        )


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
        await ensure_room_access(
            room_id,
            current_user["id"],
            service.room_repo,
            ParticipantRepository(db),
        )
        from app.shared.constants.timer import TimerPhase

        timer = await service.timer_repo.get_by_room_id(room_id)
        if not timer:
            raise TimerNotFoundException(room_id)

        room = await service.room_repo.get_by_id(room_id)
        if not room:
            raise RoomNotFoundException(room_id)

        completed_session_type = (
            "work" if timer.phase == TimerPhase.WORK.value else "break"
        )
        next_session_type = "break" if completed_session_type == "work" else "work"

        completion_time = timer.completed_at or datetime.now(UTC)
        timer_response = await service.complete_phase(room_id, completed_at=completion_time)

        # ✅ 자동 세션 기록: WORK/BREAK 단계 완료 시 세션 기록
        await service.record_work_sessions_for_timer(
            db,
            timer,
            room,
            completion_time,
        )

        # Broadcast timer completion and state update
        await broadcast_timer_complete(
            room_id,
            completed_session_type,
            next_session_type,
            auto_start=timer_response.status == "running",
        )
        await broadcast_timer_update(room_id, timer_response)

        return timer_response
    except AppException:
        raise
    except Exception as e:
        logger.exception("Timer complete failed: room_id=%s user_id=%s error=%s", room_id, current_user["id"], e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "TIMER_INTERNAL_ERROR", "message": "Timer operation failed"},
        )
