"""Presence service for managing user online/offline status."""

from datetime import datetime
from typing import Optional

from app.domain.friend.schemas import FriendPresence
from app.infrastructure.repositories.presence_repository import PresenceRepository
from app.infrastructure.repositories.friend_repository import FriendRepository


class PresenceService:
    """Service for managing user presence (online/offline status)."""

    def __init__(
        self,
        presence_repo: PresenceRepository,
        friend_repo: FriendRepository,
    ):
        self.presence_repo = presence_repo
        self.friend_repo = friend_repo

    async def set_online(self, user_id: str) -> FriendPresence:
        """Set user online and return presence."""
        presence = await self.presence_repo.set_online(user_id)
        return FriendPresence.model_validate(presence)

    async def set_offline(self, user_id: str) -> FriendPresence:
        """Set user offline and return presence."""
        presence = await self.presence_repo.set_offline(user_id)
        return FriendPresence.model_validate(presence)

    async def increment_connection(self, user_id: str) -> int:
        """Increment connection count and return new count."""
        return await self.presence_repo.increment_connection_count(user_id)

    async def decrement_connection(self, user_id: str) -> int:
        """Decrement connection count and return new count."""
        return await self.presence_repo.decrement_connection_count(user_id)

    async def get_user_presence(self, user_id: str) -> Optional[FriendPresence]:
        """Get presence for a specific user."""
        presence = await self.presence_repo.get_presence(user_id)
        if presence:
            return FriendPresence.model_validate(presence)
        return None

    async def get_friends_presence(self, user_id: str) -> list[FriendPresence]:
        """Get presence information for all friends of a user."""
        # Get user's friends
        friends = await self.friend_repo.get_user_friends(user_id)
        friend_ids = [f.friend_id for f in friends]

        if not friend_ids:
            return []

        # Get presence for all friends
        presences = await self.presence_repo.get_multiple_presence(friend_ids)

        # Convert to response models
        return [FriendPresence.model_validate(p) for p in presences]

    async def get_online_friends(self, user_id: str) -> list[str]:
        """Get list of friend IDs who are currently online."""
        presences = await self.get_friends_presence(user_id)
        return [p.user_id for p in presences if p.is_online]

    async def update_status_message(
        self, user_id: str, status_message: Optional[str]
    ) -> FriendPresence:
        """Update user's status message."""
        presence = await self.presence_repo.get_presence(user_id)

        if presence:
            presence = await self.presence_repo.upsert_presence(
                user_id, presence.is_online, status_message
            )
        else:
            # Create new presence with status message
            presence = await self.presence_repo.upsert_presence(
                user_id, False, status_message
            )

        return FriendPresence.model_validate(presence)

    async def cleanup_stale_connections(self, threshold_minutes: int = 5) -> int:
        """Clean up stale connections."""
        return await self.presence_repo.cleanup_stale_connections(threshold_minutes)

    async def broadcast_presence_change(
        self, user_id: str, is_online: bool
    ) -> list[str]:
        """
        Get list of friend IDs to broadcast presence change to.
        This should be called after presence change to notify friends.
        Returns list of user_ids who should receive the update.
        """
        # Get user's friends
        friends = await self.friend_repo.get_user_friends(user_id)
        friend_ids = [f.friend_id for f in friends]

        # Return friend IDs for WebSocket broadcast
        return friend_ids
