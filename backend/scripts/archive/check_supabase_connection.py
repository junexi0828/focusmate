#!/usr/bin/env python3
"""Check Supabase connection and provide troubleshooting info."""

import sys
from pathlib import Path


def check_env_file():
    """Check .env file for Supabase configuration."""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found!")
        return None

    with open(env_path) as f:
        content = f.read()

    # Find DATABASE_URL
    for line in content.split("\n"):
        if line.startswith("DATABASE_URL=") and "supabase" in line.lower():
            url = line.split("=", 1)[1].strip()
            # Remove comments
            if "(" in url:
                url = url.split("(")[0].strip()
            return url

    return None


def test_connection(url):
    """Test database connection."""
    print("🔍 Testing Supabase connection...")
    print(f"📍 Connection String: {url[:60]}...")
    print()

    try:
        import asyncio

        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import create_async_engine

        engine = create_async_engine(url, pool_pre_ping=True)

        async def test():
            try:
                async with engine.begin() as conn:
                    result = await conn.execute(text("SELECT version()"))
                    version = result.scalar()
                    print("✅ Connection successful!")
                    print(f"📊 PostgreSQL version: {version[:80]}")

                    # Check tables
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
                    print(f"📋 Tables in database: {table_count}")

                    await engine.dispose()
                    return True
            except Exception as e:
                print(f"❌ Connection failed: {e}")
                await engine.dispose()
                return False

        return asyncio.run(test())
    except ImportError:
        print("❌ Required packages not installed")
        print("   Run: pip install sqlalchemy asyncpg")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main function."""
    print("=" * 60)
    print("Supabase Connection Checker")
    print("=" * 60)
    print()

    # Check .env file
    url = check_env_file()
    if not url:
        print("❌ Supabase DATABASE_URL not found in .env file")
        print()
        print("💡 To configure Supabase:")
        print("   1. Go to Supabase Dashboard > Settings > Database")
        print("   2. Copy the connection string")
        print("   3. Update .env file with:")
        print(
            "      DATABASE_URL=postgresql+asyncpg://postgres:[PASSWORD]@db.xevhqwaxxlcsqzhmawjr.supabase.co:5432/postgres"
        )
        return 1

    # Test connection
    success = test_connection(url)

    if not success:
        print()
        print("💡 Troubleshooting:")
        print("   1. Verify connection string in Supabase Dashboard")
        print("   2. Check if your IP is whitelisted")
        print("   3. Verify database password")
        print("   4. Try Connection Pooler if IPv4 network:")
        print(
            "      DATABASE_URL=postgresql+asyncpg://postgres.xevhqwaxxlcsqzhmawjr:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres"
        )
        print("   5. Check Supabase project status in dashboard")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
