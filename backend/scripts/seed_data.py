"""Seed data script for development.

Creates sample data for testing and development purposes.
Run with: python scripts/seed_data.py
"""

import asyncio
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.infrastructure.database.session import get_db
from app.infrastructure.database.models import (
    Room,
    Participant,
    Timer,
    RoomReservation,
)
from app.infrastructure.database.models.user import User
from app.infrastructure.repositories.room_repository import RoomRepository
from app.infrastructure.repositories.participant_repository import ParticipantRepository
from app.infrastructure.repositories.timer_repository import TimerRepository
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.room_reservation_repository import (
    RoomReservationRepository,
)
from app.shared.utils.uuid import generate_uuid
from app.core.security import hash_password


async def seed_data():
    """Create seed data for development."""
    print("🌱 Starting seed data creation...")

    async for db in get_db():
        try:
            # Get repositories
            user_repo = UserRepository(db)
            room_repo = RoomRepository(db)
            participant_repo = ParticipantRepository(db)
            timer_repo = TimerRepository(db)
            reservation_repo = RoomReservationRepository(db)

            # Find admin user
            admin_user = await user_repo.get_by_email(settings.ADMIN_EMAIL)
            if not admin_user:
                print(f"❌ Admin user ({settings.ADMIN_EMAIL}) not found!")
                print("   Please create admin account first.")
                return

            print(f"✅ Found admin user: {admin_user.email}")

            # Create sample rooms
            print("\n📦 Creating sample rooms...")
            sample_rooms = []
            room_names = [
                "오전 집중 세션",
                "오후 스터디",
                "야간 코딩",
                "주말 프로젝트",
                "팀 미팅",
            ]

            for i, name in enumerate(room_names):
                # Check if room already exists
                existing = await room_repo.get_by_name(name)
                if existing:
                    print(f"   ⏭️  Room '{name}' already exists, skipping...")
                    sample_rooms.append(existing)
                    continue

                room = Room(
                    id=generate_uuid(),
                    name=name,
                    work_duration=25 * 60 if i < 3 else 30 * 60,  # 25 or 30 minutes
                    break_duration=5 * 60 if i < 3 else 10 * 60,  # 5 or 10 minutes
                    auto_start_break=True,
                    is_active=True,
                    host_id=admin_user.id,
                )
                created_room = await room_repo.create(room)
                sample_rooms.append(created_room)
                print(f"   ✅ Created room: {name}")

            # Create sample participants for rooms
            print("\n👥 Creating sample participants...")
            participant_names = ["김철수", "이영희", "박민수", "최지은", "정대현"]

            for room in sample_rooms[:3]:  # First 3 rooms only
                # Admin as host
                # Check if admin is already a participant in this room
                room_participants = await participant_repo.get_by_room_id(room.id, active_only=False)
                admin_is_participant = any(p.user_id == admin_user.id for p in room_participants)

                if not admin_is_participant:
                    host_participant = Participant(
                        id=generate_uuid(),
                        room_id=room.id,
                        user_id=admin_user.id,
                        username=admin_user.username,
                        is_connected=True,
                        is_host=True,
                        joined_at=datetime.now(timezone.utc),
                    )
                    await participant_repo.create(host_participant)
                    print(f"   ✅ Added admin as host to room: {room.name}")

                # Add 2-3 other participants
                for i, name in enumerate(participant_names[:3]):
                    participant = Participant(
                        id=generate_uuid(),
                        room_id=room.id,
                        user_id=None,  # Anonymous participant
                        username=name,
                        is_connected=i < 2,  # First 2 are connected
                        is_host=False,
                        joined_at=datetime.now(timezone.utc) - timedelta(minutes=i * 5),
                    )
                    await participant_repo.create(participant)
                print(f"   ✅ Added participants to room: {room.name}")

            # Create sample timers
            print("\n⏱️  Creating sample timers...")
            for room in sample_rooms[:2]:  # First 2 rooms only
                timer = Timer(
                    id=generate_uuid(),
                    room_id=room.id,
                    state="idle",
                    current_duration=room.work_duration,
                    remaining_seconds=room.work_duration,
                    session_type="work",
                )
                await timer_repo.create(timer)
                print(f"   ✅ Created timer for room: {room.name}")

            # Create sample reservations
            print("\n📅 Creating sample reservations...")
            now = datetime.now(timezone.utc)
            reservation_times = [
                now + timedelta(hours=2),  # 2 hours from now
                now + timedelta(days=1),  # Tomorrow
                now + timedelta(days=2, hours=3),  # Day after tomorrow
            ]

            for i, scheduled_at in enumerate(reservation_times):
                reservation = RoomReservation(
                    id=generate_uuid(),
                    room_id=None,  # Room not created yet
                    user_id=admin_user.id,
                    scheduled_at=scheduled_at,
                    work_duration=25 * 60,
                    break_duration=5 * 60,
                    description=f"샘플 예약 {i + 1}",
                    is_active=True,
                    is_completed=False,
                )
                await reservation_repo.create(reservation)
                print(f"   ✅ Created reservation for {scheduled_at.strftime('%Y-%m-%d %H:%M')}")

            await db.commit()
            print("\n✅ Seed data creation completed!")
            print(f"\n📊 Summary:")
            print(f"   - Rooms: {len(sample_rooms)}")
            print(f"   - Participants: ~{len(participant_names[:3]) * 3}")
            print(f"   - Timers: 2")
            print(f"   - Reservations: {len(reservation_times)}")
            print(f"\n💡 You can now test with admin account: {settings.ADMIN_EMAIL}")

        except Exception as e:
            await db.rollback()
            print(f"\n❌ Error creating seed data: {e}")
            import traceback
            traceback.print_exc()
        finally:
            break


if __name__ == "__main__":
    asyncio.run(seed_data())

