"""Unit tests for Redis Circuit Breaker."""

import asyncio
import pytest
from unittest.mock import AsyncMock, patch

from app.infrastructure.redis.circuit_breaker import (
    RedisCircuitBreaker,
    CircuitOpenError,
)


class TestCircuitBreaker:
    """Test Circuit Breaker state transitions and behavior."""

    @pytest.fixture
    def breaker(self):
        """Create a circuit breaker with short timeouts for testing."""
        return RedisCircuitBreaker(
            failure_threshold=3,
            recovery_timeout=1,  # 1 second for faster tests
            success_threshold=2,
        )

    @pytest.mark.asyncio
    async def test_closed_state_success(self, breaker):
        """Test successful calls in CLOSED state."""
        async def success_func():
            return "success"

        result = await breaker.call(success_func)
        assert result == "success"
        assert breaker.state == breaker.CLOSED
        assert breaker.failure_count == 0

    @pytest.mark.asyncio
    async def test_transition_to_open_on_failures(self, breaker):
        """Test circuit opens after failure threshold."""
        async def failing_func():
            raise Exception("Redis error")

        # Fail 3 times (threshold)
        for _ in range(3):
            with pytest.raises(Exception):
                await breaker.call(failing_func)

        # Circuit should be OPEN
        assert breaker.state == breaker.OPEN
        assert breaker.failure_count == 3

    @pytest.mark.asyncio
    async def test_fail_fast_when_open(self, breaker):
        """Test circuit fails fast when OPEN."""
        async def failing_func():
            raise Exception("Redis error")

        # Open the circuit
        for _ in range(3):
            with pytest.raises(Exception):
                await breaker.call(failing_func)

        # Next call should fail fast without calling function
        with pytest.raises(CircuitOpenError):
            await breaker.call(failing_func)

    @pytest.mark.asyncio
    async def test_transition_to_half_open(self, breaker):
        """Test circuit transitions to HALF_OPEN after timeout."""
        async def failing_func():
            raise Exception("Redis error")

        # Open the circuit
        for _ in range(3):
            with pytest.raises(Exception):
                await breaker.call(failing_func)

        assert breaker.state == breaker.OPEN

        # Wait for recovery timeout
        await asyncio.sleep(1.1)

        # Next call should transition to HALF_OPEN
        async def success_func():
            return "success"

        result = await breaker.call(success_func)
        assert result == "success"
        assert breaker.state == breaker.HALF_OPEN

    @pytest.mark.asyncio
    async def test_half_open_to_closed_on_success(self, breaker):
        """Test circuit closes after success threshold in HALF_OPEN."""
        async def failing_func():
            raise Exception("Redis error")

        # Open the circuit
        for _ in range(3):
            with pytest.raises(Exception):
                await breaker.call(failing_func)

        # Wait for recovery timeout
        await asyncio.sleep(1.1)

        # Succeed twice (success threshold)
        async def success_func():
            return "success"

        await breaker.call(success_func)
        assert breaker.state == breaker.HALF_OPEN

        await breaker.call(success_func)
        assert breaker.state == breaker.CLOSED

    @pytest.mark.asyncio
    async def test_half_open_to_open_on_failure(self, breaker):
        """Test circuit reopens on failure in HALF_OPEN."""
        async def failing_func():
            raise Exception("Redis error")

        # Open the circuit
        for _ in range(3):
            with pytest.raises(Exception):
                await breaker.call(failing_func)

        # Wait for recovery timeout
        await asyncio.sleep(1.1)

        # Fail in HALF_OPEN
        with pytest.raises(Exception):
            await breaker.call(failing_func)

        # Should reopen
        assert breaker.state == breaker.OPEN

    @pytest.mark.asyncio
    async def test_stats_tracking(self, breaker):
        """Test circuit breaker statistics."""
        async def success_func():
            return "success"

        async def failing_func():
            raise Exception("Redis error")

        # Some successes
        await breaker.call(success_func)
        await breaker.call(success_func)

        # Some failures
        with pytest.raises(Exception):
            await breaker.call(failing_func)

        stats = breaker.get_stats()
        assert stats["total_calls"] == 3
        assert stats["total_successes"] == 2
        assert stats["total_failures"] == 1
        assert stats["success_rate"] == 66.67
        assert stats["state"] == breaker.CLOSED

    @pytest.mark.asyncio
    async def test_manual_reset(self, breaker):
        """Test manual circuit reset."""
        async def failing_func():
            raise Exception("Redis error")

        # Open the circuit
        for _ in range(3):
            with pytest.raises(Exception):
                await breaker.call(failing_func)

        assert breaker.state == breaker.OPEN

        # Manual reset
        breaker.reset()
        assert breaker.state == breaker.CLOSED
        assert breaker.failure_count == 0
