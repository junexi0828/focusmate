"""Base WebSocket connection manager with common functionality."""

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from fastapi import WebSocket

# Configure logger
logger = logging.getLogger(__name__)

# Type variable for connection key (room_id, user_id, etc.)
KeyType = TypeVar("KeyType")


class BaseConnectionManager(ABC, Generic[KeyType]):
    """Base class for WebSocket connection managers.

    Provides common functionality for managing WebSocket connections,
    including connection lifecycle, message sending, and error handling.
    """

    def __init__(self) -> None:
        """Initialize base connection manager."""
        self.active_connections: dict[KeyType, list[WebSocket]] = {}
        logger.info(f"{self.__class__.__name__} initialized")

    async def _accept_websocket(self, websocket: WebSocket) -> None:
        """Accept a WebSocket connection.

        Args:
            websocket: WebSocket connection to accept
        """
        await websocket.accept()
        logger.debug(f"WebSocket connection accepted")

    def _add_connection(self, websocket: WebSocket, key: KeyType) -> None:
        """Add a connection to the active connections.

        Args:
            websocket: WebSocket connection
            key: Connection key (room_id, user_id, etc.)
        """
        if key not in self.active_connections:
            self.active_connections[key] = []
        self.active_connections[key].append(websocket)
        logger.info(f"Connection added for key={key}, total={len(self.active_connections[key])}")

    def _remove_connection(self, websocket: WebSocket, key: KeyType) -> None:
        """Remove a connection from active connections.

        Args:
            websocket: WebSocket connection
            key: Connection key (room_id, user_id, etc.)
        """
        if key in self.active_connections:
            if websocket in self.active_connections[key]:
                self.active_connections[key].remove(websocket)
                logger.info(f"Connection removed for key={key}, remaining={len(self.active_connections[key])}")

            # Clean up empty key
            if not self.active_connections[key]:
                del self.active_connections[key]
                logger.debug(f"No more connections for key={key}, removed from active connections")

    async def _send_json(self, websocket: WebSocket, message: dict[str, Any]) -> bool:
        """Send JSON message to a WebSocket.

        Args:
            websocket: Target WebSocket
            message: Message to send

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            await websocket.send_text(json.dumps(message))
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}", exc_info=True)
            return False

    async def _broadcast_with_cleanup(
        self,
        connections: list[WebSocket],
        message: dict[str, Any],
        key: KeyType
    ) -> None:
        """Broadcast message to connections and clean up failed ones.

        Args:
            connections: List of WebSocket connections
            message: Message to broadcast
            key: Connection key for cleanup
        """
        disconnected = []
        for connection in connections:
            success = await self._send_json(connection, message)
            if not success:
                disconnected.append(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            logger.warning(f"Removing disconnected connection for key={key}")
            self._remove_connection(connection, key)

    def get_connection_count(self, key: KeyType) -> int:
        """Get number of active connections for a key.

        Args:
            key: Connection key

        Returns:
            Number of active connections
        """
        return len(self.active_connections.get(key, []))

    @abstractmethod
    async def connect(self, websocket: WebSocket, *args, **kwargs) -> None:
        """Connect a WebSocket. Must be implemented by subclasses.

        Args:
            websocket: WebSocket connection
            *args, **kwargs: Additional arguments specific to implementation
        """
        pass

    @abstractmethod
    def disconnect(self, websocket: WebSocket, *args, **kwargs) -> None:
        """Disconnect a WebSocket. Must be implemented by subclasses.

        Args:
            websocket: WebSocket connection
            *args, **kwargs: Additional arguments specific to implementation
        """
        pass
