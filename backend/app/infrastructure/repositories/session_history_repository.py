"""Session history repository."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.session_history import SessionHistory


class SessionHistoryRepository:
    """Repository for session history data access."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, session: SessionHistory) -> SessionHistory:
        """Create session record."""
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        return session

    async def get_by_user_since(self, user_id: str, since: datetime) -> list[SessionHistory]:
        """Get user sessions since date."""
        result = await self.db.execute(
            select(SessionHistory)
            .where(SessionHistory.user_id == user_id)
            .where(SessionHistory.completed_at >= since)
            .order_by(SessionHistory.completed_at.desc())
        )
        return list(result.scalars().all())
