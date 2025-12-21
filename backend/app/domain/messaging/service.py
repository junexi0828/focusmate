"""Messaging domain service - 1:1 conversations and messages."""

from datetime import UTC, datetime

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


class MessagingService:
    """Messaging service for 1:1 conversations."""

    def __init__(
        self,
        conversation_repo: ConversationRepository,
        message_repo: MessageRepository,
        user_repo: UserRepository,
    ) -> None:
        self.conversation_repo = conversation_repo
        self.message_repo = message_repo
        self.user_repo = user_repo

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

        return response

    async def get_user_conversations(self, user_id: str) -> list[ConversationListResponse]:
        """Get all conversations for a user."""
        conversations = await self.conversation_repo.get_user_conversations(user_id)

        result = []
        for conv in conversations:
            # Determine the other user
            other_user_id = conv.user2_id if conv.user1_id == user_id else conv.user1_id
            other_user = await self.user_repo.get_by_id(other_user_id)

            # Get unread count for this user
            unread_count = (
                conv.user1_unread_count if conv.user1_id == user_id else conv.user2_unread_count
            )

            # Get last message
            last_message = None
            if conv.last_message_at:
                messages = await self.message_repo.get_by_conversation(conv.id, limit=1)
                if messages:
                    last_message = messages[-1].content[:50]  # Truncate to 50 chars

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

        # Build message responses
        message_responses = []
        for msg in messages:
            response = MessageResponse.model_validate(msg)

            # Add usernames
            sender = await self.user_repo.get_by_id(msg.sender_id)
            receiver = await self.user_repo.get_by_id(msg.receiver_id)
            if sender:
                response.sender_username = sender.username
            if receiver:
                response.receiver_username = receiver.username

            message_responses.append(response)

        # Build conversation response
        conv_response = ConversationResponse.model_validate(conversation)

        # Add other user info
        other_user_id = (
            conversation.user2_id if conversation.user1_id == user_id else conversation.user1_id
        )
        other_user = await self.user_repo.get_by_id(other_user_id)
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
