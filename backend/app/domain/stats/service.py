"""Stats domain service - session tracking and statistics."""

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Optional

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

    async def get_user_stats(
        self,
        user_id: str,
        days: int = 7,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> dict:
        """Get user statistics for last N days or date range.

        Args:
            user_id: User identifier
            days: Number of days to look back (used if start_date/end_date not provided)
            start_date: Start date for date range filtering
            end_date: End date for date range filtering

        Returns:
            Dictionary with total_focus_time, total_sessions, average_session, and sessions list
        """
        if start_date and end_date:
            since = start_date
            until = end_date
        else:
            since = datetime.now(timezone.utc) - timedelta(days=days)
            until = datetime.now(timezone.utc)

        sessions = await self.repository.get_by_user_date_range(user_id, since, until)

        work_sessions = [s for s in sessions if s.session_type == "work"]
        total_focus_time = sum(s.duration_minutes for s in work_sessions)
        total_sessions = len(work_sessions)

        return {
            "total_focus_time": total_focus_time,
            "total_sessions": total_sessions,
            "average_session": total_focus_time // total_sessions if total_sessions else 0,
            "sessions": [
                {
                    "session_id": s.id,
                    "id": s.id,  # Keep for backward compatibility
                    "user_id": s.user_id,
                    "room_id": s.room_id,
                    "session_type": s.session_type,
                    "type": s.session_type,  # Keep for backward compatibility
                    "duration_minutes": s.duration_minutes,
                    "duration": s.duration_minutes,  # Keep for backward compatibility
                    "completed_at": s.completed_at.isoformat(),
                    "room_name": getattr(s, "room_name", None),  # Include room_name if available
                }
                for s in sessions
            ],
        }

    async def get_hourly_pattern(self, user_id: str, days: int = 30) -> dict:
        """Get hourly focus pattern for radar chart.

        Args:
            user_id: User identifier
            days: Number of days to analyze (default: 30)

        Returns:
            Dictionary with hourly focus time distribution (0-23 hours)
        """
        since = datetime.now(timezone.utc) - timedelta(days=days)
        until = datetime.now(timezone.utc)
        sessions = await self.repository.get_by_user_date_range(user_id, since, until)

        # Initialize hourly buckets (0-23)
        hourly_focus = defaultdict(int)

        for session in sessions:
            if session.session_type == "work":
                # Get hour in user's local time (assuming UTC for now)
                hour = session.completed_at.hour
                hourly_focus[hour] += session.duration_minutes

        # Convert to list format for frontend (0-23 hours)
        hourly_data = [hourly_focus.get(hour, 0) for hour in range(24)]

        return {
            "hourly_focus_time": hourly_data,
            "total_days": days,
            "peak_hour": max(hourly_focus.items(), key=lambda x: x[1])[0] if hourly_focus else None,
        }

    async def get_monthly_comparison(self, user_id: str, months: int = 6) -> dict:
        """Get monthly comparison data for line chart.

        Args:
            user_id: User identifier
            months: Number of months to compare (default: 6)

        Returns:
            Dictionary with monthly statistics
        """
        since = datetime.now(timezone.utc) - timedelta(days=months * 30)
        until = datetime.now(timezone.utc)
        sessions = await self.repository.get_by_user_date_range(user_id, since, until)

        # Group by month
        monthly_stats = defaultdict(lambda: {"focus_time": 0, "sessions": 0, "break_time": 0})

        for session in sessions:
            month_key = session.completed_at.strftime("%Y-%m")
            if session.session_type == "work":
                monthly_stats[month_key]["focus_time"] += session.duration_minutes
                monthly_stats[month_key]["sessions"] += 1
            else:
                monthly_stats[month_key]["break_time"] += session.duration_minutes

        # Convert to sorted list
        monthly_data = []
        for month_key in sorted(monthly_stats.keys()):
            stats = monthly_stats[month_key]
            monthly_data.append({
                "month": month_key,
                "focus_time_minutes": stats["focus_time"],
                "focus_time_hours": round(stats["focus_time"] / 60, 2),
                "sessions": stats["sessions"],
                "break_time_minutes": stats["break_time"],
                "average_session": stats["focus_time"] // stats["sessions"] if stats["sessions"] > 0 else 0,
            })

        return {
            "monthly_data": monthly_data,
            "total_months": len(monthly_data),
        }

    async def get_goal_achievement(
        self,
        user_id: str,
        goal_type: str,
        goal_value: int,
        period: str = "week",
    ) -> dict:
        """Get goal achievement rate for progress ring.

        Args:
            user_id: User identifier
            goal_type: Type of goal ('focus_time' or 'sessions')
            goal_value: Target value for the goal
            period: Time period ('day', 'week', 'month')

        Returns:
            Dictionary with current progress, goal, and achievement rate
        """
        # Calculate date range based on period
        now = datetime.now(timezone.utc)
        if period == "day":
            since = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            # Start of current week (Monday)
            days_since_monday = now.weekday()
            since = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "month":
            since = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            since = now - timedelta(days=7)  # Default to week

        sessions = await self.repository.get_by_user_date_range(user_id, since, now)
        work_sessions = [s for s in sessions if s.session_type == "work"]

        if goal_type == "focus_time":
            current_value = sum(s.duration_minutes for s in work_sessions)
            achievement_rate = min(100, int((current_value / goal_value) * 100)) if goal_value > 0 else 0
        elif goal_type == "sessions":
            current_value = len(work_sessions)
            achievement_rate = min(100, int((current_value / goal_value) * 100)) if goal_value > 0 else 0
        else:
            current_value = 0
            achievement_rate = 0

        return {
            "goal_type": goal_type,
            "goal_value": goal_value,
            "current_value": current_value,
            "achievement_rate": achievement_rate,
            "period": period,
            "is_achieved": current_value >= goal_value,
            "remaining": max(0, goal_value - current_value),
        }
