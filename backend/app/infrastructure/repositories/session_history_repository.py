"""Session history repository."""

from datetime import datetime
from typing import Optional

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

    async def get_by_user_date_range(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> list[SessionHistory]:
        """Get user sessions within date range.

        Args:
            user_id: User identifier
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            List of session history records ordered by completed_at descending
        """
        result = await self.db.execute(
            select(SessionHistory)
            .where(SessionHistory.user_id == user_id)
            .where(SessionHistory.completed_at >= start_date)
            .where(SessionHistory.completed_at <= end_date)
            .order_by(SessionHistory.completed_at.desc())
        )
        return list(result.scalars().all())
