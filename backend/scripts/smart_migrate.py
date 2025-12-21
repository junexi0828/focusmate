#!/usr/bin/env python3
"""Smart migration script that handles existing tables gracefully.

This script checks if tables already exist and initializes Alembic version table
if needed, preventing duplicate table errors.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings


async def check_alembic_version_table() -> bool:
    """Check if alembic_version table exists."""
    engine = create_async_engine(
        settings.DATABASE_URL, pool_pre_ping=True, echo=False
    )
    try:
        async with engine.begin() as conn:
            result = await conn.execute(
                text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = 'alembic_version'
                    )
                """)
            )
            exists = result.scalar()
            return exists
    finally:
        await engine.dispose()


async def check_tables_exist() -> bool:
    """Check if any application tables exist."""
    engine = create_async_engine(
        settings.DATABASE_URL, pool_pre_ping=True, echo=False
    )
    try:
        async with engine.begin() as conn:
            # Check for a few key tables
            result = await conn.execute(
                text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name IN ('user', 'achievement', 'room')
                    )
                """)
            )
            exists = result.scalar()
            return exists
    finally:
        await engine.dispose()


def main():
    """Main migration logic."""
    import subprocess

    print("🔄 Smart Migration Check")
    print("=" * 60)

    # Check if alembic_version table exists
    alembic_exists = asyncio.run(check_alembic_version_table())
    tables_exist = asyncio.run(check_tables_exist())

    print(f"📊 Alembic version table: {'✅ exists' if alembic_exists else '❌ not found'}")
    print(f"📊 Application tables: {'✅ exist' if tables_exist else '❌ not found'}")
    print()

    # If tables exist but alembic_version doesn't, we need to stamp
    if tables_exist and not alembic_exists:
        print("⚠️  Tables exist but Alembic version table is missing.")
        print("   Initializing Alembic version table...")
        print()

        result = subprocess.run(
            ["alembic", "stamp", "head"],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✅ Alembic version table initialized successfully")
            print()
        else:
            print("⚠️  Warning: Failed to initialize Alembic version table")
            print(f"   Error: {result.stderr}")
            print("   Continuing anyway...")
            print()

    # Run migrations
    print("🔄 Running database migrations...")
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print("✅ Database migrations completed successfully")
        return 0
    else:
        # Check if error is about duplicate tables
        if "already exists" in result.stderr or "DuplicateTable" in result.stderr:
            print("⚠️  Warning: Some tables already exist")
            print("   This is normal if the database was set up manually.")
            print("   Attempting to stamp current state...")
            print()

            # Try to stamp head to sync Alembic with current state
            stamp_result = subprocess.run(
                ["alembic", "stamp", "head"],
                cwd=Path(__file__).parent.parent,
                capture_output=True,
                text=True,
            )

            if stamp_result.returncode == 0:
                print("✅ Alembic version synced with existing tables")
                return 0
            else:
                print("⚠️  Could not sync Alembic version")
                print("   You may need to manually run: alembic stamp head")
                return 1
        else:
            print("❌ Migration failed:")
            print(result.stderr)
            return 1


if __name__ == "__main__":
    sys.exit(main())

