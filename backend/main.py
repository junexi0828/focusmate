"""Main FastAPI application entry point.

Fully restored and optimized version for production on NAS.
"""

import sys
import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

# 1. CRITICAL: Absolute Path setup
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.gzip import GZipMiddleware

# Core application components
from app.api.v1.router import api_router
from app.core.config import settings
from app.infrastructure.database.session import close_db
from app.infrastructure.redis.pubsub_manager import redis_pubsub_manager
from app.infrastructure.websocket.notification_manager import notification_ws_manager

# Configure logging
logging.basicConfig(
    level=settings.APP_LOG_LEVEL.upper(),
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages application startup and shutdown events."""
    logger.info("🚀 Starting Focus Mate Backend...")
    logger.info(f"📍 Environment: {settings.APP_ENV}")

    # Initialize Redis Pub/Sub (Main Event Bus)
    try:
        await redis_pubsub_manager.connect()
        await redis_pubsub_manager.start_listener()
        logger.info("✅ Redis Pub/Sub connected and listener started")
    except Exception:
        logger.exception("⚠️ Redis Pub/Sub initialization failed")

    # Start Background Workers (Restored!)
    try:
        from app.infrastructure.tasks.redis_timer_listener import timer_listener
        from app.infrastructure.tasks.reservation_notifications import notification_worker

        # Start background tasks
        await timer_listener.start()
        await notification_worker.start()
        logger.info("✅ Background workers (Timer/Notifications) started")
    except Exception:
        logger.exception("⚠️ Background workers failed to start")

    yield

    # Shutdown
    logger.info("🛑 Stopping Focus Mate Backend...")
    # Stop background workers first
    try:
        from app.infrastructure.tasks.redis_timer_listener import timer_listener
        from app.infrastructure.tasks.reservation_notifications import notification_worker
        await timer_listener.stop()
        await notification_worker.stop()
    except Exception:
        pass

    await redis_pubsub_manager.disconnect()
    await notification_ws_manager.disconnect()
    await close_db()
    logger.info("👋 Focus Mate Backend stopped")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
    docs_url="/docs" if settings.APP_DEBUG else None,
)

# Middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=list(settings.TRUSTED_HOSTS))

if settings.CORS_ORIGINS:
    origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [str(settings.CORS_ORIGINS)]
    allow_methods = ["*"]
    allow_headers = ["*"]
    if settings.APP_ENV == "production":
        allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
        allow_headers = ["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).rstrip("/") for origin in origins],
        allow_credentials=True,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
        expose_headers=["Content-Disposition"],
    )

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="focusmate_session",
    max_age=3600 * 24 * 7,
    same_site="lax",
    https_only=settings.APP_ENV == "production",
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Routers
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Focus Mate API Running", "env": settings.APP_ENV}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "mode": "production"}
