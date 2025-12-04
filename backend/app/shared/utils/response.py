"""Standard API response utilities."""

from typing import Any

from pydantic import BaseModel, ConfigDict


class SuccessResponse(BaseModel):
    """Standard success response format."""

    model_config = ConfigDict(strict=True)

    status: str = "success"
    data: Any
    message: str | None = None


class ErrorResponse(BaseModel):
    """Standard error response format."""

    model_config = ConfigDict(strict=True)

    status: str = "error"
    error: dict[str, Any]


def success_response(data: Any, message: str | None = None) -> dict[str, Any]:
    """Create success response."""
    return {"status": "success", "data": data, "message": message}


def error_response(code: str, message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    """Create error response."""
    return {
        "status": "error",
        "error": {"code": code, "message": message, "details": details or {}},
    }
