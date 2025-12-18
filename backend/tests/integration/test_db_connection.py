#!/usr/bin/env python3
"""Test database connection and show status."""

import asyncio
from app.infrastructure.database.session import engine
from sqlalchemy import text
from app.core.config import settings


async def test_connection():
    """Test database connection and show information."""
    print("🔍 Testing database connection...")
    print(f"📍 DATABASE_URL: {settings.DATABASE_URL[:60]}...")
    print()

    try:
        async with engine.begin() as conn:
            # Test connection
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print("✅ Database connection successful!")
            print(f"📊 PostgreSQL version: {version[:80]}")
            print()

            # Get table count
            result = await conn.execute(
                text(
                    """
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """
                )
            )
            table_count = result.scalar()
            print(f"📋 Total tables: {table_count}")

            # List tables
            if table_count > 0:
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
                print("\n📑 Tables:")
                for i, table in enumerate(tables, 1):
                    print(f"   {i}. {table}")

            # Check alembic version
            try:
                result = await conn.execute(
                    text(
                        """
                    SELECT version_num
                    FROM alembic_version
                """
                    )
                )
                alembic_version = result.scalar()
                print(f"\n🔄 Alembic version: {alembic_version}")
            except Exception:
                print("\n⚠️  Alembic version table not found")

    except Exception as e:
        print(f"❌ Database connection failed!")
        print(f"   Error: {e}")
        print()
        print("💡 Troubleshooting:")
        print("   1. Check if PostgreSQL is running: pg_isready")
        print("   2. Verify DATABASE_URL in .env file")
        print("   3. Check database credentials")
        return False

    return True


if __name__ == "__main__":
    success = asyncio.run(test_connection())
    exit(0 if success else 1)
