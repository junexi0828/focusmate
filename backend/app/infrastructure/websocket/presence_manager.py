"""Presence WebSocket connection manager."""

import logging
from typing import Any

from fastapi import WebSocket

from app.infrastructure.websocket.base_manager import BaseConnectionManager


logger = logging.getLogger(__name__)


class PresenceConnectionManager(BaseConnectionManager[str]):
    """Manages WebSocket connections for user presence tracking.

    Key is user_id (str).
    Supports multiple connections per user (multiple devices).
    """

    def __init__(self) -> None:
        """Initialize presence connection manager."""
        super().__init__()
        # Track user_id for each websocket
        self.websocket_to_user: dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        """Accept and register a WebSocket connection for a user.

        Args:
            websocket: WebSocket connection
            user_id: User ID
        """
        await self._accept_websocket(websocket)
        self._add_connection(websocket, user_id)
        self.websocket_to_user[websocket] = user_id
        logger.info(f"User {user_id} connected to presence manager")

    def disconnect(self, websocket: WebSocket, user_id: str) -> None:
        """Remove a WebSocket connection.

        Args:
            websocket: WebSocket connection
            user_id: User ID
        """
        self._remove_connection(websocket, user_id)
        if websocket in self.websocket_to_user:
            del self.websocket_to_user[websocket]
        logger.info(f"User {user_id} disconnected from presence manager")

    async def send_to_user(self, user_id: str, message: dict[str, Any]) -> int:
        """Send message to all connections of a specific user.

        Args:
            user_id: Target user ID
            message: Message to send

        Returns:
            Number of successful sends
        """
        if user_id not in self.active_connections:
            return 0

        success_count = 0
        failed_websockets = []

        for websocket in self.active_connections[user_id]:
            if await self._send_json(websocket, message):
                success_count += 1
            else:
                failed_websockets.append(websocket)

        # Clean up failed connections
        for websocket in failed_websockets:
            self.disconnect(websocket, user_id)

        return success_count

    async def broadcast_to_users(
        self, user_ids: list[str], message: dict[str, Any]
    ) -> dict[str, int]:
        """Broadcast message to multiple users.

        Args:
            user_ids: List of user IDs to send to
            message: Message to send

        Returns:
            Dict mapping user_id to number of successful sends
        """
        results = {}
        for user_id in user_ids:
            count = await self.send_to_user(user_id, message)
            if count > 0:
                results[user_id] = count
        return results

    async def broadcast_presence_update(
        self, user_id: str, friend_ids: list[str], is_online: bool
    ) -> dict[str, int]:
        """Broadcast presence update to all friends.

        Args:
            user_id: User whose presence changed
            friend_ids: List of friend user IDs to notify
            is_online: Online status

        Returns:
            Dict mapping friend_id to number of successful sends
        """
        message = {
            "type": "friend_online" if is_online else "friend_offline",
            "user_id": user_id,
            "is_online": is_online,
        }
        return await self.broadcast_to_users(friend_ids, message)

    def get_connection_count(self, user_id: str) -> int:
        """Get number of active connections for a user.

        Args:
            user_id: User ID

        Returns:
            Number of active connections
        """
        if user_id not in self.active_connections:
            return 0
        return len(self.active_connections[user_id])

    def is_user_connected(self, user_id: str) -> bool:
        """Check if user has any active connections.

        Args:
            user_id: User ID

        Returns:
            True if user has at least one connection
        """
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0


# Global presence connection manager instance
presence_manager = PresenceConnectionManager()
