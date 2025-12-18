"""Presence repository."""

from datetime import datetime, timezone
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.presence import UserPresence


class PresenceRepository:
    """Repository for user presence operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert_presence(
        self, user_id: str, is_online: bool, status_message: str | None = None
    ) -> UserPresence:
        """Create or update user presence."""
        # Try to get existing presence
        existing = await self.get_presence(user_id)

        if existing:
            # Update existing
            existing.is_online = is_online
            existing.last_seen_at = datetime.now(timezone.utc)
            if status_message is not None:
                existing.status_message = status_message
            await self.session.commit()
            await self.session.refresh(existing)
            return existing
        else:
            # Create new
            presence = UserPresence(
                id=user_id,
                is_online=is_online,
                last_seen_at=datetime.now(timezone.utc),
                connection_count=0,
                status_message=status_message,
            )
            self.session.add(presence)
            await self.session.commit()
            await self.session.refresh(presence)
            return presence

    async def get_presence(self, user_id: str) -> UserPresence | None:
        """Get user presence by user ID."""
        result = await self.session.execute(
            select(UserPresence).where(UserPresence.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_multiple_presence(self, user_ids: list[str]) -> list[UserPresence]:
        """Get presence for multiple users."""
        result = await self.session.execute(
            select(UserPresence).where(UserPresence.id.in_(user_ids))
        )
        return list(result.scalars().all())

    async def increment_connection_count(self, user_id: str) -> int:
        """Increment connection count and return new count."""
        presence = await self.get_presence(user_id)

        if presence:
            presence.connection_count += 1
            presence.is_online = True
            presence.last_seen_at = datetime.now(timezone.utc)
            await self.session.commit()
            await self.session.refresh(presence)
            return presence.connection_count
        else:
            # Create new presence with count 1
            presence = await self.upsert_presence(user_id, True)
            presence.connection_count = 1
            await self.session.commit()
            await self.session.refresh(presence)
            return 1

    async def decrement_connection_count(self, user_id: str) -> int:
        """Decrement connection count and return new count."""
        presence = await self.get_presence(user_id)

        if presence and presence.connection_count > 0:
            presence.connection_count -= 1
            presence.last_seen_at = datetime.now(timezone.utc)

            # Set offline if no more connections
            if presence.connection_count == 0:
                presence.is_online = False

            await self.session.commit()
            await self.session.refresh(presence)
            return presence.connection_count

        return 0

    async def set_online(self, user_id: str) -> UserPresence:
        """Set user online status."""
        return await self.upsert_presence(user_id, True)

    async def set_offline(self, user_id: str) -> UserPresence:
        """Set user offline status."""
        presence = await self.upsert_presence(user_id, False)
        presence.connection_count = 0
        await self.session.commit()
        await self.session.refresh(presence)
        return presence

    async def cleanup_stale_connections(self, threshold_minutes: int = 5) -> int:
        """Clean up stale connections (users online but no recent activity)."""
        from datetime import timedelta

        threshold_time = datetime.now(timezone.utc) - timedelta(minutes=threshold_minutes)

        # Update users who are marked online but haven't been seen recently
        result = await self.session.execute(
            update(UserPresence)
            .where(
                UserPresence.is_online == True,
                UserPresence.last_seen_at < threshold_time,
            )
            .values(is_online=False, connection_count=0)
        )
        await self.session.commit()

        return result.rowcount
