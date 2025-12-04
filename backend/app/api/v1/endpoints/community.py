"""Community API endpoints - posts, comments, likes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

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
    PostUpdate,
)
from app.domain.community.service import CommunityService
from app.infrastructure.database.session import DatabaseSession
from app.infrastructure.repositories.community_repository import (
    CommentLikeRepository,
    CommentRepository,
    PostLikeRepository,
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
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> CommunityService:
    """Get community service."""
    return CommunityService(
        post_repo, comment_repo, post_like_repo, comment_like_repo, user_repo
    )


# Post Endpoints
@router.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    data: PostCreate,
    user_id: str = Query(..., description="User ID creating the post"),
    service: Annotated[CommunityService, Depends(get_community_service)] = None,
) -> PostResponse:
    """Create a new community post.

    Args:
        data: Post details (title, content, category)
        user_id: ID of the user creating the post
        service: Community service

    Returns:
        Created post with author info
    """
    return await service.create_post(user_id, data)


@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: str,
    service: Annotated[CommunityService, Depends(get_community_service)],
) -> PostResponse:
    """Get a specific post by ID.

    Args:
        post_id: Post identifier
        service: Community service

    Returns:
        Post details with author info

    Raises:
        HTTPException: If post not found
    """
    try:
        return await service.get_post(post_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get("/posts", response_model=PostListResult)
async def get_posts(
    category: str | None = Query(None, description="Filter by category"),
    user_id: str | None = Query(None, description="Filter by user ID"),
    search: str | None = Query(None, description="Search in title and content"),
    limit: int = Query(20, ge=1, le=100, description="Number of posts to return"),
    offset: int = Query(0, ge=0, description="Number of posts to skip"),
    service: Annotated[CommunityService, Depends(get_community_service)] = None,
) -> PostListResult:
    """Get posts with optional filters and pagination.

    Args:
        category: Optional category filter
        user_id: Optional user ID filter
        search: Optional search query
        limit: Maximum number of posts to return
        offset: Number of posts to skip
        service: Community service

    Returns:
        Paginated list of posts with total count
    """
    filters = PostFilters(
        category=category,
        user_id=user_id,
        search=search,
        limit=limit,
        offset=offset,
    )
    return await service.get_posts(filters)


@router.put("/posts/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: str,
    data: PostUpdate,
    user_id: str = Query(..., description="User ID requesting update"),
    service: Annotated[CommunityService, Depends(get_community_service)] = None,
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
    user_id: str = Query(..., description="User ID requesting deletion"),
    service: Annotated[CommunityService, Depends(get_community_service)] = None,
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
    user_id: str = Query(..., description="User ID toggling like"),
    service: Annotated[CommunityService, Depends(get_community_service)] = None,
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
    user_id: str = Query(..., description="User ID creating comment"),
    service: Annotated[CommunityService, Depends(get_community_service)] = None,
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
    service: Annotated[CommunityService, Depends(get_community_service)],
) -> list[CommentResponse]:
    """Get all comments for a post with nested replies.

    Args:
        post_id: Post identifier
        service: Community service

    Returns:
        List of root-level comments with nested replies
    """
    return await service.get_post_comments(post_id)


@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: str,
    data: CommentUpdate,
    user_id: str = Query(..., description="User ID requesting update"),
    service: Annotated[CommunityService, Depends(get_community_service)] = None,
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
    user_id: str = Query(..., description="User ID requesting deletion"),
    service: Annotated[CommunityService, Depends(get_community_service)] = None,
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
    user_id: str = Query(..., description="User ID toggling like"),
    service: Annotated[CommunityService, Depends(get_community_service)] = None,
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
