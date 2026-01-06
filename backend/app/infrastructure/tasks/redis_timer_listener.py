"""Redis-based timer expiry listener using TTL and Keyspace Notifications.

This module provides an event-driven alternative to polling-based timer cleanup.
When a timer expires, Redis automatically triggers a notification that we listen for.

Advantages over APScheduler:
- Second-level accuracy (vs ±1 minute)
- No database polling
- Multi-server safe (Redis handles deduplication)
- Event-driven architecture
"""
import json
import logging
from datetime import datetime, UTC
from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.domain.timer.service import TimerService
from app.infrastructure.database.session import get_db

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

        except Exception as e:
            logger.error(f"❌ Failed to connect Redis Timer Listener: {e}")
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
                timer_service = TimerService()
                await timer_service.complete_timer(room_id, db)

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

        if self.pubsub:
            await self.pubsub.unsubscribe()
            await self.pubsub.close()

        if self.redis:
            await self.redis.close()

        logger.info("✅ Redis Timer Listener disconnected")


# Global instance
redis_timer_listener = RedisTimerListener()
