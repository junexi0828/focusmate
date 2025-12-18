"""Repository for unified chat operations."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.chat import ChatMember, ChatMessage, ChatRoom


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

    async def get_room_by_id(self, room_id: UUID) -> Optional[ChatRoom]:
        """Get room by ID."""
        result = await self.session.execute(
            select(ChatRoom).where(ChatRoom.room_id == room_id)
        )
        return result.scalar_one_or_none()

    async def get_user_rooms(
        self, user_id: str, room_type: Optional[str] = None
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

    async def get_direct_room(self, user1_id: str, user2_id: str) -> Optional[ChatRoom]:
        """Get existing direct chat room between two users."""
        # Get all direct rooms and filter in Python (simpler than JSON query)
        result = await self.session.execute(
            select(ChatRoom).where(ChatRoom.room_type == "direct")
        )
        rooms = result.scalars().all()

        # Find room with both users
        for room in rooms:
            if room.room_metadata and "user_ids" in room.room_metadata:
                user_ids = room.room_metadata.get("user_ids", [])
                if user1_id in user_ids and user2_id in user_ids:
                    return room

        return None

    async def update_room(self, room_id: UUID, update_data: dict) -> Optional[ChatRoom]:
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

    async def get_member(self, room_id: UUID, user_id: str) -> Optional[ChatMember]:
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
            # Get all rooms where user is a member
            rooms_result = await self.session.execute(
                select(ChatMember.room_id, ChatMember.last_read_at)
                .where(
                    and_(
                        ChatMember.user_id == user_id,
                        ChatMember.is_active == True,
                    )
                )
            )

            total_unread = 0
            for row in rooms_result:
                room_id = row.room_id
                last_read_at = row.last_read_at
                # Count messages in this room after last_read_at
                query = select(func.count()).select_from(ChatMessage).where(
                    and_(
                        ChatMessage.room_id == room_id,
                        ChatMessage.sender_id != user_id,  # Don't count own messages
                        ChatMessage.is_deleted == False,
                    )
                )

                if last_read_at:
                    query = query.where(ChatMessage.created_at > last_read_at)

                result = await self.session.execute(query)
                count = result.scalar() or 0
                total_unread += count

            return total_unread
        except Exception:
            # If chat tables don't exist or there's any error, return 0
            return 0

    async def update_member_read_status(
        self, room_id: UUID, user_id: str, last_read_at: datetime
    ) -> Optional[ChatMember]:
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
            room.updated_at = datetime.now(timezone.utc)

        # Increment unread_count for all members except sender
        members_result = await self.session.execute(
            select(ChatMember).where(
                and_(
                    ChatMember.room_id == message_data["room_id"],
                    ChatMember.user_id != message_data["sender_id"],
                    ChatMember.is_active == True,
                )
            )
        )
        for member in members_result.scalars().all():
            member.unread_count += 1

        await self.session.commit()
        await self.session.refresh(message)

        return message

    async def get_messages(
        self,
        room_id: UUID,
        limit: int = 50,
        before_message_id: Optional[UUID] = None,
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

    async def get_message_by_id(self, message_id: UUID) -> Optional[ChatMessage]:
        """Get message by ID."""
        result = await self.session.execute(
            select(ChatMessage).where(ChatMessage.message_id == message_id)
        )
        return result.scalar_one_or_none()

    async def get_last_message(self, room_id: UUID) -> Optional[ChatMessage]:
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
    ) -> Optional[ChatMessage]:
        """Update message content."""
        message = await self.get_message_by_id(message_id)
        if not message:
            return None

        message.content = content
        message.is_edited = True
        message.updated_at = datetime.now(timezone.utc)

        await self.session.commit()
        await self.session.refresh(message)
        return message

    async def delete_message(self, message_id: UUID) -> Optional[ChatMessage]:
        """Soft delete message."""
        message = await self.get_message_by_id(message_id)
        if not message:
            return None

        message.is_deleted = True
        message.deleted_at = datetime.now(timezone.utc)

        await self.session.commit()
        await self.session.refresh(message)
        return message

    async def get_room_unread_count(self, room_id: UUID, user_id: str) -> int:
        """Get unread message count for user in room."""
        member = await self.get_member(room_id, user_id)
        if not member:
            return 0

        if not member.last_read_at:
            # Count all messages
            result = await self.session.execute(
                select(func.count(ChatMessage.message_id)).where(
                    and_(
                        ChatMessage.room_id == room_id,
                        ChatMessage.sender_id != user_id,
                        ChatMessage.is_deleted == False,
                    )
                )
            )
        else:
            # Count messages after last read
            result = await self.session.execute(
                select(func.count(ChatMessage.message_id)).where(
                    and_(
                        ChatMessage.room_id == room_id,
                        ChatMessage.sender_id != user_id,
                        ChatMessage.created_at > member.last_read_at,
                        ChatMessage.is_deleted == False,
                    )
                )
            )

        unread_count = result.scalar() or 0

        # Update member's unread_count
        member.unread_count = unread_count
        await self.session.commit()

        return unread_count

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
        expires_at: Optional[datetime],
        max_uses: Optional[int],
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

    async def get_room_by_invitation_code(self, code: str) -> Optional[ChatRoom]:
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

    async def get_direct_room(self, user_id: str, recipient_id: str) -> Optional[ChatRoom]:
        """Get existing direct chat room between two users."""
        result = await self.session.execute(
            select(ChatRoom)
            .join(ChatMember, ChatRoom.room_id == ChatMember.room_id)
            .where(
                and_(
                    ChatRoom.room_type == "direct",
                    ChatMember.user_id == user_id,
                    ChatMember.is_active == True,
                )
            )
        )
        rooms = list(result.scalars().all())

        # Check if any room has the recipient as a member
        for room in rooms:
            members_result = await self.session.execute(
                select(ChatMember).where(
                    and_(
                        ChatMember.room_id == room.room_id,
                        ChatMember.user_id == recipient_id,
                        ChatMember.is_active == True,
                    )
                )
            )
            if members_result.scalar_one_or_none():
                return room

        return None
