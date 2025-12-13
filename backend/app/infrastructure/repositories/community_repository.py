"""Community repository - posts, comments, and likes."""

from datetime import datetime
from typing import Optional

from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.community import (
    Comment,
    CommentLike,
    Post,
    PostLike,
    PostRead,
)
from app.infrastructure.database.models.user import User


class PostRepository:
    """Repository for post data access."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, post: Post) -> Post:
        """Create post."""
        self.db.add(post)
        await self.db.flush()
        await self.db.refresh(post)
        return post

    async def get_by_id(self, post_id: str) -> Post | None:
        """Get post by ID."""
        result = await self.db.execute(
            select(Post).where(Post.id == post_id).where(Post.is_deleted == False)
        )
        return result.scalar_one_or_none()

    async def get_posts(
        self,
        limit: int = 20,
        offset: int = 0,
        category: Optional[str] = None,
        user_id: Optional[str] = None,
        search_query: Optional[str] = None,
        author_username: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> tuple[list[Post], int]:
        """Get posts with optional filtering and search."""
        # Join with User table for author username search
        query = select(Post).join(User, Post.user_id == User.id).where(Post.is_deleted == False)

        if category:
            query = query.where(Post.category == category)
        if user_id:
            query = query.where(Post.user_id == user_id)
        if author_username:
            # Search by author username
            username_pattern = f"%{author_username}%"
            query = query.where(User.username.ilike(username_pattern))
        if search_query:
            # Search in title and content
            search_pattern = f"%{search_query}%"
            query = query.where(
                or_(
                    Post.title.ilike(search_pattern),
                    Post.content.ilike(search_pattern),
                )
            )
        if date_from:
            query = query.where(Post.created_at >= date_from)
        if date_to:
            query = query.where(Post.created_at <= date_to)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply ordering (pinned first, then by created_at)
        query = query.order_by(desc(Post.is_pinned), desc(Post.created_at))

        query = query.limit(limit).offset(offset)

        # Execute
        result = await self.db.execute(query)
        posts = list(result.scalars().all())

        return posts, total

    async def update(self, post: Post) -> Post:
        """Update post."""
        await self.db.flush()
        await self.db.refresh(post)
        return post

    async def delete(self, post: Post) -> None:
        """Soft delete post."""
        post.is_deleted = True
        await self.db.flush()

    async def increment_comment_count(self, post_id: str) -> None:
        """Increment comment count for a post."""
        post = await self.get_by_id(post_id)
        if post:
            post.comment_count += 1
            await self.db.flush()

    async def decrement_comment_count(self, post_id: str) -> None:
        """Decrement comment count for a post."""
        post = await self.get_by_id(post_id)
        if post and post.comment_count > 0:
            post.comment_count -= 1
            await self.db.flush()

    async def get_count_by_user(self, user_id: str) -> int:
        """Get total post count for a user (excluding deleted posts).

        Args:
            user_id: User identifier

        Returns:
            Total number of posts by the user
        """
        result = await self.db.execute(
            select(func.count(Post.id))
            .where(Post.user_id == user_id)
            .where(Post.is_deleted == False)
        )
        return result.scalar() or 0


class CommentRepository:
    """Repository for comment data access."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, comment: Comment) -> Comment:
        """Create comment."""
        self.db.add(comment)
        await self.db.flush()
        await self.db.refresh(comment)
        return comment

    async def get_by_id(self, comment_id: str) -> Comment | None:
        """Get comment by ID."""
        result = await self.db.execute(
            select(Comment)
            .where(Comment.id == comment_id)
            .where(Comment.is_deleted == False)
        )
        return result.scalar_one_or_none()

    async def get_by_post(self, post_id: str) -> list[Comment]:
        """Get all comments for a post."""
        result = await self.db.execute(
            select(Comment)
            .where(Comment.post_id == post_id)
            .where(Comment.is_deleted == False)
            .order_by(Comment.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_replies(self, parent_comment_id: str) -> list[Comment]:
        """Get replies to a comment."""
        result = await self.db.execute(
            select(Comment)
            .where(Comment.parent_comment_id == parent_comment_id)
            .where(Comment.is_deleted == False)
            .order_by(Comment.created_at.asc())
        )
        return list(result.scalars().all())

    async def update(self, comment: Comment) -> Comment:
        """Update comment."""
        await self.db.flush()
        await self.db.refresh(comment)
        return comment

    async def delete(self, comment: Comment) -> None:
        """Soft delete comment."""
        comment.is_deleted = True
        await self.db.flush()


class PostLikeRepository:
    """Repository for post like data access."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, post_like: PostLike) -> PostLike:
        """Create post like."""
        self.db.add(post_like)
        await self.db.flush()
        await self.db.refresh(post_like)
        return post_like

    async def get_by_post_and_user(self, post_id: str, user_id: str) -> PostLike | None:
        """Check if user already liked post."""
        result = await self.db.execute(
            select(PostLike)
            .where(PostLike.post_id == post_id)
            .where(PostLike.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def delete(self, post_like: PostLike) -> None:
        """Remove post like."""
        await self.db.delete(post_like)
        await self.db.flush()


class CommentLikeRepository:
    """Repository for comment like data access."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, comment_like: CommentLike) -> CommentLike:
        """Create comment like."""
        self.db.add(comment_like)
        await self.db.flush()
        await self.db.refresh(comment_like)
        return comment_like

    async def get_by_comment_and_user(
        self, comment_id: str, user_id: str
    ) -> CommentLike | None:
        """Check if user already liked comment."""
        result = await self.db.execute(
            select(CommentLike)
            .where(CommentLike.comment_id == comment_id)
            .where(CommentLike.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def delete(self, comment_like: CommentLike) -> None:
        """Remove comment like."""
        await self.db.delete(comment_like)
        await self.db.flush()


class PostReadRepository:
    """Repository for post read data access."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_or_update(self, post_read: PostRead) -> PostRead:
        """Create or update post read record."""
        # Check if read record already exists
        existing = await self.get_by_post_and_user(post_read.post_id, post_read.user_id)
        if existing:
            # Update read_at timestamp
            existing.read_at = post_read.read_at
            await self.db.flush()
            await self.db.refresh(existing)
            return existing
        else:
            # Create new read record
            self.db.add(post_read)
            await self.db.flush()
            await self.db.refresh(post_read)
            return post_read

    async def get_by_post_and_user(self, post_id: str, user_id: str) -> PostRead | None:
        """Check if user has read the post."""
        result = await self.db.execute(
            select(PostRead)
            .where(PostRead.post_id == post_id)
            .where(PostRead.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_read_posts_by_user(self, user_id: str) -> list[str]:
        """Get list of post IDs that user has read."""
        result = await self.db.execute(
            select(PostRead.post_id).where(PostRead.user_id == user_id)
        )
        return [row[0] for row in result.all()]

    async def get_read_status_for_posts(
        self, post_ids: list[str], user_id: str
    ) -> dict[str, bool]:
        """Get read status for multiple posts."""
        if not post_ids:
            return {}
        result = await self.db.execute(
            select(PostRead.post_id)
            .where(PostRead.post_id.in_(post_ids))
            .where(PostRead.user_id == user_id)
        )
        read_post_ids = {row[0] for row in result.all()}
        return {post_id: post_id in read_post_ids for post_id in post_ids}
