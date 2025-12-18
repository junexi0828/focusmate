"""Invitation service for managing room invitation codes."""

import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from app.core.config import settings
from app.core.exceptions import ConflictException, NotFoundException
from app.domain.chat.schemas import (
    ChatRoomResponse,
    FriendRoomCreate,
    InvitationCodeCreate,
    InvitationCodeInfo,
    InvitationJoinRequest,
)
from app.infrastructure.repositories.chat_repository import ChatRepository
from app.infrastructure.repositories.friend_repository import FriendRepository


class InvitationService:
    """Service for room invitation codes."""

    def __init__(
        self,
        chat_repo: ChatRepository,
        friend_repo: Optional[FriendRepository] = None,
    ):
        self.chat_repo = chat_repo
        self.friend_repo = friend_repo

    def _generate_code(self, length: int = 8) -> str:
        """Generate random invitation code."""
        alphabet = string.ascii_uppercase + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))

    async def generate_invitation_code(
        self, room_id: UUID, data: InvitationCodeCreate
    ) -> InvitationCodeInfo:
        """Generate invitation code for a room."""
        # Get room
        room = await self.chat_repo.get_room_by_id(room_id)
        if not room:
            raise NotFoundException("Room not found")

        # Generate unique code
        code = self._generate_code(settings.INVITATION_CODE_LENGTH)

        # Check if code already exists (very unlikely, but let's be safe)
        max_attempts = 10
        for _ in range(max_attempts):
            existing = await self.chat_repo.get_room_by_invitation_code(code)
            if not existing:
                break
            code = self._generate_code(settings.INVITATION_CODE_LENGTH)
        else:
            raise ConflictException("Failed to generate unique invitation code")

        # Calculate expiration
        expires_at = None
        if data.expires_hours:
            expires_at = datetime.now(timezone.utc) + timedelta(hours=data.expires_hours)

        # Update room with invitation code
        await self.chat_repo.update_room_invitation(
            room_id, code, expires_at, data.max_uses
        )

        return InvitationCodeInfo(
            code=code,
            room_id=room_id,
            expires_at=expires_at,
            max_uses=data.max_uses,
            current_uses=0,
            is_valid=True,
        )

    async def validate_invitation_code(self, code: str) -> InvitationCodeInfo:
        """Validate invitation code and return info."""
        room = await self.chat_repo.get_room_by_invitation_code(code)
        if not room:
            raise NotFoundException("Invalid invitation code")

        # Check expiration
        is_valid = True
        if room.invitation_expires_at:
            if datetime.now(timezone.utc) > room.invitation_expires_at:
                is_valid = False

        # Check max uses
        if room.invitation_max_uses:
            if room.invitation_use_count >= room.invitation_max_uses:
                is_valid = False

        return InvitationCodeInfo(
            code=code,
            room_id=room.room_id,
            expires_at=room.invitation_expires_at,
            max_uses=room.invitation_max_uses,
            current_uses=room.invitation_use_count,
            is_valid=is_valid,
        )

    async def join_by_invitation_code(
        self, user_id: str, data: InvitationJoinRequest
    ) -> ChatRoomResponse:
        """Join room using invitation code."""
        # Validate code
        code_info = await self.validate_invitation_code(data.invitation_code)
        if not code_info.is_valid:
            raise ConflictException("Invitation code is expired or has reached max uses")

        room_id = code_info.room_id

        # Check if user is already a member
        member = await self.chat_repo.get_member(room_id, user_id)
        if member and member.is_active:
            # Already a member, just return room
            room = await self.chat_repo.get_room_by_id(room_id)
            return ChatRoomResponse.model_validate(room)

        # Add user as member
        await self.chat_repo.add_member(
            {
                "room_id": room_id,
                "user_id": user_id,
                "role": "member",
                "is_active": True,
            }
        )

        # Increment usage count
        await self.chat_repo.increment_invitation_usage(room_id)

        # Return room info
        room = await self.chat_repo.get_room_by_id(room_id)
        return ChatRoomResponse.model_validate(room)

    async def create_room_with_friends(
        self, user_id: str, data: FriendRoomCreate
    ) -> ChatRoomResponse:
        """Create a room with friends."""
        if not self.friend_repo:
            raise ConflictException("Friend repository not available")

        # Verify all friend IDs are actual friends
        for friend_id in data.friend_ids:
            friendship = await self.friend_repo.get_friendship(user_id, friend_id)
            if not friendship:
                raise NotFoundException(f"User {friend_id} is not your friend")

        # Create team room
        room_data = {
            "room_type": "team",
            "room_name": data.room_name or f"{user_id[:8]}'s Room",
            "description": data.description,
            "room_metadata": {
                "type": "friends",
                "created_by": user_id,
                "friend_ids": data.friend_ids,
            },
            "display_mode": "open",
            "is_active": True,
        }

        room = await self.chat_repo.create_room(room_data)

        # Add creator as owner
        await self.chat_repo.add_member(
            {
                "room_id": room.room_id,
                "user_id": user_id,
                "role": "owner",
                "is_active": True,
            }
        )

        # Add all friends as members
        for friend_id in data.friend_ids:
            await self.chat_repo.add_member(
                {
                    "room_id": room.room_id,
                    "user_id": friend_id,
                    "role": "member",
                    "is_active": True,
                }
            )

        # Generate invitation code if requested
        if data.generate_invitation:
            code_data = InvitationCodeCreate(
                expires_hours=data.invitation_expires_hours
            )
            await self.generate_invitation_code(room.room_id, code_data)

        # Refresh to get invitation code if generated
        room = await self.chat_repo.get_room_by_id(room.room_id)
        return ChatRoomResponse.model_validate(room)
