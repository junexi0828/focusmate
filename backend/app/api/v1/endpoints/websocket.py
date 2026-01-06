"""WebSocket endpoint for real-time communication."""

import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from app.core.exceptions import InvalidTimerStateException, RoomNotFoundException, TimerNotFoundException
from app.infrastructure.websocket.manager import connection_manager
from app.infrastructure.database.session import get_db
from app.infrastructure.repositories.room_repository import RoomRepository
from app.infrastructure.repositories.timer_repository import TimerRepository
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.participant_repository import ParticipantRepository
from app.domain.timer.service import TimerService
from app.infrastructure.redis.pubsub_manager import redis_pubsub_manager
from app.core.config import settings
from datetime import UTC, datetime
from app.shared.constants.timer import TimerPhase


logger = logging.getLogger(__name__)
router = APIRouter(tags=["websocket"])


@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    db: AsyncSession = Depends(get_db),
    token: str | None = Query(None),
) -> None:
    """WebSocket endpoint for room real-time updates.

    Clients connect to receive:
    - Timer state updates
    - Participant join/leave events
    - Room setting changes

    Message Format:
        {
            "event": "timer_update" | "participant_update" | "room_updated",
            "data": {...}
        }

    Args:
        websocket: WebSocket connection
        room_id: Room identifier
        token: JWT token for authentication
    """
    current_user = None
    try:
        # Authenticate user
        if token:
            try:
                payload = jwt.decode(
                    token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
                )
                user_id: str = payload.get("sub")
                if user_id:
                    user_repo = UserRepository(db)
                    user = await user_repo.get_by_id(user_id)
                    if user and user.is_active:
                        current_user = user
            except (JWTError, Exception) as e:
                logger.warning(f"[Room WS] Auth failed for room_id={room_id}: {e}")
                # We typically close if auth fails, but for public rooms we might allow guests?
                # For now, let's enforce auth or handle guests if needed.
                # Assuming auth is required based on "current_user" usage below.
                await websocket.close(code=1008, reason="Authentication failed")
                return

        if not current_user:
            await websocket.close(code=1008, reason="Authentication required")
            return

        logger.info(f"[Room WS] Connection attempt by {current_user.username} for room_id={room_id}")
        await connection_manager.connect(websocket, room_id)

        # Subscribe to Redis channel for multi-server broadcasting
        try:
            from uuid import UUID
            await redis_pubsub_manager.subscribe_to_room(UUID(room_id))
        except Exception as e:
            logger.error(f"[Room WS] Failed to subscribe to Redis channel: {e}")

        logger.info(f"[Room WS] Connected {current_user.username} to room_id={room_id}")

        timer_service = TimerService(
            TimerRepository(db),
            RoomRepository(db),
        )

        # Send welcome message
        await connection_manager.send_personal_message(
            {
                "event": "connected",
                "data": {
                    "room_id": room_id,
                    "message": "Connected to room",
                    "user_id": current_user.id,
                },
                "timestamp": datetime.now(UTC).isoformat(),
            },
            websocket,
        )

        participant_repo = ParticipantRepository(db)
        await participant_repo.mark_connected_by_user_and_room(current_user.id, room_id)
        participant_count = await participant_repo.count_active_participants(room_id)

        # Notify others of new connection (Global Broadcast)
        await redis_pubsub_manager.publish_event(
            UUID(room_id),
            "participant_update",
            {
                "action": "joined",
                "participant": {
                    "id": current_user.id,
                    "username": current_user.username,
                    "name": current_user.name,
                },
                "current_count": participant_count,
                "room_id": room_id,
            },
        )

        while True:
            try:
                # Receive messages from client
                data = await websocket.receive_json()

                # Process client messages
                message_type = data.get("type", "message")
                logger.debug(
                    f"[Room WS] Received message type={message_type} from {current_user.username} in room_id={room_id}"
                )

                # Handle ping/pong
                if message_type == "ping":
                    await connection_manager.send_personal_message(
                        {
                            "event": "pong",
                            "timestamp": datetime.now(UTC).isoformat(),
                        },
                        websocket,
                    )
                    continue

                if message_type in {
                    "timer_start",
                    "timer_pause",
                    "timer_resume",
                    "timer_reset",
                    "timer_complete",
                }:
                    timer_state = None
                    completed_session_type = None

                    try:
                        if message_type == "timer_start":
                            session_type = data.get("data", {}).get("session_type", "work")
                            timer_state = await timer_service.start_timer(
                                room_id,
                                session_type,
                                db=db,
                            )
                        elif message_type == "timer_pause":
                            timer_state = await timer_service.pause_timer(room_id)
                        elif message_type == "timer_resume":
                            timer_state = await timer_service.resume_timer(room_id)
                        elif message_type == "timer_reset":
                            timer_state = await timer_service.reset_timer(room_id)
                        elif message_type == "timer_complete":
                            timer = await timer_service.timer_repo.get_by_room_id(room_id)
                            if not timer:
                                raise TimerNotFoundException(room_id)
                            room = await timer_service.room_repo.get_by_id(room_id)
                            if not room:
                                raise RoomNotFoundException(room_id)

                            completed_session_type = (
                                "work" if timer.phase == TimerPhase.WORK.value else "break"
                            )
                            completion_time = timer.completed_at or datetime.now(UTC)
                            timer_state = await timer_service.complete_phase(
                                room_id,
                                completed_at=completion_time,
                            )
                            if timer.phase == TimerPhase.WORK.value:
                                await timer_service.record_work_sessions_for_timer(
                                    db,
                                    timer,
                                    room,
                                    completion_time,
                                )
                    except InvalidTimerStateException:
                        timer_state = await timer_service.get_timer_state(room_id, db=db)

                    if timer_state:
                        # Global Broadcast for timer events
                        if completed_session_type:
                            next_session_type = (
                                "break" if completed_session_type == "work" else "work"
                            )
                            await redis_pubsub_manager.publish_event(
                                UUID(room_id),
                                "timer_complete",
                                {
                                    "completed_session_type": completed_session_type,
                                    "next_session_type": next_session_type,
                                    "auto_start": timer_state.status == "running",
                                }
                            )

                        await redis_pubsub_manager.publish_event(
                            UUID(room_id),
                            "timer_update",
                            timer_state.model_dump()
                        )
                    continue

                # Ignore unknown message types
                continue

            except ValueError as e:
                logger.warning(
                    f"[Room WS] Invalid message format from {current_user.username}: {e}"
                )
                continue

            except RuntimeError as e:
                # Connection was closed
                if 'Cannot call "receive"' in str(e) or "Connection closed" in str(e):
                    break
                logger.error(f"[Room WS] RuntimeError for {current_user.username}: {e}")
                break

            except Exception as e:
                logger.error(
                    f"[Room WS] Error processing message: {e}",
                    exc_info=True,
                )
                continue

    except WebSocketDisconnect as e:
        logger.info(
            f"[Room WS] Client disconnected from room_id={room_id} (code: {e.code})"
        )
        connection_manager.disconnect(websocket, room_id)

        # Unsubscribe if no more connections in this room (on this server)
        if connection_manager.get_room_connection_count(room_id) == 0:
            try:
                from uuid import UUID
                await redis_pubsub_manager.unsubscribe_from_room(UUID(room_id))
            except Exception as ex:
                logger.error(f"[Room WS] Failed to unsubscribe: {ex}")

        # Notify others of disconnection (Global Broadcast)
        try:
            if current_user:
                from uuid import UUID
                participant_repo = ParticipantRepository(db)
                await participant_repo.mark_disconnected_by_user_and_room(current_user.id, room_id)
                participant_count = await participant_repo.count_active_participants(room_id)
                await redis_pubsub_manager.publish_event(
                    UUID(room_id),
                    "participant_update",
                    {
                        "action": "left",
                        "participant_id": current_user.id,
                        "current_count": participant_count,
                        "room_id": room_id,
                    }
                )
        except Exception as e:
            logger.error(
                f"[Room WS] Error broadcasting disconnect for room_id={room_id}: {e}"
            )

    except Exception as e:
        logger.error(f"[Room WS] Fatal error for room_id={room_id}: {e}", exc_info=True)
        connection_manager.disconnect(websocket, room_id)
        try:
            await websocket.close(code=1011)
        except Exception:
            pass
