"""Slow request monitoring middleware."""

import logging
import time
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


logger = logging.getLogger(__name__)


class SlowRequestMiddleware(BaseHTTPMiddleware):
    """Log requests that exceed a latency threshold."""

    def __init__(self, app: ASGIApp, threshold_ms: int = 1500) -> None:
        super().__init__(app)
        self.threshold_ms = threshold_ms

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.time()
        response = await call_next(request)
        duration_ms = (time.time() - start) * 1000
        if duration_ms >= self.threshold_ms:
            request_id = getattr(request.state, "request_id", None)
            logger.warning(
                "Slow request: path=%s method=%s status=%s duration_ms=%.1f request_id=%s",
                request.url.path,
                request.method,
                response.status_code,
                duration_ms,
                request_id,
            )
        return response
