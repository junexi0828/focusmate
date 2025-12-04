"""Custom exceptions for the application.

Provides domain-specific exceptions with error codes.
"""

from typing import Any


class AppException(Exception):
    """Base exception for all application errors.

    Attributes:
        message: Human-readable error message
        code: Machine-readable error code
        details: Additional error context
    """

    def __init__(
        self,
        message: str,
        code: str = "APP_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize exception.

        Args:
            message: Error message
            code: Error code
            details: Additional context
        """
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)


# =============================================================================
# Room Exceptions
# =============================================================================


class RoomNotFoundException(AppException):
    """Raised when a room is not found."""

    def __init__(self, room_id: str) -> None:
        """Initialize exception.

        Args:
            room_id: Room identifier
        """
        super().__init__(
            message=f"Room with id '{room_id}' not found",
            code="ROOM_NOT_FOUND",
            details={"room_id": room_id},
        )


class RoomNameTakenException(AppException):
    """Raised when a room name is already taken."""

    def __init__(self, room_name: str) -> None:
        """Initialize exception.

        Args:
            room_name: Room name
        """
        super().__init__(
            message=f"Room name '{room_name}' is already taken",
            code="ROOM_NAME_TAKEN",
            details={"room_name": room_name},
        )


class RoomFullException(AppException):
    """Raised when a room is at maximum capacity."""

    def __init__(self, room_id: str, max_participants: int) -> None:
        """Initialize exception.

        Args:
            room_id: Room identifier
            max_participants: Maximum allowed participants
        """
        super().__init__(
            message=f"Room '{room_id}' is full (max: {max_participants})",
            code="ROOM_FULL",
            details={"room_id": room_id, "max_participants": max_participants},
        )


# =============================================================================
# Timer Exceptions
# =============================================================================


class TimerNotFoundException(AppException):
    """Raised when a timer is not found."""

    def __init__(self, timer_id: str) -> None:
        """Initialize exception.

        Args:
            timer_id: Timer identifier
        """
        super().__init__(
            message=f"Timer with id '{timer_id}' not found",
            code="TIMER_NOT_FOUND",
            details={"timer_id": timer_id},
        )


class InvalidTimerStateException(AppException):
    """Raised when timer operation is invalid for current state."""

    def __init__(self, current_state: str, operation: str) -> None:
        """Initialize exception.

        Args:
            current_state: Current timer state
            operation: Attempted operation
        """
        super().__init__(
            message=f"Cannot {operation} timer in {current_state} state",
            code="INVALID_TIMER_STATE",
            details={"current_state": current_state, "operation": operation},
        )


# =============================================================================
# Participant Exceptions
# =============================================================================


class ParticipantNotFoundException(AppException):
    """Raised when a participant is not found."""

    def __init__(self, participant_id: str) -> None:
        """Initialize exception.

        Args:
            participant_id: Participant identifier
        """
        super().__init__(
            message=f"Participant with id '{participant_id}' not found",
            code="PARTICIPANT_NOT_FOUND",
            details={"participant_id": participant_id},
        )


# =============================================================================
# Validation Exceptions
# =============================================================================


class ValidationException(AppException):
    """Raised when input validation fails."""

    def __init__(self, field: str, message: str) -> None:
        """Initialize exception.

        Args:
            field: Field that failed validation
            message: Validation error message
        """
        super().__init__(
            message=f"Validation error for '{field}': {message}",
            code="VALIDATION_ERROR",
            details={"field": field, "error": message},
        )


# =============================================================================
# Authentication/Authorization Exceptions
# =============================================================================


class UnauthorizedException(AppException):
    """Raised when user is not authenticated."""

    def __init__(self, message: str = "Authentication required") -> None:
        """Initialize exception.

        Args:
            message: Error message
        """
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
        )


class ForbiddenException(AppException):
    """Raised when user lacks required permissions."""

    def __init__(self, message: str = "Insufficient permissions") -> None:
        """Initialize exception.

        Args:
            message: Error message
        """
        super().__init__(
            message=message,
            code="FORBIDDEN",
        )


# =============================================================================
# General Exceptions
# =============================================================================


class NotFoundException(AppException):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str) -> None:
        """Initialize exception.

        Args:
            message: Error message describing what was not found
        """
        super().__init__(
            message=message,
            code="NOT_FOUND",
        )
