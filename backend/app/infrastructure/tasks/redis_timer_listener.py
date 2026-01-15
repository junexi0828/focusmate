"""Redis-based timer expiry listener using TTL and Keyspace Notifications.

This module provides an event-driven alternative to polling-based timer cleanup.
When a timer expires, Redis automatically triggers a notification that we listen for.

Advantages over APScheduler:
- Second-level accuracy (vs ±1 minute)
- No database polling
- Multi-server safe (Redis handles deduplication)
- Event-driven architecture
"""
import logging
from datetime import datetime, UTC
from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.domain.timer.service import TimerService
from app.infrastructure.database.session import get_db
from app.shared.constants.timer import TimerStatus

logger = logging.getLogger(__name__)


class RedisTimerListener:
    """Listen for Redis TTL expiry events and complete timers.

    Uses Redis Keyspace Notifications to detect when timer keys expire.
    When a key like 'timer:expire:{room_id}' expires, we automatically
    complete the timer and record the session.
    """

    def __init__(self):
        self.redis = None
        self.pubsub = None
        self.running = False
        self.available = False

    async def connect(self):
        """Connect to Redis and enable keyspace notifications."""
        try:
            self.redis = await aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                encoding="utf-8"
            )

            # Enable keyspace notifications for expired events
            # 'Ex' = Expired events + Keyevent events
            await self.redis.config_set('notify-keyspace-events', 'Ex')

            self.pubsub = self.redis.pubsub()

            # Subscribe to expired key events on database 0
            await self.pubsub.psubscribe('__keyevent@0__:expired')

            logger.info("✅ Redis Timer Listener connected and subscribed to expiry events")
            self.available = True

        except Exception as e:
            logger.error(f"❌ Failed to connect Redis Timer Listener: {e}")
            self.available = False
            raise

    async def listen(self):
        """Listen for timer expiry events and process them with auto-reconnection.

        This runs in a background task and processes expired timer keys.
        Robustly handles connection failures with retry logic.
        """
        self.running = True
        import asyncio

        retry_count = 0
        max_retries = 5
        base_delay = 1

        while self.running:
            try:
                if not self.redis or not self.pubsub:
                    logger.info("🔄 Redis Listener reconnecting...")
                    await self.connect()

                logger.info("🎧 Redis Timer Listener started monitoring")

                # Reset retry count on successful connection
                retry_count = 0

                async for message in self.pubsub.listen():
                    if not self.running:
                        break

                    if message['type'] == 'pmessage':
                        key = message['data']
                        if key.startswith('timer:expire:'):
                            room_id = key.split(':')[-1]
                            # Run handling in background to not block listener
                            asyncio.create_task(self._handle_timer_expiry(room_id))

            except Exception as e:
                logger.error(f"❌ Redis Listener connection lost: {e}")
                self.available = False
                # Clean up potentially broken connection
                try:
                    if self.pubsub: await self.pubsub.close()
                    if self.redis: await self.redis.close()
                except: pass
                self.pubsub = None
                self.redis = None

                if not self.running:
                    break

                # Exponential backoff
                retry_count += 1
                delay = min(base_delay * (2 ** (retry_count - 1)), 60) # Max 60s
                logger.warning(f"⚠️ Retrying Redis listener in {delay}s (Attempt {retry_count})...")
                await asyncio.sleep(delay)

        logger.info("🛑 Redis Timer Listener stopped permanently")

    async def _handle_timer_expiry(self, room_id: str):
        """Handle timer expiry event.

        Args:
            room_id: Room ID whose timer expired
        """
        logger.info(f"⏰ Timer expired for room {room_id}")

        # Get database session
        async for db in get_db():
            try:
                # Complete the timer
                # Initialize repositories with the session
                from app.infrastructure.repositories.timer_repository import TimerRepository
                from app.infrastructure.repositories.room_repository import RoomRepository
                from app.infrastructure.redis.pubsub_manager import redis_pubsub_manager
                from app.shared.constants.timer import TimerPhase, TimerStatus
                from uuid import UUID

                timer_repo = TimerRepository(db)
                room_repo = RoomRepository(db)
                timer_service = TimerService(timer_repo, room_repo)

                logger.info(f"⏳ Processing expiry for room {room_id} via TimerService.complete_phase")

                # Check if timer exists and is running
                timer = await timer_repo.get_by_room_id(room_id)
                if not timer or timer.status != TimerStatus.RUNNING.value:
                    logging.getLogger(__name__).info(f"⏭️ Timer for room {room_id} is not running, skipping expiry.")
                    return

                # Delegate to complete_phase which handles:
                # 1. State transition (Work -> Break)
                # 2. Stats recording (calls record_work_sessions_for_timer)
                # 3. Auto-start logic (is_auto_start check)
                timer_state = await timer_service.complete_phase(room_id, db=db)

                # Re-fetch timer to check previous phase for notification
                # (complete_phase returns the NEXT phase state)
                # We need to know what Just completed.
                # If current(new) phase is BREAK, then WORK completed.
                completed_session_type = "work" if timer_state.phase == "break" else "break"
                next_session_type = timer_state.phase

                # Global Broadcast
                await redis_pubsub_manager.publish_event(
                    UUID(room_id),
                    "timer_complete",
                    {
                        "completed_session_type": completed_session_type,
                        "next_session_type": next_session_type,
                        "auto_start": timer_state.status == "running",
                    }
                )

                await redis_pubsub_manager.publish_event(
                    UUID(room_id),
                    "timer_update",
                    timer_state.model_dump()
                )

                logger.info(f"✅ Successfully completed expired timer for room {room_id} (Auto-Start: {timer_state.status == 'running'})")

            except Exception as e:
                logger.error(
                    f"❌ Failed to complete timer for room {room_id}: {e}",
                    exc_info=True
                )
            # No finally block needed - get_db context manager handles commit/rollback/close
            break  # Process only once per session

    async def disconnect(self):
        """Disconnect from Redis and stop listening."""
        self.running = False
        self.available = False

        if self.pubsub:
            await self.pubsub.unsubscribe()
            await self.pubsub.close()

        if self.redis:
            await self.redis.close()

        logger.info("✅ Redis Timer Listener disconnected")

    def is_available(self) -> bool:
        """Check if Redis timer listener is connected and available."""
        return self.available


# Global instance
redis_timer_listener = RedisTimerListener()
