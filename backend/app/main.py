"""Main FastAPI application entry point.

This module initializes the FastAPI app, sets up middleware,
includes API routers, and defines the application lifespan.
"""

import logging
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.gzip import GZipMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.infrastructure.database.session import close_db
from app.infrastructure.redis.pubsub_manager import redis_pubsub_manager
from app.infrastructure.websocket.notification_manager import notification_ws_manager

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s", "module": "%(module)s", "function": "%(funcName)s", "line": %(lineno)d}',
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages application startup and shutdown events."""
    logger.info("🚀 Starting Focus Mate Backend...")
    logger.info(f"📍 Environment: {settings.APP_ENV}")

    # Initialize Redis Pub/Sub (Chat/Global Events)
    try:
        await redis_pubsub_manager.connect()
        # Note: start_listener() is called after we have some initial subscriptions if needed,
        # but the current manager handles empty subscription state safely.
        await redis_pubsub_manager.start_listener()
        logger.info("✅ Redis Pub/Sub initialized")
    except Exception:
        logger.exception("⚠️ Redis Pub/Sub initialization failed")

    # Ensure database is connected (migrations are handled by Alembic in production)
    if settings.APP_ENV not in {"production", "staging"}:
        try:
            from app.infrastructure.database.session import init_db
            await init_db()
            logger.info("✅ Database initialized for development")
        except Exception:
            logger.exception("⚠️ Database initialization failed")
    else:
        logger.info("✅ Database ready (using Alembic migrations in production)")

    # Initialize background workers
    from app.infrastructure.tasks import (
        redis_timer_listener,
        reservation_notification_worker,
    )
    from app.core.notify import send_slack_notification

    # Send startup notification
    await send_slack_notification(
        message=f"🚀 FocusMate Backend Started ({settings.APP_ENV})",
        level="info"
    )

    listener_task = None
    fallback_scheduler = None
    notification_worker_task = None

    try:
        logger.info("🔄 Starting background tasks...")

        # 1. Redis Timer Listener
        await redis_timer_listener.connect()
        listener_task = asyncio.create_task(redis_timer_listener.listen())
        logger.info("✅ Redis Timer Listener started")

        # 2. Reservation Notification Worker
        notification_worker_task = asyncio.create_task(reservation_notification_worker.start())
        logger.info("✅ Reservation Notification Worker started")

    except Exception:
        logger.exception("⚠️ Background worker initialization failed")
        await send_slack_notification(
            message="⚠️ Background worker initialization failed",
            level="error"
        )

    # APScheduler Fallback for timers if Redis is not available
    if not redis_timer_listener.is_available():
        try:
            from apscheduler.schedulers.asyncio import AsyncIOScheduler
            from app.infrastructure.tasks.timer_cleanup_apscheduler import check_expired_timers

            fallback_scheduler = AsyncIOScheduler()
            fallback_scheduler.add_job(
                check_expired_timers,
                "interval",
                minutes=1,
                id="timer_cleanup_fallback",
                replace_existing=True,
            )
            fallback_scheduler.start()
            logger.info("✅ APScheduler fallback started (timer cleanup every 1 minute)")
        except Exception:
            logger.exception("⚠️ APScheduler fallback initialization failed")

    yield

    # Shutdown logic
    logger.info("🛑 Stopping Focus Mate Backend...")

    # Send shutdown notification
    await send_slack_notification(
        message=f"🛑 FocusMate Backend Stopped ({settings.APP_ENV})",
        level="warning"
    )

    if listener_task:
        await redis_timer_listener.stop()
        listener_task.cancel()
        try:
            await listener_task
        except asyncio.CancelledError:
            pass

    if notification_worker_task:
        await reservation_notification_worker.stop()
        notification_worker_task.cancel()
        try:
            await notification_worker_task
        except asyncio.CancelledError:
            pass

    if fallback_scheduler:
        fallback_scheduler.shutdown()

    await redis_pubsub_manager.disconnect()
    await notification_ws_manager.disconnect()
    await close_db()
    logger.info("👋 Focus Mate Backend stopped")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
    docs_url="/docs" if settings.APP_DEBUG else None,
    redoc_url="/redoc" if settings.APP_DEBUG else None,
)

# Trust Proxy Headers
app.add_middleware(TrustedHostMiddleware, allowed_hosts=list(settings.TRUSTED_HOSTS))

# CORS Middleware
if settings.CORS_ORIGINS:
    # Handle both string and list formats for flexibility
    origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [str(settings.CORS_ORIGINS)]

    # Enforce secure CORS policy in production
    allow_methods = ["*"]
    allow_headers = ["*"]

    if settings.APP_ENV == "production":
        # More explicit methods for production
        allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
        logger.warning(f"⚠️ CORS_ALLOW_METHODS='{settings.CORS_ALLOW_METHODS}' in production; enforcing explicit method allowlist")

        # Explicit headers for production
        allow_headers = ["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"]
        logger.warning(f"⚠️ CORS_ALLOW_HEADERS='{settings.CORS_ALLOW_HEADERS}' in production; enforcing explicit header allowlist")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).rstrip("/") for origin in origins],
        allow_credentials=True,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
        expose_headers=["Content-Disposition"],
    )

# Session Middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="focusmate_session",
    max_age=3600 * 24 * 7,  # 1 week
    same_site="lax",
    https_only=settings.APP_ENV == "production",
)

# GZip Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "version": settings.VERSION,
        "environment": settings.APP_ENV,
        "docs_url": "/docs" if settings.APP_DEBUG else "Disabled in production",
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "environment": settings.APP_ENV}
