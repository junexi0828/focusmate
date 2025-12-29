"""Friend domain schemas."""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class FriendRequestCreate(BaseModel):
    """Schema for creating a friend request."""
    receiver_id: str = Field(..., description="ID of user to send friend request to")


class FriendRequestResponse(BaseModel):
    """Schema for friend request response."""
    id: str
    sender_id: str
    receiver_id: str
    status: str
    created_at: datetime
    responded_at: Optional[datetime] = None

    # Sender/receiver info
    sender_username: Optional[str] = None
    sender_profile_image: Optional[str] = None
    receiver_username: Optional[str] = None
    receiver_profile_image: Optional[str] = None

    model_config = {"from_attributes": True}


class FriendResponse(BaseModel):
    """Schema for friend response."""
    id: str
    user_id: str
    friend_id: str
    created_at: datetime
    is_blocked: bool = False

    # Friend user info
    friend_username: str
    friend_email: Optional[str] = None
    friend_profile_image: Optional[str] = None
    friend_bio: Optional[str] = None

    # Presence info
    friend_is_online: bool = False
    friend_last_seen_at: Optional[datetime] = None
    friend_status_message: Optional[str] = None

    model_config = {"from_attributes": True}


class FriendListResponse(BaseModel):
    """Schema for friend list response."""
    friends: List[FriendResponse]
    total: int


class FriendPresence(BaseModel):
    """Schema for friend presence information."""
    user_id: str
    is_online: bool
    last_seen_at: datetime
    status_message: Optional[str] = None

    model_config = {"from_attributes": True}


class FriendSearchParams(BaseModel):
    """Schema for friend search parameters."""
    query: Optional[str] = None
    filter_type: Literal["all", "online", "blocked"] = "all"
    limit: int = Field(50, ge=1, le=100)
