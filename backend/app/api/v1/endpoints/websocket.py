"""WebSocket endpoint for real-time communication."""

import logging
import asyncio

from typing import Any
from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from app.core.exceptions import InvalidTimerStateException, RoomNotFoundException, TimerNotFoundException
from app.infrastructure.websocket.chat_manager import connection_manager
from app.infrastructure.repositories.room_repository import RoomRepository
from app.infrastructure.repositories.timer_repository import TimerRepository
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.participant_repository import ParticipantRepository
from app.domain.timer.service import TimerService
from app.infrastructure.redis.pubsub_manager import redis_pubsub_manager
from app.core.config import settings
from app.api.utils.websocket_auth import extract_ws_token
from datetime import UTC, datetime
from app.shared.constants.timer import TimerPhase
from app.domain.room_chat.service import RoomChatService
from app.infrastructure.redis.room_chat_cache import append_message, get_recent_messages


logger = logging.getLogger(__name__)
router = APIRouter(tags=["websocket"])


async def _commit_or_rollback(db: AsyncSession) -> None:
    """Commit a transaction or rollback on failure."""
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise


@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
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
    # Accept connection immediately to establish handshake (prevents 1006)
    await websocket.accept()

    from app.infrastructure.database.session import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        current_user = None
        token_id = None
        try:
            # Authenticate user
            jwt_token = extract_ws_token(websocket, token)
            if jwt_token:
                user_id = None
                try:
                    payload = jwt.decode(
                        jwt_token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
                    )
                    user_id = payload.get("sub")
                except (JWTError, Exception) as e:
                    logger.warning(f"[Room WS] Token decode failed for room_id={room_id}: {e}")

                if user_id:
                    try:
                        # Extract token ID (JTI) for tracking session activity
                        token_id = payload.get("jti")

                        user_repo = UserRepository(db)
                        user = await user_repo.get_by_id(user_id)
                        if user and user.is_active:
                            current_user = user
                    except Exception as db_e:
                        logger.error(
                            f"[Room WS] DB Authentication failed for user_id={user_id}: {db_e}",
                            exc_info=True,
                        )
                        # current_user remains None, triggering 1008 close below
                else:
                    await websocket.close(code=1008, reason="Authentication failed")
                    return

            if not current_user:
                # Connection is already accepted, so we can send a close frame
                await websocket.close(code=1008, reason="Authentication failed")
                return

            logger.info(
                f"[Room WS] Connection attempt by {current_user.username} for room_id={room_id}"
            )
            await connection_manager.connect(websocket, UUID(room_id), str(current_user.id))

            # Subscribe to Redis channel for multi-server broadcasting
            try:
                await redis_pubsub_manager.subscribe_to_room(UUID(room_id))
            except Exception as e:
                logger.error(f"[Room WS] Failed to subscribe to Redis channel: {e}")

            logger.info(f"[Room WS] Connected {current_user.username} to room_id={room_id}")

            # Track session in background (fire-and-forget)
            # This prevents Redis latency from blocking the WebSocket connection
            asyncio.create_task(_track_session_background(current_user, room_id))

            timer_service = TimerService(
                TimerRepository(db),
                RoomRepository(db),
            )
            chat_service = RoomChatService()
            participant_repo = ParticipantRepository(db)
            is_participant = False
            from app.infrastructure.redis.session_helpers import track_user_activity

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

            # Mark participant as connected (non-critical, don't fail connection if this fails)
            participant_count = 1
            try:
                participant = await participant_repo.get_by_user_and_room(
                    current_user.id, room_id
                )
                is_participant = participant is not None
                await participant_repo.mark_connected_by_user_and_room(current_user.id, room_id)
                participant_count = await participant_repo.count_active_participants(room_id)
                await _commit_or_rollback(db)
            except Exception as e:
                logger.warning(f"[Room WS] Failed to mark participant connected: {e}")

            # Send recent chat backfill (best effort)
            try:
                recent_messages = await get_recent_messages(room_id)
                if recent_messages:
                    await connection_manager.send_personal_message(
                        {
                            "event": "chat_backfill",
                            "data": {"messages": recent_messages},
                            "timestamp": datetime.now(UTC).isoformat(),
                        },
                        websocket,
                    )
            except Exception as e:
                logger.debug(f"[Room WS] Chat backfill failed: {e}")

            # Notify others of new connection (Global Broadcast)
            try:
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
            except Exception as e:
                logger.warning(f"[Room WS] Failed to publish participant join event: {e}")

            while True:
                try:
                    # Receive messages from client
                    data = await websocket.receive_json()

                    # Track activity on ANY message (keeps session alive)
                    if token_id:
                        try:
                            await track_user_activity(current_user.id, token_id, room_id)
                        except Exception as e:
                            logger.debug(f"[Room WS] Activity tracking failed: {e}")

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
                    if message_type == "pong":
                        continue
                    if message_type == "chat_message":
                        try:
                            if not is_participant:
                                participant = await participant_repo.get_by_user_and_room(
                                    current_user.id, room_id
                                )
                                is_participant = participant is not None

                            if not is_participant:
                                await connection_manager.send_personal_message(
                                    {
                                        "event": "error",
                                        "error": {
                                            "code": "NOT_IN_ROOM",
                                            "message": "방에 참여한 사용자만 채팅할 수 있습니다.",
                                        },
                                        "timestamp": datetime.now(UTC).isoformat(),
                                    },
                                    websocket,
                                )
                                continue

                            content = data.get("data", {}).get("content", "")
                            sender_name = (
                                current_user.name
                                or current_user.username
                                or "사용자"
                            )
                            chat_message = chat_service.build_message(
                                room_id=room_id,
                                sender_id=current_user.id,
                                sender_name=sender_name,
                                content=content,
                            )
                            message_payload = chat_message.model_dump(mode="json")
                            await append_message(room_id, message_payload)
                            await redis_pubsub_manager.publish_event(
                                UUID(room_id),
                                "chat_message",
                                {"message": message_payload},
                            )
                        except ValueError as e:
                            await connection_manager.send_personal_message(
                                {
                                    "event": "error",
                                    "error": {
                                        "code": "INVALID_CHAT_MESSAGE",
                                        "message": str(e),
                                    },
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
                                timer_state = await timer_service.reset_timer(room_id, db=db)
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
                                    db=db,
                                )
                            await _commit_or_rollback(db)
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
                                timer_state.model_dump(mode="json")
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
            connection_manager.disconnect(websocket, UUID(room_id))

            # Unsubscribe if no more connections in this room (on this server)
            if connection_manager.get_room_connection_count(room_id) == 0:
                try:
                    await redis_pubsub_manager.unsubscribe_from_room(UUID(room_id))
                except Exception as ex:
                    logger.error(f"[Room WS] Failed to unsubscribe: {ex}")

            # Notify others of disconnection (Global Broadcast)
            try:
                if current_user:
                    participant_repo = ParticipantRepository(db)
                    await participant_repo.mark_disconnected_by_user_and_room(
                        current_user.id, room_id
                    )
                    participant_count = await participant_repo.count_active_participants(room_id)
                    await _commit_or_rollback(db)
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
            connection_manager.disconnect(websocket, UUID(room_id))
            try:
                await websocket.close(code=1011)
            except Exception:
                pass


async def _track_session_background(user: Any, room_id: str) -> None:
    """Track session activity in background to avoid blocking WebSocket handshake.

    Args:
        user: Current user object
        room_id: Room identifier
    """
    try:
        from app.infrastructure.redis.session_helpers import get_token_id, track_user_activity
        from app.infrastructure.redis.circuit_breaker import CircuitOpenError

        token_id = await get_token_id(user.id)
        if token_id:
            await track_user_activity(user.id, token_id, room_id)
            logger.debug(f"[Room WS] ✅ Session tracking active for user {user.id}")
        else:
            logger.debug(f"[Room WS] ⚠️ No token_id found for user {user.id}")
    except CircuitOpenError:
        logger.debug(f"[Room WS] ⚠️ Redis circuit open, skipping session tracking for user {user.id}")
    except Exception as e:
        logger.warning(f"[Room WS] ⚠️ Background session tracking failed: {e}")
