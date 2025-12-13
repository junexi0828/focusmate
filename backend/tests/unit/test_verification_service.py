"""Unit tests for verification service."""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock

from app.domain.verification.service import VerificationService
from app.infrastructure.repositories.verification_repository import VerificationRepository


@pytest.fixture
def mock_verification_repository():
    """Create mock verification repository."""
    return AsyncMock(spec=VerificationRepository)


@pytest.fixture
def verification_service(mock_verification_repository):
    """Create verification service with mocked dependencies."""
    return VerificationService(repository=mock_verification_repository)


class TestVerificationService:
    """Test cases for VerificationService."""

    @pytest.mark.asyncio
    async def test_create_verification_request(self, verification_service, mock_verification_repository):
        """Test creating a verification request."""
        user_id = str(uuid4())
        verification_type = "identity"

        expected_request = {
            "id": str(uuid4()),
            "user_id": user_id,
            "verification_type": verification_type,
            "status": "pending",
        }

        mock_verification_repository.create.return_value = expected_request

        result = await verification_service.create_request(user_id, verification_type)

        assert result is not None
        assert result["user_id"] == user_id
        assert result["status"] == "pending"
        mock_verification_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_approve_verification(self, verification_service, mock_verification_repository):
        """Test approving a verification request."""
        verification_id = str(uuid4())
        admin_id = str(uuid4())

        expected_result = {
            "id": verification_id,
            "status": "approved",
            "approved_by": admin_id,
        }

        mock_verification_repository.update_status.return_value = expected_result

        result = await verification_service.approve(verification_id, admin_id)

        assert result["status"] == "approved"
        assert result["approved_by"] == admin_id


def test_verification_service_import():
    """Test that verification service can be imported."""
    from app.domain.verification.service import VerificationService
    assert VerificationService is not None
