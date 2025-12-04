"""WebSocket connection manager for real-time communication."""

import json
from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    """Manages WebSocket connections for rooms.
    
    Handles connection lifecycle and message broadcasting.
    """

    def __init__(self) -> None:
        """Initialize connection manager."""
        # room_id -> list of WebSocket connections
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str) -> None:
        """Accept and register a WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            room_id: Room identifier
        """
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: str) -> None:
        """Remove a WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            room_id: Room identifier
        """
        if room_id in self.active_connections:
            if websocket in self.active_connections[room_id]:
                self.active_connections[room_id].remove(websocket)
            # Clean up empty room
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

    async def send_personal_message(self, message: dict[str, Any], websocket: WebSocket) -> None:
        """Send message to specific connection.
        
        Args:
            message: Message data
            websocket: Target WebSocket
        """
        await websocket.send_text(json.dumps(message))

    async def broadcast_to_room(self, message: dict[str, Any], room_id: str) -> None:
        """Broadcast message to all connections in a room.
        
        Args:
            message: Message data
            room_id: Room identifier
        """
        if room_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[room_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception:
                    # Mark for removal if send fails
                    disconnected.append(connection)
            
            # Clean up disconnected clients
            for connection in disconnected:
                self.disconnect(connection, room_id)

    def get_room_connection_count(self, room_id: str) -> int:
        """Get number of active connections in a room.
        
        Args:
            room_id: Room identifier
            
        Returns:
            Connection count
        """
        return len(self.active_connections.get(room_id, []))


# Global connection manager instance
connection_manager = ConnectionManager()
