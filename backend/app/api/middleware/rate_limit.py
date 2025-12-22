"""Rate limiting middleware using Redis.

Prevents abuse by limiting the number of requests from a single IP address
or authenticated user within a specified time window.
"""

import time
from collections.abc import Callable

import redis.asyncio as aioredis
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis for distributed rate limiting."""

    def __init__(
        self,
        app: ASGIApp,
        redis_url: str | None = None,
        requests_per_minute: int = 60,
        burst_limit: int | None = None,
        exempt_paths: list[str] | None = None,
    ):
        """Initialize rate limiting middleware.

        Args:
            app: ASGI application
            redis_url: Redis connection URL (defaults to settings.REDIS_URL)
            requests_per_minute: Maximum requests allowed per minute (default: 60)
            burst_limit: Maximum burst requests (defaults to 2x requests_per_minute)
            exempt_paths: List of URL paths to exempt from rate limiting
        """
        super().__init__(app)
        self.redis_url = redis_url or settings.REDIS_URL
        self.redis: aioredis.Redis | None = None
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit or (requests_per_minute * 2)
        self.exempt_paths = exempt_paths or ["/health", "/docs", "/redoc", "/openapi.json"]

        # Stricter limits for sensitive endpoints
        self.strict_limits = {
            "/api/v1/auth/login": 5,  # 5 requests per minute
            "/api/v1/auth/register": 3,  # 3 requests per minute
            "/api/v1/auth/password-reset/request": 3,
            "/api/v1/auth/password-reset/complete": 3,
        }

    async def connect_redis(self):
        """Connect to Redis if not already connected."""
        if not self.redis:
            try:
                self.redis = await aioredis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                )
            except Exception as e:
                print(f"Rate limit middleware: Failed to connect to Redis: {e}")
                # Continue without rate limiting if Redis is unavailable
                self.redis = None

    def get_client_identifier(self, request: Request) -> str:
        """Get unique identifier for the client.

        Uses authenticated user ID if available, otherwise falls back to IP address.

        Args:
            request: The incoming request

        Returns:
            Unique client identifier
        """
        # Try to get user ID from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"

        # Fall back to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Get the first IP in the chain (client IP)
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        return f"ip:{client_ip}"

    def get_rate_limit(self, path: str) -> int:
        """Get rate limit for a specific path.

        Args:
            path: Request path

        Returns:
            Rate limit (requests per minute)
        """
        # Check for strict limits on sensitive endpoints
        for strict_path, limit in self.strict_limits.items():
            if path.startswith(strict_path):
                return limit

        return self.requests_per_minute

    async def is_rate_limited(
        self, client_id: str, path: str
    ) -> tuple[bool, dict[str, int]]:
        """Check if client has exceeded rate limit.

        Uses sliding window algorithm with Redis.

        Args:
            client_id: Unique client identifier
            path: Request path

        Returns:
            Tuple of (is_limited, rate_limit_info)
            rate_limit_info contains: limit, remaining, reset_time
        """
        if not self.redis:
            await self.connect_redis()
            if not self.redis:
                # If Redis is unavailable, allow the request
                return False, {"limit": 0, "remaining": 0, "reset": 0}

        current_time = int(time.time())
        window_start = current_time - 60  # 1 minute window

        # Get rate limit for this path
        rate_limit = self.get_rate_limit(path)

        # Create Redis key for this client and path
        key = f"rate_limit:{client_id}:{path}"

        try:
            # Use Redis pipeline for atomic operations
            pipe = self.redis.pipeline()

            # Remove old entries outside the time window
            pipe.zremrangebyscore(key, 0, window_start)

            # Count requests in current window
            pipe.zcard(key)

            # Add current request timestamp
            pipe.zadd(key, {str(current_time): current_time})

            # Set expiration to 2 minutes (cleanup old keys)
            pipe.expire(key, 120)

            results = await pipe.execute()
            request_count = results[1]  # Get count from zcard operation

            # Calculate remaining requests
            remaining = max(0, rate_limit - request_count - 1)
            reset_time = current_time + 60

            is_limited = request_count >= rate_limit

            return is_limited, {
                "limit": rate_limit,
                "remaining": remaining,
                "reset": reset_time,
            }

        except Exception as e:
            print(f"Rate limit check error: {e}")
            # On error, allow the request
            return False, {"limit": rate_limit, "remaining": rate_limit, "reset": current_time + 60}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting.

        Args:
            request: Incoming request
            call_next: Next middleware/endpoint

        Returns:
            Response or 429 Too Many Requests
        """
        # Check if path is exempt from rate limiting
        path = request.url.path
        if any(path.startswith(exempt) for exempt in self.exempt_paths):
            return await call_next(request)

        # Get client identifier
        client_id = self.get_client_identifier(request)

        # Check rate limit
        is_limited, rate_info = await self.is_rate_limited(client_id, path)

        if is_limited:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Please try again in {rate_info['reset'] - int(time.time())} seconds.",
                    "limit": rate_info["limit"],
                    "remaining": 0,
                    "reset": rate_info["reset"],
                },
                headers={
                    "X-RateLimit-Limit": str(rate_info["limit"]),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(rate_info["reset"]),
                    "Retry-After": str(rate_info["reset"] - int(time.time())),
                },
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(rate_info["reset"])

        return response
