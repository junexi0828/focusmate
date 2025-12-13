"""Community domain schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# Post Schemas
class PostCreate(BaseModel):
    """Schema for creating a new post."""

    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, max_length=10000)
    category: str = Field(..., min_length=1, max_length=50)


class PostUpdate(BaseModel):
    """Schema for updating a post."""

    title: str | None = Field(None, min_length=1, max_length=200)
    content: str | None = Field(None, min_length=1, max_length=10000)
    category: str | None = Field(None, min_length=1, max_length=50)


class PostResponse(BaseModel):
    """Post response schema."""

    model_config = ConfigDict(from_attributes=True, strict=True)

    id: str
    user_id: str
    title: str
    content: str
    category: str
    likes: int
    comment_count: int
    is_pinned: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    author_username: str | None = None
    is_liked: bool = False  # Whether current user liked this post
    is_read: bool = False  # Whether current user has read this post


class PostListResponse(BaseModel):
    """Simplified post list response."""

    model_config = ConfigDict(from_attributes=True, strict=True)

    id: str
    user_id: str
    title: str
    category: str
    likes: int
    comment_count: int
    is_pinned: bool
    created_at: datetime
    author_username: str | None = None
    is_liked: bool = False  # Whether current user liked this post
    is_read: bool = False  # Whether current user has read this post


# Comment Schemas
class CommentCreate(BaseModel):
    """Schema for creating a new comment."""

    content: str = Field(..., min_length=1, max_length=5000)
    parent_comment_id: str | None = Field(None, max_length=36)


class CommentUpdate(BaseModel):
    """Schema for updating a comment."""

    content: str = Field(..., min_length=1, max_length=5000)


class CommentResponse(BaseModel):
    """Comment response schema."""

    model_config = ConfigDict(from_attributes=True, strict=True)

    id: str
    post_id: str
    user_id: str
    content: str
    parent_comment_id: str | None
    likes: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    author_username: str | None = None
    is_liked: bool = False  # Whether current user liked this comment
    replies: list["CommentResponse"] = []  # Nested replies


# Like Schemas
class LikeResponse(BaseModel):
    """Like action response."""

    success: bool
    liked: bool  # True if liked, False if unliked
    new_count: int


# Search and Filter
class PostFilters(BaseModel):
    """Filters for post search."""

    category: str | None = None
    user_id: str | None = None
    search: str | None = None  # Search in title and content
    author_username: str | None = None  # Search by author username
    date_from: datetime | None = None  # Filter posts from this date
    date_to: datetime | None = None  # Filter posts until this date
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class PostListResult(BaseModel):
    """Paginated post list result."""

    posts: list[PostListResponse]
    total: int
    limit: int
    offset: int
