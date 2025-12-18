"""Room repository implementation."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models import Room


class RoomRepository:
    """Repository for room data access."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository.

        Args:
            db: Database session
        """
        self.db = db

    async def create(self, room: Room) -> Room:
        """Create a new room.

        Args:
            room: Room model

        Returns:
            Created room
        """
        self.db.add(room)
        await self.db.flush()
        await self.db.refresh(room)
        return room

    async def get_by_id(self, room_id: str) -> Room | None:
        """Get room by ID.

        Args:
            room_id: Room identifier

        Returns:
            Room if found, None otherwise
        """
        result = await self.db.execute(select(Room).where(Room.id == room_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str, active_only: bool = True) -> Room | None:
        """Get room by name.

        Args:
            name: Room name
            active_only: Only check active rooms (default: True)

        Returns:
            Room if found, None otherwise
        """
        query = select(Room).where(Room.name == name)
        if active_only:
            query = query.where(Room.is_active == True)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update(self, room: Room) -> Room:
        """Update room.

        Args:
            room: Room model with updated fields

        Returns:
            Updated room
        """
        await self.db.flush()
        await self.db.refresh(room)
        return room

    async def get_all_active(self) -> list[Room]:
        """Get all active rooms.

        Returns:
            List of active rooms
        """
        result = await self.db.execute(
            select(Room).where(Room.is_active == True).order_by(Room.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete(self, room: Room) -> None:
        """Delete room.

        Args:
            room: Room to delete
        """
        await self.db.delete(room)
        await self.db.flush()
