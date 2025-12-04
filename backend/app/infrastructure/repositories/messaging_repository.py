"""Messaging repository - conversations and messages."""

from datetime import datetime

from sqlalchemy import and_, desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.message import Conversation, Message


class ConversationRepository:
    """Repository for conversation data access."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, conversation: Conversation) -> Conversation:
        """Create conversation."""
        self.db.add(conversation)
        await self.db.flush()
        await self.db.refresh(conversation)
        return conversation

    async def get_by_id(self, conversation_id: str) -> Conversation | None:
        """Get conversation by ID."""
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def get_by_participants(self, user1_id: str, user2_id: str) -> Conversation | None:
        """Get conversation between two users (order independent)."""
        result = await self.db.execute(
            select(Conversation).where(
                or_(
                    and_(Conversation.user1_id == user1_id, Conversation.user2_id == user2_id),
                    and_(Conversation.user1_id == user2_id, Conversation.user2_id == user1_id),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_user_conversations(self, user_id: str) -> list[Conversation]:
        """Get all conversations for a user."""
        result = await self.db.execute(
            select(Conversation)
            .where(
                or_(
                    Conversation.user1_id == user_id,
                    Conversation.user2_id == user_id,
                )
            )
            .order_by(desc(Conversation.last_message_at))
        )
        return list(result.scalars().all())

    async def update(self, conversation: Conversation) -> Conversation:
        """Update conversation."""
        await self.db.flush()
        await self.db.refresh(conversation)
        return conversation


class MessageRepository:
    """Repository for message data access."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, message: Message) -> Message:
        """Create message."""
        self.db.add(message)
        await self.db.flush()
        await self.db.refresh(message)
        return message

    async def get_by_id(self, message_id: str) -> Message | None:
        """Get message by ID."""
        result = await self.db.execute(
            select(Message).where(Message.id == message_id)
        )
        return result.scalar_one_or_none()

    async def get_by_conversation(
        self, conversation_id: str, limit: int = 50, offset: int = 0
    ) -> list[Message]:
        """Get messages in a conversation with pagination."""
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(desc(Message.created_at))
            .limit(limit)
            .offset(offset)
        )
        messages = list(result.scalars().all())
        return list(reversed(messages))  # Reverse to show oldest first

    async def get_unread_by_receiver(self, receiver_id: str, conversation_id: str) -> list[Message]:
        """Get unread messages for a receiver in a conversation."""
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .where(Message.receiver_id == receiver_id)
            .where(Message.is_read == False)
            .order_by(Message.created_at.asc())
        )
        return list(result.scalars().all())

    async def mark_as_read(self, message_ids: list[str], read_at: datetime) -> int:
        """Mark multiple messages as read.

        Returns:
            Number of messages marked as read
        """
        count = 0
        for message_id in message_ids:
            message = await self.get_by_id(message_id)
            if message and not message.is_read:
                message.is_read = True
                message.read_at = read_at
                count += 1

        await self.db.flush()
        return count

    async def update(self, message: Message) -> Message:
        """Update message."""
        await self.db.flush()
        await self.db.refresh(message)
        return message
