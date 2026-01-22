"""Redis cache helpers for lightweight room chat."""

from __future__ import annotations

import json
import logging

from app.infrastructure.redis.client import get_redis


logger = logging.getLogger(__name__)

DEFAULT_MESSAGE_LIMIT = 50
DEFAULT_TTL_SECONDS = 60 * 60 * 2


def _room_chat_key(room_id: str) -> str:
    return f"focus:room:{room_id}:chat"


async def append_message(
    room_id: str,
    message: dict,
    *,
    limit: int = DEFAULT_MESSAGE_LIMIT,
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
) -> None:
    """Append a message and keep only the most recent items."""
    try:
        redis = await get_redis()
        key = _room_chat_key(room_id)
        payload = json.dumps(message)
        await redis.lpush(key, payload)
        await redis.ltrim(key, 0, max(0, limit - 1))
        await redis.expire(key, ttl_seconds)
    except Exception as exc:
        logger.debug("Room chat cache append failed: %s", exc)


async def get_recent_messages(
    room_id: str,
    *,
    limit: int = DEFAULT_MESSAGE_LIMIT,
) -> list[dict]:
    """Fetch recent messages in chronological order (oldest first)."""
    try:
        redis = await get_redis()
        key = _room_chat_key(room_id)
        raw_items = await redis.lrange(key, 0, max(0, limit - 1))
        messages = []
        for raw in raw_items:
            try:
                messages.append(json.loads(raw))
            except json.JSONDecodeError:
                continue
        messages.reverse()
        return messages
    except Exception as exc:
        logger.debug("Room chat cache fetch failed: %s", exc)
        return []

