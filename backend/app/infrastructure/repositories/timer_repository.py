"""Timer repository implementation."""

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

    async def update(self, timer: Timer) -> Timer:
        """Update timer."""
        await self.db.flush()
        await self.db.refresh(timer)
        return timer
