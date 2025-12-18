"""Timer domain service with state machine logic."""

from datetime import datetime, timedelta, timezone

from app.core.exceptions import (
    InvalidTimerStateException,
    RoomNotFoundException,
    TimerNotFoundException,
)
from app.domain.timer.schemas import TimerStateResponse
from app.infrastructure.database.models import Timer
from app.infrastructure.repositories.room_repository import RoomRepository
from app.infrastructure.repositories.timer_repository import TimerRepository
from app.shared.constants.timer import TimerPhase, TimerStatus
from app.shared.utils.uuid import generate_uuid


class TimerService:
    """Timer business logic with server-authoritative state management."""

    def __init__(
        self,
        timer_repository: TimerRepository,
        room_repository: RoomRepository,
    ) -> None:
        """Initialize service.

        Args:
            timer_repository: Timer repository
            room_repository: Room repository
        """
        self.timer_repo = timer_repository
        self.room_repo = room_repository

    async def get_or_create_timer(self, room_id: str) -> TimerStateResponse:
        """Get timer for room, creating if not exists.

        Args:
            room_id: Room identifier

        Returns:
            Timer state

        Raises:
            RoomNotFoundException: If room not found
        """
        # Verify room exists
        room = await self.room_repo.get_by_id(room_id)
        if not room:
            raise RoomNotFoundException(room_id)

        # Get or create timer
        timer = await self.timer_repo.get_by_room_id(room_id)
        if not timer:
            timer = Timer(
                id=generate_uuid(),
                room_id=room_id,
                status=TimerStatus.IDLE.value,
                phase=TimerPhase.WORK.value,
                duration=room.work_duration * 60,  # Convert to seconds
                remaining_seconds=room.work_duration * 60,
                is_auto_start=room.auto_start_break,
            )
            timer = await self.timer_repo.create(timer)

        # IDLE timers don't have target_timestamp
        response_dict = {
            **TimerStateResponse.model_validate(timer).model_dump(),
            "target_timestamp": None,
            "session_type": "work" if timer.phase == TimerPhase.WORK.value else "break",
        }
        return TimerStateResponse(**response_dict)

    async def start_timer(self, room_id: str) -> TimerStateResponse:
        """Start timer.

        Args:
            room_id: Room identifier

        Returns:
            Updated timer state

        Raises:
            TimerNotFoundException: If timer not found
            InvalidTimerStateException: If timer cannot be started
        """
        # Get or create timer if it doesn't exist
        timer = await self.timer_repo.get_by_room_id(room_id)
        if not timer:
            # Create timer if it doesn't exist
            timer_state = await self.get_or_create_timer(room_id)
            timer = await self.timer_repo.get_by_room_id(room_id)
            if not timer:
                raise TimerNotFoundException(room_id)

        # Validate state transition - allow start from IDLE, PAUSED, or COMPLETED
        if timer.status not in [TimerStatus.IDLE.value, TimerStatus.PAUSED.value, TimerStatus.COMPLETED.value]:
            raise InvalidTimerStateException(timer.status, "start")

        # If timer is COMPLETED, reset to IDLE first
        if timer.status == TimerStatus.COMPLETED.value:
            # Get room to reset timer with correct duration
            room = await self.room_repo.get_by_id(room_id)
            if room:
                timer.remaining_seconds = room.work_duration * 60 if timer.phase == TimerPhase.WORK.value else room.break_duration * 60
                timer.status = TimerStatus.IDLE.value
                timer.completed_at = None

        # Update timer
        timer.status = TimerStatus.RUNNING.value
        timer.started_at = datetime.now(timezone.utc)
        timer.paused_at = None

        updated_timer = await self.timer_repo.update(timer)

        # Calculate target_timestamp for client countdown
        target_timestamp = None
        if updated_timer.started_at and updated_timer.remaining_seconds > 0:
            target_timestamp = (
                updated_timer.started_at + timedelta(seconds=updated_timer.remaining_seconds)
            ).isoformat()

        # Create response with additional fields
        response_dict = {
            **TimerStateResponse.model_validate(updated_timer).model_dump(),
            "target_timestamp": target_timestamp,
            "session_type": "work" if updated_timer.phase == TimerPhase.WORK.value else "break",
        }
        return TimerStateResponse(**response_dict)

    async def pause_timer(self, room_id: str) -> TimerStateResponse:
        """Pause timer.

        Args:
            room_id: Room identifier

        Returns:
            Updated timer state

        Raises:
            TimerNotFoundException: If timer not found
            InvalidTimerStateException: If timer cannot be paused
        """
        # Get or create timer if it doesn't exist
        timer = await self.timer_repo.get_by_room_id(room_id)
        if not timer:
            # Create timer if it doesn't exist (shouldn't happen, but handle gracefully)
            timer_state = await self.get_or_create_timer(room_id)
            timer = await self.timer_repo.get_by_room_id(room_id)
            if not timer:
                raise TimerNotFoundException(room_id)

        # Validate state transition - allow pause from RUNNING or COMPLETED
        if timer.status not in [TimerStatus.RUNNING.value, TimerStatus.COMPLETED.value]:
            raise InvalidTimerStateException(timer.status, "pause")

        # Calculate elapsed time
        if timer.started_at:
            elapsed = (datetime.now(timezone.utc) - timer.started_at).total_seconds()
            timer.remaining_seconds = max(0, timer.remaining_seconds - int(elapsed))

        # Update timer
        timer.status = TimerStatus.PAUSED.value
        timer.paused_at = datetime.now(timezone.utc)

        updated_timer = await self.timer_repo.update(timer)

        # Paused timers don't have target_timestamp
        response_dict = {
            **TimerStateResponse.model_validate(updated_timer).model_dump(),
            "target_timestamp": None,
            "session_type": "work" if updated_timer.phase == TimerPhase.WORK.value else "break",
        }
        return TimerStateResponse(**response_dict)

    async def resume_timer(self, room_id: str) -> TimerStateResponse:
        """Resume paused timer.

        Args:
            room_id: Room identifier

        Returns:
            Updated timer state

        Raises:
            TimerNotFoundException: If timer not found
            InvalidTimerStateException: If timer cannot be resumed
        """
        # Get or create timer if it doesn't exist
        timer = await self.timer_repo.get_by_room_id(room_id)
        if not timer:
            raise TimerNotFoundException(room_id)

        # Validate state transition - only resume from PAUSED
        if timer.status != TimerStatus.PAUSED.value:
            raise InvalidTimerStateException(timer.status, "resume")

        # Update timer
        timer.status = TimerStatus.RUNNING.value
        timer.started_at = datetime.now(timezone.utc)
        timer.paused_at = None

        updated_timer = await self.timer_repo.update(timer)

        # Calculate target_timestamp for client countdown
        target_timestamp = None
        if updated_timer.started_at and updated_timer.remaining_seconds > 0:
            target_timestamp = (
                updated_timer.started_at + timedelta(seconds=updated_timer.remaining_seconds)
            ).isoformat()

        response_dict = {
            **TimerStateResponse.model_validate(updated_timer).model_dump(),
            "target_timestamp": target_timestamp,
            "session_type": "work" if updated_timer.phase == TimerPhase.WORK.value else "break",
        }
        return TimerStateResponse(**response_dict)

    async def reset_timer(self, room_id: str) -> TimerStateResponse:
        """Reset timer to initial state.

        Args:
            room_id: Room identifier

        Returns:
            Reset timer state

        Raises:
            TimerNotFoundException: If timer not found
            RoomNotFoundException: If room not found
        """
        timer = await self.timer_repo.get_by_room_id(room_id)
        if not timer:
            raise TimerNotFoundException(room_id)

        room = await self.room_repo.get_by_id(room_id)
        if not room:
            raise RoomNotFoundException(room_id)

        # Reset to work phase
        timer.status = TimerStatus.IDLE.value
        timer.phase = TimerPhase.WORK.value
        timer.duration = room.work_duration * 60
        timer.remaining_seconds = room.work_duration * 60
        timer.started_at = None
        timer.paused_at = None
        timer.completed_at = None

        updated_timer = await self.timer_repo.update(timer)

        # Reset timers don't have target_timestamp
        response_dict = {
            **TimerStateResponse.model_validate(updated_timer).model_dump(),
            "target_timestamp": None,
            "session_type": "work" if updated_timer.phase == TimerPhase.WORK.value else "break",
        }
        return TimerStateResponse(**response_dict)

    async def complete_phase(self, room_id: str) -> TimerStateResponse:
        """Complete current timer phase and transition to next phase.

        Args:
            room_id: Room identifier

        Returns:
            Updated timer state in next phase

        Raises:
            TimerNotFoundException: If timer not found
            RoomNotFoundException: If room not found
            InvalidTimerStateException: If timer is not running/completed
        """
        timer = await self.timer_repo.get_by_room_id(room_id)
        if not timer:
            raise TimerNotFoundException(room_id)

        room = await self.room_repo.get_by_id(room_id)
        if not room:
            raise RoomNotFoundException(room_id)

        # Validate state
        if timer.status not in [TimerStatus.RUNNING.value, TimerStatus.COMPLETED.value]:
            raise InvalidTimerStateException(timer.status, "complete")

        # Mark as completed
        timer.status = TimerStatus.COMPLETED.value
        timer.completed_at = datetime.now(timezone.utc)
        timer.remaining_seconds = 0

        # Transition to next phase
        if timer.phase == TimerPhase.WORK.value:
            # Work completed → Break
            # room.break_duration is in minutes, convert to seconds
            timer.phase = TimerPhase.BREAK.value
            timer.duration = room.break_duration * 60  # Convert minutes to seconds
            timer.remaining_seconds = room.break_duration * 60  # Convert minutes to seconds

            # Auto-start break if enabled
            if timer.is_auto_start:
                timer.status = TimerStatus.RUNNING.value
                timer.started_at = datetime.now(timezone.utc)
            else:
                timer.status = TimerStatus.IDLE.value
                timer.started_at = None
        else:
            # Break completed → Work
            # room.work_duration is in minutes, convert to seconds
            timer.phase = TimerPhase.WORK.value
            timer.duration = room.work_duration * 60  # Convert minutes to seconds
            timer.remaining_seconds = room.work_duration * 60  # Convert minutes to seconds
            timer.status = TimerStatus.IDLE.value
            timer.started_at = None

        timer.paused_at = None
        updated_timer = await self.timer_repo.update(timer)

        # Calculate target_timestamp if auto-started
        target_timestamp = None
        if updated_timer.status == TimerStatus.RUNNING.value and updated_timer.started_at:
            target_timestamp = (
                updated_timer.started_at + timedelta(seconds=updated_timer.remaining_seconds)
            ).isoformat()

        response_dict = {
            **TimerStateResponse.model_validate(updated_timer).model_dump(),
            "target_timestamp": target_timestamp,
            "session_type": "work" if updated_timer.phase == TimerPhase.WORK.value else "break",
        }
        return TimerStateResponse(**response_dict)

    async def get_timer_state(self, room_id: str) -> TimerStateResponse:
        """Get current timer state (with real-time calculation).

        Args:
            room_id: Room identifier

        Returns:
            Current timer state

        Raises:
            TimerNotFoundException: If timer not found
        """
        timer = await self.timer_repo.get_by_room_id(room_id)
        if not timer:
            raise TimerNotFoundException(room_id)

        # Calculate real-time remaining seconds if running
        if timer.status == TimerStatus.RUNNING.value and timer.started_at:
            elapsed = (datetime.now(timezone.utc) - timer.started_at).total_seconds()
            current_remaining = max(0, timer.remaining_seconds - int(elapsed))

            # Check if timer completed
            if current_remaining == 0:
                timer.status = TimerStatus.COMPLETED.value
                timer.completed_at = datetime.now(timezone.utc)
                timer.remaining_seconds = 0
                await self.timer_repo.update(timer)

        # Calculate target_timestamp if running
        target_timestamp = None
        if timer.status == TimerStatus.RUNNING.value and timer.started_at:
            target_timestamp = (
                timer.started_at + timedelta(seconds=timer.remaining_seconds)
            ).isoformat()

        response_dict = {
            **TimerStateResponse.model_validate(timer).model_dump(),
            "target_timestamp": target_timestamp,
            "session_type": "work" if timer.phase == TimerPhase.WORK.value else "break",
        }
        return TimerStateResponse(**response_dict)
