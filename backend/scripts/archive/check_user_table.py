#!/usr/bin/env python3
"""Check if user table exists and has data."""

import asyncio
import sys
from pathlib import Path


# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings


async def check_user_table():
    """Check user table existence and data."""
    print("=" * 60)
    print("User Table Checker")
    print("=" * 60)
    print()

    print(f"📍 Database URL: {settings.DATABASE_URL.split('@')[0]}@...")
    print()

    try:
        engine = create_async_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            echo=False
        )

        async with engine.begin() as conn:
            # 1. Check if user table exists
            print("1️⃣ Checking if 'user' table exists...")
            result = await conn.execute(
                text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = 'user'
                    )
                """)
            )
            table_exists = result.scalar()

            if not table_exists:
                print("❌ 'user' table does NOT exist!")
                print()
                print("💡 Solution:")
                print("   Run database migrations:")
                print("   cd backend && alembic upgrade head")
                await engine.dispose()
                return False

            print("✅ 'user' table exists")
            print()

            # 2. Check table structure
            print("2️⃣ Checking 'user' table structure...")
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

            print(f"   Found {len(columns)} columns:")
            for col in columns[:10]:  # Show first 10 columns
                print(f"   - {col[0]} ({col[1]})")
            if len(columns) > 10:
                print(f"   ... and {len(columns) - 10} more columns")
            print()

            # 3. Check row count
            print("3️⃣ Checking user data...")
            result = await conn.execute(
                text('SELECT COUNT(*) FROM "user"')
            )
            user_count = result.scalar()

            print(f"   Total users: {user_count}")
            print()

            if user_count == 0:
                print("⚠️  No users found in database!")
                print()
                print("💡 Solution:")
                print("   Run seed script to create test users:")
                print("   cd backend && python scripts/seed_comprehensive.py")
            else:
                # 4. Show sample users (without passwords)
                print("4️⃣ Sample users (first 5):")
                result = await conn.execute(
                    text("""
                        SELECT id, email, username, is_active, is_verified, created_at
                        FROM "user"
                        ORDER BY created_at DESC
                        LIMIT 5
                    """)
                )
                users = result.fetchall()

                for user in users:
                    print(f"   - {user[1]} ({user[2]}) - Active: {user[3]}, Verified: {user[4]}")
                print()

            # 5. Check for login-related columns
            print("5️⃣ Checking login-related columns...")
            required_columns = ["email", "hashed_password", "username", "is_active"]
            result = await conn.execute(
                text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                    AND table_name = 'user'
                """)
            )
            existing_columns = [row[0] for row in result.fetchall()]

            missing_columns = [col for col in required_columns if col not in existing_columns]

            if missing_columns:
                print(f"❌ Missing columns: {', '.join(missing_columns)}")
                print()
                print("💡 Solution:")
                print("   Run database migrations:")
                print("   cd backend && alembic upgrade head")
            else:
                print("✅ All required login columns exist")
                print(f"   Required columns: {', '.join(required_columns)}")
                print()

            await engine.dispose()

            print("=" * 60)
            if user_count > 0 and not missing_columns:
                print("✅ User table is healthy and ready for login!")
            elif user_count == 0:
                print("⚠️  User table exists but has no data")
            else:
                print("⚠️  User table has issues")
            print("=" * 60)

            return True

    except Exception as e:
        print(f"❌ Error checking user table: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(check_user_table())
    sys.exit(0 if success else 1)

