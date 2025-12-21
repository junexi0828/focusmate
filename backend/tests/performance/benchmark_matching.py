"""Standalone performance benchmark for matching algorithm.

This script demonstrates the performance improvements of the optimized matching algorithm.
"""

import random
import time
from collections import defaultdict
from uuid import uuid4


class MockPool:
    """Mock pool for benchmarking."""

    def __init__(
        self,
        pool_id: str,
        member_count: int,
        gender: str,
        department: str,
        grade: int,
        preferred_match_type: str = "any",
        preferred_categories: list[str] = None,
    ):
        self.pool_id = pool_id
        self.member_count = member_count
        self.gender = gender
        self.department = department
        self.grade = str(grade)
        self.preferred_match_type = preferred_match_type
        self.preferred_categories = preferred_categories or []


def generate_test_pools(count: int) -> list[MockPool]:
    """Generate test pools for benchmarking."""
    pools = []
    departments = ["컴퓨터공학", "전자공학", "경영학", "경제학", "심리학"]
    match_types = ["same_department", "major_category", "any"]
    categories = ["공학", "경영", "사회과학"]

    for i in range(count):
        pool = MockPool(
            pool_id=str(uuid4()),
            member_count=(i % 3) + 2,  # 2, 3, or 4 members
            gender="male" if i % 2 == 0 else "female",
            department=departments[i % len(departments)],
            grade=(i % 4) + 1,  # Grades 1-4
            preferred_match_type=match_types[i % len(match_types)],
            preferred_categories=[categories[i % len(categories)]],
        )
        pools.append(pool)

    return pools


def original_algorithm(pools: list[MockPool]) -> tuple[list[tuple[str, str]], float]:
    """Original matching algorithm (simpler scoring)."""
    start_time = time.time()

    matches = []
    processed = set()

    for pool in pools:
        if pool.pool_id in processed:
            continue

        candidates = []
        for candidate in pools:
            if candidate.pool_id == pool.pool_id:
                continue
            if candidate.pool_id in processed:
                continue
            if candidate.member_count != pool.member_count:
                continue
            if candidate.gender == pool.gender:
                continue

            # Basic scoring
            score = 0
            if pool.preferred_match_type == "same_department":
                if pool.department == candidate.department:
                    score += 100
            elif pool.preferred_match_type == "any":
                score += 30

            if candidate.preferred_match_type == "same_department":
                if pool.department == candidate.department:
                    score += 100
            elif candidate.preferred_match_type == "any":
                score += 30

            if score > 0:
                candidates.append((candidate, score))

        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            # Add some randomness for fairness
            top_candidates = candidates[:min(3, len(candidates))]
            best_match = random.choice(top_candidates)[0]
            matches.append((pool.pool_id, best_match.pool_id))
            processed.add(pool.pool_id)
            processed.add(best_match.pool_id)

    execution_time = time.time() - start_time
    return matches, execution_time


def optimized_algorithm(pools: list[MockPool]) -> tuple[list[tuple[str, str]], float]:
    """Optimized matching algorithm with better scoring and grouping."""
    DEPARTMENT_CATEGORIES = {
        "컴퓨터공학": "공학",
        "전자공학": "공학",
        "경영학": "경영",
        "경제학": "경영",
        "심리학": "사회과학",
    }

    def get_category(department: str) -> str:
        return DEPARTMENT_CATEGORIES.get(department, "기타")

    def check_category_match(pool_a: MockPool, pool_b: MockPool) -> bool:
        if pool_a.preferred_categories and pool_b.preferred_categories:
            return bool(set(pool_a.preferred_categories) & set(pool_b.preferred_categories))
        cat_a = get_category(pool_a.department)
        cat_b = get_category(pool_b.department)
        return cat_a == cat_b

    def calculate_score(pool_a: MockPool, pool_b: MockPool) -> int:
        score = 0

        if pool_a.gender == pool_b.gender:
            return 0

        same_dept = pool_a.department == pool_b.department
        a_prefers_dept = pool_a.preferred_match_type == "same_department"
        b_prefers_dept = pool_b.preferred_match_type == "same_department"

        if same_dept:
            if a_prefers_dept and b_prefers_dept:
                score += 200
            elif a_prefers_dept or b_prefers_dept:
                score += 100
            else:
                score += 50

        a_prefers_cat = pool_a.preferred_match_type == "major_category"
        b_prefers_cat = pool_b.preferred_match_type == "major_category"

        if a_prefers_cat or b_prefers_cat:
            if check_category_match(pool_a, pool_b):
                if a_prefers_cat and b_prefers_cat:
                    score += 160
                else:
                    score += 80

        a_prefers_any = pool_a.preferred_match_type == "any"
        b_prefers_any = pool_b.preferred_match_type == "any"

        if a_prefers_any and b_prefers_any:
            score += 60

        if pool_a.grade and pool_b.grade:
            grade_diff = abs(int(pool_a.grade) - int(pool_b.grade))
            if grade_diff == 0:
                score += 20
            elif grade_diff == 1:
                score += 10

        return score

    start_time = time.time()

    # Group pools by configuration for efficient matching
    pools_by_config = defaultdict(list)
    for pool in pools:
        key = (pool.member_count, pool.gender)
        pools_by_config[key].append(pool)

    matches = []
    processed_pools = set()

    # Process each configuration
    for (member_count, gender), pool_list in pools_by_config.items():
        opposite_gender = "male" if gender == "female" else "female"
        opposite_key = (member_count, opposite_gender)

        if opposite_key not in pools_by_config:
            continue

        opposite_pools = pools_by_config[opposite_key]

        # Score all possible pairs
        all_scores = []
        for pool in pool_list:
            if pool.pool_id in processed_pools:
                continue

            for candidate in opposite_pools:
                if candidate.pool_id in processed_pools:
                    continue

                score = calculate_score(pool, candidate)
                if score > 0:
                    all_scores.append((pool.pool_id, candidate.pool_id, score))

        # Sort by score and create matches greedily
        all_scores.sort(key=lambda x: x[2], reverse=True)

        for pool_id, candidate_id, score in all_scores:
            if pool_id not in processed_pools and candidate_id not in processed_pools:
                matches.append((pool_id, candidate_id))
                processed_pools.add(pool_id)
                processed_pools.add(candidate_id)

    execution_time = time.time() - start_time
    return matches, execution_time


def run_benchmark():
    """Run comprehensive performance comparison."""
    test_sizes = [10, 50, 100, 200, 500, 1000]

    print("\n" + "=" * 80)
    print("MATCHING ALGORITHM PERFORMANCE BENCHMARK")
    print("=" * 80 + "\n")

    results = []

    for size in test_sizes:
        print(f"\n--- Testing with {size} pools ---")

        # Generate test data
        pools = generate_test_pools(size)

        # Benchmark original
        original_matches, original_time = original_algorithm(pools)
        print(f"Original:  {original_time:.4f}s, {len(original_matches)} matches")

        # Benchmark optimized
        optimized_matches, optimized_time = optimized_algorithm(pools)
        print(f"Optimized: {optimized_time:.4f}s, {len(optimized_matches)} matches")

        # Calculate improvement
        if original_time > 0:
            speedup = original_time / optimized_time
            improvement = ((original_time - optimized_time) / original_time) * 100
            print(f"Speedup: {speedup:.2f}x ({improvement:.1f}% faster)")
        else:
            speedup = 1.0
            improvement = 0

        results.append({
            "size": size,
            "original_time": original_time,
            "original_matches": len(original_matches),
            "optimized_time": optimized_time,
            "optimized_matches": len(optimized_matches),
            "speedup": speedup,
            "improvement": improvement,
        })

    # Print summary
    print("\n" + "=" * 80)
    print("PERFORMANCE SUMMARY")
    print("=" * 80)
    print(f"{'Pools':<10} {'Original (s)':<15} {'Optimized (s)':<15} {'Speedup':<10} {'Improvement':<12}")
    print("-" * 80)

    for result in results:
        print(
            f"{result['size']:<10} "
            f"{result['original_time']:<15.4f} "
            f"{result['optimized_time']:<15.4f} "
            f"{result['speedup']:<10.2f}x "
            f"{result['improvement']:<12.1f}%"
        )

    # Calculate average improvement
    avg_speedup = sum(r["speedup"] for r in results) / len(results)
    avg_improvement = sum(r["improvement"] for r in results) / len(results)

    print("\n" + "=" * 80)
    print(f"Average Speedup: {avg_speedup:.2f}x")
    print(f"Average Improvement: {avg_improvement:.1f}%")
    print("\n" + "=" * 80)
    print("Key Optimizations:")
    print("1. ✓ Batch processing: Group pools by configuration (member_count, gender)")
    print("2. ✓ In-memory scoring: All scoring done in memory without DB queries")
    print("3. ✓ Optimized matching: Global score-based greedy algorithm")
    print("4. ✓ Better scoring: More sophisticated preference system")
    print("5. ✓ Early filtering: Skip incompatible pools before scoring")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_benchmark()
