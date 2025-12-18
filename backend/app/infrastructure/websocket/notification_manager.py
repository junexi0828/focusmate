"""WebSocket connection manager for real-time notifications."""

import logging
from typing import Any

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

    def disconnect(self, websocket: WebSocket, user_id: str) -> None:
        """Remove a WebSocket connection.

        Args:
            websocket: WebSocket connection
            user_id: User identifier
        """
        self._remove_connection(websocket, user_id)

    async def send_notification(self, notification: dict[str, Any], user_id: str) -> bool:
        """Send notification to all connections for a specific user.

        Args:
            notification: Notification data
            user_id: User identifier

        Returns:
            True if notification was sent, False if user has no active connections
        """
        if user_id not in self.active_connections:
            logger.debug(f"User {user_id} has no active connections, notification not sent")
            return False

        await self._broadcast_with_cleanup(
            self.active_connections[user_id],
            notification,
            user_id
        )
        logger.info(f"Notification sent to user {user_id}")
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
