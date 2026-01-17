#!/usr/bin/env python3
"""실제 데이터베이스에 존재하는 테이블 확인"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.infrastructure.database.session import engine, init_db_engine


async def check_tables():
    """실제 데이터베이스 테이블 확인"""
    if engine is None:
        init_db_engine()

    async with engine.begin() as conn:
        result = await conn.execute(
            text(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """
            )
        )
        tables = [row[0] for row in result.fetchall()]

        print(f"\n📋 실제 데이터베이스 테이블 목록 ({len(tables)}개):")
        print("=" * 70)
        for i, table in enumerate(tables, 1):
            print(f"  {i:2d}. {table}")
        print("=" * 70)

        return tables


if __name__ == "__main__":
    tables = asyncio.run(check_tables())
    print(f"\n총 {len(tables)}개 테이블이 존재합니다.")

