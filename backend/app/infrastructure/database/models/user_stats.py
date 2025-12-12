"""User goals and manual session models."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.infrastructure.database.base import Base


class UserGoal(Base):
    """User daily/weekly goals."""

    __tablename__ = "user_goals"

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # Goals
    daily_goal_minutes = Column(Integer, nullable=False, default=120)
    weekly_goal_sessions = Column(Integer, nullable=False, default=5)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class ManualSession(Base):
    """Manually logged sessions."""

    __tablename__ = "manual_sessions"

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # Session details
    duration_minutes = Column(Integer, nullable=False)
    session_type = Column(String, nullable=False)  # 'focus' or 'break'
    completed_at = Column(DateTime(timezone=True), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
