"""WebSocket connection manager for unified chat system."""

import json
from typing import Dict, Set
from uuid import UUID

from fastapi import WebSocket


class ConnectionManager:
    """Manages WebSocket connections for real-time chat."""

    def __init__(self):
        # room_id -> set of websockets
        self.active_connections: Dict[UUID, Set[WebSocket]] = {}
        # websocket -> user_id
        self.user_connections: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, room_id: UUID, user_id: str):
        """Connect user to a room."""
        await websocket.accept()

        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()

        self.active_connections[room_id].add(websocket)
        self.user_connections[websocket] = user_id

    def disconnect(self, websocket: WebSocket, room_id: UUID):
        """Disconnect user from a room."""
        if room_id in self.active_connections:
            self.active_connections[room_id].discard(websocket)

            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

        if websocket in self.user_connections:
            del self.user_connections[websocket]

    async def broadcast_to_room(self, room_id: UUID, message: dict):
        """Broadcast message to all connections in a room."""
        if room_id not in self.active_connections:
            return

        disconnected = set()
        for connection in self.active_connections[room_id]:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)

        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection, room_id)

    async def send_to_user(self, user_id: str, message: dict):
        """Send message to specific user across all their connections."""
        for websocket, uid in self.user_connections.items():
            if uid == user_id:
                try:
                    await websocket.send_json(message)
                except Exception:
                    pass

    def get_room_connection_count(self, room_id: UUID) -> int:
        """Get number of active connections in a room."""
        return len(self.active_connections.get(room_id, set()))


# Global connection manager instance
connection_manager = ConnectionManager()
