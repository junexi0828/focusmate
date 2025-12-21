"""Service layer for matching proposals."""

from datetime import datetime
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
    ) -> MatchingProposal | None:
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
    ) -> MatchingProposal | None:
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

    async def get_proposal_statistics(self) -> dict:
        """Get comprehensive proposal statistics."""
        from datetime import datetime, timedelta

        from sqlalchemy import func, select

        from app.infrastructure.database.models.matching import MatchingProposal

        # Total proposals
        total_result = await self.proposal_repo.session.execute(
            select(func.count(MatchingProposal.proposal_id))
        )
        total_proposals = total_result.scalar() or 0

        # By final status
        status_result = await self.proposal_repo.session.execute(
            select(
                MatchingProposal.final_status,
                func.count(MatchingProposal.proposal_id),
            )
            .group_by(MatchingProposal.final_status)
        )
        by_status = {row[0]: row[1] for row in status_result.all()}

        # Matched proposals
        matched_count = by_status.get("matched", 0)
        success_rate = (
            round((matched_count / total_proposals * 100), 2)
            if total_proposals > 0
            else 0.0
        )

        # Average matching time (from created to matched)
        avg_match_time_result = await self.proposal_repo.session.execute(
            select(
                func.avg(
                    func.extract(
                        "epoch",
                        MatchingProposal.matched_at - MatchingProposal.created_at,
                    )
                    / 3600
                )
            ).where(MatchingProposal.matched_at.isnot(None))
        )
        average_matching_time_hours = avg_match_time_result.scalar() or 0.0

        # Min/Max matching time
        min_match_time_result = await self.proposal_repo.session.execute(
            select(
                func.min(
                    func.extract(
                        "epoch",
                        MatchingProposal.matched_at - MatchingProposal.created_at,
                    )
                    / 3600
                )
            ).where(MatchingProposal.matched_at.isnot(None))
        )
        min_matching_time_hours = min_match_time_result.scalar() or 0.0

        max_match_time_result = await self.proposal_repo.session.execute(
            select(
                func.max(
                    func.extract(
                        "epoch",
                        MatchingProposal.matched_at - MatchingProposal.created_at,
                    )
                    / 3600
                )
            ).where(MatchingProposal.matched_at.isnot(None))
        )
        max_matching_time_hours = max_match_time_result.scalar() or 0.0

        # Daily matches (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        date_expr = func.date(MatchingProposal.matched_at).label("date")
        daily_matches_result = await self.proposal_repo.session.execute(
            select(
                date_expr,
                func.count(MatchingProposal.proposal_id).label("count"),
            )
            .where(
                MatchingProposal.matched_at.isnot(None),
                MatchingProposal.matched_at >= thirty_days_ago,
            )
            .group_by(date_expr)
            .order_by(date_expr.desc())
        )
        daily_matches = [
            {"date": str(row.date), "count": row.count}
            for row in daily_matches_result.all()
        ]

        # Weekly matches (last 12 weeks)
        twelve_weeks_ago = datetime.utcnow() - timedelta(weeks=12)
        week_expr = func.date_trunc("week", MatchingProposal.matched_at).label("week")
        weekly_matches_result = await self.proposal_repo.session.execute(
            select(
                week_expr,
                func.count(MatchingProposal.proposal_id).label("count"),
            )
            .where(
                MatchingProposal.matched_at.isnot(None),
                MatchingProposal.matched_at >= twelve_weeks_ago,
            )
            .group_by(week_expr)
            .order_by(week_expr.desc())
        )
        weekly_matches = [
            {"week": str(row.week), "count": row.count}
            for row in weekly_matches_result.all()
        ]

        # Monthly matches (last 12 months)
        twelve_months_ago = datetime.utcnow() - timedelta(days=365)
        month_expr = func.date_trunc("month", MatchingProposal.matched_at).label("month")
        monthly_matches_result = await self.proposal_repo.session.execute(
            select(
                month_expr,
                func.count(MatchingProposal.proposal_id).label("count"),
            )
            .where(
                MatchingProposal.matched_at.isnot(None),
                MatchingProposal.matched_at >= twelve_months_ago,
            )
            .group_by(month_expr)
            .order_by(month_expr.desc())
        )
        monthly_matches = [
            {"month": str(row.month), "count": row.count}
            for row in monthly_matches_result.all()
        ]

        # Acceptance/Rejection rates
        accepted_count = by_status.get("matched", 0)
        rejected_count = by_status.get("rejected", 0)
        pending_count = by_status.get("pending", 0)

        acceptance_rate = (
            round((accepted_count / total_proposals * 100), 2)
            if total_proposals > 0
            else 0.0
        )
        rejection_rate = (
            round((rejected_count / total_proposals * 100), 2)
            if total_proposals > 0
            else 0.0
        )

        return {
            "total_proposals": total_proposals,
            "by_status": by_status,
            "matched_count": matched_count,
            "success_rate": success_rate,
            "acceptance_rate": acceptance_rate,
            "rejection_rate": rejection_rate,
            "pending_count": pending_count,
            "average_matching_time_hours": round(average_matching_time_hours, 2),
            "min_matching_time_hours": round(min_matching_time_hours, 2),
            "max_matching_time_hours": round(max_matching_time_hours, 2),
            "daily_matches": daily_matches,
            "weekly_matches": weekly_matches,
            "monthly_matches": monthly_matches,
        }
