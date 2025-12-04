"""Stats domain service - session tracking and statistics."""

from datetime import datetime, timedelta, timezone

from app.infrastructure.database.models.session_history import SessionHistory
from app.infrastructure.repositories.session_history_repository import SessionHistoryRepository
from app.shared.utils.uuid import generate_uuid


class StatsService:
    """Statistics and session tracking service."""

    def __init__(self, repository: SessionHistoryRepository) -> None:
        self.repository = repository

    async def record_session(
        self,
        user_id: str,
        room_id: str,
        session_type: str,
        duration_minutes: int,
    ) -> dict:
        """Record a completed session."""
        session = SessionHistory(
            id=generate_uuid(),
            user_id=user_id,
            room_id=room_id,
            session_type=session_type,
            duration_minutes=duration_minutes,
            completed_at=datetime.now(timezone.utc),
        )
        await self.repository.create(session)
        return {"status": "recorded", "session_id": session.id}

    async def get_user_stats(self, user_id: str, days: int = 7) -> dict:
        """Get user statistics for last N days."""
        since = datetime.now(timezone.utc) - timedelta(days=days)
        sessions = await self.repository.get_by_user_since(user_id, since)
        
        total_focus_time = sum(s.duration_minutes for s in sessions if s.session_type == "work")
        total_sessions = len([s for s in sessions if s.session_type == "work"])
        
        return {
            "total_focus_time": total_focus_time,
            "total_sessions": total_sessions,
            "average_session": total_focus_time // total_sessions if total_sessions else 0,
            "sessions": [
                {
                    "id": s.id,
                    "type": s.session_type,
                    "duration": s.duration_minutes,
                    "completed_at": s.completed_at.isoformat(),
                }
                for s in sessions
            ],
        }
