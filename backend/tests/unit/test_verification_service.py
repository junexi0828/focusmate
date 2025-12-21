"""Unit tests for verification service."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.domain.verification.schemas import VerificationSubmit
from app.domain.verification.service import VerificationService


@pytest.fixture
def mock_verification_repository():
    """Create mock verification repository."""
    return AsyncMock()


@pytest.fixture
def verification_service(mock_verification_repository):
    """Create verification service with mocked dependencies."""
    return VerificationService(repository=mock_verification_repository)


class TestVerificationService:
    """Test cases for VerificationService."""

    @pytest.mark.asyncio
    async def test_submit_verification(self, verification_service, mock_verification_repository):
        """Test submitting a verification request."""
        user_id = str(uuid4())
        data = VerificationSubmit(
            school_name="Test University",
            department="Computer Science",
            grade="3",
            gender="male",
            documents=["doc1.jpg"]
        )

        # Mock returns object with attributes (like SQLAlchemy model)
        mock_verification_obj = MagicMock()
        mock_verification_obj.verification_id = uuid4()
        mock_verification_obj.user_id = user_id
        mock_verification_obj.school_name = data.school_name
        mock_verification_obj.department = data.department
        mock_verification_obj.major_category = None
        mock_verification_obj.grade = data.grade
        mock_verification_obj.gender = data.gender
        mock_verification_obj.verification_status = "pending"
        mock_verification_obj.badge_visible = True
        mock_verification_obj.department_visible = True
        mock_verification_obj.submitted_at = datetime.utcnow()
        mock_verification_obj.verified_at = None
        mock_verification_obj.submitted_documents = data.documents

        mock_verification_repository.get_verification_by_user.return_value = None
        mock_verification_repository.create_verification.return_value = mock_verification_obj
        # Service may call update_verification if email is sent
        mock_verification_repository.update_verification.return_value = mock_verification_obj

        result = await verification_service.submit_verification(user_id, data)

        assert result is not None
        assert result.user_id == user_id
        assert result.verification_status == "pending"
        mock_verification_repository.create_verification.assert_called_once()

    @pytest.mark.asyncio
    async def test_review_verification(self, verification_service, mock_verification_repository):
        """Test reviewing a verification request."""
        verification_id = uuid4()
        user_id = str(uuid4())

        # Mock returns object with attributes (like SQLAlchemy model)
        mock_verification_obj = MagicMock()
        mock_verification_obj.verification_id = verification_id
        mock_verification_obj.user_id = user_id
        mock_verification_obj.school_name = "Test University"
        mock_verification_obj.department = "Computer Science"
        mock_verification_obj.major_category = None
        mock_verification_obj.grade = "3"
        mock_verification_obj.gender = "male"
        mock_verification_obj.verification_status = "approved"
        mock_verification_obj.badge_visible = True
        mock_verification_obj.department_visible = True
        mock_verification_obj.submitted_at = datetime.utcnow()
        mock_verification_obj.verified_at = datetime.utcnow()
        mock_verification_obj.submitted_documents = []

        mock_verification_repository.update_verification.return_value = mock_verification_obj

        result = await verification_service.review_verification(verification_id, approved=True)

        assert result.verification_status == "approved"
        assert result.verified_at is not None
        mock_verification_repository.update_verification.assert_called_once()


def test_verification_service_import():
    """Test that verification service can be imported."""
    from app.domain.verification.service import VerificationService
    assert VerificationService is not None
