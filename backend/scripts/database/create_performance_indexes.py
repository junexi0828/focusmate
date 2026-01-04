#!/usr/bin/env python3
"""성능 최적화 인덱스 생성 스크립트.

권장 인덱스를 데이터베이스에 생성합니다.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import AsyncSessionLocal


async def create_performance_indexes(db: AsyncSession) -> dict:
    """성능 최적화 인덱스 생성."""
    results = {
        "created": [],
        "skipped": [],
        "errors": [],
    }

    print("🔧 성능 최적화 인덱스 생성 중...\n")

    indexes = [
        {
            "name": "idx_ranking_sessions_team_completed",
            "table": "ranking_sessions",
            "columns": "team_id, completed_at DESC",
            "reason": "랭킹 리더보드 조회 성능 향상",
        },
        {
            "name": "idx_ranking_mini_games_team_played",
            "table": "ranking_mini_games",
            "columns": "team_id, played_at DESC",
            "reason": "미니게임 점수 집계 성능 향상",
        },
        {
            "name": "idx_session_history_user_completed",
            "table": "session_history",
            "columns": "user_id, completed_at DESC",
            "reason": "사용자 통계 조회 성능 향상",
        },
        {
            "name": "idx_chat_messages_room_created",
            "table": "chat_messages",
            "columns": "room_id, created_at DESC",
            "reason": "채팅 메시지 조회 성능 향상",
        },
    ]

    for idx in indexes:
        try:
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
                check_query, {"table_name": idx["table"], "index_name": idx["name"]}
            )
            exists = result.scalar() > 0

            if exists:
                print(f"⏭️  {idx['name']}: 이미 존재함 (건너뜀)")
                results["skipped"].append(idx["name"])
            else:
                # 인덱스 생성
                create_query = text(
                    f"""
                    CREATE INDEX {idx['name']}
                    ON {idx['table']} ({idx['columns']});
                """
                )

                await db.execute(create_query)
                await db.commit()

                print(f"✅ {idx['name']}: 생성 완료")
                print(f"   테이블: {idx['table']}")
                print(f"   컬럼: {idx['columns']}")
                print(f"   이유: {idx['reason']}\n")
                results["created"].append(idx["name"])

        except Exception as e:
            print(f"❌ {idx['name']}: 생성 실패 - {e}\n")
            results["errors"].append({"name": idx["name"], "error": str(e)})
            await db.rollback()

    return results


async def main():
    """메인 함수."""
    print("=" * 60)
    print("성능 최적화 인덱스 생성 스크립트")
    print("=" * 60)
    print()

    async with AsyncSessionLocal() as session:
        try:
            results = await create_performance_indexes(session)

            print("=" * 60)
            print("생성 결과 요약")
            print("=" * 60)
            print(f"✅ 생성됨: {len(results['created'])}개")
            print(f"⏭️  건너뜀: {len(results['skipped'])}개")
            print(f"❌ 실패: {len(results['errors'])}개")

            if results["created"]:
                print("\n✅ 생성된 인덱스:")
                for name in results["created"]:
                    print(f"   - {name}")

            if results["errors"]:
                print("\n❌ 생성 실패한 인덱스:")
                for error in results["errors"]:
                    print(f"   - {error['name']}: {error['error']}")

            print("\n✅ 완료!")
            sys.exit(0)

        except Exception as e:
            print(f"\n❌ 스크립트 실행 중 오류 발생: {e}")
            import traceback

            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
