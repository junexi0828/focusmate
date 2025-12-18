"""WebSocket connection manager for real-time communication."""

from typing import Any

from fastapi import WebSocket

from app.infrastructure.websocket.base_manager import BaseConnectionManager


class ConnectionManager(BaseConnectionManager[str]):
    """Manages WebSocket connections for rooms.

    Handles connection lifecycle and message broadcasting.
    Inherits common functionality from BaseConnectionManager.
    """

    async def connect(self, websocket: WebSocket, room_id: str) -> None:
        """Accept and register a WebSocket connection.

        Args:
            websocket: WebSocket connection
            room_id: Room identifier
        """
        await self._accept_websocket(websocket)
        self._add_connection(websocket, room_id)

    def disconnect(self, websocket: WebSocket, room_id: str) -> None:
        """Remove a WebSocket connection.

        Args:
            websocket: WebSocket connection
            room_id: Room identifier
        """
        self._remove_connection(websocket, room_id)

    async def send_personal_message(self, message: dict[str, Any], websocket: WebSocket) -> None:
        """Send message to specific connection.

        Args:
            message: Message data
            websocket: Target WebSocket
        """
        await self._send_json(websocket, message)

    async def broadcast_to_room(self, message: dict[str, Any], room_id: str) -> None:
        """Broadcast message to all connections in a room.

        Args:
            message: Message data
            room_id: Room identifier
        """
        if room_id in self.active_connections:
            await self._broadcast_with_cleanup(
                self.active_connections[room_id],
                message,
                room_id
            )

    def get_room_connection_count(self, room_id: str) -> int:
        """Get number of active connections in a room.

        Args:
            room_id: Room identifier

        Returns:
            Connection count
        """
        return self.get_connection_count(room_id)


# Global connection manager instance
connection_manager = ConnectionManager()
