"""Timer domain schemas."""

from datetime import datetime

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
    started_at: datetime | None
    paused_at: datetime | None
    is_auto_start: bool


class TimerControlRequest(BaseModel):
    """Timer control request (start/pause/reset)."""

    model_config = ConfigDict(strict=True)

    action: str  # "start", "pause", "reset"
