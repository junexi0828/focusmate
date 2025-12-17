"""Notification domain schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class NotificationCreate(BaseModel):
    """Notification creation request."""

    model_config = ConfigDict(strict=True)

    user_id: str = Field(..., min_length=1, max_length=36)
    type: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1)
    data: Optional[dict] = None


class NotificationResponse(BaseModel):
    """Notification response."""

    model_config = ConfigDict(strict=True, from_attributes=True)

    notification_id: str
    user_id: str
    type: str
    title: str
    message: str
    data: Optional[dict] = None
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class NotificationMarkRead(BaseModel):
    """Mark notification as read request."""

    model_config = ConfigDict(strict=True)

    notification_ids: list[str] = Field(..., min_items=1)
