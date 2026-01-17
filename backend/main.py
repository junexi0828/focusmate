"""Main FastAPI application entry point.

RESTORATION STEP 1: Enabling Redis Pub/Sub (Main Bus) only.
"""

import sys
import os
import logging
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

# 1. Absolute Path setup
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

# Configure logging
logging.basicConfig(
    level=settings.APP_LOG_LEVEL.upper(),
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages application startup and shutdown events."""
    logger.info("🚀 Starting Step 1 Restoration (Pub/Sub Enabled)...")
    logger.info(f"📍 Environment: {settings.APP_ENV}")

    # Initialize Redis Pub/Sub (Main Event Bus)
    try:
        await redis_pubsub_manager.connect()
        await redis_pubsub_manager.start_listener()
        logger.info("✅ Redis Pub/Sub connected and listener started")
    except Exception:
        logger.exception("⚠️ Redis Pub/Sub initialization failed")

    yield

    # Shutdown
    logger.info("🛑 Stopping Focus Mate Backend...")
    await redis_pubsub_manager.disconnect()
    await close_db()
    logger.info("👋 Focus Mate Backend stopped")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    openapi_url=f"/api/v1/openapi.json",
    lifespan=lifespan,
    docs_url="/docs" if settings.APP_DEBUG else None,
)

# Middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=list(settings.TRUSTED_HOSTS))

if settings.CORS_ORIGINS:
    origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [str(settings.CORS_ORIGINS)]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).rstrip("/") for origin in origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="focusmate_session",
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Routers
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Focus Mate Step 1 Running (Pub/Sub Enabled)"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "mode": "restoration-step-1"}
