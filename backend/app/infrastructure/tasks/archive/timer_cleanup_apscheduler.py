"""Background task to check and record expired timers.

This task runs periodically to ensure sessions are recorded even if
all users close their tabs before the timer expires.
"""
import logging
from datetime import datetime, UTC
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.timer.models import Timer, TimerStatus
from app.domain.timer.service import TimerService
from app.infrastructure.database.session import get_db

logger = logging.getLogger(__name__)


async def check_expired_timers():
    """Check for expired running timers and complete them.

    This function:
    1. Finds all RUNNING timers
    2. Checks if they have expired
    3. Completes expired timers (which records sessions)

    Runs every minute via APScheduler.
    """
    logger.info("[Timer Cleanup] Starting timer cleanup task...")

    async for db in get_db():
        try:
            # Get all RUNNING timers
            stmt = select(Timer).where(Timer.status == TimerStatus.RUNNING.value)
            result = await db.execute(stmt)
            running_timers = result.scalars().all()

            logger.info(f"[Timer Cleanup] Found {len(running_timers)} running timers")

            now = datetime.now(UTC)
            expired_count = 0
            error_count = 0

            for timer in running_timers:
                if not timer.started_at:
                    continue

                # Calculate if expired
                elapsed = (now - timer.started_at).total_seconds()
                if elapsed >= timer.remaining_seconds:
                    # Timer expired! Complete it
                    try:
                        timer_service = TimerService()
                        await timer_service.complete_timer(timer.room_id, db)
                        expired_count += 1
                        logger.info(
                            f"[Timer Cleanup] Auto-completed expired timer for room {timer.room_id} "
                            f"(elapsed: {int(elapsed)}s, duration: {timer.remaining_seconds}s)"
                        )
                    except Exception as e:
                        error_count += 1
                        logger.error(
                            f"[Timer Cleanup] Failed to complete timer for room {timer.room_id}: {e}",
                            exc_info=True
                        )

            if expired_count > 0:
                logger.info(f"[Timer Cleanup] Successfully completed {expired_count} expired timers")
            if error_count > 0:
                logger.warning(f"[Timer Cleanup] Failed to complete {error_count} timers")
            if expired_count == 0 and error_count == 0:
                logger.debug("[Timer Cleanup] No expired timers found")

        except Exception as e:
            logger.error(f"[Timer Cleanup] Critical error in timer cleanup task: {e}", exc_info=True)
        finally:
            await db.close()
            break  # Only use first db session

    logger.info("[Timer Cleanup] Timer cleanup task completed")
