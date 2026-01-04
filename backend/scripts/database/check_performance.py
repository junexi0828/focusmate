#!/usr/bin/env python3
"""성능 최적화 점검 스크립트.

데이터베이스 인덱스, 쿼리 최적화, N+1 문제 등을 확인합니다.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import AsyncSessionLocal


async def check_indexes(db: AsyncSession) -> dict:
    """데이터베이스 인덱스 확인."""
    results = {
        "indexes": [],
        "missing_indexes": [],
        "recommendations": [],
    }

    print("🔍 데이터베이스 인덱스 확인 중...\n")

    # 주요 테이블의 인덱스 확인
    important_tables = [
        "ranking_sessions",
        "ranking_mini_games",
        "ranking_teams",
        "session_history",
        "chat_messages",
        "chat_rooms",
        "chat_members",
    ]

    for table in important_tables:
        # 테이블의 인덱스 조회
        query = text(
            f"""
            SELECT
                indexname,
                indexdef
            FROM pg_indexes
            WHERE tablename = :table_name
            ORDER BY indexname;
        """
        )

        result = await db.execute(query, {"table_name": table})
        indexes = result.fetchall()

        if indexes:
            print(f"✅ {table}: {len(indexes)}개 인덱스")
            for idx in indexes:
                results["indexes"].append(
                    {
                        "table": table,
                        "name": idx[0],
                        "definition": idx[1],
                    }
                )
        else:
            print(f"⚠️  {table}: 인덱스 없음")
            results["missing_indexes"].append(table)

    # 권장 인덱스 확인
    print("\n📋 권장 인덱스 확인 중...\n")

    recommendations = [
        {
            "table": "ranking_sessions",
            "columns": ["team_id", "completed_at"],
            "name": "idx_ranking_sessions_team_completed",
            "reason": "랭킹 리더보드 조회 성능 향상",
        },
        {
            "table": "ranking_mini_games",
            "columns": ["team_id", "played_at"],
            "name": "idx_ranking_mini_games_team_played",
            "reason": "미니게임 점수 집계 성능 향상",
        },
        {
            "table": "session_history",
            "columns": ["user_id", "completed_at"],
            "name": "idx_session_history_user_completed",
            "reason": "사용자 통계 조회 성능 향상",
        },
        {
            "table": "chat_messages",
            "columns": ["room_id", "created_at"],
            "name": "idx_chat_messages_room_created",
            "reason": "채팅 메시지 조회 성능 향상",
        },
    ]

    for rec in recommendations:
        # 인덱스 존재 여부 확인
        check_query = text(
            f"""
            SELECT COUNT(*)
            FROM pg_indexes
            WHERE tablename = :table_name
            AND indexname = :index_name;
        """
        )

        result = await db.execute(
            check_query, {"table_name": rec["table"], "index_name": rec["name"]}
        )
        exists = result.scalar() > 0

        if not exists:
            print(f"💡 권장: {rec['table']}에 복합 인덱스 추가")
            print(f"   인덱스명: {rec['name']}")
            print(f"   컬럼: {', '.join(rec['columns'])}")
            print(f"   이유: {rec['reason']}")
            print()
            results["recommendations"].append(rec)

    return results


async def check_query_performance(db: AsyncSession) -> dict:
    """쿼리 성능 확인."""
    results = {
        "slow_queries": [],
        "optimizations": [],
    }

    print("🔍 쿼리 성능 확인 중...\n")

    # 주요 쿼리 실행 계획 확인
    test_queries = [
        {
            "name": "랭킹 리더보드 조회",
            "query": """
                SELECT
                    rs.team_id,
                    SUM(rs.duration_minutes) as total_minutes,
                    COUNT(rs.session_id) as total_sessions
                FROM ranking_sessions rs
                WHERE rs.completed_at >= NOW() - INTERVAL '7 days'
                AND rs.success = true
                AND rs.session_type = 'work'
                GROUP BY rs.team_id
                LIMIT 10;
            """,
        },
        {
            "name": "사용자 통계 조회",
            "query": """
                SELECT
                    sh.user_id,
                    SUM(sh.duration_minutes) as total_minutes,
                    COUNT(sh.id) as total_sessions
                FROM session_history sh
                WHERE sh.completed_at >= NOW() - INTERVAL '30 days'
                GROUP BY sh.user_id
                LIMIT 10;
            """,
        },
    ]

    for test in test_queries:
        try:
            # EXPLAIN ANALYZE 실행
            explain_query = text(f"EXPLAIN ANALYZE {test['query']}")
            result = await db.execute(explain_query)
            plan = "\n".join([row[0] for row in result.fetchall()])

            # 실행 계획 분석
            if "Seq Scan" in plan and "Index Scan" not in plan:
                results["optimizations"].append(
                    {
                        "query": test["name"],
                        "issue": "순차 스캔 사용 중 (인덱스 스캔 권장)",
                        "plan": plan,
                    }
                )
                print(f"⚠️  {test['name']}: 순차 스캔 사용 중")
            else:
                print(f"✅ {test['name']}: 인덱스 활용 중")

        except Exception as e:
            print(f"❌ {test['name']}: 쿼리 실행 실패 - {e}")

    return results


async def main():
    """메인 함수."""
    print("=" * 60)
    print("성능 최적화 점검 스크립트")
    print("=" * 60)
    print()

    async with AsyncSessionLocal() as session:
        try:
            # 인덱스 확인
            index_results = await check_indexes(session)

            # 쿼리 성능 확인
            query_results = await check_query_performance(session)

            # 결과 요약
            print("\n" + "=" * 60)
            print("점검 결과 요약")
            print("=" * 60)
            print(f"✅ 확인된 인덱스: {len(index_results['indexes'])}개")
            print(f"⚠️  인덱스 없는 테이블: {len(index_results['missing_indexes'])}개")
            print(f"💡 권장 인덱스: {len(index_results['recommendations'])}개")
            print(f"🔍 쿼리 최적화 제안: {len(query_results['optimizations'])}개")

            if index_results["recommendations"]:
                print("\n💡 권장 인덱스 생성 SQL:")
                for rec in index_results["recommendations"]:
                    columns = ", ".join(rec["columns"])
                    print(f"   CREATE INDEX IF NOT EXISTS {rec['name']}")
                    print(f"   ON {rec['table']} ({columns});")

            if query_results["optimizations"]:
                print("\n⚠️  쿼리 최적화 제안:")
                for opt in query_results["optimizations"]:
                    print(f"   - {opt['query']}: {opt['issue']}")

            print("\n✅ 점검 완료!")
            sys.exit(0)

        except Exception as e:
            print(f"\n❌ 점검 중 오류 발생: {e}")
            import traceback

            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
