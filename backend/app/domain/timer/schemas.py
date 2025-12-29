"""Timer domain schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TimerStateResponse(BaseModel):
    """Timer state response."""

    model_config = ConfigDict(strict=True, from_attributes=True)

    id: str
    room_id: str
    status: str
    phase: str
    duration: int
    remaining_seconds: int
    started_at: Optional[datetime]
    paused_at: Optional[datetime]
    completed_at: Optional[datetime]
    is_auto_start: bool
    target_timestamp: Optional[str] = None  # ISO timestamp when timer will complete (for running timers)
    session_type: Optional[str] = None  # "work" or "break" (derived from phase)


class TimerControlRequest(BaseModel):
    """Timer control request (start/pause/reset)."""

    model_config = ConfigDict(strict=True)

    action: str  # "start", "pause", "reset"
