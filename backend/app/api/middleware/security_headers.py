"""Security headers middleware.

Adds common security headers to API responses.
"""

from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to attach security headers to responses."""

    def __init__(
        self,
        app: ASGIApp,
        enable_hsts: bool = True,
        enable_csp: bool = False,
        csp_policy: str | None = None,
        csp_exclude_paths: list[str] | None = None,
        enable_coop: bool = True,
        enable_coep: bool = True,
        no_store_paths: list[str] | None = None,
    ) -> None:
        super().__init__(app)
        self.enable_hsts = enable_hsts
        self.enable_csp = enable_csp
        self.csp_policy = csp_policy or "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
        self.csp_exclude_paths = csp_exclude_paths or []
        self.enable_coop = enable_coop
        self.enable_coep = enable_coep
        self.no_store_paths = no_store_paths or []

    def _csp_allowed(self, path: str) -> bool:
        return not any(path.startswith(exclude) for exclude in self.csp_exclude_paths)

    def _no_store_required(self, path: str) -> bool:
        return any(path.startswith(prefix) for prefix in self.no_store_paths)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("X-DNS-Prefetch-Control", "off")
        response.headers.setdefault("X-Permitted-Cross-Domain-Policies", "none")
        response.headers.setdefault("X-Download-Options", "noopen")
        response.headers.setdefault("Cross-Origin-Resource-Policy", "same-site")
        response.headers.setdefault(
            "Permissions-Policy",
            "geolocation=(), microphone=(), camera=(), payment=(), usb=()",
        )

        if self._csp_allowed(request.url.path):
            if self.enable_coop:
                response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
            if self.enable_coep:
                response.headers.setdefault("Cross-Origin-Embedder-Policy", "require-corp")

        if self.enable_csp and self._csp_allowed(request.url.path):
            response.headers.setdefault("Content-Security-Policy", self.csp_policy)

        if self.enable_hsts and request.url.scheme == "https":
            response.headers.setdefault(
                "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
            )

        if self._no_store_required(request.url.path):
            response.headers.setdefault(
                "Cache-Control", "no-store, no-cache, must-revalidate, max-age=0"
            )
            response.headers.setdefault("Pragma", "no-cache")
            response.headers.setdefault("Expires", "0")

        return response
