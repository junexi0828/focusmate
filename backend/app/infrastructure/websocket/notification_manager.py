"""WebSocket connection manager for real-time notifications."""

from typing import Any, Dict, List
import logging

from fastapi import WebSocket

from app.infrastructure.websocket.base_manager import BaseConnectionManager


logger = logging.getLogger(__name__)


class NotificationWebSocketManager(BaseConnectionManager[str]):
    """Manages WebSocket connections for user notifications.

    Handles connection lifecycle and notification broadcasting to specific users.
    Inherits common functionality from BaseConnectionManager.
    """

    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        """Accept and register a WebSocket connection for a user.

        Args:
            websocket: WebSocket connection
            user_id: User identifier
        """
        await self._accept_websocket(websocket)
        self._add_connection(websocket, user_id)

        # Subscribe to Redis channel for multi-server broadcasting
        try:
            from app.infrastructure.redis.pubsub_manager import redis_pubsub_manager
            await redis_pubsub_manager.subscribe_to_user_notifications(user_id)
        except Exception as e:
            logger.error(f"Failed to subscribe to user notifications: {e}")

    def disconnect(self, websocket: WebSocket, user_id: str) -> None:
        """Remove a WebSocket connection.

        Args:
            websocket: WebSocket connection
            user_id: User identifier
        """
        self._remove_connection(websocket, user_id)

        # If no more connections for this user, unsubscribe from Redis
        if user_id not in self.active_connections:
            try:
                # We can't await here easily since disconnect is sync in base class
                # But typically we'd want to unsubscribe.
                # For now, we rely on the fact that if there are no listeners,
                # the Redis message will just be ignored by send_notification_local.
                # Ideally, we should fire a background task to unsubscribe.
                import asyncio
                from app.infrastructure.redis.pubsub_manager import redis_pubsub_manager
                asyncio.create_task(redis_pubsub_manager.unsubscribe_from_user_notifications(user_id))
            except Exception as e:
                logger.error(f"Failed to unsubscribe from user notifications: {e}")

    async def send_notification(self, notification: dict[str, Any], user_id: str) -> bool:
        """Send notification to user via Redis Pub/Sub with local fallback.

        ARCHITECTURE NOTE (Single Server Mode):
        Since the Redis Pub/Sub listener is disabled (see main.py:84-87),
        we immediately deliver to local connections after publishing.
        This ensures notifications are delivered in single-server deployments.

        TODO (Multi-Server Mode):
        When scaling to multiple servers, enable the Redis listener and
        add a condition: only call send_notification_local() if listener is inactive.
        Otherwise, the listener will handle delivery to avoid duplicate sends.

        Args:
            notification: Notification data
            user_id: User identifier

        Returns:
            True if delivered locally, False otherwise
        """
        try:
            from app.infrastructure.redis.pubsub_manager import redis_pubsub_manager

            # Publish to Redis (for future multi-server support & persistence)
            await redis_pubsub_manager.publish_notification(user_id, notification)

            # IMMEDIATE local delivery (since listener is disabled)
            # This prevents notification loss in single-server mode
            return await self.send_notification_local(notification, user_id)

        except Exception as e:
            logger.error(f"Error publishing notification: {e}")
            # Fallback: try local delivery even if Redis publish failed
            try:
                return await self.send_notification_local(notification, user_id)
            except Exception as local_error:
                logger.error(f"Local notification delivery also failed: {local_error}")
                return False

    async def send_notification_local(self, notification: dict[str, Any], user_id: str) -> bool:
        """Send notification to local active connections for a specific user.

        This is called by the Redis Pub/Sub listener when a message is received.

        Args:
            notification: Notification data
            user_id: User identifier

        Returns:
            True if notification was sent locally, False if user has no local connections
        """
        if user_id not in self.active_connections:
            # This is normal in a multi-server setup
            return False

        await self._broadcast_with_cleanup(
            self.active_connections[user_id],
            notification,
            user_id
        )
        logger.info(f"Notification sent to user {user_id} (local)")
        return True

    async def broadcast_notification(self, notification: dict[str, Any], user_ids: list[str]) -> None:
        """Broadcast notification to multiple users.

        Args:
            notification: Notification data
            user_ids: List of user identifiers
        """
        logger.info(f"Broadcasting notification to {len(user_ids)} users")
        for user_id in user_ids:
            await self.send_notification(notification, user_id)

    def is_user_online(self, user_id: str) -> bool:
        """Check if user has any active WebSocket connections.

        Args:
            user_id: User identifier

        Returns:
            True if user is online
        """
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0

    def get_online_users(self) -> list[str]:
        """Get list of all online user IDs.

        Returns:
            List of user IDs with active connections
        """
        return list(self.active_connections.keys())

    def get_user_connection_count(self, user_id: str) -> int:
        """Get number of active connections for a user.

        Args:
            user_id: User identifier

        Returns:
            Connection count
        """
        return self.get_connection_count(user_id)


# Global notification WebSocket manager instance
notification_ws_manager = NotificationWebSocketManager()
