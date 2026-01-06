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
        """Listen for timer expiry events and process them.

        This runs in a background task and processes expired timer keys.
        """
        self.running = True
        logger.info("🎧 Redis Timer Listener started")

        try:
            async for message in self.pubsub.listen():
                if not self.running:
                    break

                if message['type'] == 'pmessage':
                    key = message['data']

                    # Check if this is a timer expiry key
                    if key.startswith('timer:expire:'):
                        room_id = key.split(':')[-1]
                        await self._handle_timer_expiry(room_id)

        except Exception as e:
            logger.error(f"❌ Error in Redis Timer Listener: {e}", exc_info=True)
        finally:
            logger.info("🛑 Redis Timer Listener stopped")

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

                timer = await timer_repo.get_by_room_id(room_id)
                if not timer or timer.status != TimerStatus.RUNNING.value:
                    return

                room = await room_repo.get_by_id(room_id)
                if not room:
                    return

                completion_time = timer.completed_at or datetime.now(UTC)
                timer.status = TimerStatus.COMPLETED.value
                timer.completed_at = completion_time
                timer.remaining_seconds = 0
                await timer_repo.update(timer)

                await timer_service.record_work_sessions_for_timer(
                    db,
                    timer,
                    room,
                    completion_time,
                )

                timer_state = await timer_service.get_timer_state(room_id, db=db)

                # Global Broadcast: Publish to Redis Channel
                completed_session_type = (
                    "work" if timer.phase == TimerPhase.WORK.value else "break"
                )
                next_session_type = "break" if completed_session_type == "work" else "work"

                await redis_pubsub_manager.publish_event(
                    UUID(room_id),
                    "timer_complete",
                    {
                        "completed_session_type": completed_session_type,
                        "next_session_type": next_session_type,
                        "auto_start": False,
                    }
                )

                await redis_pubsub_manager.publish_event(
                    UUID(room_id),
                    "timer_update",
                    timer_state.model_dump()
                )

                logger.info(f"✅ Successfully completed expired timer for room {room_id}")

            except Exception as e:
                logger.error(
                    f"❌ Failed to complete timer for room {room_id}: {e}",
                    exc_info=True
                )
            finally:
                await db.close()
                break  # Only use first db session

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
