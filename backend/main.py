"""Main FastAPI application entry point.

This module initializes the FastAPI app, sets up middleware,
includes API routers, and defines the application lifespan.
"""

import sys
import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

# 1. CRITICAL: Path configuration for NAS and multiprocessing compatibility
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

print(f"DIAGNOSTIC: PROJECT_ROOT={PROJECT_ROOT}")
print(f"DIAGNOSTIC: sys.path={sys.path}")
print(f"DIAGNOSTIC: os.listdir={os.listdir(PROJECT_ROOT)}")

# 2. Imports (Absolute imports are preferred after path setup)
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
    logger.info(f"📍 Project Root: {PROJECT_ROOT}")
    logger.info(f"📍 Python Path: {sys.path[:3]}...")

    # Initialize Redis Pub/Sub (Main Event Bus)
    try:
        await redis_pubsub_manager.connect()
        # Keep listener disabled for the very first stable deployment
        # await redis_pubsub_manager.start_listener()
        logger.info("✅ Redis Pub/Sub connected")
    except Exception:
        logger.exception("⚠️ Redis Pub/Sub connection failed")

    # DB readiness check (skip auto-migrations in production as requested)
    if settings.APP_ENV not in {"production", "staging"}:
        try:
            from app.infrastructure.database.session import init_db
            await init_db()
            logger.info("✅ Database initialized (dev mode)")
        except Exception:
            logger.exception("⚠️ Database initialization failed")
    else:
        logger.info("✅ Database ready (migrations managed by Alembic)")

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

# Middleware setup
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
    return {"status": "healthy"}
