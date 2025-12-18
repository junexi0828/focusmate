#!/usr/bin/env python3
"""Setup Supabase database connection.

This script helps configure Supabase connection for the Focus Mate backend.
Project Reference: xevhqwaxxlcsqzhmawjr
"""

import os
from pathlib import Path

def get_supabase_connection_string():
    """Get Supabase connection string from user input."""
    print("=" * 60)
    print("Supabase Connection Setup")
    print("=" * 60)
    print(f"Project Reference: xevhqwaxxlcsqzhmawjr")
    print()
    print("To get your Supabase connection string:")
    print("1. Go to https://supabase.com/dashboard/project/xevhqwaxxlcsqzhmawjr")
    print("2. Navigate to Settings > Database")
    print("3. Find 'Connection string' section")
    print("4. Copy the 'URI' or 'Connection pooling' connection string")
    print()

    # Try to get from environment variable first
    supabase_url = os.getenv("SUPABASE_DATABASE_URL")

    if not supabase_url:
        print("Enter your Supabase connection string:")
        print("Format: postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres")
        print("Or: postgresql://postgres:[password]@db.[ref].supabase.co:5432/postgres")
        supabase_url = input("> ").strip()

    if not supabase_url:
        print("❌ No connection string provided")
        return None

    # Convert to asyncpg format if needed
    if supabase_url.startswith("postgresql://"):
        # Replace with asyncpg driver
        supabase_url = supabase_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    return supabase_url

def update_env_file(connection_string: str):
    """Update .env file with Supabase connection string."""
    env_path = Path(".env")

    if not env_path.exists():
        print("❌ .env file not found!")
        return False

    # Read current .env
    with open(env_path, "r") as f:
        lines = f.readlines()

    # Update DATABASE_URL
    updated = False
    new_lines = []
    for line in lines:
        if line.startswith("DATABASE_URL="):
            new_lines.append(f"DATABASE_URL={connection_string}\n")
            updated = True
        else:
            new_lines.append(line)

    if not updated:
        # Add if not found
        new_lines.append(f"\n# Supabase Database\nDATABASE_URL={connection_string}\n")

    # Write back
    with open(env_path, "w") as f:
        f.writelines(new_lines)

    print("✅ .env file updated with Supabase connection string")
    return True

def test_connection(connection_string: str):
    """Test Supabase connection."""
    print("\n🔍 Testing Supabase connection...")

    try:
        import asyncio
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text

        engine = create_async_engine(connection_string)

        async def test():
            async with engine.begin() as conn:
                result = await conn.execute(text("SELECT version()"))
                version = result.scalar()
                print(f"✅ Connection successful!")
                print(f"📊 PostgreSQL version: {version[:80]}")

                # Check tables
                result = await conn.execute(text("""
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                """))
                table_count = result.scalar()
                print(f"📋 Tables in database: {table_count}")

                await engine.dispose()

        asyncio.run(test())
        return True
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Verify your connection string is correct")
        print("   2. Check if your IP is whitelisted in Supabase")
        print("   3. Ensure database password is correct")
        return False

def main():
    """Main setup function."""
    print("🚀 Supabase Database Setup")
    print()

    # Get connection string
    connection_string = get_supabase_connection_string()
    if not connection_string:
        return

    # Update .env file
    if not update_env_file(connection_string):
        return

    # Test connection
    if test_connection(connection_string):
        print("\n✅ Supabase setup complete!")
        print("\n📝 Next steps:")
        print("   1. Run migrations: alembic upgrade head")
        print("   2. Test the connection: python test_db_connection.py")
    else:
        print("\n⚠️  Setup completed but connection test failed")
        print("   Please verify your connection string and try again")

if __name__ == "__main__":
    main()

