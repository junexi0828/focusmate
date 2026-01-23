"""Focus Mate Backend - FastAPI Application Entry Point.

ISO/IEC 25010 Quality Standards Compliant.
"""

from typing import Any, Dict, Union
import re
import logging
import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from prometheus_fastapi_instrumentator import Instrumentator

from app.api.middleware.rate_limit import RateLimitMiddleware
from app.api.middleware.request_logging import RequestLoggingMiddleware, get_request_id
from app.api.middleware.security_headers import SecurityHeadersMiddleware
from app.api.middleware.slow_request import SlowRequestMiddleware
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import AppException
from app.core.logging_config import setup_logging
from app.infrastructure.database.session import close_db, init_db
from app.infrastructure.redis.pubsub_manager import redis_pubsub_manager

# 로깅 설정 초기화
setup_logging()
logger = logging.getLogger("app")

# Initialize Sentry
if settings.SENTRY_ENABLED and settings.SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        from sentry_sdk.integrations.redis import RedisIntegration

        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.APP_ENV,
            traces_sample_rate=1.0 if settings.is_development else 0.1,
            integrations=[
                FastApiIntegration(transaction_style="url"),
                SqlalchemyIntegration(),
                RedisIntegration(),
            ],
        )
        logging.getLogger("app").info("✅ Sentry initialized")
    except ImportError:
        logging.getLogger("app").warning("⚠️ sentry-sdk not installed, skipping Sentry init")
    except Exception as e:
        logging.getLogger("app").warning(f"⚠️ Sentry init failed: {e}")



@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager.

    Handles startup and shutdown events.
    """
    logger = logging.getLogger("app")
    logger.info("🚀 Starting Focus Mate Backend (gradual restoration)...")
    logger.info("📍 Environment: %s", settings.APP_ENV)

    # Initialize database
    if settings.is_development:
        await init_db()
        logger.info("✅ Database initialized (development)")
    else:
        logger.info("✅ Database ready (using Alembic migrations in production)")

    # Initialize Redis Pub/Sub
    await redis_pubsub_manager.connect()
    await redis_pubsub_manager.start_listener()
    logger.info("✅ Redis Pub/Sub initialized")

    logger.info("🔍 DEBUG: About to yield (with DB and Redis only)...")
    yield
    logger.info("🔍 DEBUG: Passed yield - shutting down...")

    # Shutdown
    logger.info("🛑 Shutting down Focus Mate Backend...")
    try:
        await redis_pubsub_manager.disconnect()
        logger.info("✅ Redis Pub/Sub disconnected")
    except Exception:
        logger.exception("⚠️ Error disconnecting Redis")

    await close_db()
    logger.info("✅ Database connections closed")

# ORIGINAL LIFESPAN (disabled for testing)
@asynccontextmanager
async def lifespan_ORIGINAL(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager.

    Handles startup and shutdown events.
    """
    logger = logging.getLogger("app")

    async def _cancel_task(task: asyncio.Task | None, task_name: str) -> None:
        if not task:
            return
        task.cancel()
        try:
            await task
            logger.info("✅ %s task stopped", task_name)
        except asyncio.CancelledError:
            logger.info("✅ %s task cancelled", task_name)
        except Exception:
            logger.exception("⚠️ Error stopping %s task", task_name)
    # Startup
    logger.info("🚀 Starting Focus Mate Backend...")
    logger.info("📍 Environment: %s", settings.APP_ENV)

    if settings.DEV_RESET_DB and settings.is_development:
        logger.warning("⚠️ Resetting database (development only)...")

    # Initialize database (only in development to avoid schema drift)
    # In production, use Alembic migrations instead
    if settings.is_development:
        await init_db()
        logger.info("✅ Database initialized (development mode)")
    else:
        logger.info("✅ Database ready (using Alembic migrations in production)")

    # Initialize Redis Pub/Sub
    try:
        await redis_pubsub_manager.connect()
        await redis_pubsub_manager.start_listener()
        logger.info("✅ Redis Pub/Sub initialized")
    except Exception as e:
        logger.warning(
            "⚠️ Redis Pub/Sub initialization failed: %s. "
            "Real-time chat synchronization will use fallback mode. "
            "To enable Redis Pub/Sub, ensure Redis is running at %s",
            str(e)[:100],
            settings.REDIS_URL
        )

    # Initialize Redis Timer Listener (TTL-based expiry)
    from app.infrastructure.tasks import (
        redis_timer_listener,
        reservation_notification_worker,
    )
    from app.core.notify import send_slack_notification

    # Send startup notification (non-blocking)
    asyncio.create_task(
        send_slack_notification(
            message=f"🚀 FocusMate Backend Started ({settings.APP_ENV})",
            level="info"
        )
    )

    listener_task = None
    fallback_scheduler = None

    # [DISABLED] Redis Timer Listener due to persistent blocking/hang issues with psubscribe.
    # We rely fully on APScheduler (running every 1 minute) for timer cleanup.
    # This guarantees stability over the potential (but fragile) speed of Redis notifications.
    logger.info("⚠️ Redis Timer Listener disabled (using APScheduler only)")

    # try:
    #     await asyncio.wait_for(redis_timer_listener.connect(), timeout=5.0)
    #     # Start listener in background task
    #     listener_task = asyncio.create_task(redis_timer_listener.listen())
    #     logger.info("✅ Redis Timer Listener started (real-time TTL-based expiry)")
    # except asyncio.TimeoutError:
    #     logger.warning(
    #         "⚠️ Redis Timer Listener connection timeout after 5s. "
    #         "Continuing with APScheduler safety net."
    #     )
    # except Exception as e:
    #     logger.warning(
    #         "⚠️ Redis Timer Listener initialization failed: %s. "
    #         "Continuing with APScheduler safety net.",
    #         str(e)[:100]
    #     )

    # ALWAYS start APScheduler as safety net (dual protection strategy)
    # This ensures no timer expiry events are lost, even if Redis Listener misses them
    # [TEMPORARILY DISABLED FOR DEBUGGING]
    fallback_scheduler = None
    logger.info("⚠️ APScheduler DISABLED for debugging")
    # try:
    #     from apscheduler.schedulers.asyncio import AsyncIOScheduler
    #     from app.infrastructure.tasks.timer_cleanup_apscheduler import check_expired_timers
    #
    #     fallback_scheduler = AsyncIOScheduler()
    #     fallback_scheduler.add_job(
    #         check_expired_timers,
    #         "interval",
    #         minutes=1,
    #         id="timer_cleanup_safety_net",
    #         replace_existing=True,
    #     )
    #     fallback_scheduler.start()
    #
    #     if redis_timer_listener.is_available():
    #         logger.info("✅ APScheduler started as safety net (checks every 1 minute, dual protection)")
    #     else:
    #         logger.info("✅ APScheduler started as primary timer (checks every 1 minute)")
    # except Exception:
    #     logger.exception("❌ APScheduler initialization failed - timer expiry may not work!")

    # Initialize Reservation Notification Worker (polling-based)
    # [TEMPORARILY DISABLED FOR DEBUGGING]
    reservation_task = None
    logger.info("⚠️ Reservation Notification Worker DISABLED for debugging")
    # try:
    #     reservation_task = asyncio.create_task(reservation_notification_worker.start())
    #     logger.info("✅ Reservation Notification Worker started (60s interval)")
    # except Exception as e:
    #     logger.warning(
    #         "⚠️ Reservation Notification Worker initialization failed: %s.",
    #         str(e)[:100]
    #     )

    logger.info("🔍 DEBUG: About to reach yield statement...")
    yield
    logger.info("🔍 DEBUG: Passed yield statement (should not appear until shutdown)")

    # Shutdown
    logger.info("🛑 Shutting down Focus Mate Backend...")
    # Send shutdown notification (with timeout to prevent hanging)
    try:
        await asyncio.wait_for(
            send_slack_notification(
                message=f"🛑 FocusMate Backend Shutting Down ({settings.APP_ENV})",
                level="warning"
            ),
            timeout=2.0
        )
    except asyncio.TimeoutError:
        logger.warning("Slack shutdown notification timed out")

    # Stop Redis Timer Listener
    try:
        await redis_timer_listener.disconnect()
        await _cancel_task(listener_task, "Redis Timer Listener")
    except Exception:
        logger.exception("⚠️ Error stopping Redis Timer Listener")

    # Stop APScheduler fallback
    try:
        if fallback_scheduler:
            fallback_scheduler.shutdown(wait=False)
        logger.info("✅ APScheduler fallback stopped")
    except Exception:
        logger.exception("⚠️ Error stopping APScheduler fallback")

    # Stop Reservation Notification Worker
    try:
        await reservation_notification_worker.stop()
        await _cancel_task(reservation_task, "Reservation Notification Worker")
    except Exception:
        logger.exception("⚠️ Error stopping Reservation Notification Worker")

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

# Slow request logging - detects latency regressions
app.add_middleware(
    SlowRequestMiddleware,
    threshold_ms=settings.APP_SLOW_REQUEST_THRESHOLD_MS,
)

# GZip middleware - compresses responses for bandwidth optimization
# Should be added first to compress all responses
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,  # Only compress responses larger than 1KB
    compresslevel=6,  # Compression level (1-9, default 6 for balance)
)

# Security headers middleware - attaches common hardening headers
if settings.SECURITY_HEADERS_ENABLED:
    app.add_middleware(
        SecurityHeadersMiddleware,
        enable_hsts=settings.SECURITY_HSTS_ENABLED and settings.is_production,
        enable_csp=settings.SECURITY_CSP_ENABLED,
        csp_policy=settings.SECURITY_CSP_POLICY,
        csp_exclude_paths=["/docs", "/redoc", "/openapi.json"],
        no_store_paths=["/api/v1/auth"],
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
if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=settings.RATE_LIMIT_PER_MINUTE,
        burst_limit=settings.RATE_LIMIT_BURST,
        exempt_paths=["/health", "/docs", "/redoc", "/openapi.json"],
    )

# CORS middleware - must be added before routes
# This ensures OPTIONS preflight requests are handled correctly
# Allow ngrok URLs in development using regex pattern (fixed regex)
ngrok_regex = r"^https://.*\.ngrok(-free)?\.(app|io)$"
# Allow production frontend origins by regex (covers apex and subdomains)
prod_origin_regex = r"^https://(.*\.)?eieconcierge\.com$"
# Prefer explicit config, otherwise pick by environment
origin_regex = settings.CORS_ORIGIN_REGEX
if not origin_regex:
    if settings.is_development:
        origin_regex = ngrok_regex
    elif settings.is_production:
        origin_regex = prod_origin_regex
# Handle CORS_ORIGINS="*" case: cannot use allow_credentials=True with "*"
# CORS policy normalization
cors_origins = settings.CORS_ORIGINS
allow_credentials = settings.CORS_ALLOW_CREDENTIALS
allow_methods = settings.CORS_ALLOW_METHODS
allow_headers = settings.CORS_ALLOW_HEADERS
expose_headers = settings.CORS_EXPOSE_HEADERS
# Check if CORS_ORIGINS contains "*" (validator converts to list)
if isinstance(cors_origins, list) and len(cors_origins) == 1 and cors_origins[0] == "*":
    # When using "*", credentials must be False
    allow_credentials = False
    logger.warning("⚠️ CORS_ORIGINS='*' detected, setting allow_credentials=False for security")

if settings.is_production:
    if isinstance(allow_methods, list) and "*" in allow_methods:
        allow_methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
        logger.warning("⚠️ CORS_ALLOW_METHODS='*' in production; enforcing explicit method allowlist")
    if isinstance(allow_headers, list) and "*" in allow_headers:
        allow_headers = [
            "Authorization",
            "Content-Type",
            "Accept",
            "Origin",
            "X-Requested-With",
            "X-Request-ID",
        ]
        logger.warning("⚠️ CORS_ALLOW_HEADERS='*' in production; enforcing explicit header allowlist")
    if isinstance(expose_headers, list) and "*" in expose_headers:
        expose_headers = ["X-Request-ID", "X-App-Version", "Content-Disposition"]
        logger.warning("⚠️ CORS_EXPOSE_HEADERS='*' in production; enforcing explicit expose headers")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=origin_regex,
    allow_credentials=allow_credentials,
    allow_methods=allow_methods,
    allow_headers=allow_headers,
    expose_headers=expose_headers,
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Fallback CORS headers for edge cases where middleware is bypassed
@app.middleware("http")
async def cors_fallback(request: Request, call_next):  # type: ignore[override]
    response = await call_next(request)
    if "access-control-allow-origin" in response.headers:
        return response

    origin = request.headers.get("origin")
    if not origin:
        return response

    allowed = False
    if isinstance(cors_origins, list) and origin in cors_origins:
        allowed = True
    if not allowed and origin_regex:
        try:
            if re.fullmatch(origin_regex, origin):
                allowed = True
        except re.error:
            allowed = False

    if allowed:
        response.headers["Access-Control-Allow-Origin"] = origin
        if allow_credentials:
            response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers.setdefault("Vary", "Origin")

    return response

# Standard response metadata header
@app.middleware("http")
async def response_meta(request: Request, call_next):  # type: ignore[override]
    response = await call_next(request)
    response.headers.setdefault("X-App-Version", settings.APP_VERSION)
    return response


def _add_cors_headers(headers: dict, request: Request) -> None:
    origin = request.headers.get("origin")
    if not origin:
        return
    if isinstance(cors_origins, list) and origin in cors_origins:
        headers["Access-Control-Allow-Origin"] = origin
    elif origin_regex:
        try:
            if re.fullmatch(origin_regex, origin):
                headers["Access-Control-Allow-Origin"] = origin
        except re.error:
            return
    if "Access-Control-Allow-Origin" in headers:
        if allow_credentials:
            headers["Access-Control-Allow-Credentials"] = "true"
        headers.setdefault("Vary", "Origin")


# Exception handler for custom exceptions
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle custom application exceptions with enhanced logging."""
    import logging

    logger = logging.getLogger("app")
    request_id = getattr(request.state, "request_id", None)

    # Use status code from exception
    status_code = exc.status_code

    # Log error with context
    logger.warning(
        f"Application error: code={exc.code} message={exc.message} "
        f"path={request.url.path} method={request.method} request_id={request_id}",
        extra={
            "error_code": exc.code,
            "error_message": exc.message,
            "error_details": exc.details,
            "request_path": request.url.path,
            "request_method": request.method,
            "request_id": request_id,
        },
    )

    headers = {}
    if request_id:
        headers["X-Request-ID"] = request_id
    _add_cors_headers(headers, request)
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
            "request_id": request_id,
        },
        headers=headers,
    )


# Global exception handler for unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions with proper logging."""
    import logging
    import traceback

    logger = logging.getLogger("app")
    request_id = getattr(request.state, "request_id", None)

    # Log full exception with traceback
    logger.error(
        f"Unhandled exception: {type(exc).__name__}: {str(exc)} "
        f"path={request.url.path} method={request.method} request_id={request_id}",
        exc_info=True,
        extra={
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "request_path": request.url.path,
            "request_method": request.method,
            "request_id": request_id,
            "traceback": traceback.format_exc(),
        },
    )

    # In production, don't expose internal error details
    if settings.is_development:
        error_message = f"{type(exc).__name__}: {str(exc)}"
    else:
        error_message = "An internal server error occurred"

    headers = {}
    if request_id:
        headers["X-Request-ID"] = request_id
    _add_cors_headers(headers, request)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": error_message,
                "details": {},
            },
            "request_id": request_id,
        },
        headers=headers,
    )


# Health check endpoint
# Health check endpoint (mapped from v1 controller)
from app.api.v1.endpoints import health

app.include_router(health.router, include_in_schema=False)  # /health is covered by api/v1/health in schema


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    status_code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMITED",
        500: "INTERNAL_SERVER_ERROR",
        503: "SERVICE_UNAVAILABLE",
    }
    code = status_code_map.get(exc.status_code, "HTTP_ERROR")
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    details = exc.detail if isinstance(exc.detail, dict) else {}
    if isinstance(details, dict) and details.get("code"):
        code = details["code"]
    logger = logging.getLogger("app")
    logger.warning(
        "HTTPException: status=%s path=%s method=%s request_id=%s detail=%s",
        exc.status_code,
        request.url.path,
        request.method,
        request_id,
        exc.detail,
    )
    headers = {}
    if request_id:
        headers["X-Request-ID"] = request_id
    _add_cors_headers(headers, request)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error": {"code": code, "message": message, "details": details},
            "request_id": request_id,
        },
        headers=headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    logger = logging.getLogger("app")
    logger.warning(
        "Validation error: path=%s method=%s request_id=%s errors=%s",
        request.url.path,
        request.method,
        request_id,
        exc.errors(),
    )
    headers = {}
    if request_id:
        headers["X-Request-ID"] = request_id
    _add_cors_headers(headers, request)
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation error",
                "details": exc.errors(),
            },
            "request_id": request_id,
        },
        headers=headers,
    )




# Include API router
app.include_router(api_router, prefix="/api/v1")

# Prometheus metrics instrumentation
# Exposes metrics at /metrics endpoint
# if settings.PROMETHEUS_ENABLED:
#     Instrumentator().instrument(app).expose(app)

# Mount static files for uploads
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)

# Mount chat uploads
chat_uploads_dir = uploads_dir / "chat"
chat_uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount(
    "/uploads/chat", StaticFiles(directory=str(chat_uploads_dir)), name="chat_uploads"
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
