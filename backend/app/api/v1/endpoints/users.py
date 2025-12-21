"""User search and profile API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select

from app.api.deps import DatabaseSession, get_current_user_required
from app.infrastructure.database.models.user import User


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/search")
async def search_users(
    current_user: Annotated[dict, Depends(get_current_user_required)],
    db: DatabaseSession,
    query: str = Query(
        ..., min_length=1, description="Search query (username or email)"
    ),
    limit: int = Query(10, ge=1, le=50, description="Max results"),
) -> dict:
    """Search users by username or email.

    Args:
        query: Search query (username or email)
        limit: Maximum number of results
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of matching users
    """
    # Search by username or email
    stmt = (
        select(User)
        .where(or_(User.username.ilike(f"%{query}%"), User.email.ilike(f"%{query}%")))
        .limit(limit)
    )

    result = await db.execute(stmt)
    users = result.scalars().all()

    return {
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "bio": user.bio,
                "profile_image": user.profile_image,
            }
            for user in users
            if user.id != current_user["id"]  # Exclude current user
        ],
        "total": len(users),
    }


@router.get("/me")
async def get_current_user_profile(
    current_user: Annotated[dict, Depends(get_current_user_required)],
    db: DatabaseSession,
) -> dict:
    """Get current user's full profile including ID.

    Returns:
        Current user's profile with all details including ID
    """
    stmt = select(User).where(User.id == current_user["id"])
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        return current_user

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "bio": user.bio,
        "school": user.school,
        "profile_image": user.profile_image,
        "is_verified": user.is_verified,
        "total_focus_time": user.total_focus_time,
        "total_sessions": user.total_sessions,
    }
