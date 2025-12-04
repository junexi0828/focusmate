"""SessionHistory ORM Model - stores completed pomodoro sessions."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, TimestampMixin


class SessionHistory(Base, TimestampMixin):
    """Session history model - records completed pomodoro sessions."""

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    room_id: Mapped[str] = mapped_column(String(36), nullable=False)
    session_type: Mapped[str] = mapped_column(String(20), nullable=False)  # "work" or "break"
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
