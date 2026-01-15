"""Repository for unified chat operations."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, case, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.chat import ChatMember, ChatMessage, ChatRoom
from datetime import UTC, datetime


class ChatRepository:
    """Repository for unified chat database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # Room operations
    async def create_room(self, room_data: dict) -> ChatRoom:
        """Create a new chat room."""
        room = ChatRoom(**room_data)
        self.session.add(room)
        await self.session.commit()
        await self.session.refresh(room)
        return room

    async def get_room_by_id(self, room_id: UUID) -> ChatRoom | None:
        """Get room by ID."""
        result = await self.session.execute(
            select(ChatRoom).where(ChatRoom.room_id == room_id)
        )
        return result.scalar_one_or_none()

    async def get_user_rooms(
        self, user_id: str, room_type: str | None = None
    ) -> list[ChatRoom]:
        """Get all rooms for a user."""
        query = (
            select(ChatRoom)
            .join(ChatMember)
            .where(
                and_(
                    ChatMember.user_id == user_id,
                    ChatMember.is_active == True,
                    ChatRoom.is_active == True,
                )
            )
            .order_by(ChatRoom.last_message_at.desc().nullslast())
        )

        if room_type:
            query = query.where(ChatRoom.room_type == room_type)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_room(self, room_id: UUID, update_data: dict) -> ChatRoom | None:
        """Update room."""
        room = await self.get_room_by_id(room_id)
        if not room:
            return None

        for key, value in update_data.items():
            setattr(room, key, value)

        await self.session.commit()
        await self.session.refresh(room)
        return room

    # Member operations
    async def add_member(self, member_data: dict) -> ChatMember:
        """Add member to room."""
        member = ChatMember(**member_data)
        self.session.add(member)
        await self.session.commit()
        await self.session.refresh(member)
        return member

    async def get_room_members(self, room_id: UUID) -> list[ChatMember]:
        """Get all members of a room."""
        result = await self.session.execute(
            select(ChatMember)
            .where(ChatMember.room_id == room_id)
            .where(ChatMember.is_active == True)
        )
        return list(result.scalars().all())

    async def get_members_for_rooms(self, room_ids: list[UUID]) -> list[ChatMember]:
        """Get active members for multiple rooms in one query."""
        if not room_ids:
            return []
        result = await self.session.execute(
            select(ChatMember)
            .where(ChatMember.room_id.in_(room_ids))
            .where(ChatMember.is_active == True)
        )
        return list(result.scalars().all())

    async def get_member(self, room_id: UUID, user_id: str) -> ChatMember | None:
        """Get specific member."""
        result = await self.session.execute(
            select(ChatMember).where(
                and_(
                    ChatMember.room_id == room_id,
                    ChatMember.user_id == user_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_unread_count(self, user_id: str) -> int:
        """Get total unread message count for a user across all rooms."""
        try:
            result = await self.session.execute(
                select(func.coalesce(func.sum(ChatMember.unread_count), 0)).where(
                    and_(
                        ChatMember.user_id == user_id,
                        ChatMember.is_active == True,
                    )
                )
            )
            return int(result.scalar() or 0)
        except Exception:
            # If chat tables don't exist or there's any error, return 0
            return 0

    async def update_member_read_status(
        self, room_id: UUID, user_id: str, last_read_at: datetime
    ) -> ChatMember | None:
        """Update member's read status."""
        member = await self.get_member(room_id, user_id)
        if not member:
            return None

        member.last_read_at = last_read_at
        member.unread_count = 0

        await self.session.commit()
        await self.session.refresh(member)
        return member

    # Message operations
    async def create_message(self, message_data: dict) -> ChatMessage:
        """Create a new message."""
        message = ChatMessage(**message_data)
        self.session.add(message)
        await self.session.flush()  # Flush to get created_at

        # Update room's last_message_at in same transaction
        room = await self.get_room_by_id(message_data["room_id"])
        if room:
            room.last_message_at = message.created_at
            room.updated_at = datetime.now(UTC)

        # Increment unread_count for all members except sender
        await self.session.execute(
            update(ChatMember)
            .where(
                and_(
                    ChatMember.room_id == message_data["room_id"],
                    ChatMember.user_id != message_data["sender_id"],
                    ChatMember.is_active == True,
                )
            )
            .values(unread_count=ChatMember.unread_count + 1)
        )

        await self.session.commit()
        await self.session.refresh(message)

        return message

    async def get_messages(
        self,
        room_id: UUID,
        limit: int = 50,
        before_message_id: UUID | None = None,
    ) -> list[ChatMessage]:
        """Get messages from a room."""
        query = (
            select(ChatMessage)
            .where(ChatMessage.room_id == room_id)
            .where(ChatMessage.is_deleted == False)
            .order_by(ChatMessage.created_at.desc())
        )

        if before_message_id:
            before_message = await self.get_message_by_id(before_message_id)
            if before_message:
                query = query.where(ChatMessage.created_at < before_message.created_at)

        result = await self.session.execute(query.limit(limit))
        messages = list(result.scalars().all())
        return list(reversed(messages))  # Return in chronological order

    async def get_message_by_id(self, message_id: UUID) -> ChatMessage | None:
        """Get message by ID."""
        result = await self.session.execute(
            select(ChatMessage).where(ChatMessage.message_id == message_id)
        )
        return result.scalar_one_or_none()

    async def get_last_message(self, room_id: UUID) -> ChatMessage | None:
        """Get the last message in a room."""
        result = await self.session.execute(
            select(ChatMessage)
            .where(
                and_(
                    ChatMessage.room_id == room_id,
                    ChatMessage.is_deleted == False,
                )
            )
            .order_by(ChatMessage.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def update_message(
        self, message_id: UUID, content: str
    ) -> ChatMessage | None:
        """Update message content."""
        message = await self.get_message_by_id(message_id)
        if not message:
            return None

        message.content = content
        message.is_edited = True
        message.updated_at = datetime.now(UTC)

        await self.session.commit()
        await self.session.refresh(message)
        return message

    async def delete_message(self, message_id: UUID) -> ChatMessage | None:
        """Soft delete message."""
        message = await self.get_message_by_id(message_id)
        if not message:
            return None

        message.is_deleted = True
        message.deleted_at = datetime.now(UTC)
        await self.session.flush()

        # Decrement unread_count for members who hadn't read this message
        await self.session.execute(
            update(ChatMember)
            .where(
                and_(
                    ChatMember.room_id == message.room_id,
                    ChatMember.user_id != message.sender_id,
                    ChatMember.is_active == True,
                    or_(
                        ChatMember.last_read_at.is_(None),
                        ChatMember.last_read_at < message.created_at,
                    ),
                )
            )
            .values(
                unread_count=case(
                    (ChatMember.unread_count > 0, ChatMember.unread_count - 1),
                    else_=0,
                )
            )
        )

        # If the deleted message was the latest, roll back last_message_at
        room = await self.get_room_by_id(message.room_id)
        if room and room.last_message_at == message.created_at:
            latest_result = await self.session.execute(
                select(ChatMessage.created_at)
                .where(
                    and_(
                        ChatMessage.room_id == message.room_id,
                        ChatMessage.is_deleted == False,
                    )
                )
                .order_by(ChatMessage.created_at.desc())
                .limit(1)
            )
            room.last_message_at = latest_result.scalar_one_or_none()

        await self.session.commit()
        await self.session.refresh(message)
        return message

    async def get_room_unread_count(self, room_id: UUID, user_id: str) -> int:
        """Get unread message count for user in room."""
        member = await self.get_member(room_id, user_id)
        if not member:
            return 0
        return member.unread_count

    async def search_messages(
        self, room_id: UUID, query: str, limit: int = 50
    ) -> list[ChatMessage]:
        """Search messages in a room."""
        result = await self.session.execute(
            select(ChatMessage)
            .where(
                and_(
                    ChatMessage.room_id == room_id,
                    ChatMessage.is_deleted == False,
                    ChatMessage.content.ilike(f"%{query}%"),
                )
            )
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )
        messages = list(result.scalars().all())
        return list(reversed(messages))  # Return in chronological order

    # Invitation code operations
    async def update_room_invitation(
        self,
        room_id: UUID,
        code: str,
        expires_at: datetime | None,
        max_uses: int | None,
    ) -> ChatRoom:
        """Update room invitation code."""
        room = await self.get_room_by_id(room_id)
        if not room:
            raise ValueError("Room not found")

        room.invitation_code = code
        room.invitation_expires_at = expires_at
        room.invitation_max_uses = max_uses
        room.invitation_use_count = 0

        await self.session.commit()
        await self.session.refresh(room)
        return room

    async def get_room_by_invitation_code(self, code: str) -> ChatRoom | None:
        """Get room by invitation code."""
        result = await self.session.execute(
            select(ChatRoom).where(ChatRoom.invitation_code == code)
        )
        return result.scalar_one_or_none()

    async def increment_invitation_usage(self, room_id: UUID) -> int:
        """Increment invitation code usage count."""
        room = await self.get_room_by_id(room_id)
        if not room:
            raise ValueError("Room not found")

        room.invitation_use_count += 1
        await self.session.commit()
        await self.session.refresh(room)
        return room.invitation_use_count

    async def get_direct_room(self, user_id: str, recipient_id: str) -> ChatRoom | None:
        """Get existing direct chat room between two users."""
        result = await self.session.execute(
            select(ChatRoom)
            .join(ChatMember, ChatRoom.room_id == ChatMember.room_id)
            .where(
                and_(
                    ChatRoom.room_type == "direct",
                    ChatMember.user_id.in_([user_id, recipient_id]),
                    ChatMember.is_active == True,
                )
            )
            .group_by(ChatRoom.room_id)
            .having(func.count(func.distinct(ChatMember.user_id)) == 2)
            .order_by(ChatRoom.last_message_at.desc().nullslast())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_user_rooms_with_context(
        self, user_id: str, room_type: str | None = None
    ) -> list[tuple[ChatRoom, int, str | None, str | None]]:
        """Get rooms with unread counts and last message data in one query."""
        last_message_subq = (
            select(
                ChatMessage.room_id.label("room_id"),
                ChatMessage.content.label("content"),
                ChatMessage.sender_id.label("sender_id"),
                func.row_number()
                .over(
                    partition_by=ChatMessage.room_id,
                    order_by=ChatMessage.created_at.desc(),
                )
                .label("rn"),
            )
            .where(ChatMessage.is_deleted == False)
            .subquery()
        )

        query = (
            select(
                ChatRoom,
                ChatMember.unread_count,
                last_message_subq.c.content,
                last_message_subq.c.sender_id,
            )
            .join(ChatMember, ChatMember.room_id == ChatRoom.room_id)
            .outerjoin(
                last_message_subq,
                and_(
                    ChatRoom.room_id == last_message_subq.c.room_id,
                    last_message_subq.c.rn == 1,
                ),
            )
            .where(
                and_(
                    ChatMember.user_id == user_id,
                    ChatMember.is_active == True,
                    ChatRoom.is_active == True,
                )
            )
            .order_by(ChatRoom.last_message_at.desc().nullslast())
        )

        if room_type:
            query = query.where(ChatRoom.room_type == room_type)

        result = await self.session.execute(query)
        return list(result.all())
