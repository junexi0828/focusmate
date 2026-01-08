"""Redis helpers for session management."""

import json
from datetime import datetime, UTC
from typing import Any

from app.infrastructure.redis.client import get_redis


async def store_token_mapping(user_id: str, token_id: str) -> None:
    """Store user_id -> token_id mapping for WebSocket auth."""
    redis = await get_redis()
    redis_key = f"session:token_map:{user_id}"
    await redis.set(redis_key, token_id)


async def get_token_id(user_id: str) -> str | None:
    """Get the latest token_id for a user."""
    redis = await get_redis()
    redis_key = f"session:token_map:{user_id}"
    return await redis.get(redis_key)


async def track_user_activity(
    user_id: str,
    token_id: str,
    room_id: str | None = None
) -> None:
    """Track user activity and extend session TTL.

    Args:
        user_id: User identifier
        token_id: Refresh token identifier (for per-device tracking)
        room_id: Optional room identifier
    """
    redis = await get_redis()
    redis_key = f"session:active:{user_id}:{token_id}"

    value = {
        "last_seen": datetime.now(UTC).isoformat(),
        "room_id": room_id
    }

    # Set with 1 hour TTL (sliding window)
    await redis.setex(redis_key, 3600, json.dumps(value))


async def check_user_activity(user_id: str, token_id: str) -> bool:
    """Check if user has recent activity.

    Args:
        user_id: User identifier
        token_id: Refresh token identifier

    Returns:
        True if session is active (within last hour)
    """
    redis = await get_redis()
    redis_key = f"session:active:{user_id}:{token_id}"

    return await redis.exists(redis_key) > 0


async def clear_user_activity(user_id: str, token_id: str) -> None:
    """Clear user activity (on logout).

    Args:
        user_id: User identifier
        token_id: Refresh token identifier
    """
    redis = await get_redis()
    redis_key = f"session:active:{user_id}:{token_id}"

    await redis.delete(redis_key)
