"""Timer repository implementation."""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models import Timer


class TimerRepository:
    """Repository for timer data access."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, timer: Timer) -> Timer:
        """Create timer."""
        self.db.add(timer)
        await self.db.flush()
        await self.db.refresh(timer)
        return timer

    async def get_by_room_id(self, room_id: str) -> Timer | None:
        """Get timer by room ID."""
        result = await self.db.execute(select(Timer).where(Timer.room_id == room_id))
        return result.scalar_one_or_none()

    async def get_with_room_by_room_id(self, room_id: str) -> tuple[Timer, "Room"] | None:
        """Get timer with room data by room ID using JOIN.

        This method fetches both timer and room in a single query,
        avoiding N+1 query problem.

        Args:
            room_id: Room identifier

        Returns:
            Tuple of (Timer, Room) if found, None otherwise
        """
        from app.infrastructure.database.models import Room

        result = await self.db.execute(
            select(Timer, Room)
            .join(Room, Timer.room_id == Room.id)
            .where(Timer.room_id == room_id)
        )
        row = result.first()
        return (row[0], row[1]) if row else None

    async def update(self, timer: Timer) -> Timer:
        """Update timer."""
        await self.db.flush()
        await self.db.refresh(timer)
        return timer
