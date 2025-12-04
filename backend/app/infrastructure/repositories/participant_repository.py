"""Participant repository implementation."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models import Participant


class ParticipantRepository:
    """Repository for participant data access."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, participant: Participant) -> Participant:
        """Create participant."""
        self.db.add(participant)
        await self.db.flush()
        await self.db.refresh(participant)
        return participant

    async def get_by_id(self, participant_id: str) -> Participant | None:
        """Get participant by ID."""
        result = await self.db.execute(
            select(Participant).where(Participant.id == participant_id)
        )
        return result.scalar_one_or_none()

    async def get_by_room_id(self, room_id: str, active_only: bool = True) -> list[Participant]:
        """Get all participants in a room."""
        query = select(Participant).where(Participant.room_id == room_id)
        if active_only:
            query = query.where(Participant.is_connected == True)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_active_participants(self, room_id: str) -> int:
        """Count active participants in a room."""
        participants = await self.get_by_room_id(room_id, active_only=True)
        return len(participants)

    async def update(self, participant: Participant) -> Participant:
        """Update participant."""
        await self.db.flush()
        await self.db.refresh(participant)
        return participant

    async def mark_disconnected(self, participant_id: str) -> Participant | None:
        """Mark participant as disconnected."""
        participant = await self.get_by_id(participant_id)
        if participant:
            participant.is_connected = False
            participant.left_at = datetime.now(timezone.utc)
            return await self.update(participant)
        return None
