"""Community domain service - posts, comments, and social interactions."""

from datetime import datetime, timezone

from app.core.exceptions import NotFoundException, UnauthorizedException
from app.domain.community.schemas import (
    CommentCreate,
    CommentResponse,
    CommentUpdate,
    LikeResponse,
    PostCreate,
    PostFilters,
    PostListResponse,
    PostListResult,
    PostResponse,
    PostUpdate,
)
from app.infrastructure.database.models.community import Comment, CommentLike, Post, PostLike
from app.infrastructure.repositories.community_repository import (
    CommentLikeRepository,
    CommentRepository,
    PostLikeRepository,
    PostRepository,
)
from app.infrastructure.repositories.user_repository import UserRepository
from app.shared.utils.uuid import generate_uuid


class CommunityService:
    """Community service for posts, comments, and social interactions."""

    def __init__(
        self,
        post_repo: PostRepository,
        comment_repo: CommentRepository,
        post_like_repo: PostLikeRepository,
        comment_like_repo: CommentLikeRepository,
        user_repo: UserRepository,
    ) -> None:
        self.post_repo = post_repo
        self.comment_repo = comment_repo
        self.post_like_repo = post_like_repo
        self.comment_like_repo = comment_like_repo
        self.user_repo = user_repo

    # Post Operations
    async def create_post(self, user_id: str, data: PostCreate) -> PostResponse:
        """Create a new post."""
        post = Post(
            id=generate_uuid(),
            user_id=user_id,
            title=data.title,
            content=data.content,
            category=data.category,
            likes=0,
            comment_count=0,
            is_pinned=False,
            is_deleted=False,
        )

        created_post = await self.post_repo.create(post)
        response = PostResponse.model_validate(created_post)

        # Add author username
        user = await self.user_repo.get_by_id(user_id)
        if user:
            response.author_username = user.username

        return response

    async def get_post(self, post_id: str) -> PostResponse:
        """Get post by ID with author info."""
        post = await self.post_repo.get_by_id(post_id)
        if not post:
            raise NotFoundException(f"Post {post_id} not found")

        response = PostResponse.model_validate(post)

        # Add author username
        user = await self.user_repo.get_by_id(post.user_id)
        if user:
            response.author_username = user.username

        return response

    async def get_posts(self, filters: PostFilters) -> PostListResult:
        """Get posts with filters and pagination."""
        posts, total = await self.post_repo.get_all(
            category=filters.category,
            user_id=filters.user_id,
            search=filters.search,
            limit=filters.limit,
            offset=filters.offset,
        )

        # Convert to list responses with author info
        post_responses = []
        for post in posts:
            response = PostListResponse.model_validate(post)
            user = await self.user_repo.get_by_id(post.user_id)
            if user:
                response.author_username = user.username
            post_responses.append(response)

        return PostListResult(
            posts=post_responses,
            total=total,
            limit=filters.limit,
            offset=filters.offset,
        )

    async def update_post(self, post_id: str, user_id: str, data: PostUpdate) -> PostResponse:
        """Update post (only by author)."""
        post = await self.post_repo.get_by_id(post_id)
        if not post:
            raise NotFoundException(f"Post {post_id} not found")

        # Check authorization
        if post.user_id != user_id:
            raise UnauthorizedException("You can only edit your own posts")

        # Update fields
        if data.title is not None:
            post.title = data.title
        if data.content is not None:
            post.content = data.content
        if data.category is not None:
            post.category = data.category

        updated_post = await self.post_repo.update(post)
        response = PostResponse.model_validate(updated_post)

        # Add author username
        user = await self.user_repo.get_by_id(post.user_id)
        if user:
            response.author_username = user.username

        return response

    async def delete_post(self, post_id: str, user_id: str) -> dict:
        """Delete post (only by author)."""
        post = await self.post_repo.get_by_id(post_id)
        if not post:
            raise NotFoundException(f"Post {post_id} not found")

        # Check authorization
        if post.user_id != user_id:
            raise UnauthorizedException("You can only delete your own posts")

        await self.post_repo.delete(post)
        return {"status": "deleted", "post_id": post_id}

    async def toggle_post_like(self, post_id: str, user_id: str) -> LikeResponse:
        """Toggle like on a post."""
        post = await self.post_repo.get_by_id(post_id)
        if not post:
            raise NotFoundException(f"Post {post_id} not found")

        # Check if already liked
        existing_like = await self.post_like_repo.get_by_post_and_user(post_id, user_id)

        if existing_like:
            # Unlike
            await self.post_like_repo.delete(existing_like)
            post.likes = max(0, post.likes - 1)
            await self.post_repo.update(post)
            return LikeResponse(success=True, liked=False, new_count=post.likes)
        else:
            # Like
            post_like = PostLike(
                id=generate_uuid(),
                post_id=post_id,
                user_id=user_id,
                created_at=datetime.now(timezone.utc),
            )
            await self.post_like_repo.create(post_like)
            post.likes += 1
            await self.post_repo.update(post)
            return LikeResponse(success=True, liked=True, new_count=post.likes)

    # Comment Operations
    async def create_comment(
        self, post_id: str, user_id: str, data: CommentCreate
    ) -> CommentResponse:
        """Create a comment on a post."""
        # Verify post exists
        post = await self.post_repo.get_by_id(post_id)
        if not post:
            raise NotFoundException(f"Post {post_id} not found")

        # If parent_comment_id provided, verify it exists
        if data.parent_comment_id:
            parent_comment = await self.comment_repo.get_by_id(data.parent_comment_id)
            if not parent_comment:
                raise NotFoundException(f"Parent comment {data.parent_comment_id} not found")

        comment = Comment(
            id=generate_uuid(),
            post_id=post_id,
            user_id=user_id,
            content=data.content,
            parent_comment_id=data.parent_comment_id,
            likes=0,
            is_deleted=False,
        )

        created_comment = await self.comment_repo.create(comment)

        # Increment post comment count
        await self.post_repo.increment_comment_count(post_id)

        response = CommentResponse.model_validate(created_comment)

        # Add author username
        user = await self.user_repo.get_by_id(user_id)
        if user:
            response.author_username = user.username

        return response

    async def get_post_comments(self, post_id: str) -> list[CommentResponse]:
        """Get all comments for a post with nested replies."""
        comments = await self.comment_repo.get_by_post(post_id)

        # Build comment map
        comment_map = {}
        for comment in comments:
            response = CommentResponse.model_validate(comment)
            user = await self.user_repo.get_by_id(comment.user_id)
            if user:
                response.author_username = user.username
            comment_map[comment.id] = response

        # Build tree structure
        root_comments = []
        for comment in comments:
            response = comment_map[comment.id]
            if comment.parent_comment_id:
                # Add to parent's replies
                parent = comment_map.get(comment.parent_comment_id)
                if parent:
                    parent.replies.append(response)
            else:
                # Root level comment
                root_comments.append(response)

        return root_comments

    async def update_comment(
        self, comment_id: str, user_id: str, data: CommentUpdate
    ) -> CommentResponse:
        """Update comment (only by author)."""
        comment = await self.comment_repo.get_by_id(comment_id)
        if not comment:
            raise NotFoundException(f"Comment {comment_id} not found")

        # Check authorization
        if comment.user_id != user_id:
            raise UnauthorizedException("You can only edit your own comments")

        comment.content = data.content
        updated_comment = await self.comment_repo.update(comment)

        response = CommentResponse.model_validate(updated_comment)

        # Add author username
        user = await self.user_repo.get_by_id(comment.user_id)
        if user:
            response.author_username = user.username

        return response

    async def delete_comment(self, comment_id: str, user_id: str) -> dict:
        """Delete comment (only by author)."""
        comment = await self.comment_repo.get_by_id(comment_id)
        if not comment:
            raise NotFoundException(f"Comment {comment_id} not found")

        # Check authorization
        if comment.user_id != user_id:
            raise UnauthorizedException("You can only delete your own comments")

        await self.comment_repo.delete(comment)

        # Decrement post comment count
        await self.post_repo.decrement_comment_count(comment.post_id)

        return {"status": "deleted", "comment_id": comment_id}

    async def toggle_comment_like(self, comment_id: str, user_id: str) -> LikeResponse:
        """Toggle like on a comment."""
        comment = await self.comment_repo.get_by_id(comment_id)
        if not comment:
            raise NotFoundException(f"Comment {comment_id} not found")

        # Check if already liked
        existing_like = await self.comment_like_repo.get_by_comment_and_user(comment_id, user_id)

        if existing_like:
            # Unlike
            await self.comment_like_repo.delete(existing_like)
            comment.likes = max(0, comment.likes - 1)
            await self.comment_repo.update(comment)
            return LikeResponse(success=True, liked=False, new_count=comment.likes)
        else:
            # Like
            comment_like = CommentLike(
                id=generate_uuid(),
                comment_id=comment_id,
                user_id=user_id,
                created_at=datetime.now(timezone.utc),
            )
            await self.comment_like_repo.create(comment_like)
            comment.likes += 1
            await self.comment_repo.update(comment)
            return LikeResponse(success=True, liked=True, new_count=comment.likes)
