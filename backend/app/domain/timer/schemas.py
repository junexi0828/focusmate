"""Timer domain schemas."""


from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class TimerStateResponse(BaseModel):
    """Timer state response."""

    model_config = ConfigDict(strict=True, from_attributes=True)

    id: str
    room_id: str
    status: str
    phase: str
    duration: int
    remaining_seconds: int
    started_at: datetime | None
    paused_at: datetime | None
    completed_at: datetime | None
    is_auto_start: bool
    target_timestamp: str | None = None  # ISO timestamp when timer will complete (for running timers)
    session_type: str | None = None  # "work" or "break" (derived from phase)


class TimerControlRequest(BaseModel):
    """Timer control request (start/pause/reset)."""

    model_config = ConfigDict(strict=True)

    action: str  # "start", "pause", "reset"


class StartTimerRequest(BaseModel):
    """Start timer request with session type."""

    model_config = ConfigDict(strict=True)

    session_type: str = "work"  # "work" or "break"
