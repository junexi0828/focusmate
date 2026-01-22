"""Redis Pub/Sub integration for chat system with fault tolerance.

Production-grade PubSub with:
- Circuit Breaker pattern for fault isolation
- Graceful degradation on Redis failures
- Comprehensive error handling
"""

from typing import Optional
import asyncio
import json
import logging
from uuid import UUID

import redis.asyncio as aioredis

from app.core.config import settings
from app.infrastructure.websocket.chat_manager import connection_manager
from app.infrastructure.redis.circuit_breaker import RedisCircuitBreaker, CircuitOpenError

logger = logging.getLogger(__name__)

class RedisPubSubManager:
    """Manages Redis Pub/Sub for cross-server message synchronization."""

    def __init__(self, redis_url: str | None = None):
        self.redis_url = redis_url or settings.REDIS_URL
        self.redis: aioredis.Redis | None = None
        self.pubsub: aioredis.client.PubSub | None = None
        self.subscriptions: set[str] = set()
        self._listener_task: asyncio.Task | None = None
        self._running = False
        # Circuit breaker for fault isolation
        self._circuit_breaker = RedisCircuitBreaker(
            failure_threshold=5,
            recovery_timeout=30,
            success_threshold=2,
        )

    async def connect(self):
        """Connect to Redis."""
        # aioredis.from_url() returns a Redis client directly, no await needed
        self.redis = aioredis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=settings.REDIS_DECODE_RESPONSES,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
            socket_connect_timeout=settings.REDIS_CONNECT_TIMEOUT,
            retry_on_timeout=settings.REDIS_RETRY_ON_TIMEOUT,
            health_check_interval=settings.REDIS_HEALTH_CHECK_INTERVAL,
        )
        self.pubsub = self.redis.pubsub()

    async def disconnect(self):
        """Disconnect from Redis."""
        # Stop listener task first
        await self.stop_listener()

        if self.pubsub:
            await self.pubsub.close()
        if self.redis:
            await self.redis.close()

    async def publish_message(self, room_id: UUID, message_data: dict):
        """Publish message to Redis channel with circuit breaker protection."""
        if not self.redis:
            logger.warning("[PubSub] Redis not connected, skipping message publish")
            await self._broadcast_local(room_id, {"type": "message", "data": message_data})
            return

        try:
            await self._circuit_breaker.call(self._publish_message_impl, room_id, message_data)
        except CircuitOpenError:
            logger.warning(f"[PubSub] Circuit open, skipping message publish to room {room_id}")
        except Exception as e:
            logger.error(f"[PubSub] Failed to publish message to room {room_id}: {e}")

    async def _publish_message_impl(self, room_id: UUID, message_data: dict):
        """Internal implementation of publish_message."""
        channel = f"chat:room:{room_id}"
        await self.redis.publish(
            channel,
            json.dumps(
                {
                    "type": "message",
                    "data": message_data,
                }
            ),
        )

    async def publish_event(self, room_id: UUID, event_type: str, event_data: dict):
        """Publish event to Redis channel with circuit breaker protection."""
        if not self.redis:
            logger.warning(f"[PubSub] Redis not connected, skipping event publish: {event_type}")
            await self._broadcast_local(room_id, {"type": event_type, "data": event_data})
            return

        try:
            await self._circuit_breaker.call(self._publish_event_impl, room_id, event_type, event_data)
        except CircuitOpenError:
            logger.warning(f"[PubSub] Circuit open, skipping event {event_type} to room {room_id}")
        except Exception as e:
            logger.error(f"[PubSub] Failed to publish event {event_type} to room {room_id}: {e}")

    async def _publish_event_impl(self, room_id: UUID, event_type: str, event_data: dict):
        """Internal implementation of publish_event."""
        channel = f"chat:room:{room_id}"
        await self.redis.publish(
            channel,
            json.dumps(
                {
                    "type": event_type,
                    "data": event_data,
                }
            ),
        )

    async def subscribe_to_room(self, room_id: UUID):
        """Subscribe to room channel with error handling."""
        if not self.pubsub:
            logger.warning(f"[PubSub] PubSub not initialized, skipping subscribe to room {room_id}")
            return

        try:
            channel = f"chat:room:{room_id}"
            if channel not in self.subscriptions:
                await self.pubsub.subscribe(channel)
                self.subscriptions.add(channel)
                logger.debug(f"[PubSub] Subscribed to room {room_id}")
        except Exception as e:
            logger.error(f"[PubSub] Failed to subscribe to room {room_id}: {e}")

    async def _broadcast_local(self, room_id: UUID, message: dict) -> None:
        """Fallback to local broadcast when Redis is unavailable."""
        try:
            await connection_manager.broadcast_to_room(room_id, message)
        except Exception as exc:
            logger.error(f"[PubSub] Local broadcast failed for room {room_id}: {exc}")

    async def unsubscribe_from_room(self, room_id: UUID):
        """Unsubscribe from room channel with error handling."""
        if not self.pubsub:
            logger.warning(f"[PubSub] PubSub not initialized, skipping unsubscribe from room {room_id}")
            return

        try:
            channel = f"chat:room:{room_id}"
            if channel in self.subscriptions:
                await self.pubsub.unsubscribe(channel)
                self.subscriptions.discard(channel)
                logger.debug(f"[PubSub] Unsubscribed from room {room_id}")
        except Exception as e:
            logger.error(f"[PubSub] Failed to unsubscribe from room {room_id}: {e}")

    async def listen(self):
        """Listen for messages from Redis and broadcast to WebSocket connections."""
        backoff_seconds = 1
        while self._running:
            try:
                if not self.pubsub or not self.redis:
                    await self.connect()

                async for message in self.pubsub.listen():
                    if not self._running:
                        break
                    if message["type"] != "message":
                        continue

                    try:
                        channel = message["channel"]
                        data = json.loads(message["data"])

                        if channel.startswith("chat:room:"):
                            # Extract room_id from channel name
                            room_id = UUID(channel.split(":")[-1])
                            # Broadcast to WebSocket connections
                            await connection_manager.broadcast_to_room(room_id, data)
                        elif channel.startswith("notification:user:"):
                            # Extract user_id from channel name
                            user_id = channel.split(":")[-1]
                            # Broadcast to local WebSocket connections for this user
                            from app.infrastructure.websocket.notification_manager import (
                                notification_ws_manager,
                            )

                            await notification_ws_manager.send_notification_local(
                                data, user_id
                            )
                    except Exception as e:
                        logging.getLogger(__name__).error(f"Error processing Redis message: {e}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[PubSub] Listener error: {e}")
                await self._reset_connection()
                if not self._running:
                    break
                await asyncio.sleep(backoff_seconds)
                backoff_seconds = min(backoff_seconds * 2, 60)
            else:
                backoff_seconds = 1

    async def publish_notification(self, user_id: str, notification_data: dict):
        """Publish notification to Redis channel with circuit breaker protection."""
        if not self.redis:
            logger.warning(f"[PubSub] Redis not connected, skipping notification for user {user_id}")
            return

        try:
            await self._circuit_breaker.call(self._publish_notification_impl, user_id, notification_data)
        except CircuitOpenError:
            logger.warning(f"[PubSub] Circuit open, skipping notification for user {user_id}")
        except Exception as e:
            logger.error(f"[PubSub] Failed to publish notification for user {user_id}: {e}")

    async def _publish_notification_impl(self, user_id: str, notification_data: dict):
        """Internal implementation of publish_notification."""
        channel = f"notification:user:{user_id}"
        await self.redis.publish(
            channel,
            json.dumps(notification_data)
        )

    async def subscribe_to_user_notifications(self, user_id: str):
        """Subscribe to user notification channel."""
        if not self.pubsub:
            return

        channel = f"notification:user:{user_id}"
        if channel not in self.subscriptions:
            await self.pubsub.subscribe(channel)
            self.subscriptions.add(channel)

    async def unsubscribe_from_user_notifications(self, user_id: str):
        """Unsubscribe from user notification channel."""
        if not self.pubsub:
            return

        channel = f"notification:user:{user_id}"
        if channel in self.subscriptions:
            await self.pubsub.unsubscribe(channel)
            self.subscriptions.discard(channel)

    async def start_listener(self):
        """Start background listener task."""
        if self._listener_task is None or self._listener_task.done():
            self._running = True
            self._listener_task = asyncio.create_task(self.listen())

    async def stop_listener(self):
        """Stop background listener task."""
        self._running = False
        if self._listener_task and not self._listener_task.done():
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass

    async def _reset_connection(self) -> None:
        """Reset Redis and PubSub connections after failures."""
        try:
            if self.pubsub:
                await self.pubsub.close()
        except Exception:
            pass
        try:
            if self.redis:
                await self.redis.close()
        except Exception:
            pass
        self.pubsub = None
        self.redis = None
        self._listener_task = None

    # Presence operations
    async def publish_presence(self, user_id: str, is_online: bool, metadata: dict | None = None):
        """Publish presence change to all servers.

        Args:
            user_id: User ID
            is_online: Online status
            metadata: Optional metadata (e.g., status_message, last_seen_at)
        """
        if not self.redis:
            return

        channel = "presence:updates"
        await self.redis.publish(
            channel,
            json.dumps(
                {
                    "type": "presence_update",
                    "user_id": user_id,
                    "is_online": is_online,
                    "metadata": metadata or {},
                }
            ),
        )

    async def subscribe_to_presence(self):
        """Subscribe to presence updates channel."""
        if not self.pubsub:
            return

        channel = "presence:updates"
        if channel not in self.subscriptions:
            await self.pubsub.subscribe(channel)
            self.subscriptions.add(channel)

    async def set_online_user(self, user_id: str):
        """Add user to online users set in Redis.

        Args:
            user_id: User ID
        """
        if not self.redis:
            return

        await self.redis.sadd("presence:online_users", user_id)

    async def remove_online_user(self, user_id: str):
        """Remove user from online users set in Redis.

        Args:
            user_id: User ID
        """
        if not self.redis:
            return

        await self.redis.srem("presence:online_users", user_id)

    async def get_online_users(self) -> set[str]:
        """Get set of online user IDs from Redis.

        Returns:
            Set of user IDs who are online
        """
        if not self.redis:
            return set()

        try:
            users = await self.redis.smembers("presence:online_users")
            return set(users) if users else set()
        except Exception as e:
            logging.getLogger(__name__).error(f"Error getting online users: {e}")
            return set()

    async def cache_user_presence(
        self, user_id: str, presence_data: dict, ttl_seconds: int = 86400
    ):
        """Cache user presence data in Redis.

        Args:
            user_id: User ID
            presence_data: Presence data to cache
            ttl_seconds: TTL in seconds (default 24 hours)
        """
        if not self.redis:
            return

        key = f"presence:user:{user_id}"
        await self.redis.hset(key, mapping=presence_data)
        await self.redis.expire(key, ttl_seconds)

    async def get_cached_presence(self, user_id: str) -> dict | None:
        """Get cached presence data from Redis.

        Args:
            user_id: User ID

        Returns:
            Cached presence data or None
        """
        if not self.redis:
            return None

        try:
            key = f"presence:user:{user_id}"
            data = await self.redis.hgetall(key)
            return dict(data) if data else None
        except Exception as e:
            logging.getLogger(__name__).error(f"Error getting cached presence: {e}")
            return None

    async def set_timer_ttl(self, room_id: str, duration_seconds: int, data: dict) -> None:
        """Set Redis TTL key for timer expiry with circuit breaker protection.

        Args:
            room_id: Room ID
            duration_seconds: Timer duration in seconds
            data: Data to store (e.g. started_at)
        """
        if not self.redis:
            logger.warning(f"[PubSub] Redis not connected, skipping set_timer_ttl for room {room_id}")
            return

        try:
            await self._circuit_breaker.call(self._set_timer_ttl_impl, room_id, duration_seconds, data)
        except CircuitOpenError:
            logger.warning(f"[PubSub] Circuit open, skipping timer TTL for room {room_id}")
        except Exception as e:
            logger.error(f"[PubSub] Failed to set timer TTL for room {room_id}: {e}")

    async def _set_timer_ttl_impl(self, room_id: str, duration_seconds: int, data: dict):
        """Internal implementation of set_timer_ttl."""
        key = f"timer:expire:{room_id}"
        await self.redis.setex(key, duration_seconds, json.dumps(data))
        logger.info(f"✅ Set Redis TTL for room {room_id}: {duration_seconds}s")
# Global Redis Pub/Sub manager instance
redis_pubsub_manager = RedisPubSubManager()
