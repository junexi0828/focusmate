"""API dependencies."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.room.service import RoomService
from app.infrastructure.database.session import get_db
from app.infrastructure.repositories.room_repository import RoomRepository
from app.infrastructure.repositories.timer_repository import TimerRepository

DatabaseSession = Annotated[AsyncSession, Depends(get_db)]


def get_room_repository(db: DatabaseSession) -> RoomRepository:
    """Get room repository."""
    return RoomRepository(db)


def get_timer_repository(db: DatabaseSession) -> TimerRepository:
    """Get timer repository."""
    return TimerRepository(db)


def get_room_service(repo: Annotated[RoomRepository, Depends(get_room_repository)]) -> RoomService:
    """Get room service."""
    return RoomService(repo)
