"""WebSocket connection manager for unified chat system."""

import logging
from typing import Dict, Set
from uuid import UUID

from fastapi import WebSocket

from app.infrastructure.websocket.base_manager import BaseConnectionManager

logger = logging.getLogger(__name__)


class ChatConnectionManager(BaseConnectionManager[UUID]):
    """Manages WebSocket connections for real-time chat.

    Inherits common functionality from BaseConnectionManager and adds
    chat-specific features like user tracking.
    """

    def __init__(self):
        super().__init__()
        # Override to use Set instead of List for better performance
        self.active_connections: Dict[UUID, Set[WebSocket]] = {}
        # websocket -> user_id mapping
        self.user_connections: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, room_id: UUID, user_id: str):
        """Connect user to a room.

        Args:
            websocket: WebSocket connection
            room_id: Room identifier
            user_id: User identifier
        """
        await self._accept_websocket(websocket)

        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()

        self.active_connections[room_id].add(websocket)
        self.user_connections[websocket] = user_id
        logger.info(f"User {user_id} connected to chat room {room_id}")

    def disconnect(self, websocket: WebSocket, room_id: UUID):
        """Disconnect user from a room.

        Args:
            websocket: WebSocket connection
            room_id: Room identifier
        """
        user_id = self.user_connections.get(websocket, "unknown")

        if room_id in self.active_connections:
            self.active_connections[room_id].discard(websocket)

            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
                logger.debug(f"Chat room {room_id} is now empty")

        if websocket in self.user_connections:
            del self.user_connections[websocket]

        logger.info(f"User {user_id} disconnected from chat room {room_id}")

    async def broadcast_to_room(self, room_id: UUID, message: dict):
        """Broadcast message to all connections in a room.

        Args:
            room_id: Room identifier
            message: Message to broadcast
        """
        if room_id not in self.active_connections:
            return

        disconnected = set()
        for connection in self.active_connections[room_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message in room {room_id}: {e}", exc_info=True)
                disconnected.add(connection)

        # Remove disconnected connections
        for connection in disconnected:
            logger.warning(f"Removing disconnected connection from room {room_id}")
            self.disconnect(connection, room_id)

    async def send_to_user(self, user_id: str, message: dict):
        """Send message to specific user across all their connections.

        Args:
            user_id: User identifier
            message: Message to send
        """
        sent_count = 0
        for websocket, uid in self.user_connections.items():
            if uid == user_id:
                try:
                    await websocket.send_json(message)
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Failed to send message to user {user_id}: {e}", exc_info=True)

        if sent_count > 0:
            logger.debug(f"Sent message to user {user_id} ({sent_count} connections)")

    def get_room_connection_count(self, room_id: UUID) -> int:
        """Get number of active connections in a room.

        Args:
            room_id: Room identifier

        Returns:
            Number of active connections
        """
        return len(self.active_connections.get(room_id, set()))


# Global connection manager instance
connection_manager = ChatConnectionManager()
