"""Create all database tables directly using SQLAlchemy."""

import asyncio
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent))

from app.infrastructure.database.base import Base

# Import all models to register them with Base
import app.infrastructure.database.models  # noqa: F401

from app.infrastructure.database.session import engine, init_db_engine


async def create_all_tables():
    """Create all database tables."""
    print("🔧 Creating all database tables...")
    print("=" * 70)

    if engine is None:
        init_db_engine()

    async with engine.begin() as conn:
        # Drop all tables first (optional - comment out if you want to keep existing data)
        # await conn.run_sync(Base.metadata.drop_all)
        # print("✅ Dropped all existing tables")

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Created all tables successfully!")

    print("=" * 70)
    print("\n📊 Tables created:")
    print("   - user, user_stats, user_goal, manual_session, session_history")
    print("   - room, participant, timer, room_reservation")
    print("   - post, comment, post_like")
    print("   - ranking_team, ranking_team_member, ranking_team_invitation")
    print("   - ranking_verification_request")
    print("   - chat_room, chat_member, chat_message")
    print("   - achievement, user_achievement")
    print("   - notification")
    print("=" * 70)
    print("\n🎯 Next step: Run seed script")
    print("   python scripts/database/seed_comprehensive.py")


if __name__ == "__main__":
    asyncio.run(create_all_tables())
