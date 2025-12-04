"""Achievement ORM Model - stores gamification achievements."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, TimestampMixin


class Achievement(Base, TimestampMixin):
    """Achievement model - defines available achievements and their requirements."""

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str] = mapped_column(String(50), nullable=False)  # Icon identifier
    category: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # "sessions", "time", "streak", "social"
    requirement_type: Mapped[str] = mapped_column(String(20), nullable=False)  # "total_sessions", "total_focus_time", "streak_days"
    requirement_value: Mapped[int] = mapped_column(Integer, nullable=False)  # Threshold to unlock
    points: Mapped[int] = mapped_column(Integer, default=10)  # Points awarded
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class UserAchievement(Base, TimestampMixin):
    """User achievement junction table - tracks which users unlocked which achievements."""

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    achievement_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    unlocked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    progress: Mapped[int] = mapped_column(Integer, default=0)  # Current progress towards requirement
