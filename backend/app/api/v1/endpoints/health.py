"""Health check endpoints for monitoring system status.

Provides endpoints for:
- Overall system health
- Component-specific health (Redis, Database)
- Circuit breaker status
- Session tracking metrics
"""

import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import get_db
from app.infrastructure.redis.client import health_check as redis_health_check
from app.infrastructure.redis.session_helpers import get_circuit_breaker_stats

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)) -> dict:
    """Overall system health check.

    Returns:
        Dictionary with overall status and component health
    """
    # Check Redis
    redis_healthy = await redis_health_check()

    # Check Database
    db_healthy = True
    try:
        await db.execute("SELECT 1")
    except Exception as e:
        logger.error(f"[Health] Database check failed: {e}")
        db_healthy = False

    # Get circuit breaker stats
    circuit_stats = get_circuit_breaker_stats()

    # Determine overall status
    overall_status = "healthy"
    if not redis_healthy or not db_healthy:
        overall_status = "degraded"
    if not db_healthy:
        overall_status = "unhealthy"

    return {
        "status": overall_status,
        "components": {
            "database": {
                "status": "up" if db_healthy else "down",
                "critical": True,
            },
            "redis": {
                "status": "up" if redis_healthy else "down",
                "critical": False,
            },
            "circuit_breaker": {
                "state": circuit_stats["state"],
                "failure_count": circuit_stats["failure_count"],
                "success_rate": circuit_stats["success_rate"],
                "circuit_open_count": circuit_stats["circuit_open_count"],
            },
        },
    }


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
