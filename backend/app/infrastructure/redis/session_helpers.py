"""Redis helpers for session management with fault isolation.

Production-grade session tracking with:
- Circuit Breaker pattern for fault isolation
- Exponential backoff retry logic
- Graceful degradation on failures
- Comprehensive logging and metrics
"""

import asyncio
import json
import logging
from datetime import datetime, UTC
from typing import Any

from app.infrastructure.redis.client import get_redis
from app.infrastructure.redis.circuit_breaker import RedisCircuitBreaker, CircuitOpenError

logger = logging.getLogger(__name__)

# Module-level circuit breaker instance (shared across all operations)
_circuit_breaker = RedisCircuitBreaker(
    failure_threshold=5,
    recovery_timeout=30,
    success_threshold=2,
)


async def store_token_mapping(user_id: str, token_id: str) -> None:
    """Store user_id -> token_id mapping for WebSocket auth.

    Args:
        user_id: User identifier
        token_id: Refresh token identifier

    Raises:
        Exception: If Redis operation fails after retries
    """
    try:
        await _circuit_breaker.call(_store_token_mapping_impl, user_id, token_id)
    except CircuitOpenError:
        logger.warning(
            f"[Session] Circuit open, skipping token mapping for user {user_id}"
        )
        raise
    except Exception as e:
        logger.error(f"[Session] Failed to store token mapping for user {user_id}: {e}")
        raise


async def _store_token_mapping_impl(user_id: str, token_id: str) -> None:
    """Internal implementation with retry logic."""
    redis = await get_redis()
    redis_key = f"session:token_map:{user_id}"

    # Retry with exponential backoff: 1s, 2s, 4s
    for attempt in range(3):
        try:
            await redis.set(redis_key, token_id)
            logger.debug(f"[Session] Token mapping stored for user {user_id}")
            return
        except Exception as e:
            if attempt == 2:  # Last attempt
                raise
            wait_time = 2 ** attempt
            logger.warning(
                f"[Session] Retry {attempt + 1}/3 for store_token_mapping "
                f"after {wait_time}s: {e}"
            )
            await asyncio.sleep(wait_time)


async def get_token_id(user_id: str) -> str | None:
    """Get the latest token_id for a user with circuit breaker protection.

    Args:
        user_id: User identifier

    Returns:
        Token ID if found, None if not found or on failure
    """
    try:
        return await _circuit_breaker.call(_get_token_id_impl, user_id)
    except CircuitOpenError:
        logger.warning(
            f"[Session] Circuit open, skipping token_id lookup for user {user_id}"
        )
        return None
    except Exception as e:
        logger.error(f"[Session] Failed to get token_id for user {user_id}: {e}")
        return None


async def _get_token_id_impl(user_id: str) -> str | None:
    """Internal implementation with retry logic."""
    redis = await get_redis()
    redis_key = f"session:token_map:{user_id}"

    # Retry with exponential backoff: 1s, 2s, 4s
    for attempt in range(3):
        try:
            result = await redis.get(redis_key)
            if result:
                logger.debug(f"[Session] Token ID retrieved for user {user_id}")
            return result
        except Exception as e:
            if attempt == 2:  # Last attempt
                raise
            wait_time = 2 ** attempt
            logger.warning(
                f"[Session] Retry {attempt + 1}/3 for get_token_id "
                f"after {wait_time}s: {e}"
            )
            await asyncio.sleep(wait_time)


async def track_user_activity(
    user_id: str,
    token_id: str,
    room_id: str | None = None
) -> None:
    """Track user activity and extend session TTL with circuit breaker protection.

    Args:
        user_id: User identifier
        token_id: Refresh token identifier (for per-device tracking)
        room_id: Optional room identifier
    """
    try:
        await _circuit_breaker.call(_track_user_activity_impl, user_id, token_id, room_id)
    except CircuitOpenError:
        logger.debug(
            f"[Session] Circuit open, skipping activity tracking for user {user_id}"
        )
        # Graceful degradation - don't raise, just skip tracking
    except Exception as e:
        logger.warning(
            f"[Session] Failed to track activity for user {user_id}: {e}"
        )
        # Graceful degradation - don't raise, just skip tracking


async def _track_user_activity_impl(
    user_id: str,
    token_id: str,
    room_id: str | None = None
) -> None:
    """Internal implementation with retry logic."""
    redis = await get_redis()
    redis_key = f"session:active:{user_id}:{token_id}"

    value = {
        "last_seen": datetime.now(UTC).isoformat(),
        "room_id": room_id
    }

    # Retry with exponential backoff: 1s, 2s, 4s
    for attempt in range(3):
        try:
            # Set with 1 hour TTL (sliding window)
            await redis.setex(redis_key, 3600, json.dumps(value))
            logger.debug(
                f"[Session] Activity tracked for user {user_id} "
                f"in room {room_id or 'N/A'}"
            )
            return
        except Exception as e:
            if attempt == 2:  # Last attempt
                raise
            wait_time = 2 ** attempt
            logger.warning(
                f"[Session] Retry {attempt + 1}/3 for track_user_activity "
                f"after {wait_time}s: {e}"
            )
            await asyncio.sleep(wait_time)


async def check_user_activity(user_id: str, token_id: str) -> bool:
    """Check if user has recent activity with circuit breaker protection.

    Args:
        user_id: User identifier
        token_id: Refresh token identifier

    Returns:
        True if session is active (within last hour), False otherwise or on failure
    """
    try:
        return await _circuit_breaker.call(_check_user_activity_impl, user_id, token_id)
    except CircuitOpenError:
        logger.warning(
            f"[Session] Circuit open, assuming no activity for user {user_id}"
        )
        return False
    except Exception as e:
        logger.error(
            f"[Session] Failed to check activity for user {user_id}: {e}"
        )
        return False


async def _check_user_activity_impl(user_id: str, token_id: str) -> bool:
    """Internal implementation with retry logic."""
    redis = await get_redis()
    redis_key = f"session:active:{user_id}:{token_id}"

    # Retry with exponential backoff: 1s, 2s, 4s
    for attempt in range(3):
        try:
            result = await redis.exists(redis_key) > 0
            logger.debug(
                f"[Session] Activity check for user {user_id}: "
                f"{'active' if result else 'inactive'}"
            )
            return result
        except Exception as e:
            if attempt == 2:  # Last attempt
                raise
            wait_time = 2 ** attempt
            logger.warning(
                f"[Session] Retry {attempt + 1}/3 for check_user_activity "
                f"after {wait_time}s: {e}"
            )
            await asyncio.sleep(wait_time)


async def clear_user_activity(user_id: str, token_id: str) -> None:
    """Clear user activity (on logout) with circuit breaker protection.

    Args:
        user_id: User identifier
        token_id: Refresh token identifier
    """
    try:
        await _circuit_breaker.call(_clear_user_activity_impl, user_id, token_id)
    except CircuitOpenError:
        logger.warning(
            f"[Session] Circuit open, skipping activity clear for user {user_id}"
        )
        # Graceful degradation - activity will expire naturally
    except Exception as e:
        logger.warning(
            f"[Session] Failed to clear activity for user {user_id}: {e}"
        )
        # Graceful degradation - activity will expire naturally


async def _clear_user_activity_impl(user_id: str, token_id: str) -> None:
    """Internal implementation with retry logic."""
    redis = await get_redis()
    redis_key = f"session:active:{user_id}:{token_id}"

    # Retry with exponential backoff: 1s, 2s, 4s
    for attempt in range(3):
        try:
            await redis.delete(redis_key)
            logger.debug(f"[Session] Activity cleared for user {user_id}")
            return
        except Exception as e:
            if attempt == 2:  # Last attempt
                raise
            wait_time = 2 ** attempt
            logger.warning(
                f"[Session] Retry {attempt + 1}/3 for clear_user_activity "
                f"after {wait_time}s: {e}"
            )
            await asyncio.sleep(wait_time)


def get_circuit_breaker_stats() -> dict[str, Any]:
    """Get circuit breaker statistics for monitoring.

    Returns:
        Dictionary with circuit breaker state and metrics
    """
    return _circuit_breaker.get_stats()

