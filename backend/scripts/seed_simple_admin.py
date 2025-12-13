"""Simple seed script - creates admin account only.

Run with: python scripts/seed_simple_admin.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.security import hash_password
from app.infrastructure.database.session import get_db
from app.infrastructure.database.models.user import User
from app.infrastructure.repositories.user_repository import UserRepository
from app.shared.utils.uuid import generate_uuid


async def create_admin():
    """Create admin user if not exists."""
    async for db in get_db():
        try:
            user_repo = UserRepository(db)

            # Check if admin exists
            admin = await user_repo.get_by_email(settings.ADMIN_EMAIL)

            if admin:
                print(f"✅ Admin user already exists: {settings.ADMIN_EMAIL}")
                return

            # Create admin user
            admin = User(
                id=generate_uuid(),
                email=settings.ADMIN_EMAIL,
                username="Admin",
                hashed_password=hash_password("admin123"),
                is_active=True,
                is_verified=True,
                is_admin=True,
                bio="System Administrator",
                total_focus_time=0,
                total_sessions=0,
            )

            db.add(admin)
            await db.commit()

            print(f"✅ Created admin user: {settings.ADMIN_EMAIL}")
            print(f"   Password: admin123")
            print(f"\\n🎉 Setup complete!")
            print(f"\\n📝 Next steps:")
            print(f"   1. Start backend: cd backend && uvicorn app.main:app --reload")
            print(f"   2. Start frontend: cd frontend && npm run dev")
            print(f"   3. Login with admin@focusmate.dev / admin123")
            print(f"   4. Create test data manually through the UI")

        except Exception as e:
            print(f"❌ Error: {e}")
            await db.rollback()
            raise
        finally:
            break


if __name__ == "__main__":
    asyncio.run(create_admin())
