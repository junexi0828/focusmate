#!/usr/bin/env python3
"""Check which columns exist in user table."""

import asyncio
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings


async def check_columns():
    """Check user table columns."""
    engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True, echo=False)

    async with engine.begin() as conn:
        result = await conn.execute(
            text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = 'user'
                ORDER BY ordinal_position
            """)
        )
        columns = result.fetchall()

        print("Current user table columns:")
        existing_columns = []
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")
            existing_columns.append(col[0])

        print("\nColumns to add:")
        needed_columns = ["password_reset_token", "password_reset_expires", "naver_id", "school", "profile_image"]
        for col in needed_columns:
            if col in existing_columns:
                print(f"  ✅ {col} (already exists)")
            else:
                print(f"  ❌ {col} (missing)")

        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_columns())

