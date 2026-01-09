"""Redis client helper for session management.

Production-grade Redis client with:
- Connection pooling for high concurrency
- Socket timeouts to prevent hanging
- Retry logic for transient failures
- Health check for monitoring
"""

import logging
import redis.asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger(__name__)

_redis_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    """Get a shared Redis client instance with connection pooling.

    Configuration:
        - Max connections: 10 (supports high concurrency)
        - Socket timeout: 5s (prevents hanging)
        - Retry on timeout: True (handles transient failures)

    Returns:
        Configured Redis client instance

    Raises:
        redis.ConnectionError: If unable to connect to Redis
    """
    global _redis_client
    if _redis_client is None:
        try:
            # Create Redis client with production-optimized settings
            # connection_pool is created automatically by from_url
            _redis_client = await aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=50,  # Increased for higher concurrency
                socket_timeout=1.0,  # Fail fast (1s)
                socket_connect_timeout=1.0,  # Fail fast on connect (1s)
                retry_on_timeout=True,
                health_check_interval=30,
            )
            logger.info(f"[Redis Client] Connected to {settings.REDIS_URL}")
        except Exception as e:
            logger.error(f"[Redis Client] Failed to initialize: {e}")
            raise
    return _redis_client


async def health_check() -> bool:
    """Check Redis connection health.

    Returns:
        True if Redis is reachable and responding, False otherwise
    """
    try:
        redis = await get_redis()
        result = await redis.ping()
        logger.debug("[Redis Client] Health check: OK")
        return result
    except Exception as e:
        logger.warning(f"[Redis Client] Health check failed: {e}")
        return False


async def close_redis() -> None:
    """Close Redis connection pool.

    Should be called on application shutdown.
    """
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
        logger.info("[Redis Client] Connection pool closed")
