"""Friend domain schemas."""

from datetime import datetime
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
    responded_at: datetime | None = None

    # Sender/receiver info
    sender_username: str | None = None
    sender_profile_image: str | None = None
    receiver_username: str | None = None
    receiver_profile_image: str | None = None

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
    friend_email: str | None = None
    friend_profile_image: str | None = None
    friend_bio: str | None = None
    friend_is_online: bool = False

    model_config = {"from_attributes": True}


class FriendListResponse(BaseModel):
    """Schema for friend list response."""
    friends: list[FriendResponse]
    total: int
