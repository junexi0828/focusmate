
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, UTC

from app.domain.ranking.service import RankingService
from app.domain.ranking.schemas import TeamCreate, TeamInvitationCreate

@pytest.fixture
def mock_repo():
    repo = AsyncMock()
    # Mock session for internal repo creation check
    repo.session = AsyncMock()
    return repo

@pytest.fixture
def mock_user_repo():
    return AsyncMock()

@pytest.fixture
def mock_notification_service():
    return AsyncMock()

@pytest.fixture
def ranking_service(mock_repo, mock_user_repo, mock_notification_service):
    return RankingService(mock_repo, mock_user_repo, mock_notification_service)

@pytest.mark.asyncio
async def test_invite_member_sends_notification(ranking_service, mock_repo, mock_user_repo, mock_notification_service):
    # Setup
    team_id = uuid4()
    inviter_id = "inviter_user_id"
    invitee_email = "invitee@example.com"
    invitee_id = "invitee_user_id"

    # Mock data
    mock_team = MagicMock()
    mock_team.team_id = team_id
    mock_team.team_name = "Test Team"
    mock_team.leader_id = inviter_id

    mock_inviter = MagicMock()
    mock_inviter.id = inviter_id
    mock_inviter.username = "Inviter"

    mock_invitee = MagicMock()
    mock_invitee.id = invitee_id
    mock_invitee.email = invitee_email

    mock_invitation = MagicMock()
    mock_invitation.invitation_id = uuid4()
    mock_invitation.email = invitee_email
    mock_invitation.status = "pending"
    mock_invitation.expires_at = datetime.now(UTC)

    # Configure mocks
    mock_repo.get_team_by_id = AsyncMock(return_value=mock_team)
    mock_repo.get_team_members = AsyncMock(return_value=[]) # Empty list means not full
    mock_repo.create_invitation = AsyncMock(return_value=mock_invitation)

    mock_user_repo.get_by_email = AsyncMock(return_value=mock_invitee)
    mock_user_repo.get_by_id = AsyncMock(return_value=mock_inviter)

    # Execute
    invitation_data = TeamInvitationCreate(email=invitee_email)
    await ranking_service.invite_member(team_id, invitation_data, inviter_id)

    # Verify
    mock_notification_service.create_notification.assert_called_once()
    call_args = mock_notification_service.create_notification.call_args[0][0]

    assert call_args.user_id == invitee_id
    assert call_args.type == "team_invitation"
    assert call_args.data["team_name"] == "Test Team"
    assert call_args.data["inviter_name"] == "Inviter"

@pytest.mark.asyncio
async def test_accept_invitation_sends_notification(ranking_service, mock_repo, mock_user_repo, mock_notification_service):
    # Setup
    invitation_id = uuid4()
    user_id = "accepter_user_id"
    inviter_id = "inviter_user_id"
    team_id = uuid4()

    # Mock data
    mock_invitation = MagicMock()
    mock_invitation.invitation_id = invitation_id
    mock_invitation.team_id = team_id
    mock_invitation.invited_by = inviter_id
    mock_invitation.status = "pending"
    mock_invitation.expires_at = datetime.now(UTC)
    # Future expiration to be valid (using now + something large would be safer,
    # but service checks invite.expires_at < now. If we mock it properly...)
    # Actually service check: if invitation.expires_at < datetime.now(UTC):
    # So we need a future date
    from datetime import timedelta
    mock_invitation.expires_at = datetime.now(UTC) + timedelta(days=1)

    mock_team = MagicMock()
    mock_team.team_id = team_id
    mock_team.team_name = "Test Team"

    mock_accepter = MagicMock()
    mock_accepter.id = user_id
    mock_accepter.username = "Accepter"

    # Configure mocks
    mock_repo.get_invitation_by_id = AsyncMock(return_value=mock_invitation)
    mock_repo.get_member_by_user_and_team = AsyncMock(return_value=None) # Not already member
    mock_repo.add_team_member = AsyncMock()
    mock_repo.update_invitation_status = AsyncMock()
    mock_repo.get_team_by_id = AsyncMock(return_value=mock_team)

    mock_user_repo.get_by_id = AsyncMock(return_value=mock_accepter)

    # Execute
    await ranking_service.accept_invitation(invitation_id, user_id)

    # Verify
    mock_notification_service.create_notification.assert_called_once()
    call_args = mock_notification_service.create_notification.call_args[0][0]

    assert call_args.user_id == inviter_id
    assert call_args.type == "team_invitation_accepted"
    assert call_args.data["responder_name"] == "Accepter"
    assert call_args.data["team_name"] == "Test Team"
    assert call_args.data["accepted"] is True
