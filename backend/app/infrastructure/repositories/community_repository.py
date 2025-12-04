"""Community repository - posts, comments, and likes."""

from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.community import Comment, CommentLike, Post, PostLike


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

    async def get_all(
        self,
        category: str | None = None,
        user_id: str | None = None,
        search: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Post], int]:
        """Get posts with filters and pagination.

        Returns:
            Tuple of (posts, total_count)
        """
        # Build query
        query = select(Post).where(Post.is_deleted == False)

        # Apply filters
        if category:
            query = query.where(Post.category == category)
        if user_id:
            query = query.where(Post.user_id == user_id)
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    Post.title.ilike(search_pattern),
                    Post.content.ilike(search_pattern)
                )
            )

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Apply ordering (pinned first, then by created_at)
        query = query.order_by(desc(Post.is_pinned), desc(Post.created_at))

        # Apply pagination
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
            select(Comment).where(Comment.id == comment_id).where(Comment.is_deleted == False)
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

    async def get_by_comment_and_user(self, comment_id: str, user_id: str) -> CommentLike | None:
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
