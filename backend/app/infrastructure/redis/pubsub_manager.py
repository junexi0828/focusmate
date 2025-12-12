"""Redis Pub/Sub integration for chat system."""

import asyncio
import json
from typing import Optional
from uuid import UUID

import redis.asyncio as aioredis

from app.core.config import settings
from app.infrastructure.websocket.chat_manager import connection_manager


class RedisPubSubManager:
    """Manages Redis Pub/Sub for cross-server message synchronization."""

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or settings.REDIS_URL
        self.redis: Optional[aioredis.Redis] = None
        self.pubsub: Optional[aioredis.client.PubSub] = None
        self.subscriptions: set[str] = set()
        self._listener_task: Optional[asyncio.Task] = None

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


# Global Redis Pub/Sub manager instance
redis_pubsub_manager = RedisPubSubManager()
