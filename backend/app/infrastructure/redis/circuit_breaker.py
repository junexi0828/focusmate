"""Circuit Breaker pattern for Redis operations.

Implements the Netflix Hystrix pattern for fault isolation and resilience.
Prevents cascading failures when Redis is unavailable.

States:
    CLOSED: Normal operation, requests pass through
    OPEN: Failure threshold exceeded, requests fail fast
    HALF_OPEN: Testing if service has recovered

References:
    - Netflix Hystrix: https://github.com/Netflix/Hystrix/wiki
    - Martin Fowler: https://martinfowler.com/bliki/CircuitBreaker.html
"""

import logging
import time
from typing import Any, Callable, TypeVar
from datetime import datetime, UTC

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CircuitOpenError(Exception):
    """Raised when circuit breaker is in OPEN state."""
    pass


class RedisCircuitBreaker:
    """Circuit Breaker for Redis operations following Netflix Hystrix pattern.

    Automatically detects failures and prevents overwhelming a failing service.

    Args:
        failure_threshold: Number of consecutive failures before opening circuit (default: 5)
        recovery_timeout: Seconds to wait before attempting recovery (default: 30)
        success_threshold: Number of successes in HALF_OPEN to close circuit (default: 2)

    Example:
        >>> breaker = RedisCircuitBreaker()
        >>> result = await breaker.call(redis.get, "key")
    """

    # Circuit states
    CLOSED = "closed"        # Normal operation
    OPEN = "open"            # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        success_threshold: int = 2,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold

        # State tracking
        self.state = self.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: float | None = None
        self.last_state_change = time.time()

        # Metrics
        self.total_calls = 0
        self.total_failures = 0
        self.total_successes = 0
        self.circuit_open_count = 0

        logger.info(
            f"[Circuit Breaker] Initialized with failure_threshold={failure_threshold}, "
            f"recovery_timeout={recovery_timeout}s, success_threshold={success_threshold}"
        )

    async def call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Execute function with circuit breaker protection.

        Args:
            func: Async function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result from func

        Raises:
            CircuitOpenError: If circuit is OPEN and recovery timeout not elapsed
            Exception: Any exception raised by func
        """
        self.total_calls += 1

        # Check if we should attempt recovery
        if self.state == self.OPEN:
            if self._should_attempt_reset():
                self._transition_to_half_open()
            else:
                # Fail fast - don't call Redis
                logger.debug("[Circuit Breaker] Circuit is OPEN, failing fast")
                raise CircuitOpenError(
                    f"Circuit breaker is OPEN. Last failure: {self.last_failure_time}. "
                    f"Will retry in {self._time_until_retry():.1f}s"
                )

        # Attempt the call
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure(e)
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        if self.last_failure_time is None:
            return True

        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.recovery_timeout

    def _time_until_retry(self) -> float:
        """Calculate seconds until next retry attempt."""
        if self.last_failure_time is None:
            return 0.0

        elapsed = time.time() - self.last_failure_time
        remaining = max(0.0, self.recovery_timeout - elapsed)
        return remaining

    def _on_success(self) -> None:
        """Handle successful call."""
        self.total_successes += 1

        if self.state == self.HALF_OPEN:
            self.success_count += 1
            logger.info(
                f"[Circuit Breaker] Success in HALF_OPEN state "
                f"({self.success_count}/{self.success_threshold})"
            )

            if self.success_count >= self.success_threshold:
                self._transition_to_closed()
        elif self.state == self.CLOSED:
            # Reset failure count on success
            if self.failure_count > 0:
                logger.debug(
                    f"[Circuit Breaker] Success after {self.failure_count} failures, resetting"
                )
                self.failure_count = 0

    def _on_failure(self, error: Exception) -> None:
        """Handle failed call."""
        self.total_failures += 1
        self.failure_count += 1
        self.last_failure_time = time.time()

        logger.warning(
            f"[Circuit Breaker] Failure #{self.failure_count} in {self.state} state: {error}"
        )

        if self.state == self.HALF_OPEN:
            # Any failure in HALF_OPEN immediately reopens circuit
            logger.warning("[Circuit Breaker] Failure in HALF_OPEN, reopening circuit")
            self._transition_to_open()
        elif self.state == self.CLOSED:
            if self.failure_count >= self.failure_threshold:
                logger.error(
                    f"[Circuit Breaker] Failure threshold ({self.failure_threshold}) "
                    f"exceeded, opening circuit"
                )
                self._transition_to_open()

    def _transition_to_open(self) -> None:
        """Transition to OPEN state."""
        self.state = self.OPEN
        self.success_count = 0
        self.last_state_change = time.time()
        self.circuit_open_count += 1

        logger.error(
            f"[Circuit Breaker] ⚠️ CIRCUIT OPENED (failure #{self.circuit_open_count}). "
            f"Will retry in {self.recovery_timeout}s"
        )

    def _transition_to_half_open(self) -> None:
        """Transition to HALF_OPEN state."""
        self.state = self.HALF_OPEN
        self.success_count = 0
        self.failure_count = 0
        self.last_state_change = time.time()

        logger.info("[Circuit Breaker] 🔄 Transitioning to HALF_OPEN, testing recovery")

    def _transition_to_closed(self) -> None:
        """Transition to CLOSED state."""
        self.state = self.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_state_change = time.time()

        logger.info("[Circuit Breaker] ✅ Circuit CLOSED, service recovered")

    def get_stats(self) -> dict[str, Any]:
        """Get circuit breaker statistics.

        Returns:
            Dictionary with current state and metrics
        """
        total = self.total_calls
        success_rate = (self.total_successes / total * 100) if total > 0 else 100.0

        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "total_calls": self.total_calls,
            "total_successes": self.total_successes,
            "total_failures": self.total_failures,
            "success_rate": round(success_rate, 2),
            "circuit_open_count": self.circuit_open_count,
            "last_failure_time": (
                datetime.fromtimestamp(self.last_failure_time, UTC).isoformat()
                if self.last_failure_time
                else None
            ),
            "time_until_retry": (
                round(self._time_until_retry(), 1)
                if self.state == self.OPEN
                else None
            ),
            "uptime_seconds": round(time.time() - self.last_state_change, 1),
        }

    def reset(self) -> None:
        """Manually reset circuit breaker to CLOSED state.

        Use this for administrative purposes or testing.
        """
        logger.warning("[Circuit Breaker] Manual reset to CLOSED state")
        self._transition_to_closed()
