"""Background task to check and record expired timers.

This task runs periodically to ensure sessions are recorded even if
Redis keyspace notifications are unavailable.
"""
import logging
from datetime import datetime, UTC
from sqlalchemy import select

from app.infrastructure.database.models import Timer
from app.infrastructure.database.session import get_db
from app.infrastructure.repositories.room_repository import RoomRepository
from app.infrastructure.repositories.timer_repository import TimerRepository
from app.domain.timer.service import TimerService
from app.shared.constants.timer import TimerStatus

logger = logging.getLogger(__name__)


async def check_expired_timers() -> None:
    """Check for expired running timers and mark them completed.

    This function:
    1. Finds all RUNNING timers
    2. Checks if they have expired
    3. Marks them COMPLETED and records work sessions
    """
    logger.info("[Timer Cleanup] Starting timer cleanup task...")

    logger.info("[Timer Cleanup] Starting timer cleanup task...")

    # Step 1: Find running timers that NEED processing (Read-only session)
    running_timer_ids = []

    # Use a separate session for initial fetch
    async for db in get_db():
        try:
            stmt = select(Timer).where(Timer.status == TimerStatus.RUNNING.value)
            result = await db.execute(stmt)
            running_timers = result.scalars().all()

            logger.info(f"[Timer Cleanup] Found {len(running_timers)} running timers to check")

            now = datetime.now(UTC)
            for timer in running_timers:
                if not timer.started_at:
                    continue
                elapsed = (now - timer.started_at).total_seconds()
                if elapsed >= timer.remaining_seconds:
                    running_timer_ids.append(timer.room_id)
        except Exception as e:
             logger.error("[Timer Cleanup] Failed to fetch timers: %s", e, exc_info=True)
        finally:
            # We don't need to save anything here
            break

    if not running_timer_ids:
        logger.debug("[Timer Cleanup] No expired timers found")
        logger.info("[Timer Cleanup] Timer cleanup task completed")
        return

    # Step 2: Process each expired timer in its own transaction
    # This ensures one failure doesn't rollback other successful completions
    expired_count = 0
    error_count = 0

    for room_id in running_timer_ids:
        async for db in get_db():
            try:
                timer_repo = TimerRepository(db)
                room_repo = RoomRepository(db)
                timer_service = TimerService(timer_repo, room_repo)

                # Re-fetch timer in this new session
                timer = await timer_repo.get_by_room_id(room_id)
                # Double check status/expiry in case it changed
                if not timer or timer.status != TimerStatus.RUNNING.value:
                    continue

                now = datetime.now(UTC)
                completion_time = timer.completed_at or now
                timer.status = TimerStatus.COMPLETED.value
                timer.completed_at = completion_time
                timer.remaining_seconds = 0
                await timer_repo.update(timer)

                room = await room_repo.get_by_id(timer.room_id)
                if room:
                    await timer_service.record_work_sessions_for_timer(
                        db,
                        timer,
                        room,
                        completion_time,
                    )

                expired_count += 1
                logger.info("[Timer Cleanup] Auto-completed expired timer for room %s", room_id)

            except Exception as e:
                error_count += 1
                logger.error(
                    "[Timer Cleanup] Failed to process timer for room %s: %s",
                    room_id,
                    e,
                    exc_info=True,
                )
            # No finally block needed - get_db context manager handles commit/rollback/close
            break

    if expired_count > 0:
        logger.info("[Timer Cleanup] Successfully completed %s expired timers", expired_count)
    if error_count > 0:
        logger.warning("[Timer Cleanup] Failed to complete %s timers", error_count)

    logger.info("[Timer Cleanup] Timer cleanup task completed")
