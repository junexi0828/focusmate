"""Timer domain service with state machine logic."""


import logging
import json
from app.core.exceptions import (
    InvalidTimerStateException,
    RoomNotFoundException,
    TimerNotFoundException,
)
from app.domain.stats.service import StatsService
from app.domain.timer.schemas import TimerStateResponse
from app.infrastructure.database.models import Participant, Timer
from app.infrastructure.repositories.room_repository import RoomRepository
from app.infrastructure.repositories.session_history_repository import SessionHistoryRepository
from app.infrastructure.repositories.timer_repository import TimerRepository
from app.shared.constants.timer import TimerPhase, TimerStatus
from app.shared.utils.uuid import generate_uuid
from datetime import UTC, datetime, timedelta
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from redis import asyncio as aioredis
from app.core.config import settings


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

    async def _set_redis_timer_ttl(self, room_id: str, duration_seconds: int):
        """Set Redis TTL key for timer expiry notification.

        When the key expires, Redis will trigger a keyspace notification
        that our RedisTimerListener will catch and process.

        Args:
            room_id: Room ID
            duration_seconds: Timer duration in seconds
        """
        try:
            redis = await aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                encoding="utf-8"
            )

            # Set key with TTL
            # Key format: timer:expire:{room_id}
            key = f"timer:expire:{room_id}"
            value = json.dumps({
                "room_id": room_id,
                "started_at": datetime.now(UTC).isoformat(),
                "duration": duration_seconds,
            })

            await redis.setex(key, duration_seconds, value)
            await redis.close()

            logging.getLogger(__name__).info(
                f"✅ Set Redis TTL for room {room_id}: {duration_seconds}s"
            )

        except Exception as e:
            # Don't fail timer start if Redis is unavailable
            # APScheduler fallback will still work
            logging.getLogger(__name__).warning(
                f"⚠️  Failed to set Redis TTL for room {room_id}: {e}"
            )

    async def record_work_sessions_for_timer(
        self,
        db: AsyncSession,
        timer: Timer,
        room,
        completed_at: datetime | None = None,
    ) -> None:
        """Record sessions for participants who were present during the timer."""
        if not timer.started_at:
            return

        completion_time = completed_at or timer.completed_at
        if not completion_time:
            return

        stmt = (
            select(Participant)
            .where(Participant.room_id == timer.room_id)
            .where(Participant.user_id.isnot(None))
            .where(Participant.joined_at <= completion_time)
            .where(or_(Participant.left_at.is_(None), Participant.left_at >= timer.started_at))
        )
        participants_result = await db.execute(stmt)
        participants = participants_result.scalars().all()

        session_repo = SessionHistoryRepository(db)
        stats_service = StatsService(session_repo, db)

        # Determine session type and duration based on timer phase
        session_type = "work" if timer.phase == TimerPhase.WORK.value else "break"
        duration_minutes = room.work_duration if timer.phase == TimerPhase.WORK.value else room.break_duration

        existing_user_ids = await session_repo.get_user_ids_by_room_type_completed_at(
            timer.room_id,
            session_type,  # Use actual session type
            completion_time,
        )

        logger = logging.getLogger(__name__)
        for participant in participants:
            if not participant.user_id or participant.user_id in existing_user_ids:
                continue
            try:
                await stats_service.record_session(
                    user_id=participant.user_id,
                    room_id=timer.room_id,
                    session_type=session_type,  # ✅ Record both work and break
                    duration_minutes=duration_minutes,  # Use appropriate duration
                    completed_at=completion_time,
                )
                logger.info(
                    "Recorded %s session for user %s in room %s",
                    session_type,
                    participant.user_id,
                    timer.room_id,
                )
            except Exception as e:
                logger.warning(
                    "Failed to record session for user %s: %s",
                    participant.user_id,
                    e,
                )

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
            "work_duration": room.work_duration * 60,  # Add duration in seconds
            "break_duration": room.break_duration * 60,  # Add duration in seconds
        }
        return TimerStateResponse(**response_dict)

    async def start_timer(
        self,
        room_id: str,
        session_type: str = "work",
        db: AsyncSession | None = None,
    ) -> TimerStateResponse:
        """Start timer.

        Args:
            room_id: Room identifier
            session_type: "work" or "break"

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

        # Check for auto-completion (lazy update) or corrupted state
        if timer.status == TimerStatus.RUNNING.value:
            # Case 1: Corrupted state (Running but no start time)
            if not timer.started_at:
                room = await self.room_repo.get_by_id(room_id)
                timer.status = TimerStatus.IDLE.value
                timer.remaining_seconds = room.work_duration * 60 if timer.phase == TimerPhase.WORK.value else room.break_duration * 60
                await self.timer_repo.update(timer)

            # Case 2: Check for expiration
            else:
                elapsed = (datetime.now(UTC) - timer.started_at).total_seconds()
                current_remaining = max(0, timer.remaining_seconds - int(elapsed))

                if current_remaining == 0:
                    completion_time = timer.completed_at or datetime.now(UTC)
                    timer.status = TimerStatus.COMPLETED.value
                    timer.completed_at = completion_time
                    timer.remaining_seconds = 0
                    await self.timer_repo.update(timer)
                    if db is not None:
                        room = await self.room_repo.get_by_id(room_id)
                        if room:
                            await self.record_work_sessions_for_timer(
                                db,
                                timer,
                                room,
                                completion_time,
                            )

        # Handle phase switch request
        current_session_type = "work" if timer.phase == TimerPhase.WORK.value else "break"
        if session_type != current_session_type:
            # User wants to start a DIFFERENT session type
            room = await self.room_repo.get_by_id(room_id)
            if not room:
                raise RoomNotFoundException(room_id)

            # Switch phase and reset
            if session_type == "work":
                timer.phase = TimerPhase.WORK.value
                timer.duration = room.work_duration * 60
                timer.remaining_seconds = room.work_duration * 60
            else:
                timer.phase = TimerPhase.BREAK.value
                timer.duration = room.break_duration * 60
                timer.remaining_seconds = room.break_duration * 60

            # Reset status to IDLE so it can be started
            timer.status = TimerStatus.IDLE.value
            timer.started_at = None
            timer.paused_at = None
            timer.completed_at = None

            # Note: We continue below to actually start it

        # Idempotency check: If already RUNNING, just return current state
        # This fixes the issue where frontend thinks it's IDLE but backend is RUNNING
        if timer.status == TimerStatus.RUNNING.value:
             # Calculate target_timestamp for client countdown
            target_timestamp = None
            if timer.started_at and timer.remaining_seconds > 0:
                target_timestamp = (
                    timer.started_at + timedelta(seconds=timer.remaining_seconds)
                ).isoformat()

            response_dict = {
                **TimerStateResponse.model_validate(timer).model_dump(),
                "target_timestamp": target_timestamp,
                "session_type": "work" if timer.phase == TimerPhase.WORK.value else "break",
                "work_duration": room.work_duration * 60,  # Add duration in seconds
                "break_duration": room.break_duration * 60,  # Add duration in seconds
            }
            return TimerStateResponse(**response_dict)

        # Validate state transition - allow start from IDLE, PAUSED, or COMPLETED
        if timer.status not in [TimerStatus.IDLE.value, TimerStatus.PAUSED.value, TimerStatus.COMPLETED.value]:
            raise InvalidTimerStateException(timer.status, "start")

        # If timer is COMPLETED, reset to IDLE first
        if timer.status == TimerStatus.COMPLETED.value:
            # Get room to reset timer with correct duration if phase matches
            # If phase was switched above, this block is skipped (status is IDLE)
            # But if same phase restart:
            room = await self.room_repo.get_by_id(room_id)
            if room:
                timer.remaining_seconds = room.work_duration * 60 if timer.phase == TimerPhase.WORK.value else room.break_duration * 60
                timer.status = TimerStatus.IDLE.value
                timer.completed_at = None

        # Update timer
        timer.status = TimerStatus.RUNNING.value
        timer.started_at = datetime.now(UTC)
        timer.paused_at = None

        updated_timer = await self.timer_repo.update(timer)

        # Set Redis TTL for automatic expiry notification
        await self._set_redis_timer_ttl(room_id, updated_timer.remaining_seconds)

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
            "work_duration": room.work_duration * 60,  # Add duration in seconds
            "break_duration": room.break_duration * 60,  # Add duration in seconds
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
            elapsed = (datetime.now(UTC) - timer.started_at).total_seconds()
            timer.remaining_seconds = max(0, timer.remaining_seconds - int(elapsed))

        # Update timer
        timer.status = TimerStatus.PAUSED.value
        timer.paused_at = datetime.now(UTC)

        updated_timer = await self.timer_repo.update(timer)

        # Paused timers don't have target_timestamp
        response_dict = {
            **TimerStateResponse.model_validate(updated_timer).model_dump(),
            "target_timestamp": None,
            "session_type": "work" if updated_timer.phase == TimerPhase.WORK.value else "break",
            "work_duration": room.work_duration * 60,  # Add duration in seconds
            "break_duration": room.break_duration * 60,  # Add duration in seconds
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
        timer.started_at = datetime.now(UTC)
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
            "work_duration": room.work_duration * 60,  # Add duration in seconds
            "break_duration": room.break_duration * 60,  # Add duration in seconds
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

        if not room:
            raise RoomNotFoundException(room_id)

        # Record partial session if timer was running
        if timer.status == TimerStatus.RUNNING.value and timer.started_at and db:
             try:
                 # Use current time as completion time for partial session
                 completion_time = datetime.now(UTC)
                 await self.record_work_sessions_for_timer(
                    db,
                    timer,
                    room,
                    completed_at=completion_time,
                 )
             except Exception as e:
                 # Log error but don't fail reset
                 logging.getLogger(__name__).warning(f"Failed to record statistics on timer reset: {e}")

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
            "work_duration": room.work_duration * 60,  # Add duration in seconds
            "break_duration": room.break_duration * 60,  # Add duration in seconds
        }
        return TimerStateResponse(**response_dict)

    async def complete_phase(
        self,
        room_id: str,
        completed_at: datetime | None = None,
    ) -> TimerStateResponse:
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
        completion_time = timer.completed_at or completed_at or datetime.now(UTC)
        timer.status = TimerStatus.COMPLETED.value
        timer.completed_at = completion_time
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
                timer.started_at = datetime.now(UTC)
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

    async def get_timer_state(
        self,
        room_id: str,
        db: AsyncSession | None = None,
    ) -> TimerStateResponse:
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
            elapsed = (datetime.now(UTC) - timer.started_at).total_seconds()
            current_remaining = max(0, timer.remaining_seconds - int(elapsed))

            # Check if timer completed
            if current_remaining == 0:
                completion_time = timer.completed_at or datetime.now(UTC)
                timer.status = TimerStatus.COMPLETED.value
                timer.completed_at = completion_time
                timer.remaining_seconds = 0
                await self.timer_repo.update(timer)
                if db is not None:
                    room = await self.room_repo.get_by_id(room_id)
                    if room:
                        await self.record_work_sessions_for_timer(
                            db,
                            timer,
                            room,
                            completion_time,
                        )

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
