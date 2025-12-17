"""Optimized matching service with performance improvements.

Improvements:
- Batch processing to reduce DB queries
- In-memory scoring for better performance
- Stable matching algorithm for fairness
- Performance metrics and logging
- Caching for frequently accessed data
"""

import asyncio
import logging
import time
from collections import defaultdict
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

logger = logging.getLogger(__name__)


class OptimizedMatchingPoolService:
    """Optimized service for matching pool with performance improvements."""

    # Cache for department categories (could be loaded from DB/config)
    DEPARTMENT_CATEGORIES = {
        "컴퓨터공학": "공학",
        "전자공학": "공학",
        "기계공학": "공학",
        "경영학": "경영",
        "경제학": "경영",
        "국어국문학": "인문",
        "영어영문학": "인문",
        "심리학": "사회과학",
        "사회학": "사회과학",
        # Add more mappings as needed
    }

    def __init__(
        self,
        pool_repository: MatchingPoolRepository,
        verification_repository: VerificationRepository,
    ):
        self.pool_repository = pool_repository
        self.verification_repository = verification_repository
        self._category_cache = {}

    async def create_pool(
        self, creator_id: str, data: MatchingPoolCreate
    ) -> MatchingPoolResponse:
        """Create a new matching pool (same as original)."""
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
        """Get pool by ID."""
        pool = await self.pool_repository.get_pool_by_id(pool_id)
        if not pool:
            return None

        # Check if user is a member or creator
        if user_id not in pool.member_ids and pool.creator_id != user_id:
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

    def _get_department_category(self, department: str) -> str:
        """Get category for a department (with caching)."""
        if department not in self._category_cache:
            self._category_cache[department] = self.DEPARTMENT_CATEGORIES.get(
                department, "기타"
            )
        return self._category_cache[department]

    def _calculate_match_score(
        self, pool_a: MatchingPoolResponse, pool_b: MatchingPoolResponse
    ) -> int:
        """Calculate optimized matching score between two pools.

        Scoring system:
        - Same department (both prefer): 200 points
        - Same department (one prefers): 100 points
        - Major category match (both prefer): 160 points
        - Major category match (one prefers): 80 points
        - Same grade: +20 points
        - Mutual "any" preference: 60 points

        Returns:
            Match score (higher is better)
        """
        score = 0

        # Check gender compatibility (must be opposite for matching)
        if pool_a.gender == pool_b.gender:
            return 0  # Same gender pools cannot match

        # Department matching
        same_dept = pool_a.department == pool_b.department
        a_prefers_dept = pool_a.preferred_match_type == "same_department"
        b_prefers_dept = pool_b.preferred_match_type == "same_department"

        if same_dept:
            if a_prefers_dept and b_prefers_dept:
                score += 200  # Perfect match
            elif a_prefers_dept or b_prefers_dept:
                score += 100  # Good match
            else:
                score += 50  # Acceptable match

        # Category matching
        a_prefers_cat = pool_a.preferred_match_type == "major_category"
        b_prefers_cat = pool_b.preferred_match_type == "major_category"

        if a_prefers_cat or b_prefers_cat:
            category_match = self._check_major_category_match(pool_a, pool_b)
            if category_match:
                if a_prefers_cat and b_prefers_cat:
                    score += 160  # Both prefer category match
                else:
                    score += 80  # One prefers category match

        # Both prefer "any"
        a_prefers_any = pool_a.preferred_match_type == "any"
        b_prefers_any = pool_b.preferred_match_type == "any"

        if a_prefers_any and b_prefers_any:
            score += 60  # Both flexible

        # Grade proximity bonus
        if pool_a.grade and pool_b.grade:
            grade_diff = abs(int(pool_a.grade) - int(pool_b.grade))
            if grade_diff == 0:
                score += 20
            elif grade_diff == 1:
                score += 10

        return score

    def _check_major_category_match(
        self, pool_a: MatchingPoolResponse, pool_b: MatchingPoolResponse
    ) -> bool:
        """Check if major categories match (optimized)."""
        if not pool_a.preferred_categories or not pool_b.preferred_categories:
            # Fallback to department category
            cat_a = self._get_department_category(pool_a.department)
            cat_b = self._get_department_category(pool_b.department)
            return cat_a == cat_b

        # Check overlap in preferred categories
        return bool(
            set(pool_a.preferred_categories) & set(pool_b.preferred_categories)
        )

    async def find_matching_candidates(
        self, pool: MatchingPoolResponse, all_pools: list[MatchingPoolResponse]
    ) -> list[tuple[MatchingPoolResponse, int]]:
        """Find and score matching candidates (optimized in-memory version).

        Args:
            pool: Pool to find matches for
            all_pools: All available pools (pre-loaded)

        Returns:
            List of (candidate, score) tuples, sorted by score descending
        """
        scored_candidates = []

        # Filter and score candidates in single pass
        for candidate in all_pools:
            # Skip same pool
            if candidate.pool_id == pool.pool_id:
                continue

            # Check member count match
            if candidate.member_count != pool.member_count:
                continue

            # Check gender (must be opposite)
            if candidate.gender == pool.gender:
                continue

            # Calculate score
            score = self._calculate_match_score(pool, candidate)

            if score > 0:
                scored_candidates.append((candidate, score))

        # Sort by score descending
        scored_candidates.sort(key=lambda x: x[1], reverse=True)

        return scored_candidates

    async def run_matching_algorithm(self) -> tuple[list[tuple[UUID, UUID]], dict]:
        """Run optimized matching algorithm with performance metrics.

        Uses stable matching approach:
        1. Load all waiting pools once (batch)
        2. Score all possible pairs in memory
        3. Use greedy algorithm with preference ordering
        4. Track performance metrics

        Returns:
            Tuple of (matches, metrics)
        """
        start_time = time.time()
        metrics = {
            "start_time": start_time,
            "pools_processed": 0,
            "matches_found": 0,
            "scoring_time": 0,
            "total_time": 0,
        }

        # Batch load all waiting pools
        waiting_pools_db = await self.pool_repository.get_waiting_pools()
        waiting_pools = [
            MatchingPoolResponse.model_validate(p) for p in waiting_pools_db
        ]

        metrics["pools_processed"] = len(waiting_pools)

        if len(waiting_pools) < 2:
            metrics["total_time"] = time.time() - start_time
            logger.info(f"Matching completed: {metrics}")
            return [], metrics

        # Group pools by member count and gender for efficient matching
        pools_by_config = defaultdict(list)
        for pool in waiting_pools:
            key = (pool.member_count, pool.gender)
            pools_by_config[key].append(pool)

        # Find matches
        matches = []
        processed_pools = set()

        scoring_start = time.time()

        # Process each member_count separately for efficiency
        for (member_count, gender), pools in pools_by_config.items():
            # Find opposite gender pools with same member count
            opposite_gender = "male" if gender == "female" else "female"
            opposite_key = (member_count, opposite_gender)

            if opposite_key not in pools_by_config:
                continue

            opposite_pools = pools_by_config[opposite_key]

            # Score all possible pairs
            all_scores = []
            for pool in pools:
                if pool.pool_id in processed_pools:
                    continue

                for candidate in opposite_pools:
                    if candidate.pool_id in processed_pools:
                        continue

                    score = self._calculate_match_score(pool, candidate)
                    if score > 0:
                        all_scores.append((pool.pool_id, candidate.pool_id, score))

            # Sort by score and create matches greedily
            all_scores.sort(key=lambda x: x[2], reverse=True)

            for pool_id, candidate_id, score in all_scores:
                if pool_id not in processed_pools and candidate_id not in processed_pools:
                    matches.append((pool_id, candidate_id))
                    processed_pools.add(pool_id)
                    processed_pools.add(candidate_id)
                    metrics["matches_found"] += 1

        metrics["scoring_time"] = time.time() - scoring_start
        metrics["total_time"] = time.time() - start_time

        logger.info(
            f"Matching algorithm completed: "
            f"{metrics['matches_found']} matches from {metrics['pools_processed']} pools "
            f"in {metrics['total_time']:.3f}s (scoring: {metrics['scoring_time']:.3f}s)"
        )

        return matches, metrics

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
