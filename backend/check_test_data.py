"""Check what test data exists in the database."""

import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings


async def check_test_data():
    """Check existing test data."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)

    async with engine.connect() as conn:
        # Check users
        print("=" * 60)
        print("Checking Users")
        print("=" * 60)

        result = await conn.execute(text("""
            SELECT id, username, email
            FROM "user"
            LIMIT 5;
        """))

        users = result.fetchall()
        if users:
            print(f"\n✓ Found {len(users)} users (showing first 5):")
            for user in users:
                print(f"  - {user[1]} ({user[2]}) - ID: {user[0]}")
        else:
            print("✗ No users found")

        # Check friendships
        print("\n" + "=" * 60)
        print("Checking Friendships")
        print("=" * 60)

        result = await conn.execute(text("""
            SELECT COUNT(*) as count
            FROM friend
            WHERE is_blocked = false;
        """))

        count = result.scalar()
        print(f"\n✓ Found {count} active friendships")

        if count > 0:
            result = await conn.execute(text("""
                SELECT f.user_id, u1.username, f.friend_id, u2.username
                FROM friend f
                JOIN "user" u1 ON f.user_id = u1.id
                JOIN "user" u2 ON f.friend_id = u2.id
                WHERE f.is_blocked = false
                LIMIT 3;
            """))

            friendships = result.fetchall()
            print("\nSample friendships:")
            for fs in friendships:
                print(f"  {fs[1]} ↔ {fs[3]}")

        # Check chat rooms
        print("\n" + "=" * 60)
        print("Checking Chat Rooms")
        print("=" * 60)

        result = await conn.execute(text("""
            SELECT COUNT(*) as count
            FROM chat_rooms
            WHERE is_active = true;
        """))

        count = result.scalar()
        print(f"\n✓ Found {count} active chat rooms")

        if count > 0:
            result = await conn.execute(text("""
                SELECT room_id, room_type, room_name
                FROM chat_rooms
                WHERE is_active = true
                LIMIT 3;
            """))

            rooms = result.fetchall()
            print("\nSample rooms:")
            for room in rooms:
                print(f"  {room[2] or '(unnamed)'} ({room[1]}) - ID: {room[0]}")

        # Check presence data
        print("\n" + "=" * 60)
        print("Checking Presence Data")
        print("=" * 60)

        result = await conn.execute(text("""
            SELECT COUNT(*) as count
            FROM user_presence;
        """))

        count = result.scalar()
        print(f"\n✓ Found {count} presence records")

        if count > 0:
            result = await conn.execute(text("""
                SELECT up.id, u.username, up.is_online, up.connection_count
                FROM user_presence up
                JOIN "user" u ON up.id = u.id
                LIMIT 3;
            """))

            presences = result.fetchall()
            print("\nSample presence data:")
            for pres in presences:
                status = "ONLINE" if pres[2] else "OFFLINE"
                print(f"  {pres[1]}: {status} (connections: {pres[3]})")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_test_data())
