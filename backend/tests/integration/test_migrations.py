"""Test script to verify database migrations."""

import asyncio
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings


async def verify_migrations():
    """Verify that migrations were applied correctly."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)

    async with engine.connect() as conn:
        # Check user_presence table
        print("=" * 60)
        print("Checking user_presence table...")
        print("=" * 60)

        result = await conn.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'user_presence'
            ORDER BY ordinal_position;
        """))

        presence_columns = result.fetchall()
        if presence_columns:
            print("✓ user_presence table exists")
            print("\nColumns:")
            for col in presence_columns:
                print(f"  - {col[0]}: {col[1]} (nullable: {col[2]})")
        else:
            print("✗ user_presence table NOT found")

        # Check chat_rooms invitation fields
        print("\n" + "=" * 60)
        print("Checking chat_rooms invitation fields...")
        print("=" * 60)

        result = await conn.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'chat_rooms'
            AND column_name LIKE 'invitation%'
            ORDER BY ordinal_position;
        """))

        invitation_columns = result.fetchall()
        if invitation_columns:
            print("✓ Invitation fields added to chat_rooms")
            print("\nInvitation columns:")
            for col in invitation_columns:
                print(f"  - {col[0]}: {col[1]} (nullable: {col[2]})")
        else:
            print("✗ Invitation fields NOT found in chat_rooms")

        # Check indexes
        print("\n" + "=" * 60)
        print("Checking indexes...")
        print("=" * 60)

        result = await conn.execute(text("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename IN ('user_presence', 'chat_rooms')
            AND indexname NOT LIKE '%pkey%'
            ORDER BY tablename, indexname;
        """))

        indexes = result.fetchall()
        if indexes:
            print("Indexes found:")
            for idx in indexes:
                print(f"\n  {idx[0]}:")
                print(f"    {idx[1]}")
        else:
            print("No custom indexes found")

        print("\n" + "=" * 60)
        print("Migration verification complete!")
        print("=" * 60)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(verify_migrations())
