"""WebSocket endpoint for real-time communication."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.infrastructure.websocket.manager import connection_manager

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
    await connection_manager.connect(websocket, room_id)

    # Send welcome message
    await connection_manager.send_personal_message(
        {
            "type": "connected",
            "data": {
                "room_id": room_id,
                "message": "Connected to room",
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        websocket,
    )

    # Notify others of new connection
    await connection_manager.broadcast_to_room(
        {
            "type": "participant_joined",
            "data": {
                "room_id": room_id,
                "connection_count": connection_manager.get_room_connection_count(room_id),
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        room_id,
    )

    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_json()

            # Process client messages
            # Frontend sends: { type: "timer_start", data: {...} }
            message_type = data.get("type", "message")

            # Handle ping/pong
            if message_type == "ping":
                await connection_manager.send_personal_message(
                    {
                        "type": "pong",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                    websocket,
                )
                continue

            # Broadcast timer actions to all in room
            await connection_manager.broadcast_to_room(
                {
                    "type": message_type,
                    "data": data.get("data", {}),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
                room_id,
            )

    except WebSocketDisconnect:
        # Handle disconnection
        connection_manager.disconnect(websocket, room_id)

        # Notify others of disconnection
        await connection_manager.broadcast_to_room(
            {
                "type": "participant_left",
                "data": {
                    "room_id": room_id,
                    "connection_count": connection_manager.get_room_connection_count(room_id),
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            room_id,
        )
