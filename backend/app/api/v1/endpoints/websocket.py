"""WebSocket endpoint for real-time communication."""

import logging
from datetime import UTC, datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.infrastructure.websocket.manager import connection_manager


logger = logging.getLogger(__name__)
router = APIRouter(tags=["websocket"])


@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str) -> None:
    """WebSocket endpoint for room real-time updates.

    Clients connect to receive:
    - Timer state updates
    - Participant join/leave events
    - Room setting changes

    Message Format:
        {
            "type": "timer_update" | "participant_joined" | "participant_left" | "room_updated",
            "data": {...}
        }

    Args:
        websocket: WebSocket connection
        room_id: Room identifier
    """
    try:
        logger.info(f"[Room WS] Connection attempt for room_id={room_id}")
        await connection_manager.connect(websocket, room_id)
        logger.info(f"[Room WS] Connected to room_id={room_id}")

        # Send welcome message
        await connection_manager.send_personal_message(
            {
                "type": "connected",
                "data": {
                    "room_id": room_id,
                    "message": "Connected to room",
                },
                "timestamp": datetime.now(UTC).isoformat(),
            },
            websocket,
        )

        # Notify others of new connection
        await connection_manager.broadcast_to_room(
            {
                "type": "participant_joined",
                "data": {
                    "room_id": room_id,
                    "connection_count": connection_manager.get_room_connection_count(
                        room_id
                    ),
                },
                "timestamp": datetime.now(UTC).isoformat(),
            },
            room_id,
        )

        while True:
            try:
                # Receive messages from client
                data = await websocket.receive_json()

                # Process client messages
                # Frontend sends: { type: "timer_start", data: {...} }
                message_type = data.get("type", "message")
                logger.debug(
                    f"[Room WS] Received message type={message_type} from room_id={room_id}"
                )

                # Handle ping/pong
                if message_type == "ping":
                    await connection_manager.send_personal_message(
                        {
                            "type": "pong",
                            "timestamp": datetime.now(UTC).isoformat(),
                        },
                        websocket,
                    )
                    continue

                # Broadcast timer actions to all in room
                await connection_manager.broadcast_to_room(
                    {
                        "type": message_type,
                        "data": data.get("data", {}),
                        "timestamp": datetime.now(UTC).isoformat(),
                    },
                    room_id,
                )

            except ValueError as e:
                # Invalid JSON or message format
                logger.warning(
                    f"[Room WS] Invalid message format from room_id={room_id}: {e}"
                )
                try:
                    await connection_manager.send_personal_message(
                        {
                            "type": "error",
                            "error": {
                                "code": "invalid_message",
                                "message": "Invalid message format",
                            },
                            "timestamp": datetime.now(UTC).isoformat(),
                        },
                        websocket,
                    )
                except Exception:
                    pass
                continue

            except RuntimeError as e:
                # Connection was closed
                if 'Cannot call "receive"' in str(e) or "Connection closed" in str(e):
                    logger.info(f"[Room WS] Connection closed for room_id={room_id}")
                    break
                logger.error(f"[Room WS] RuntimeError for room_id={room_id}: {e}")
                break

            except Exception as e:
                logger.error(
                    f"[Room WS] Error processing message for room_id={room_id}: {e}",
                    exc_info=True,
                )
                try:
                    await connection_manager.send_personal_message(
                        {
                            "type": "error",
                            "error": {
                                "code": "server_error",
                                "message": "Internal server error",
                            },
                            "timestamp": datetime.now(UTC).isoformat(),
                        },
                        websocket,
                    )
                except Exception:
                    pass
                continue

    except WebSocketDisconnect as e:
        logger.info(
            f"[Room WS] Client disconnected from room_id={room_id} (code: {e.code})"
        )
        connection_manager.disconnect(websocket, room_id)

        # Notify others of disconnection
        try:
            await connection_manager.broadcast_to_room(
                {
                    "type": "participant_left",
                    "data": {
                        "room_id": room_id,
                        "connection_count": connection_manager.get_room_connection_count(
                            room_id
                        ),
                    },
                    "timestamp": datetime.now(UTC).isoformat(),
                },
                room_id,
            )
        except Exception as e:
            logger.error(
                f"[Room WS] Error broadcasting disconnect for room_id={room_id}: {e}"
            )

    except Exception as e:
        logger.error(f"[Room WS] Fatal error for room_id={room_id}: {e}", exc_info=True)
        connection_manager.disconnect(websocket, room_id)
        try:
            await websocket.close(code=1011)  # Internal error
        except Exception:
            pass
