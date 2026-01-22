"""Health check endpoints for monitoring system status.

Provides endpoints for:
- Overall system health
- Component-specific health (Redis, Database)
- Circuit breaker status
- Session tracking metrics
"""

import logging
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import get_db
from app.infrastructure.redis.client import health_check as redis_health_check
from app.infrastructure.redis.session_helpers import get_circuit_breaker_stats

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Overall system health check.

    Returns:
        Dictionary with overall status and component health
    """
    from app.core.config import settings
    from sqlalchemy import text
    from fastapi import status

    health_status = {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "components": {
            "database": "unknown",
            "redis": "unknown",
        },
    }

    is_healthy = True

    # Check Redis
    redis_healthy = await redis_health_check()
    health_status["components"]["redis"] = "connected" if redis_healthy else "disconnected"
    if not redis_healthy:
        is_healthy = False

    # Check Database
    try:
        await db.execute(text("SELECT 1"))
        health_status["components"]["database"] = "connected"
    except Exception as e:
        logger.error(f"[Health] Database check failed: {e}")
        health_status["components"]["database"] = f"error: {str(e)}"
        is_healthy = False

    # Get circuit breaker stats
    circuit_stats = get_circuit_breaker_stats()
    health_status["components"]["circuit_breaker"] = {
        "state": circuit_stats["state"],
        "failure_count": circuit_stats["failure_count"],
        "success_rate": circuit_stats["success_rate"],
    }

    # Determine overall status and HTTP code
    if not is_healthy:
        health_status["status"] = "degraded"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return health_status


@router.get("/health/redis")
async def redis_health() -> dict:
    """Redis-specific health check.

    Returns:
        Dictionary with Redis health status
    """
    is_healthy = await redis_health_check()

    return {
        "status": "up" if is_healthy else "down",
        "message": "Redis is reachable" if is_healthy else "Redis is unreachable",
    }


@router.get("/health/database")
async def database_health(db: AsyncSession = Depends(get_db)) -> dict:
    """Database-specific health check.

    Returns:
        Dictionary with database health status
    """
    try:
        await db.execute("SELECT 1")
        return {
            "status": "up",
            "message": "Database is reachable",
        }
    except Exception as e:
        logger.error(f"[Health] Database check failed: {e}")
        return {
            "status": "down",
            "message": f"Database is unreachable: {str(e)}",
        }


@router.get("/metrics/session")
async def session_metrics() -> dict:
    """Session tracking metrics.

    Returns:
        Dictionary with circuit breaker statistics and session tracking metrics
    """
    stats = get_circuit_breaker_stats()

    return {
        "circuit_breaker": {
            "state": stats["state"],
            "uptime_seconds": stats["uptime_seconds"],
        },
        "tracking": {
            "total_calls": stats["total_calls"],
            "total_successes": stats["total_successes"],
            "total_failures": stats["total_failures"],
            "success_rate": stats["success_rate"],
        },
        "failures": {
            "current_failure_count": stats["failure_count"],
            "circuit_open_count": stats["circuit_open_count"],
            "last_failure_time": stats["last_failure_time"],
            "time_until_retry": stats["time_until_retry"],
        },
    }
