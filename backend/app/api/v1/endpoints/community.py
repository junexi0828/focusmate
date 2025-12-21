"""Community API endpoints - posts, comments, likes."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundException, UnauthorizedException
from app.domain.community.schemas import (
    CommentCreate,
    CommentResponse,
    CommentUpdate,
    LikeResponse,
    PostCreate,
    PostFilters,
    PostListResult,
    PostResponse,
    PostSortBy,
    PostUpdate,
)
from app.domain.community.service import CommunityService
from app.infrastructure.database.session import DatabaseSession
from app.infrastructure.repositories.community_repository import (
    CommentLikeRepository,
    CommentRepository,
    PostLikeRepository,
    PostReadRepository,
    PostRepository,
)
from app.infrastructure.repositories.user_repository import UserRepository


router = APIRouter(prefix="/community", tags=["community"])


# Dependency Injection
def get_post_repository(db: DatabaseSession) -> PostRepository:
    """Get post repository."""
    return PostRepository(db)


def get_comment_repository(db: DatabaseSession) -> CommentRepository:
    """Get comment repository."""
    return CommentRepository(db)


def get_post_like_repository(db: DatabaseSession) -> PostLikeRepository:
    """Get post like repository."""
    return PostLikeRepository(db)


def get_comment_like_repository(db: DatabaseSession) -> CommentLikeRepository:
    """Get comment like repository."""
    return CommentLikeRepository(db)


def get_post_read_repository(db: DatabaseSession) -> PostReadRepository:
    """Get post read repository."""
    return PostReadRepository(db)


def get_user_repository(db: DatabaseSession) -> UserRepository:
    """Get user repository."""
    return UserRepository(db)


def get_community_service(
    post_repo: Annotated[PostRepository, Depends(get_post_repository)],
    comment_repo: Annotated[CommentRepository, Depends(get_comment_repository)],
    post_like_repo: Annotated[PostLikeRepository, Depends(get_post_like_repository)],
    comment_like_repo: Annotated[
        CommentLikeRepository, Depends(get_comment_like_repository)
    ],
    post_read_repo: Annotated[PostReadRepository, Depends(get_post_read_repository)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> CommunityService:
    """Get community service."""
    return CommunityService(
        post_repo,
        comment_repo,
        post_like_repo,
        comment_like_repo,
        post_read_repo,
        user_repo,
    )


# Post Endpoints
@router.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    data: PostCreate,
    db: DatabaseSession,
    service: Annotated[CommunityService, Depends(get_community_service)],
    user_id: str = Query(..., description="User ID creating the post"),
) -> PostResponse:
    """Create a new community post.

    Args:
        data: Post details (title, content, category)
        user_id: ID of the user creating the post
        service: Community service
        db: Database session

    Returns:
        Created post with author info
    """
    post = await service.create_post(user_id, data)

    # Check and unlock achievements after post creation
    try:
        from app.domain.achievement.service import AchievementService
        from app.infrastructure.repositories.achievement_repository import (
            AchievementRepository,
            UserAchievementRepository,
        )
        from app.infrastructure.repositories.community_repository import PostRepository
        from app.infrastructure.repositories.session_history_repository import (
            SessionHistoryRepository,
        )
        from app.infrastructure.repositories.user_repository import UserRepository

        achievement_repo = AchievementRepository(db)
        user_achievement_repo = UserAchievementRepository(db)
        user_repo = UserRepository(db)
        post_repo = PostRepository(db)
        session_repo = SessionHistoryRepository(db)

        achievement_service = AchievementService(
            achievement_repo,
            user_achievement_repo,
            user_repo,
            post_repo,
            session_repo,
        )

        # Check achievements in background (don't wait for result)
        await achievement_service.check_and_unlock_achievements(user_id)
    except Exception as e:
        # Log error but don't fail the post creation
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to check achievements after post creation: {e}")

    return post


@router.get("/posts", response_model=PostListResult)
async def get_posts(
    db: DatabaseSession,
    service: Annotated[CommunityService, Depends(get_community_service)],
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category: str | None = Query(None, description="Filter by category"),
    search: str | None = Query(None, description="Search in title and content"),
    author_username: str | None = Query(
        None, description="Filter by author username"
    ),
    date_from: str | None = Query(
        None, description="Filter posts from this date (ISO 8601 format)"
    ),
    date_to: str | None = Query(
        None, description="Filter posts until this date (ISO 8601 format)"
    ),
    sort_by: PostSortBy = Query(
        PostSortBy.RECENT,
        description="Sort posts by: recent, popular, trending, or most_commented",
    ),
    current_user: Annotated[dict | None, Depends(get_current_user)] = None,
) -> PostListResult:
    """Get community posts with optional filtering, sorting, and search.

    Args:
        limit: Maximum number of posts to return
        offset: Number of posts to skip
        category: Optional category filter
        search: Optional search query (searches in title and content)
        author_username: Optional filter by author username
        date_from: Optional filter posts from this date (ISO 8601 format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
        date_to: Optional filter posts until this date (ISO 8601 format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
        sort_by: Sort option (recent, popular, trending, most_commented)
        current_user: Current authenticated user (optional, for like status and read status)
    """
    # Parse date strings to datetime objects
    parsed_date_from = None
    parsed_date_to = None

    if date_from:
        try:
            # Try parsing ISO 8601 format
            parsed_date_from = datetime.fromisoformat(date_from.replace("Z", "+00:00"))
        except ValueError:
            try:
                # Try parsing date-only format (YYYY-MM-DD)
                parsed_date_from = datetime.strptime(date_from, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date_from format. Use ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)",
                )

    if date_to:
        try:
            # Try parsing ISO 8601 format
            parsed_date_to = datetime.fromisoformat(date_to.replace("Z", "+00:00"))
        except ValueError:
            try:
                # Try parsing date-only format (YYYY-MM-DD)
                parsed_date_to = datetime.strptime(date_to, "%Y-%m-%d")
                # Set to end of day
                parsed_date_to = parsed_date_to.replace(hour=23, minute=59, second=59)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date_to format. Use ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)",
                )

    filters = PostFilters(
        limit=limit,
        offset=offset,
        category=category,
        search=search,
        author_username=author_username,
        date_from=parsed_date_from,
        date_to=parsed_date_to,
        sort_by=sort_by,
    )
    current_user_id = current_user["id"] if current_user else None
    return await service.get_posts(filters=filters, current_user_id=current_user_id)


@router.get("/posts/stats/categories")
async def get_category_stats(
    db: DatabaseSession,
) -> dict[str, int]:
    """Get post count statistics by category.

    Returns:
        Dictionary mapping category names to post counts
    """
    from app.infrastructure.repositories.community_repository import PostRepository

    post_repo = PostRepository(db)
    return await post_repo.get_category_counts()


@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: str,
    db: DatabaseSession,
    service: Annotated[CommunityService, Depends(get_community_service)],
    current_user: Annotated[dict | None, Depends(get_current_user)] = None,
) -> PostResponse:
    """Get a specific post by ID.

    Args:
        post_id: Post identifier
        current_user: Current authenticated user (optional)
        service: Community service

    Returns:
        Post details with author info and like status

    Raises:
        HTTPException: If post not found
    """
    try:
        current_user_id = current_user["id"] if current_user else None
        return await service.get_post(post_id, current_user_id=current_user_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.put("/posts/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: str,
    data: PostUpdate,
    service: Annotated[CommunityService, Depends(get_community_service)],
    user_id: str = Query(..., description="User ID requesting update"),
) -> PostResponse:
    """Update a post (only by author).

    Args:
        post_id: Post identifier
        data: Updated post data
        user_id: ID of user requesting update
        service: Community service

    Returns:
        Updated post

    Raises:
        HTTPException: If post not found or unauthorized
    """
    try:
        return await service.update_post(post_id, user_id, data)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)


@router.delete("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post(
    post_id: str,
    service: Annotated[CommunityService, Depends(get_community_service)],
    user_id: str = Query(..., description="User ID requesting deletion"),
) -> dict:
    """Delete a post (only by author).

    Args:
        post_id: Post identifier
        user_id: ID of user requesting deletion
        service: Community service

    Returns:
        Deletion confirmation

    Raises:
        HTTPException: If post not found or unauthorized
    """
    try:
        return await service.delete_post(post_id, user_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)


@router.post("/posts/{post_id}/like", response_model=LikeResponse)
async def toggle_post_like(
    post_id: str,
    service: Annotated[CommunityService, Depends(get_community_service)],
    user_id: str = Query(..., description="User ID toggling like"),
) -> LikeResponse:
    """Toggle like on a post (like if not liked, unlike if already liked).

    Args:
        post_id: Post identifier
        user_id: ID of user toggling like
        service: Community service

    Returns:
        Like action result with new like count

    Raises:
        HTTPException: If post not found
    """
    try:
        return await service.toggle_post_like(post_id, user_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


# Comment Endpoints
@router.post(
    "/posts/{post_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    post_id: str,
    data: CommentCreate,
    service: Annotated[CommunityService, Depends(get_community_service)],
    user_id: str = Query(..., description="User ID creating comment"),
) -> CommentResponse:
    """Create a comment on a post.

    Args:
        post_id: Post identifier
        data: Comment content and optional parent_comment_id for replies
        user_id: ID of user creating comment
        service: Community service

    Returns:
        Created comment with author info

    Raises:
        HTTPException: If post or parent comment not found
    """
    try:
        return await service.create_comment(post_id, user_id, data)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get("/posts/{post_id}/comments", response_model=list[CommentResponse])
async def get_post_comments(
    post_id: str,
    db: DatabaseSession,
    service: Annotated[CommunityService, Depends(get_community_service)],
    current_user: Annotated[dict | None, Depends(get_current_user)] = None,
) -> list[CommentResponse]:
    """Get all comments for a post with nested replies and like status.

    Args:
        post_id: Post identifier
        current_user: Current authenticated user (optional)
        service: Community service

    Returns:
        List of root-level comments with nested replies and like status
    """
    current_user_id = current_user["id"] if current_user else None
    return await service.get_post_comments(post_id, current_user_id=current_user_id)


@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: str,
    data: CommentUpdate,
    service: Annotated[CommunityService, Depends(get_community_service)],
    user_id: str = Query(..., description="User ID requesting update"),
) -> CommentResponse:
    """Update a comment (only by author).

    Args:
        comment_id: Comment identifier
        data: Updated comment content
        user_id: ID of user requesting update
        service: Community service

    Returns:
        Updated comment

    Raises:
        HTTPException: If comment not found or unauthorized
    """
    try:
        return await service.update_comment(comment_id, user_id, data)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)


@router.delete("/comments/{comment_id}", status_code=status.HTTP_200_OK)
async def delete_comment(
    comment_id: str,
    service: Annotated[CommunityService, Depends(get_community_service)],
    user_id: str = Query(..., description="User ID requesting deletion"),
) -> dict:
    """Delete a comment (only by author).

    Args:
        comment_id: Comment identifier
        user_id: ID of user requesting deletion
        service: Community service

    Returns:
        Deletion confirmation

    Raises:
        HTTPException: If comment not found or unauthorized
    """
    try:
        return await service.delete_comment(comment_id, user_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)


@router.post("/comments/{comment_id}/like", response_model=LikeResponse)
async def toggle_comment_like(
    comment_id: str,
    service: Annotated[CommunityService, Depends(get_community_service)],
    user_id: str = Query(..., description="User ID toggling like"),
) -> LikeResponse:
    """Toggle like on a comment (like if not liked, unlike if already liked).

    Args:
        comment_id: Comment identifier
        user_id: ID of user toggling like
        service: Community service

    Returns:
        Like action result with new like count

    Raises:
        HTTPException: If comment not found
    """
    try:
        return await service.toggle_comment_like(comment_id, user_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.post("/posts/{post_id}/read", status_code=status.HTTP_200_OK)
async def mark_post_as_read(
    post_id: str,
    service: Annotated[CommunityService, Depends(get_community_service)],
    user_id: str = Query(..., description="User ID marking post as read"),
) -> dict:
    """Mark a post as read by a user.

    Args:
        post_id: Post identifier
        user_id: ID of user marking post as read
        service: Community service

    Returns:
        Status confirmation

    Raises:
        HTTPException: If post not found
    """
    try:
        return await service.mark_post_as_read(post_id, user_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
