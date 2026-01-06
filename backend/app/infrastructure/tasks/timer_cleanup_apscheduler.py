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

    async for db in get_db():
        try:
            stmt = select(Timer).where(Timer.status == TimerStatus.RUNNING.value)
            result = await db.execute(stmt)
            running_timers = result.scalars().all()

            logger.info(f"[Timer Cleanup] Found {len(running_timers)} running timers")

            now = datetime.now(UTC)
            expired_count = 0
            error_count = 0

            timer_repo = TimerRepository(db)
            room_repo = RoomRepository(db)
            timer_service = TimerService(timer_repo, room_repo)

            for timer in running_timers:
                if not timer.started_at:
                    continue

                elapsed = (now - timer.started_at).total_seconds()
                if elapsed >= timer.remaining_seconds:
                    try:
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
                        logger.info(
                            "[Timer Cleanup] Auto-completed expired timer for room %s (elapsed: %s, duration: %s)",
                            timer.room_id,
                            int(elapsed),
                            timer.remaining_seconds,
                        )
                    except Exception as e:
                        error_count += 1
                        logger.error(
                            "[Timer Cleanup] Failed to complete timer for room %s: %s",
                            timer.room_id,
                            e,
                            exc_info=True,
                        )

            if expired_count > 0:
                logger.info("[Timer Cleanup] Successfully completed %s expired timers", expired_count)
            if error_count > 0:
                logger.warning("[Timer Cleanup] Failed to complete %s timers", error_count)
            if expired_count == 0 and error_count == 0:
                logger.debug("[Timer Cleanup] No expired timers found")

        except Exception as e:
            logger.error("[Timer Cleanup] Critical error in timer cleanup task: %s", e, exc_info=True)
        finally:
            await db.close()
            break

    logger.info("[Timer Cleanup] Timer cleanup task completed")
