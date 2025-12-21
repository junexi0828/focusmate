"""Redis Pub/Sub integration for chat system."""

import asyncio
import json
from uuid import UUID

import redis.asyncio as aioredis

from app.core.config import settings
from app.infrastructure.websocket.chat_manager import connection_manager


class RedisPubSubManager:
    """Manages Redis Pub/Sub for cross-server message synchronization."""

    def __init__(self, redis_url: str | None = None):
        self.redis_url = redis_url or settings.REDIS_URL
        self.redis: aioredis.Redis | None = None
        self.pubsub: aioredis.client.PubSub | None = None
        self.subscriptions: set[str] = set()
        self._listener_task: asyncio.Task | None = None

    async def connect(self):
        """Connect to Redis."""
        self.redis = await aioredis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        self.pubsub = self.redis.pubsub()

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.pubsub:
            await self.pubsub.close()
        if self.redis:
            await self.redis.close()

    async def publish_message(self, room_id: UUID, message_data: dict):
        """Publish message to Redis channel."""
        if not self.redis:
            return

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
        """Publish event to Redis channel."""
        if not self.redis:
            return

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
        """Subscribe to room channel."""
        if not self.pubsub:
            return

        channel = f"chat:room:{room_id}"
        if channel not in self.subscriptions:
            await self.pubsub.subscribe(channel)
            self.subscriptions.add(channel)

    async def unsubscribe_from_room(self, room_id: UUID):
        """Unsubscribe from room channel."""
        if not self.pubsub:
            return

        channel = f"chat:room:{room_id}"
        if channel in self.subscriptions:
            await self.pubsub.unsubscribe(channel)
            self.subscriptions.discard(channel)

    async def listen(self):
        """Listen for messages from Redis and broadcast to WebSocket connections."""
        if not self.pubsub:
            return

        async for message in self.pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    channel = message["channel"]

                    # Extract room_id from channel name
                    room_id = UUID(channel.split(":")[-1])

                    # Broadcast to WebSocket connections
                    await connection_manager.broadcast_to_room(room_id, data)

                except Exception as e:
                    print(f"Error processing Redis message: {e}")

    async def start_listener(self):
        """Start background listener task."""
        asyncio.create_task(self.listen())

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
            print(f"Error getting online users: {e}")
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
            print(f"Error getting cached presence: {e}")
            return None


# Global Redis Pub/Sub manager instance
redis_pubsub_manager = RedisPubSubManager()
