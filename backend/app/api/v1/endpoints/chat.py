"""Chat API endpoints."""

from typing import Annotated, List, Optional
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.websockets import WebSocketState

from app.api.deps import DatabaseSession, get_current_user
from app.core.security import decode_jwt_token
from app.domain.chat.schemas import (
    ChatMemberResponse,
    ChatRoomListResponse,
    ChatRoomResponse,
    DirectChatCreate,
    MessageCreate,
    MessageListResponse,
    MessageResponse,
    MessageUpdate,
    TeamChatCreate,
)
from app.domain.chat.service import ChatService
from app.infrastructure.repositories.chat_repository import ChatRepository
from app.infrastructure.redis.pubsub_manager import redis_pubsub_manager
from app.infrastructure.websocket.chat_manager import connection_manager
from app.services.chat_file_upload import ChatFileUploadService

router = APIRouter(prefix="/chats", tags=["chats"])


def get_chat_service(db: Annotated[DatabaseSession, Depends()]) -> ChatService:
    """Get chat service dependency."""
    repository = ChatRepository(db)
    return ChatService(repository)


# Room Endpoints
@router.get("/rooms", response_model=ChatRoomListResponse)
async def get_user_rooms(
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    service: Annotated[ChatService, Depends(get_chat_service)] = None,
    room_type: Optional[str] = Query(None, regex="^(direct|team|matching)$"),
) -> ChatRoomListResponse:
    """Get all chat rooms for the current user."""
    user_id = current_user["id"]
    rooms = await service.get_user_rooms(user_id, room_type)
    return ChatRoomListResponse(rooms=rooms, total=len(rooms))


@router.get("/unread-count")
async def get_unread_count(
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    service: Annotated[ChatService, Depends(get_chat_service)] = None,
) -> dict:
    """Get total unread message count for the current user."""
    try:
        user_id = current_user["id"]
        count = await service.get_unread_count(user_id)
        return {"count": count}
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Get unread count error: {str(e)}", exc_info=True)
        # Return 0 if there's an error (e.g., chat tables don't exist yet)
        return {"count": 0}


@router.post("/rooms/direct", status_code=status.HTTP_201_CREATED)
async def create_direct_chat(
    data: DirectChatCreate,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    service: Annotated[ChatService, Depends(get_chat_service)] = None,
) -> ChatRoomResponse:
    """Create or get direct chat."""
    try:
        return await service.create_direct_chat(current_user["id"], data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/rooms/team", status_code=status.HTTP_201_CREATED)
async def create_team_chat(
    data: TeamChatCreate,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    service: Annotated[ChatService, Depends(get_chat_service)] = None,
) -> ChatRoomResponse:
    """Create team chat."""
    try:
        return await service.create_team_chat(current_user["id"], data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/rooms/{room_id}")
async def get_room(
    room_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    service: Annotated[ChatService, Depends(get_chat_service)] = None,
) -> ChatRoomResponse:
    """Get room details."""
    try:
        return await service.get_room(room_id, current_user["id"])
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/rooms/{room_id}/members", response_model=List[ChatMemberResponse])
async def get_room_members(
    room_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    service: Annotated[ChatService, Depends(get_chat_service)] = None,
) -> List[ChatMemberResponse]:
    """Get all members of a chat room."""
    # Verify user is member
    member = await service.repository.get_member(room_id, current_user["id"])
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this room",
        )

    # Get all members
    members = await service.repository.get_room_members(room_id)
    return [ChatMemberResponse.model_validate(m) for m in members]


# Message Endpoints
@router.get("/rooms/{room_id}/messages")
async def get_messages(
    room_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    before_message_id: Optional[UUID] = None,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    service: Annotated[ChatService, Depends(get_chat_service)] = None,
) -> MessageListResponse:
    """Get messages from room."""
    try:
        return await service.get_messages(
            room_id, current_user["id"], limit, before_message_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/rooms/{room_id}/messages", status_code=status.HTTP_201_CREATED)
async def send_message(
    room_id: UUID,
    data: MessageCreate,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    service: Annotated[ChatService, Depends(get_chat_service)] = None,
) -> MessageResponse:
    """Send a message."""
    try:
        message = await service.send_message(room_id, current_user["id"], data)

        # Publish to Redis for cross-server synchronization
        await redis_pubsub_manager.publish_message(
            room_id,
            message.model_dump(mode="json"),
        )

        # Also broadcast to local WebSocket connections
        await connection_manager.broadcast_to_room(
            room_id,
            {
                "type": "message",
                "message": message.model_dump(mode="json"),
            },
        )

        return message
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/rooms/{room_id}/messages/{message_id}")
async def update_message(
    room_id: UUID,
    message_id: UUID,
    data: MessageUpdate,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    service: Annotated[ChatService, Depends(get_chat_service)] = None,
) -> MessageResponse:
    """Update a message."""
    try:
        message = await service.update_message(
            message_id, current_user["id"], data.content
        )

        # Publish update to Redis
        await redis_pubsub_manager.publish_event(
            room_id,
            "message_updated",
            message.model_dump(mode="json"),
        )

        # Broadcast update
        await connection_manager.broadcast_to_room(
            room_id,
            {
                "type": "message_updated",
                "message": message.model_dump(mode="json"),
            },
        )

        return message
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/rooms/{room_id}/upload")
async def upload_files(
    room_id: UUID,
    files: List[UploadFile] = File(...),
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    service: Annotated[ChatService, Depends(get_chat_service)] = None,
) -> dict:
    """Upload files to chat room."""
    # Verify user is member
    member = await service.repository.get_member(room_id, current_user["id"])
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this room",
        )

    # Upload files
    upload_service = ChatFileUploadService()
    results = await upload_service.save_multiple_files(
        files, current_user["id"], str(room_id)
    )

    return {
        "uploaded": len(results),
        "files": [{"path": path, "url": url} for path, url in results],
    }


@router.post("/rooms/{room_id}/messages/{message_id}/react")
async def add_reaction(
    room_id: UUID,
    message_id: UUID,
    emoji: str = Query(..., max_length=10),
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    service: Annotated[ChatService, Depends(get_chat_service)] = None,
) -> dict:
    """Add emoji reaction to message."""
    # Verify user is member
    member = await service.repository.get_member(room_id, current_user["id"])
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this room",
        )

    # Get message
    message = await service.repository.get_message_by_id(message_id)
    if not message or message.room_id != room_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )

    # Add reaction
    reactions = message.reactions or []
    user_id = current_user["id"]

    # Check if user already reacted with this emoji
    existing_reaction = next(
        (r for r in reactions if r.get("emoji") == emoji and user_id in r.get("users", [])),
        None,
    )

    if existing_reaction:
        return {"message": "Already reacted", "reactions": reactions}

    # Find or create reaction entry
    reaction_entry = next(
        (r for r in reactions if r.get("emoji") == emoji),
        None,
    )

    if reaction_entry:
        reaction_entry["users"].append(user_id)
        reaction_entry["count"] = len(reaction_entry["users"])
    else:
        reactions.append({
            "emoji": emoji,
            "users": [user_id],
            "count": 1,
        })

    # Update message
    message.reactions = reactions
    await service.repository.session.commit()

    # Broadcast update
    await redis_pubsub_manager.publish_event(
        room_id,
        "reaction_added",
        {"message_id": str(message_id), "emoji": emoji, "user_id": user_id},
    )

    return {"message": "Reaction added", "reactions": reactions}


@router.delete("/rooms/{room_id}/messages/{message_id}/react")
async def remove_reaction(
    room_id: UUID,
    message_id: UUID,
    emoji: str = Query(..., max_length=10),
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    service: Annotated[ChatService, Depends(get_chat_service)] = None,
) -> dict:
    """Remove emoji reaction from message."""
    # Verify user is member
    member = await service.repository.get_member(room_id, current_user["id"])
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this room",
        )

    # Get message
    message = await service.repository.get_message_by_id(message_id)
    if not message or message.room_id != room_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )

    # Remove reaction
    reactions = message.reactions or []
    user_id = current_user["id"]

    for reaction in reactions:
        if reaction.get("emoji") == emoji and user_id in reaction.get("users", []):
            reaction["users"].remove(user_id)
            reaction["count"] = len(reaction["users"])
            if reaction["count"] == 0:
                reactions.remove(reaction)
            break

    # Update message
    message.reactions = reactions
    await service.repository.session.commit()

    # Broadcast update
    await redis_pubsub_manager.publish_event(
        room_id,
        "reaction_removed",
        {"message_id": str(message_id), "emoji": emoji, "user_id": user_id},
    )

    return {"message": "Reaction removed", "reactions": reactions}


@router.delete("/rooms/{room_id}/messages/{message_id}")
async def delete_message(
    room_id: UUID,
    message_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    service: Annotated[ChatService, Depends(get_chat_service)] = None,
) -> MessageResponse:
    """Delete a message."""
    try:
        message = await service.delete_message(message_id, current_user["id"])

        # Publish deletion to Redis
        await redis_pubsub_manager.publish_event(
            room_id,
            "message_deleted",
            {"message_id": str(message_id)},
        )

        # Broadcast deletion
        await connection_manager.broadcast_to_room(
            room_id,
            {
                "type": "message_deleted",
                "message_id": str(message_id),
            },
        )

        return message
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/rooms/{room_id}/search")
async def search_messages(
    room_id: UUID,
    q: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=100),
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    service: Annotated[ChatService, Depends(get_chat_service)] = None,
) -> MessageListResponse:
    """Search messages in room."""
    # Verify user is member
    member = await service.repository.get_member(room_id, current_user["id"])
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this room",
        )

    # Search messages
    messages = await service.repository.search_messages(room_id, q, limit)

    return MessageListResponse(
        messages=[MessageResponse.model_validate(m) for m in messages],
        total=len(messages),
        has_more=len(messages) >= limit,
    )


@router.post("/rooms/{room_id}/read")
async def mark_as_read(
    room_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    service: Annotated[ChatService, Depends(get_chat_service)] = None,
) -> dict:
    """Mark all messages as read."""
    try:
        await service.mark_as_read(room_id, current_user["id"])
        return {"message": "Marked as read"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# WebSocket Endpoint
@router.websocket("/ws")
async def websocket_chat(
    websocket: WebSocket,
    token: str = Query(...),
):
    """WebSocket endpoint for real-time chat."""
    # Verify token and get user
    try:
        payload = decode_jwt_token(token)
        user_id: str = payload.get("sub")
        if not user_id:
            if websocket.client_state != WebSocketState.DISCONNECTED:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Note: Full user verification would require DB session
        # For WebSocket, we trust the JWT token for now
        # Full verification can be added if needed

    except Exception:
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()

            # Handle different message types
            if data.get("type") == "join_room":
                room_id = UUID(data["room_id"])
                await connection_manager.connect(websocket, room_id, user_id)
                await websocket.send_json({"type": "joined", "room_id": str(room_id)})

            elif data.get("type") == "leave_room":
                room_id = UUID(data["room_id"])
                connection_manager.disconnect(websocket, room_id)
                await websocket.send_json({"type": "left", "room_id": str(room_id)})

            elif data.get("type") == "typing":
                room_id = UUID(data["room_id"])
                await connection_manager.broadcast_to_room(
                    room_id,
                    {
                        "type": "typing",
                        "user_id": user_id,
                        "room_id": str(room_id),
                    },
                )

    except WebSocketDisconnect:
        # Clean up all connections for this websocket
        for room_id in list(connection_manager.active_connections.keys()):
            connection_manager.disconnect(websocket, room_id)
