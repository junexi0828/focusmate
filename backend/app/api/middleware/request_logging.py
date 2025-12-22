"""Request ID and logging middleware.

Adds unique request IDs to each request and logs request/response details
for debugging and monitoring purposes.
"""

import logging
import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request ID generation and request/response logging."""

    def __init__(
        self,
        app: ASGIApp,
        log_request_body: bool = False,
        log_response_body: bool = False,
        exclude_paths: list[str] | None = None,
    ):
        """Initialize request logging middleware.

        Args:
            app: ASGI application
            log_request_body: Whether to log request body (default: False, for security)
            log_response_body: Whether to log response body (default: False, for performance)
            exclude_paths: List of URL paths to exclude from logging
        """
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.exclude_paths = exclude_paths or ["/health", "/metrics"]

    def should_log(self, path: str) -> bool:
        """Check if request should be logged.

        Args:
            path: Request path

        Returns:
            True if request should be logged
        """
        return not any(path.startswith(exclude) for exclude in self.exclude_paths)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with ID generation and logging.

        Args:
            request: Incoming request
            call_next: Next middleware/endpoint

        Returns:
            Response with request ID header
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Check if client provided request ID
        client_request_id = request.headers.get("X-Request-ID")
        if client_request_id:
            request_id = client_request_id

        # Store request ID in request state for access in endpoints
        request.state.request_id = request_id

        # Start timer
        start_time = time.time()

        # Log request
        if self.should_log(request.url.path):
            log_data = {
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "client_host": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }

            # Optionally log request body (be careful with sensitive data)
            if self.log_request_body and request.method in ("POST", "PUT", "PATCH"):
                try:
                    body = await request.body()
                    # Store body back for endpoint to read
                    request._body = body
                    # Only log first 500 chars to avoid huge logs
                    log_data["request_body"] = body[:500].decode("utf-8", errors="ignore")
                except Exception as e:
                    log_data["request_body_error"] = str(e)

            logger.info(f"Request started: {log_data}")

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log exception
            duration = time.time() - start_time
            logger.error(
                f"Request failed: request_id={request_id} "
                f"method={request.method} path={request.url.path} "
                f"duration={duration:.3f}s error={str(e)}",
                exc_info=True,
            )
            raise

        # Calculate duration
        duration = time.time() - start_time

        # Add request ID and timing headers to response
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{duration:.3f}"

        # Log response
        if self.should_log(request.url.path):
            log_data = {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration": f"{duration:.3f}s",
            }

            # Determine log level based on status code
            if response.status_code >= 500:
                logger.error(f"Request completed with error: {log_data}")
            elif response.status_code >= 400:
                logger.warning(f"Request completed with client error: {log_data}")
            else:
                logger.info(f"Request completed: {log_data}")

        return response


def get_request_id(request: Request) -> str | None:
    """Get request ID from request state.

    Args:
        request: FastAPI request object

    Returns:
        Request ID if available, None otherwise

    Example:
        ```python
        from fastapi import Request
        from app.api.middleware.request_logging import get_request_id

        @router.get("/example")
        async def example(request: Request):
            request_id = get_request_id(request)
            logger.info(f"Processing request {request_id}")
        ```
    """
    return getattr(request.state, "request_id", None)
