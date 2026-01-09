"""Notification domain schemas."""


from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum


class NotificationPriority(str, Enum):
    """Notification priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class NotificationCreate(BaseModel):
    """Notification creation request."""

    model_config = ConfigDict(strict=True)

    user_id: str = Field(..., min_length=1, max_length=36)
    type: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1)

    # New enterprise fields
    priority: NotificationPriority = NotificationPriority.MEDIUM
    routing: dict | None = None
    group_key: str | None = Field(None, max_length=100)
    data: dict | None = None


class NotificationResponse(BaseModel):
    """Notification response."""

    model_config = ConfigDict(strict=True, from_attributes=True)

    notification_id: str
    user_id: str
    type: str
    priority: NotificationPriority = NotificationPriority.MEDIUM
    title: str
    message: str
    data: dict | None = None
    routing: dict | None = None
    group_key: str | None = None
    delivered_via_ws: bool = False
    delivered_via_email: bool = False
    is_read: bool
    read_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class NotificationMarkRead(BaseModel):
    """Mark notification as read request."""

    model_config = ConfigDict(strict=True)

    notification_ids: list[str] = Field(..., min_items=1)
