"""Focus Mate Backend - FastAPI Application Entry Point.

ISO/IEC 25010 Quality Standards Compliant.
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.middleware.rate_limit import RateLimitMiddleware
from app.api.middleware.request_logging import RequestLoggingMiddleware
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import AppException
from app.infrastructure.database.session import close_db, init_db
from app.infrastructure.redis.pubsub_manager import redis_pubsub_manager


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager.

    Handles startup and shutdown events.
    """
    logger = logging.getLogger("app")
    # Startup
    logger.info("🚀 Starting Focus Mate Backend...")
    logger.info("📍 Environment: %s", settings.APP_ENV)
    logger.info("🗄️ Database: %s", settings.DATABASE_URL.split("://")[0])

    if settings.DEV_RESET_DB and settings.is_development:
        logger.warning("⚠️ Resetting database (development only)...")

    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")

    # Initialize Redis Pub/Sub
    try:
        await redis_pubsub_manager.connect()
        await redis_pubsub_manager.start_listener()
        logger.info("✅ Redis Pub/Sub initialized")
    except Exception:
        logger.exception("⚠️ Redis Pub/Sub initialization failed")

    yield

    # Shutdown
    logger.info("🛑 Shutting down Focus Mate Backend...")

    # Disconnect Redis
    try:
        await redis_pubsub_manager.disconnect()
        logger.info("✅ Redis Pub/Sub disconnected")
    except Exception:
        logger.exception("⚠️ Error disconnecting Redis")

    await close_db()
    logger.info("✅ Database connections closed")


# Create FastAPI application
# redirect_slashes=False prevents automatic redirects that can cause CORS issues
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="High-Assurance Team Pomodoro Platform - ISO/IEC 25010 Compliant",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    redirect_slashes=False,  # Disable automatic trailing slash redirects to prevent CORS issues
)

# Request logging middleware - adds request ID and logs requests
# Should be added early to track all requests
app.add_middleware(
    RequestLoggingMiddleware,
    log_request_body=False,  # Set to True for debugging (security risk)
    log_response_body=False,  # Set to True for debugging (performance impact)
    exclude_paths=["/health", "/docs", "/redoc", "/openapi.json"],
)

# GZip middleware - compresses responses for bandwidth optimization
# Should be added first to compress all responses
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,  # Only compress responses larger than 1KB
    compresslevel=6,  # Compression level (1-9, default 6 for balance)
)

# Trusted Host middleware - protects against Host header attacks
# In production, only allow specific domains
if not settings.is_development:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.TRUSTED_HOSTS,
    )

# Rate limiting middleware - should be added before CORS
# Protects against brute force attacks and API abuse
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=60,  # Default: 60 requests per minute
    exempt_paths=["/health", "/docs", "/redoc", "/openapi.json"],
)

# CORS middleware - must be added before routes
# This ensures OPTIONS preflight requests are handled correctly
# Allow ngrok URLs in development using regex pattern
ngrok_regex = r"https://.*\.ngrok(-free)?\.(app|io)"
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=ngrok_regex if settings.is_development else None,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],  # Allow all headers including Authorization
    expose_headers=["*"],  # Expose all headers
    max_age=3600,  # Cache preflight requests for 1 hour
)


# Exception handler for custom exceptions
@app.exception_handler(AppException)
async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
    """Handle custom application exceptions."""
    return JSONResponse(
        status_code=400,
        content={
            "status": "error",
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        },
    )


# Health check endpoint
@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
    }


# Include API router
app.include_router(api_router, prefix="/api/v1")

# Mount static files for uploads
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)

# Mount chat uploads
chat_uploads_dir = uploads_dir / "chat"
chat_uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount(
    "/uploads/chat", StaticFiles(directory=str(chat_uploads_dir)), name="chat_uploads"
)

# Mount verification uploads
verification_uploads_dir = uploads_dir / "verification"
verification_uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount(
    "/uploads/verification",
    StaticFiles(directory=str(verification_uploads_dir)),
    name="verification_uploads",
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.APP_LOG_LEVEL.lower(),
    )
