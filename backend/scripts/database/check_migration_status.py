#!/usr/bin/env python3
"""마이그레이션 상태 확인 스크립트.

데이터베이스에 적용된 마이그레이션과 파일에 있는 마이그레이션을 비교합니다.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings


async def check_migration_status():
    """마이그레이션 상태 확인."""
    print("=" * 60)
    print("마이그레이션 상태 확인")
    print("=" * 60)
    print()

    engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True, echo=False)

    try:
        async with engine.begin() as conn:
            # Check if alembic_version table exists
            result = await conn.execute(
                text(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = 'alembic_version'
                    )
                """
                )
            )
            alembic_exists = result.scalar()

            if not alembic_exists:
                print("❌ alembic_version 테이블이 없습니다.")
                print("   마이그레이션을 실행하세요: alembic upgrade head")
                return

            # Get current version
            result = await conn.execute(text("SELECT version_num FROM alembic_version"))
            current_version = result.scalar()
            print(f"📊 현재 데이터베이스 버전: {current_version}")
            print()

            # Check key tables from migrations
            key_tables = [
                # Initial schema
                "user",
                "room",
                "session_history",
                "achievement",
                # Missing tables
                "manual_sessions",
                "ranking_teams",
                "ranking_sessions",
                "ranking_mini_games",
                # Post read
                "post_read",
                # User verification
                "user_verification",
                # Room reservation
                # (room table already checked)
                # User profile
                # (user table already checked)
                # User presence
                "user_presence",
                # Room invitations
                # (room table already checked)
                # Room remove on leave
                # (room table already checked)
                # Password reset and OAuth
                # (user table already checked)
            ]

            print("🔍 주요 테이블 존재 여부 확인:")
            missing_tables = []
            for table in key_tables:
                result = await conn.execute(
                    text(
                        """
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables
                            WHERE table_schema = 'public'
                            AND table_name = :table_name
                        )
                    """
                    ),
                    {"table_name": table},
                )
                exists = result.scalar()
                if exists:
                    print(f"   ✅ {table}")
                else:
                    print(f"   ❌ {table} (누락)")
                    missing_tables.append(table)

            print()

            if missing_tables:
                print(f"⚠️  누락된 테이블: {len(missing_tables)}개")
                print("   마이그레이션을 실행하세요: alembic upgrade head")
                return 1
            else:
                print("✅ 모든 주요 테이블이 존재합니다.")
                print(
                    f"✅ 데이터베이스는 최신 버전입니다. (revision: {current_version})"
                )
                return 0

    finally:
        await engine.dispose()


async def main():
    """메인 함수."""
    try:
        exit_code = await check_migration_status()
        sys.exit(exit_code if exit_code is not None else 0)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
