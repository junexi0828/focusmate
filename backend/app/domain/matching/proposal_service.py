"""Service layer for matching proposals."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from app.domain.chat.schemas import MatchingChatInfo
from app.domain.chat.service import ChatService
from app.domain.matching.proposal_schemas import ProposalAction, ProposalResponse
from app.infrastructure.database.models.matching import MatchingProposal
from app.infrastructure.repositories.chat_repository import ChatRepository
from app.infrastructure.repositories.matching_pool_repository import (
    MatchingPoolRepository,
)


class ProposalRepository:
    """Repository for matching proposals."""

    def __init__(self, session):
        self.session = session

    async def create_proposal(self, proposal_data: dict) -> MatchingProposal:
        """Create a new proposal."""
        from app.infrastructure.database.models.matching import MatchingProposal

        proposal = MatchingProposal(**proposal_data)
        self.session.add(proposal)
        await self.session.commit()
        await self.session.refresh(proposal)
        return proposal

    async def get_proposal_by_id(
        self, proposal_id: UUID
    ) -> Optional[MatchingProposal]:
        """Get proposal by ID."""
        from sqlalchemy import select

        result = await self.session.execute(
            select(MatchingProposal).where(
                MatchingProposal.proposal_id == proposal_id
            )
        )
        return result.scalar_one_or_none()

    async def get_pool_proposals(self, pool_id: UUID) -> list[MatchingProposal]:
        """Get all proposals for a pool."""
        from sqlalchemy import or_, select

        result = await self.session.execute(
            select(MatchingProposal)
            .where(
                or_(
                    MatchingProposal.pool_id_a == pool_id,
                    MatchingProposal.pool_id_b == pool_id,
                )
            )
            .where(MatchingProposal.final_status == "pending")
        )
        return list(result.scalars().all())

    async def update_proposal(
        self, proposal_id: UUID, update_data: dict
    ) -> Optional[MatchingProposal]:
        """Update proposal."""
        proposal = await self.get_proposal_by_id(proposal_id)
        if not proposal:
            return None

        for key, value in update_data.items():
            setattr(proposal, key, value)

        await self.session.commit()
        await self.session.refresh(proposal)
        return proposal


class ProposalService:
    """Service for matching proposals."""

    def __init__(
        self,
        proposal_repo: ProposalRepository,
        pool_repo: MatchingPoolRepository,
        chat_repo: ChatRepository,
    ):
        self.proposal_repo = proposal_repo
        self.pool_repo = pool_repo
        self.chat_repo = chat_repo

    async def create_proposal(
        self, pool_id_a: UUID, pool_id_b: UUID
    ) -> ProposalResponse:
        """Create a matching proposal."""
        # Verify both pools exist
        pool_a = await self.pool_repo.get_pool_by_id(pool_id_a)
        pool_b = await self.pool_repo.get_pool_by_id(pool_id_b)

        if not pool_a or not pool_b:
            raise ValueError("One or both pools not found")

        if pool_a.status != "waiting" or pool_b.status != "waiting":
            raise ValueError("Both pools must be in waiting status")

        # Create proposal
        proposal_data = {
            "pool_id_a": pool_id_a,
            "pool_id_b": pool_id_b,
            "group_a_status": "pending",
            "group_b_status": "pending",
            "final_status": "pending",
        }

        proposal = await self.proposal_repo.create_proposal(proposal_data)
        return ProposalResponse.model_validate(proposal)

    async def respond_to_proposal(
        self, proposal_id: UUID, pool_id: UUID, action: ProposalAction
    ) -> ProposalResponse:
        """Respond to a proposal (accept/reject)."""
        proposal = await self.proposal_repo.get_proposal_by_id(proposal_id)
        if not proposal:
            raise ValueError("Proposal not found")

        if proposal.final_status != "pending":
            raise ValueError("Proposal already processed")

        # Determine which group is responding
        is_group_a = proposal.pool_id_a == pool_id
        is_group_b = proposal.pool_id_b == pool_id

        if not is_group_a and not is_group_b:
            raise ValueError("Pool not part of this proposal")

        # Update status
        update_data = {}
        if is_group_a:
            update_data["group_a_status"] = action.action + "ed"
        else:
            update_data["group_b_status"] = action.action + "ed"

        # Check if both groups responded
        if action.action == "reject":
            update_data["final_status"] = "rejected"
        elif (
            (is_group_a and proposal.group_b_status == "accepted")
            or (is_group_b and proposal.group_a_status == "accepted")
        ):
            # Both accepted - create chat room
            update_data["final_status"] = "matched"
            update_data["matched_at"] = datetime.utcnow()

            # Create chat room
            chat_room = await self._create_matching_chat_room(proposal)
            update_data["chat_room_id"] = chat_room.room_id

            # Update pool statuses
            await self.pool_repo.update_pool(pool_id_a, {"status": "matched"})
            await self.pool_repo.update_pool(pool_id_b, {"status": "matched"})

        updated_proposal = await self.proposal_repo.update_proposal(
            proposal_id, update_data
        )
        return ProposalResponse.model_validate(updated_proposal)

    async def _create_matching_chat_room(self, proposal: MatchingProposal):
        """Create chat room for matched proposal."""
        pool_a = await self.pool_repo.get_pool_by_id(proposal.pool_id_a)
        pool_b = await self.pool_repo.get_pool_by_id(proposal.pool_id_b)

        # Determine display mode (use most restrictive)
        display_mode = (
            "blind"
            if pool_a.matching_type == "blind" or pool_b.matching_type == "blind"
            else "open"
        )

        # Create chat info
        chat_info = MatchingChatInfo(
            proposal_id=proposal.proposal_id,
            group_a_info={
                "member_ids": pool_a.member_ids,
                "department": pool_a.department,
            },
            group_b_info={
                "member_ids": pool_b.member_ids,
                "department": pool_b.department,
            },
            display_mode=display_mode,
        )

        # Create chat room using ChatService
        chat_service = ChatService(self.chat_repo)
        return await chat_service.create_matching_chat(chat_info)

    async def get_my_proposals(self, user_id: str) -> list[ProposalResponse]:
        """Get proposals for user's pools."""
        # Get user's active pool
        pool = await self.pool_repo.get_user_active_pool(user_id)
        if not pool:
            return []

        proposals = await self.proposal_repo.get_pool_proposals(pool.pool_id)
        return [ProposalResponse.model_validate(p) for p in proposals]
