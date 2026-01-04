#!/usr/bin/env python3
"""랭킹 계산 로직 검증 스크립트.

이 스크립트는 랭킹 시스템의 계산 로직이 올바르게 작동하는지 검증합니다.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import UTC, datetime, timedelta
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.infrastructure.database.models.ranking import (
    RankingLeaderboard,
    RankingMiniGame,
    RankingSession,
    RankingTeam,
    RankingTeamMember,
)
from app.infrastructure.database.session import AsyncSessionLocal


async def verify_ranking_calculation(db: AsyncSession) -> dict:
    """랭킹 계산 로직 검증."""
    results = {
        "passed": [],
        "failed": [],
        "warnings": [],
    }

    print("🔍 랭킹 계산 로직 검증 시작...\n")

    # 1. 팀 데이터 확인
    print("1️⃣ 팀 데이터 확인 중...")
    teams_result = await db.execute(select(RankingTeam))
    teams = teams_result.scalars().all()
    print(f"   ✅ 총 {len(teams)}개 팀 발견")

    if not teams:
        results["warnings"].append("랭킹 팀이 없습니다. 테스트 데이터가 필요합니다.")
        return results

    team_ids = [team.team_id for team in teams]

    # 2. 세션 데이터 확인
    print("\n2️⃣ 세션 데이터 확인 중...")
    sessions_result = await db.execute(
        select(
            RankingSession.team_id,
            func.sum(RankingSession.duration_minutes).label("total_minutes"),
            func.count(RankingSession.session_id).label("total_sessions"),
        )
        .where(RankingSession.team_id.in_(team_ids))
        .where(RankingSession.success == True)
        .where(RankingSession.session_type == "work")
        .group_by(RankingSession.team_id)
    )
    session_stats = {row.team_id: row for row in sessions_result.all()}
    print(f"   ✅ {len(session_stats)}개 팀의 세션 데이터 확인")

    # 3. 미니게임 점수 확인
    print("\n3️⃣ 미니게임 점수 확인 중...")
    games_result = await db.execute(
        select(
            RankingMiniGame.team_id,
            func.sum(RankingMiniGame.score).label("total_game_score"),
            func.count(RankingMiniGame.game_id).label("game_count"),
        )
        .where(RankingMiniGame.team_id.in_(team_ids))
        .group_by(RankingMiniGame.team_id)
    )
    game_stats = {row.team_id: row for row in games_result.all()}
    print(f"   ✅ {len(game_stats)}개 팀의 미니게임 점수 확인")

    # 4. 멤버 수 확인
    print("\n4️⃣ 팀 멤버 수 확인 중...")
    members_result = await db.execute(
        select(
            RankingTeamMember.team_id,
            func.count(RankingTeamMember.member_id).label("member_count"),
        )
        .where(RankingTeamMember.team_id.in_(team_ids))
        .group_by(RankingTeamMember.team_id)
    )
    member_counts = {row.team_id: row.member_count for row in members_result.all()}
    print(f"   ✅ {len(member_counts)}개 팀의 멤버 수 확인")

    # 5. 점수 계산 로직 검증
    print("\n5️⃣ 점수 계산 로직 검증 중...")
    for team in teams[:5]:  # 처음 5개 팀만 상세 검증
        team_id = team.team_id
        session_stat = session_stats.get(team_id)
        game_stat = game_stats.get(team_id)
        member_count = member_counts.get(team_id, 0)

        total_minutes = float(session_stat.total_minutes or 0) if session_stat else 0
        total_sessions = int(session_stat.total_sessions or 0) if session_stat else 0
        total_game_score = int(game_stat.total_game_score or 0) if game_stat else 0

        # 점수 계산: focus time + session bonus + game score
        calculated_score = (
            total_minutes + (total_sessions * 5) + (total_game_score / 10)
        )
        average_score = calculated_score / member_count if member_count > 0 else 0.0

        print(f"   팀: {team.team_name}")
        print(f"      - 총 집중 시간: {total_minutes:.1f}분")
        print(f"      - 총 세션 수: {total_sessions}개")
        print(f"      - 미니게임 점수: {total_game_score}점")
        print(f"      - 멤버 수: {member_count}명")
        print(f"      - 계산된 점수: {calculated_score:.2f}점")
        print(f"      - 평균 점수: {average_score:.2f}점")

        # 검증: 점수가 음수가 아닌지 확인
        if calculated_score < 0:
            results["failed"].append(
                f"팀 {team.team_name}의 점수가 음수입니다: {calculated_score}"
            )
        else:
            results["passed"].append(
                f"팀 {team.team_name}의 점수 계산 정상: {calculated_score:.2f}점"
            )

    # 6. 리더보드 캐시 확인
    print("\n6️⃣ 리더보드 캐시 확인 중...")
    cache_result = await db.execute(
        select(RankingLeaderboard).where(RankingLeaderboard.period == "weekly")
    )
    cache_entries = cache_result.scalars().all()
    print(f"   ✅ 주간 리더보드 캐시: {len(cache_entries)}개 항목")

    # 7. 기간별 계산 검증
    print("\n7️⃣ 기간별 계산 검증 중...")
    periods = ["weekly", "monthly", "all_time"]
    now = datetime.now(UTC)

    for period in periods:
        if period == "weekly":
            start_date = now - timedelta(days=7)
        elif period == "monthly":
            start_date = now - timedelta(days=30)
        else:  # all_time
            start_date = datetime.min.replace(tzinfo=UTC)

        period_sessions = await db.execute(
            select(func.count(RankingSession.session_id))
            .where(RankingSession.completed_at >= start_date)
            .where(RankingSession.success == True)
        )
        session_count = period_sessions.scalar() or 0
        print(f"   {period}: {session_count}개 세션")

    print("\n✅ 검증 완료!")
    return results


async def main():
    """메인 함수."""
    print("=" * 60)
    print("랭킹 계산 로직 검증 스크립트")
    print("=" * 60)
    print(f"환경: {settings.APP_ENV}")
    print(
        f"데이터베이스: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'local'}\n"
    )

    async with AsyncSessionLocal() as session:
        try:
            results = await verify_ranking_calculation(session)

            print("\n" + "=" * 60)
            print("검증 결과 요약")
            print("=" * 60)
            print(f"✅ 통과: {len(results['passed'])}개")
            print(f"❌ 실패: {len(results['failed'])}개")
            print(f"⚠️  경고: {len(results['warnings'])}개")

            if results["failed"]:
                print("\n❌ 실패한 검증:")
                for failure in results["failed"]:
                    print(f"   - {failure}")

            if results["warnings"]:
                print("\n⚠️  경고:")
                for warning in results["warnings"]:
                    print(f"   - {warning}")

            # Exit code
            if results["failed"]:
                sys.exit(1)
            else:
                sys.exit(0)

        except Exception as e:
            print(f"\n❌ 검증 중 오류 발생: {e}")
            import traceback

            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
