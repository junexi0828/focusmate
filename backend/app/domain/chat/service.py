"""Service layer for unified chat system."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from app.domain.chat.schemas import (
    ChatRoomResponse,
    DirectChatCreate,
    MatchingChatInfo,
    MessageCreate,
    MessageListResponse,
    MessageResponse,
    TeamChatCreate,
)
from app.infrastructure.repositories.chat_repository import ChatRepository


class ChatService:
    """Service for unified chat business logic."""

    def __init__(self, repository: ChatRepository):
        self.repository = repository

    # Room creation
    async def create_direct_chat(
        self, user_id: str, data: DirectChatCreate
    ) -> ChatRoomResponse:
        """Create or get existing direct chat."""
        # Check if direct chat already exists
        existing_room = await self.repository.get_direct_room(
            user_id, data.recipient_id
        )
        if existing_room:
            return ChatRoomResponse.model_validate(existing_room)

        # Create new direct chat
        room_data = {
            "room_type": "direct",
            "room_metadata": {
                "type": "direct",
                "user_ids": sorted([user_id, data.recipient_id]),
            },
            "is_active": True,
        }

        room = await self.repository.create_room(room_data)

        # Add both users as members
        for uid in [user_id, data.recipient_id]:
            await self.repository.add_member(
                {
                    "room_id": room.room_id,
                    "user_id": uid,
                    "role": "member",
                    "is_active": True,
                }
            )

        return ChatRoomResponse.model_validate(room)

    async def create_team_chat(
        self, user_id: str, data: TeamChatCreate
    ) -> ChatRoomResponse:
        """Create team chat."""
        room_data = {
            "room_type": "team",
            "room_name": data.room_name,
            "description": data.description,
            "room_metadata": {
                "type": "team",
                "team_id": str(data.team_id),
            },
            "display_mode": "open",
            "is_active": True,
        }

        room = await self.repository.create_room(room_data)

        # Add creator as owner
        await self.repository.add_member(
            {
                "room_id": room.room_id,
                "user_id": user_id,
                "role": "owner",
                "is_active": True,
            }
        )

        return ChatRoomResponse.model_validate(room)

    async def create_matching_chat(self, info: MatchingChatInfo) -> ChatRoomResponse:
        """Create matching chat (called from matching proposal service)."""
        room_data = {
            "room_type": "matching",
            "room_name": "매칭 그룹 채팅",
            "room_metadata": {
                "type": "matching",
                "proposal_id": str(info.proposal_id),
                "group_a_info": info.group_a_info,
                "group_b_info": info.group_b_info,
            },
            "display_mode": info.display_mode,
            "is_active": True,
        }

        room = await self.repository.create_room(room_data)

        # Add members from both groups
        for group_label, group_info in [
            ("A", info.group_a_info),
            ("B", info.group_b_info),
        ]:
            for idx, member_id in enumerate(group_info.get("member_ids", []), 1):
                await self.repository.add_member(
                    {
                        "room_id": room.room_id,
                        "user_id": member_id,
                        "role": "member",
                        "group_label": group_label,
                        "member_index": idx,
                        "anonymous_name": (
                            f"{group_label}{idx}"
                            if info.display_mode == "blind"
                            else None
                        ),
                        "is_active": True,
                    }
                )

        return ChatRoomResponse.model_validate(room)

    # Room operations
    async def get_user_rooms(
        self, user_id: str, room_type: Optional[str] = None
    ) -> list[ChatRoomResponse]:
        """Get all chat rooms for a user."""
        rooms = await self.repository.get_user_rooms(user_id, room_type)
        room_responses = []

        for room in rooms:
            # Get last message for preview
            last_message = await self.repository.get_last_message(room.room_id)

            # Get unread count for this room
            unread_count = await self.repository.get_room_unread_count(room.room_id, user_id)

            room_dict = ChatRoomResponse.model_validate(room).model_dump()
            room_dict["unread_count"] = unread_count

            if last_message:
                room_dict["last_message_content"] = last_message.content
                room_dict["last_message_sender_id"] = str(last_message.sender_id)

            room_responses.append(ChatRoomResponse(**room_dict))

        return room_responses

    async def get_unread_count(self, user_id: str) -> int:
        """Get total unread message count for a user across all rooms."""
        return await self.repository.get_unread_count(user_id)

    async def get_room(self, room_id: UUID, user_id: str) -> ChatRoomResponse:
        """Get room details."""
        room = await self.repository.get_room_by_id(room_id)
        if not room:
            raise ValueError("Room not found")

        # Verify user is member
        member = await self.repository.get_member(room_id, user_id)
        if not member:
            raise ValueError("Not a member of this room")

        unread_count = await self.repository.get_room_unread_count(room_id, user_id)
        room_response = ChatRoomResponse.model_validate(room)
        room_response.unread_count = unread_count

        return room_response

    # Message operations
    async def send_message(
        self, room_id: UUID, user_id: str, data: MessageCreate
    ) -> MessageResponse:
        """Send a message."""
        # Verify user is member
        member = await self.repository.get_member(room_id, user_id)
        if not member or not member.is_active:
            raise ValueError("Not an active member of this room")

        message_data = {
            "room_id": room_id,
            "sender_id": user_id,
            "message_type": data.message_type,
            "content": data.content,
            "attachments": data.attachments,
            "parent_message_id": data.parent_message_id,
        }

        message = await self.repository.create_message(message_data)
        return MessageResponse.model_validate(message)

    async def get_messages(
        self,
        room_id: UUID,
        user_id: str,
        limit: int = 50,
        before_message_id: Optional[UUID] = None,
    ) -> MessageListResponse:
        """Get messages from room."""
        # Verify user is member
        member = await self.repository.get_member(room_id, user_id)
        if not member:
            raise ValueError("Not a member of this room")

        messages = await self.repository.get_messages(room_id, limit, before_message_id)

        return MessageListResponse(
            messages=[MessageResponse.model_validate(m) for m in messages],
            total=len(messages),
            has_more=len(messages) == limit,
        )

    async def update_message(
        self, message_id: UUID, user_id: str, content: str
    ) -> MessageResponse:
        """Update message."""
        message = await self.repository.get_message_by_id(message_id)
        if not message:
            raise ValueError("Message not found")

        if message.sender_id != user_id:
            raise ValueError("Can only edit own messages")

        updated_message = await self.repository.update_message(message_id, content)
        return MessageResponse.model_validate(updated_message)

    async def delete_message(self, message_id: UUID, user_id: str) -> MessageResponse:
        """Delete message."""
        message = await self.repository.get_message_by_id(message_id)
        if not message:
            raise ValueError("Message not found")

        if message.sender_id != user_id:
            raise ValueError("Can only delete own messages")

        deleted_message = await self.repository.delete_message(message_id)
        return MessageResponse.model_validate(deleted_message)

    async def mark_as_read(self, room_id: UUID, user_id: str) -> None:
        """Mark all messages as read."""
        await self.repository.update_member_read_status(
            room_id, user_id, datetime.now(timezone.utc)
        )
