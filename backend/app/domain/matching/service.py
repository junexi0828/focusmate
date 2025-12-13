"""Service layer for matching pool."""

import random
from typing import Optional
from uuid import UUID

from app.domain.matching.schemas import (
    MatchingPoolCreate,
    MatchingPoolResponse,
    MatchingPoolStats,
)
from app.infrastructure.repositories.matching_pool_repository import (
    MatchingPoolRepository,
)
from app.infrastructure.repositories.verification_repository import (
    VerificationRepository,
)


class MatchingPoolService:
    """Service for matching pool business logic."""

    def __init__(
        self,
        pool_repository: MatchingPoolRepository,
        verification_repository: VerificationRepository,
    ):
        self.pool_repository = pool_repository
        self.verification_repository = verification_repository

    async def create_pool(
        self, creator_id: str, data: MatchingPoolCreate
    ) -> MatchingPoolResponse:
        """Create a new matching pool."""
        # Check if creator is verified
        creator_verification = await self.verification_repository.get_verification_by_user(
            creator_id
        )
        if not creator_verification or creator_verification.verification_status != "approved":
            raise ValueError("Creator must be verified")

        # Check if creator already has an active pool
        existing_pool = await self.pool_repository.get_pool_by_creator(creator_id)
        if existing_pool:
            raise ValueError("You already have an active pool")

        # Check if any member is already in a pool
        for member_id in data.member_ids:
            member_pool = await self.pool_repository.get_user_active_pool(member_id)
            if member_pool:
                raise ValueError(f"Member {member_id} is already in another pool")

        # Verify all members
        verifications = []
        for member_id in data.member_ids:
            verification = await self.verification_repository.get_verification_by_user(
                member_id
            )
            if not verification or verification.verification_status != "approved":
                raise ValueError(f"Member {member_id} is not verified")
            verifications.append(verification)

        # Get creator's verification for pool info
        creator_verification = verifications[
            data.member_ids.index(creator_id)
        ] if creator_id in data.member_ids else creator_verification

        # Create pool data
        pool_data = {
            "creator_id": creator_id,
            "member_count": len(data.member_ids),
            "member_ids": data.member_ids,
            "department": creator_verification.department,
            "grade": creator_verification.grade,
            "gender": creator_verification.gender,
            "preferred_match_type": data.preferred_match_type,
            "preferred_categories": data.preferred_categories,
            "matching_type": data.matching_type,
            "message": data.message,
            "status": "waiting",
        }

        pool = await self.pool_repository.create_pool(pool_data)
        return MatchingPoolResponse.model_validate(pool)

    async def get_my_pool(self, user_id: str) -> Optional[MatchingPoolResponse]:
        """Get user's active pool."""
        pool = await self.pool_repository.get_user_active_pool(user_id)
        if not pool:
            return None
        return MatchingPoolResponse.model_validate(pool)

    async def get_pool(
        self, pool_id: UUID, user_id: str
    ) -> Optional[MatchingPoolResponse]:
        """Get pool by ID (user must be a member or admin)."""
        pool = await self.pool_repository.get_pool_by_id(pool_id)
        if not pool:
            return None

        # Check if user is a member or creator
        if user_id not in pool.member_ids and pool.creator_id != user_id:
            # Allow admin access (check via verification repository)
            from app.infrastructure.repositories.user_repository import UserRepository
            user_repo = UserRepository(self.pool_repository.session)
            user = await user_repo.get_by_id(user_id)
            if not user or not getattr(user, "is_admin", False):
                return None

        return MatchingPoolResponse.model_validate(pool)

    async def cancel_pool(self, pool_id: UUID, user_id: str) -> bool:
        """Cancel a pool."""
        pool = await self.pool_repository.get_pool_by_id(pool_id)
        if not pool:
            raise ValueError("Pool not found")

        if pool.creator_id != user_id:
            raise ValueError("Only pool creator can cancel")

        if pool.status != "waiting":
            raise ValueError("Can only cancel waiting pools")

        return await self.pool_repository.delete_pool(pool_id)

    async def get_pool_statistics(self) -> MatchingPoolStats:
        """Get pool statistics."""
        stats = await self.pool_repository.get_pool_statistics()
        return MatchingPoolStats(**stats)

    async def get_comprehensive_statistics(self) -> "ComprehensiveMatchingStats":
        """Get comprehensive matching statistics."""
        from app.domain.matching.schemas import (
            ComprehensiveMatchingStats,
            MatchingProposalStats,
        )
        from app.domain.matching.proposal_service import ProposalService, ProposalRepository
        from app.infrastructure.repositories.chat_repository import ChatRepository

        # Get pool statistics
        pool_stats = await self.get_pool_statistics()

        # Get proposal statistics
        proposal_repo = ProposalRepository(self.pool_repository.session)
        chat_repo = ChatRepository(self.pool_repository.session)
        proposal_service = ProposalService(
            proposal_repo, self.pool_repository, chat_repo
        )
        proposal_stats_dict = await proposal_service.get_proposal_statistics()
        proposal_stats = MatchingProposalStats(**proposal_stats_dict)

        return ComprehensiveMatchingStats(pools=pool_stats, proposals=proposal_stats)

    async def find_matching_candidates(
        self, pool: MatchingPoolResponse
    ) -> list[MatchingPoolResponse]:
        """Find matching candidates for a pool."""
        # Get pools with same member count and opposite gender
        candidates = await self.pool_repository.get_matching_candidates(
            member_count=pool.member_count,
            gender=pool.gender,
            exclude_pool_id=pool.pool_id,
        )

        # Score and filter candidates
        scored_candidates = []
        for candidate in candidates:
            score = self._calculate_match_score(pool, candidate)
            if score > 0:
                scored_candidates.append((candidate, score))

        # Sort by score (descending)
        scored_candidates.sort(key=lambda x: x[1], reverse=True)

        # Return top candidates
        return [
            MatchingPoolResponse.model_validate(c[0]) for c in scored_candidates[:10]
        ]

    def _calculate_match_score(
        self, pool_a: MatchingPoolResponse, pool_b: MatchingPoolResponse
    ) -> int:
        """Calculate matching score between two pools."""
        score = 0

        # Pool A's preferences
        if pool_a.preferred_match_type == "same_department":
            if pool_a.department == pool_b.department:
                score += 100
            elif self._check_major_category_match(pool_a, pool_b):
                score += 50
        elif pool_a.preferred_match_type == "major_category":
            if self._check_major_category_match(pool_a, pool_b):
                score += 80
        else:  # any
            score += 30

        # Pool B's preferences
        if pool_b.preferred_match_type == "same_department":
            if pool_a.department == pool_b.department:
                score += 100
            elif self._check_major_category_match(pool_a, pool_b):
                score += 50
        elif pool_b.preferred_match_type == "major_category":
            if self._check_major_category_match(pool_a, pool_b):
                score += 80
        else:  # any
            score += 30

        return score

    def _check_major_category_match(
        self, pool_a: MatchingPoolResponse, pool_b: MatchingPoolResponse
    ) -> bool:
        """Check if major categories match."""
        if not pool_a.preferred_categories or not pool_b.preferred_categories:
            return False

        # Check if there's any overlap in preferred categories
        return bool(
            set(pool_a.preferred_categories) & set(pool_b.preferred_categories)
        )

    async def run_matching_algorithm(self) -> list[tuple[UUID, UUID]]:
        """Run matching algorithm for all waiting pools."""
        waiting_pools = await self.pool_repository.get_waiting_pools()
        matches = []

        processed_pools = set()

        for pool in waiting_pools:
            if pool.pool_id in processed_pools:
                continue

            pool_response = MatchingPoolResponse.model_validate(pool)
            candidates = await self.find_matching_candidates(pool_response)

            if candidates:
                # Select from top 3 candidates randomly for fairness
                top_candidates = candidates[:3]
                selected = random.choice(top_candidates)

                # Create match pair
                matches.append((pool.pool_id, selected.pool_id))
                processed_pools.add(pool.pool_id)
                processed_pools.add(selected.pool_id)

        return matches
