"""Messaging API endpoints - conversations and 1:1 messages."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.exceptions import NotFoundException
from app.domain.messaging.schemas import (
    ConversationDetailResponse,
    ConversationListResponse,
    MarkMessagesReadRequest,
    MarkMessagesReadResponse,
    MessageCreate,
    MessageResponse,
)
from app.domain.messaging.service import MessagingService
from app.infrastructure.database.session import DatabaseSession
from app.infrastructure.repositories.messaging_repository import (
    ConversationRepository,
    MessageRepository,
)
from app.infrastructure.repositories.user_repository import UserRepository

router = APIRouter(prefix="/messages", tags=["messaging"])


# Dependency Injection
def get_conversation_repository(db: DatabaseSession) -> ConversationRepository:
    """Get conversation repository."""
    return ConversationRepository(db)


def get_message_repository(db: DatabaseSession) -> MessageRepository:
    """Get message repository."""
    return MessageRepository(db)


def get_user_repository(db: DatabaseSession) -> UserRepository:
    """Get user repository."""
    return UserRepository(db)


def get_messaging_service(
    conversation_repo: Annotated[ConversationRepository, Depends(get_conversation_repository)],
    message_repo: Annotated[MessageRepository, Depends(get_message_repository)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> MessagingService:
    """Get messaging service."""
    return MessagingService(conversation_repo, message_repo, user_repo)


# Message Endpoints
@router.post("/send", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    data: MessageCreate,
    sender_id: str = Query(..., description="User ID sending the message"),
    service: Annotated[MessagingService, Depends(get_messaging_service)] = None,
) -> MessageResponse:
    """Send a message to another user.

    Creates a new conversation if one doesn't exist.

    Args:
        data: Message content and receiver_id
        sender_id: ID of user sending the message
        service: Messaging service

    Returns:
        Created message with sender/receiver info

    Raises:
        HTTPException: If receiver not found
    """
    try:
        return await service.send_message(sender_id, data)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


# Conversation Endpoints
@router.get("/conversations", response_model=list[ConversationListResponse])
async def get_user_conversations(
    user_id: str = Query(..., description="User ID"),
    service: Annotated[MessagingService, Depends(get_messaging_service)] = None,
) -> list[ConversationListResponse]:
    """Get all conversations for a user.

    Args:
        user_id: User identifier
        service: Messaging service

    Returns:
        List of conversations with last message and unread count
    """
    return await service.get_user_conversations(user_id)


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation_detail(
    conversation_id: str,
    user_id: str = Query(..., description="User ID requesting conversation"),
    limit: int = Query(50, ge=1, le=100, description="Max messages to return"),
    offset: int = Query(0, ge=0, description="Message offset for pagination"),
    service: Annotated[MessagingService, Depends(get_messaging_service)] = None,
) -> ConversationDetailResponse:
    """Get conversation details with messages.

    Args:
        conversation_id: Conversation identifier
        user_id: User requesting the conversation
        limit: Maximum number of messages to return
        offset: Number of messages to skip
        service: Messaging service

    Returns:
        Conversation details with paginated messages

    Raises:
        HTTPException: If conversation not found or user not authorized
    """
    try:
        return await service.get_conversation_detail(conversation_id, user_id, limit, offset)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.post("/conversations/{conversation_id}/read", response_model=MarkMessagesReadResponse)
async def mark_messages_as_read(
    conversation_id: str,
    data: MarkMessagesReadRequest,
    user_id: str = Query(..., description="User ID marking messages as read"),
    service: Annotated[MessagingService, Depends(get_messaging_service)] = None,
) -> MarkMessagesReadResponse:
    """Mark messages as read in a conversation.

    Args:
        conversation_id: Conversation identifier
        data: List of message IDs to mark as read
        user_id: User marking messages as read
        service: Messaging service

    Returns:
        Number of messages marked and new unread count

    Raises:
        HTTPException: If conversation not found or user not authorized
    """
    try:
        return await service.mark_messages_as_read(conversation_id, user_id, data.message_ids)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get("/unread-count", response_model=dict)
async def get_unread_message_count(
    user_id: str = Query(..., description="User ID"),
    service: Annotated[MessagingService, Depends(get_messaging_service)] = None,
) -> dict:
    """Get total unread message count for a user.

    Args:
        user_id: User identifier
        service: Messaging service

    Returns:
        Total unread message count
    """
    total_unread = await service.get_unread_message_count(user_id)
    return {"user_id": user_id, "unread_count": total_unread}
