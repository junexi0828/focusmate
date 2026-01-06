"""Messaging domain service - 1:1 conversations and messages."""


from typing import List
from app.core.exceptions import NotFoundException
from app.domain.messaging.schemas import (
    ConversationDetailResponse,
    ConversationListResponse,
    ConversationResponse,
    MarkMessagesReadResponse,
    MessageCreate,
    MessageResponse,
)
from app.infrastructure.database.models.message import Conversation, Message
from app.infrastructure.repositories.messaging_repository import (
    ConversationRepository,
    MessageRepository,
)
from app.infrastructure.repositories.user_repository import UserRepository
from app.shared.utils.uuid import generate_uuid
from datetime import UTC, datetime
from app.domain.notification.service import NotificationService
from app.domain.notification.notification_helper import NotificationHelper
import logging


class MessagingService:
    """Messaging service for 1:1 conversations."""

    def __init__(
        self,
        conversation_repo: ConversationRepository,
        message_repo: MessageRepository,
        user_repo: UserRepository,
        notification_service: NotificationService | None = None,
    ) -> None:
        self.conversation_repo = conversation_repo
        self.message_repo = message_repo
        self.user_repo = user_repo
        self.notification_service = notification_service

    async def send_message(self, sender_id: str, data: MessageCreate) -> MessageResponse:
        """Send a message to another user.

        Creates a new conversation if one doesn't exist between the two users.
        """
        receiver_id = data.receiver_id

        # Verify receiver exists
        receiver = await self.user_repo.get_by_id(receiver_id)
        if not receiver:
            raise NotFoundException(f"User {receiver_id} not found")

        # Get or create conversation
        conversation = await self.conversation_repo.get_by_participants(sender_id, receiver_id)

        if not conversation:
            # Create new conversation
            conversation = Conversation(
                id=generate_uuid(),
                user1_id=sender_id,
                user2_id=receiver_id,
                last_message_at=None,
                user1_unread_count=0,
                user2_unread_count=0,
            )
            conversation = await self.conversation_repo.create(conversation)

        # Create message
        message = Message(
            id=generate_uuid(),
            conversation_id=conversation.id,
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=data.content,
            is_read=False,
            read_at=None,
        )
        created_message = await self.message_repo.create(message)

        # Update conversation
        conversation.last_message_at = created_message.created_at

        # Increment unread count for receiver
        if conversation.user1_id == receiver_id:
            conversation.user1_unread_count += 1
        else:
            conversation.user2_unread_count += 1

        await self.conversation_repo.update(conversation)

        # Build response
        response = MessageResponse.model_validate(created_message)

        # Add usernames
        sender = await self.user_repo.get_by_id(sender_id)
        if sender:
            response.sender_username = sender.username
        if receiver:
            response.receiver_username = receiver.username

        # Send notification
        if self.notification_service and sender_id != receiver_id:
            try:
                sender_name = sender.username if sender else "Unknown"
                notification = NotificationHelper.create_new_message_notification(
                    user_id=receiver_id,
                    sender_name=sender_name,
                    message_preview=data.content,
                    conversation_id=conversation.id,
                )
                await self.notification_service.create_notification(notification)
            except Exception as e:
                logging.getLogger(__name__).warning(f"Failed to send message notification: {e}")

        return response

    async def get_user_conversations(self, user_id: str) -> list[ConversationListResponse]:
        """Get all conversations for a user."""
        conversations = await self.conversation_repo.get_user_conversations(user_id)

        # ✅ Early return if no conversations (defensive coding)
        if not conversations:
            return []

        # ✅ Batch load all other users (prevents N+1 query)
        # Use set() to deduplicate - same user may appear in multiple conversations
        other_user_ids = list(set(
            conv.user2_id if conv.user1_id == user_id else conv.user1_id
            for conv in conversations
        ))
        users = await self.user_repo.get_by_ids(other_user_ids)
        user_map = {user.id: user for user in users}

        # ✅ Batch load last messages (prevents N+1 queries)
        conv_ids = [conv.id for conv in conversations if conv.last_message_at]
        if conv_ids:  # Only query if there are conversations with messages
            last_messages = await self.message_repo.get_last_messages_by_conversations(conv_ids)
            message_map = {msg.conversation_id: msg for msg in last_messages}
        else:
            message_map = {}

        # Build responses using pre-loaded data
        result = []
        for conv in conversations:
            # Determine the other user
            other_user_id = conv.user2_id if conv.user1_id == user_id else conv.user1_id
            other_user = user_map.get(other_user_id)

            # Get unread count for this user
            unread_count = (
                conv.user1_unread_count if conv.user1_id == user_id else conv.user2_unread_count
            )

            # Get last message from map (O(1) lookup, no query!)
            last_message = None
            if conv.id in message_map:
                last_message = message_map[conv.id].content[:50]  # Truncate to 50 chars

            list_response = ConversationListResponse(
                id=conv.id,
                other_user_id=other_user_id,
                other_user_username=other_user.username if other_user else None,
                last_message=last_message,
                last_message_at=conv.last_message_at,
                unread_count=unread_count,
            )
            result.append(list_response)

        return result

    async def get_conversation_detail(
        self, conversation_id: str, user_id: str, limit: int = 50, offset: int = 0
    ) -> ConversationDetailResponse:
        """Get conversation details with messages.

        Args:
            conversation_id: Conversation identifier
            user_id: User requesting the conversation
            limit: Max messages to retrieve
            offset: Message offset for pagination
        """
        conversation = await self.conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise NotFoundException(f"Conversation {conversation_id} not found")

        # Verify user is a participant
        if user_id not in [conversation.user1_id, conversation.user2_id]:
            raise NotFoundException(f"Conversation {conversation_id} not found")

        # Get messages
        messages = await self.message_repo.get_by_conversation(
            conversation_id, limit=limit, offset=offset
        )

        # ✅ Early return if no messages (defensive coding)
        if not messages:
            # Still return conversation info even if no messages
            conv_response = ConversationResponse.model_validate(conversation)
            other_user_id = (
                conversation.user2_id if conversation.user1_id == user_id else conversation.user1_id
            )
            # Note: We still need to fetch the other user for conversation info
            other_user = await self.user_repo.get_by_id(other_user_id)
            conv_response.other_user_id = other_user_id
            conv_response.other_user_username = other_user.username if other_user else None
            conv_response.last_message = None

            return ConversationDetailResponse(
                conversation=conv_response,
                messages=[],
            )

        # ✅ Batch load all unique users (prevents N+1 queries)
        # Usually just 2 users (sender and receiver) for 1:1 conversations!
        # Use set() to deduplicate
        user_ids = list(set(
            user_id
            for msg in messages
            for user_id in [msg.sender_id, msg.receiver_id]
        ))
        users = await self.user_repo.get_by_ids(user_ids)
        user_map = {user.id: user for user in users}

        # Build message responses using pre-loaded data
        message_responses = []
        for msg in messages:
            response = MessageResponse.model_validate(msg)

            # Get users from map (O(1) lookup, no queries!)
            sender = user_map.get(msg.sender_id)
            receiver = user_map.get(msg.receiver_id)
            if sender:
                response.sender_username = sender.username
            if receiver:
                response.receiver_username = receiver.username

            message_responses.append(response)

        # Build conversation response
        conv_response = ConversationResponse.model_validate(conversation)

        # Add other user info from map (O(1) lookup!)
        other_user_id = (
            conversation.user2_id if conversation.user1_id == user_id else conversation.user1_id
        )
        other_user = user_map.get(other_user_id)
        conv_response.other_user_id = other_user_id
        conv_response.other_user_username = other_user.username if other_user else None

        # Add last message
        if messages:
            conv_response.last_message = messages[-1].content[:100]

        return ConversationDetailResponse(
            conversation=conv_response,
            messages=message_responses,
        )

    async def mark_messages_as_read(
        self, conversation_id: str, user_id: str, message_ids: list[str]
    ) -> MarkMessagesReadResponse:
        """Mark messages as read.

        Args:
            conversation_id: Conversation identifier
            user_id: User marking messages as read (receiver)
            message_ids: List of message IDs to mark as read
        """
        conversation = await self.conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise NotFoundException(f"Conversation {conversation_id} not found")

        # Verify user is a participant
        if user_id not in [conversation.user1_id, conversation.user2_id]:
            raise NotFoundException(f"Conversation {conversation_id} not found")

        # Mark messages as read
        read_at = datetime.now(UTC)
        marked_count = await self.message_repo.mark_as_read(message_ids, read_at)

        # Update conversation unread count
        if conversation.user1_id == user_id:
            conversation.user1_unread_count = max(0, conversation.user1_unread_count - marked_count)
            new_unread_count = conversation.user1_unread_count
        else:
            conversation.user2_unread_count = max(0, conversation.user2_unread_count - marked_count)
            new_unread_count = conversation.user2_unread_count

        await self.conversation_repo.update(conversation)

        return MarkMessagesReadResponse(
            marked_count=marked_count,
            conversation_id=conversation_id,
            new_unread_count=new_unread_count,
        )

    async def get_unread_message_count(self, user_id: str) -> int:
        """Get total unread message count for a user across all conversations."""
        conversations = await self.conversation_repo.get_user_conversations(user_id)

        total_unread = 0
        for conv in conversations:
            if conv.user1_id == user_id:
                total_unread += conv.user1_unread_count
            else:
                total_unread += conv.user2_unread_count

        return total_unread
