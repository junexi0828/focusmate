"""Main FastAPI application entry point.

This module initializes the FastAPI app, sets up middleware,
includes API routers, and defines the application lifespan.
"""

import sys
import os
import logging
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

# Force add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.gzip import GZipMiddleware

# Use relative imports or be very careful with absolute ones in multiprocessing
from .api.v1.api import api_router
from .core.config import settings
from .infrastructure.database.session import close_db
from .infrastructure.redis.pubsub_manager import redis_pubsub_manager
from .infrastructure.websocket.notification_manager import notification_ws_manager

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
        # Keep listener disabled for now to confirm 0% CPU
        # await redis_pubsub_manager.start_listener()
        logger.info("✅ Redis Pub/Sub connected (Listener disabled temporarily)")
    except Exception:
        logger.exception("⚠️ Redis Pub/Sub initialization failed")

    # In production/staging, we skip init_db() as requested
    if settings.APP_ENV not in {"production", "staging"}:
        try:
            from .infrastructure.database.session import init_db
            await init_db()
            logger.info("✅ Database initialized for development")
        except Exception:
            logger.exception("⚠️ Database initialization failed")
    else:
        logger.info("✅ Database ready (using Alembic migrations in production)")

    yield

    # Shutdown logic
    logger.info("🛑 Stopping Focus Mate Backend...")

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
)

# Trust Proxy Headers
app.add_middleware(TrustedHostMiddleware, allowed_hosts=list(settings.TRUSTED_HOSTS))

# CORS Middleware
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

# Session Middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="focusmate_session",
    max_age=3600 * 24 * 7,
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
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "environment": settings.APP_ENV}
