"""Timer domain service with state machine logic."""

from datetime import datetime, timezone

from app.core.exceptions import InvalidTimerStateException, RoomNotFoundException, TimerNotFoundException
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

        return TimerStateResponse.model_validate(timer)

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
        timer = await self.timer_repo.get_by_room_id(room_id)
        if not timer:
            raise TimerNotFoundException(room_id)

        # Validate state transition
        if timer.status not in [TimerStatus.IDLE.value, TimerStatus.PAUSED.value]:
            raise InvalidTimerStateException(timer.status, "start")

        # Update timer
        timer.status = TimerStatus.RUNNING.value
        timer.started_at = datetime.now(timezone.utc)
        timer.paused_at = None

        updated_timer = await self.timer_repo.update(timer)
        return TimerStateResponse.model_validate(updated_timer)

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
        timer = await self.timer_repo.get_by_room_id(room_id)
        if not timer:
            raise TimerNotFoundException(room_id)

        # Validate state transition
        if timer.status != TimerStatus.RUNNING.value:
            raise InvalidTimerStateException(timer.status, "pause")

        # Calculate elapsed time
        if timer.started_at:
            elapsed = (datetime.now(timezone.utc) - timer.started_at).total_seconds()
            timer.remaining_seconds = max(0, timer.remaining_seconds - int(elapsed))

        # Update timer
        timer.status = TimerStatus.PAUSED.value
        timer.paused_at = datetime.now(timezone.utc)

        updated_timer = await self.timer_repo.update(timer)
        return TimerStateResponse.model_validate(updated_timer)

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
        return TimerStateResponse.model_validate(updated_timer)

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
            timer.phase = TimerPhase.BREAK.value
            timer.duration = room.break_duration * 60
            timer.remaining_seconds = room.break_duration * 60

            # Auto-start break if enabled
            if timer.is_auto_start:
                timer.status = TimerStatus.RUNNING.value
                timer.started_at = datetime.now(timezone.utc)
            else:
                timer.status = TimerStatus.IDLE.value
                timer.started_at = None
        else:
            # Break completed → Work
            timer.phase = TimerPhase.WORK.value
            timer.duration = room.work_duration * 60
            timer.remaining_seconds = room.work_duration * 60
            timer.status = TimerStatus.IDLE.value
            timer.started_at = None

        timer.paused_at = None
        updated_timer = await self.timer_repo.update(timer)
        return TimerStateResponse.model_validate(updated_timer)

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

        return TimerStateResponse.model_validate(timer)
