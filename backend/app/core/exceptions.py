"""Custom exceptions for the application.

Provides domain-specific exceptions with error codes.
"""

from typing import Any, Dict


class AppException(Exception):
    """Base exception for all application errors.

    Attributes:
        message: Human-readable error message
        code: Machine-readable error code
        details: Additional error context
        status_code: HTTP status code
    """

    def __init__(
        self,
        message: str,
        code: str = "APP_ERROR",
        details: Dict[str, Any] | None = None,
        status_code: int = 400,
    ) -> None:
        """Initialize exception."""
        self.message = message
        self.code = code
        self.details = details or {}
        self.status_code = status_code
        super().__init__(message)


# =============================================================================
# Room Exceptions
# =============================================================================


class RoomNotFoundException(AppException):
    """Raised when a room is not found."""

    def __init__(self, room_id: str) -> None:
        super().__init__(
            message=f"Room with id '{room_id}' not found",
            code="ROOM_NOT_FOUND",
            details={"room_id": room_id},
            status_code=404,
        )


class RoomNameTakenException(AppException):
    """Raised when a room name is already taken."""

    def __init__(self, room_name: str) -> None:
        super().__init__(
            message=f"Room name '{room_name}' is already taken",
            code="ROOM_NAME_TAKEN",
            details={"room_name": room_name},
            status_code=409,
        )


class RoomHostRequiredException(AppException):
    """Raised when room host permission is required."""

    def __init__(self, room_id: str) -> None:
        super().__init__(
            message="Only the room host can perform this action",
            code="ROOM_HOST_REQUIRED",
            details={"room_id": room_id},
            status_code=403,
        )


class RoomFullException(AppException):
    """Raised when a room is at maximum capacity."""

    def __init__(self, room_id: str, max_participants: int) -> None:
        super().__init__(
            message=f"Room '{room_id}' is full (max: {max_participants})",
            code="ROOM_FULL",
            details={"room_id": room_id, "max_participants": max_participants},
            status_code=409,
        )


# =============================================================================
# Timer Exceptions
# =============================================================================


class TimerNotFoundException(AppException):
    """Raised when a timer is not found."""

    def __init__(self, timer_id: str) -> None:
        super().__init__(
            message=f"Timer with id '{timer_id}' not found",
            code="TIMER_NOT_FOUND",
            details={"timer_id": timer_id},
            status_code=404,
        )


class InvalidTimerStateException(AppException):
    """Raised when timer operation is invalid for current state."""

    def __init__(self, current_state: str, operation: str) -> None:
        super().__init__(
            message=f"Cannot {operation} timer in {current_state} state",
            code="INVALID_TIMER_STATE",
            details={"current_state": current_state, "operation": operation},
            status_code=409,
        )


# =============================================================================
# Participant Exceptions
# =============================================================================


class ParticipantNotFoundException(AppException):
    """Raised when a participant is not found."""

    def __init__(self, participant_id: str) -> None:
        super().__init__(
            message=f"Participant with id '{participant_id}' not found",
            code="PARTICIPANT_NOT_FOUND",
            details={"participant_id": participant_id},
            status_code=404,
        )


# =============================================================================
# Validation Exceptions
# =============================================================================


class ValidationException(AppException):
    """Raised when input validation fails."""

    def __init__(self, field: str, message: str) -> None:
        super().__init__(
            message=f"Validation error for '{field}': {message}",
            code="VALIDATION_ERROR",
            details={"field": field, "error": message},
            status_code=422,
        )


# =============================================================================
# Authentication/Authorization Exceptions
# =============================================================================


class UnauthorizedException(AppException):
    """Raised when user is not authenticated."""

    def __init__(self, message: str = "Authentication required") -> None:
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=401,
        )


class ForbiddenException(AppException):
    """Raised when user lacks required permissions."""

    def __init__(self, message: str = "Insufficient permissions") -> None:
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=403,
        )


# =============================================================================
# General Exceptions
# =============================================================================


class NotFoundException(AppException):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=404,
        )


class ConflictException(AppException):
    """Raised when a resource conflict occurs."""

    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            code="CONFLICT",
            status_code=409,
        )
