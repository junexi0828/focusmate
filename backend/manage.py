#!/usr/bin/env python3
"""Focus Mate Backend - Management Script

Unified management script for server, testing, migrations, and database management.

Usage:
    python manage.py [command] [options]

Commands:
    runserver      - Run development server
    test           - Run tests
    migrate        - Create database migration
    upgrade        - Apply migrations
    downgrade      - Rollback migrations
    reset-db       - Reset database
    shell          - Start Python shell
    check          - Code quality check (lint, type check)
    seed           - Generate test data
    health         - Health check

Examples:
    python manage.py runserver              # Start dev server
    python manage.py runserver --port 9000  # Change port
    python manage.py test                   # Run all tests
    python manage.py test tests/test_auth.py  # Run specific test
    python manage.py migrate "add user table"  # Create migration
    python manage.py upgrade                # Apply migrations
    python manage.py reset-db               # Reset & recreate DB
    python manage.py seed                   # Generate test data
    python manage.py check                  # Code quality check
"""

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def print_banner(text: str):
    """Print banner"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def runserver(host: str = "0.0.0.0", port: int = 8000, reload: bool = True):
    """Run development server"""
    import uvicorn

    print_banner("Focus Mate Backend Server")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Reload: {reload}")
    print(
        f"API Docs: http://{host if host != '0.0.0.0' else 'localhost'}:{port}/docs\n"
    )

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


def test(path: str = "tests/", verbose: bool = False):
    """Run tests"""
    import subprocess

    print_banner("Running Tests")

    cmd = ["pytest", path]
    if verbose:
        cmd.append("-v")
    cmd.extend(["--cov=app", "--cov-report=term-missing"])

    result = subprocess.run(cmd)
    sys.exit(result.returncode)


def migrate(message: str):
    """Create Alembic migration"""
    import subprocess

    if not message:
        print("Error: Migration message is required")
        print('Usage: python manage.py migrate "your message"')
        sys.exit(1)

    print_banner("Creating Database Migration")
    print(f"Message: {message}\n")

    result = subprocess.run(["alembic", "revision", "--autogenerate", "-m", message])

    if result.returncode == 0:
        print("\nMigration created successfully")
        print("Run 'python manage.py upgrade' to apply migration")
    else:
        print("\nMigration creation failed")
        sys.exit(1)


def upgrade(revision: str = "head"):
    """Apply migrations"""
    import subprocess

    print_banner("Applying Database Migrations")
    print(f"Target: {revision}\n")

    result = subprocess.run(["alembic", "upgrade", revision])

    if result.returncode == 0:
        print("\nMigration applied successfully")
    else:
        print("\nMigration failed")
        sys.exit(1)


def downgrade(revision: str = "-1"):
    """Rollback migration"""
    import subprocess

    print_banner("Rolling Back Database Migration")
    print(f"Target: {revision}\n")

    result = subprocess.run(["alembic", "downgrade", revision])

    if result.returncode == 0:
        print("\nMigration rolled back successfully")
    else:
        print("\nRollback failed")
        sys.exit(1)


async def _reset_db():
    """Reset database (internal function)"""
    from app.infrastructure.database.session import engine
    from app.infrastructure.database.base import Base

    print("Dropping all tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    print("Tables dropped")

    print("Creating all tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Tables created")

    await engine.dispose()


def reset_db(confirm: bool = False):
    """Reset database"""
    print_banner("Database Reset")

    if not confirm:
        response = input(
            "Are you sure you want to reset the database? This will delete all data. (yes/no): "
        )
        if response.lower() != "yes":
            print("Database reset cancelled")
            return

    asyncio.run(_reset_db())
    print("\nDatabase reset successfully")


async def _seed_data():
    """Generate test data (internal function)"""
    from datetime import datetime, timedelta, timezone
    from uuid import uuid4
    from app.infrastructure.database.session import AsyncSessionLocal
    from app.infrastructure.database.models import (
        Room,
        Participant,
        Timer,
        RoomReservation,
        SessionHistory,
        Achievement,
        UserAchievement,
        Post,
        Comment,
        PostLike,
        CommentLike,
        Conversation,
        Message,
    )
    from app.infrastructure.database.models.user import User
    from app.infrastructure.database.models.ranking import (
        RankingTeam,
        RankingTeamMember,
        RankingSession,
        RankingMiniGame,
    )
    from app.infrastructure.repositories.room_repository import RoomRepository
    from app.infrastructure.repositories.participant_repository import (
        ParticipantRepository,
    )
    from app.infrastructure.repositories.timer_repository import TimerRepository
    from app.infrastructure.repositories.user_repository import UserRepository
    from app.infrastructure.repositories.room_reservation_repository import (
        RoomReservationRepository,
    )
    from app.infrastructure.repositories.session_history_repository import (
        SessionHistoryRepository,
    )
    from app.infrastructure.repositories.achievement_repository import (
        AchievementRepository,
        UserAchievementRepository,
    )
    from app.infrastructure.repositories.community_repository import (
        PostRepository,
        CommentRepository,
        PostLikeRepository,
        CommentLikeRepository,
    )
    from app.infrastructure.repositories.messaging_repository import (
        ConversationRepository,
        MessageRepository,
    )
    from app.infrastructure.repositories.ranking_repository import RankingRepository
    from app.core.security import hash_password
    from app.core.config import settings
    from app.shared.utils.uuid import generate_uuid
    from app.shared.constants.timer import TimerStatus, TimerPhase

    async with AsyncSessionLocal() as session:
        try:
            # Get repositories
            user_repo = UserRepository(session)
            room_repo = RoomRepository(session)
            participant_repo = ParticipantRepository(session)
            timer_repo = TimerRepository(session)
            reservation_repo = RoomReservationRepository(session)
            session_history_repo = SessionHistoryRepository(session)
            achievement_repo = AchievementRepository(session)
            user_achievement_repo = UserAchievementRepository(session)
            post_repo = PostRepository(session)
            comment_repo = CommentRepository(session)
            post_like_repo = PostLikeRepository(session)
            comment_like_repo = CommentLikeRepository(session)
            conversation_repo = ConversationRepository(session)
            message_repo = MessageRepository(session)
            ranking_repo = RankingRepository(session)

            # Find admin user
            admin_user = await user_repo.get_by_email(settings.ADMIN_EMAIL)
            if not admin_user:
                print(f"❌ Admin user ({settings.ADMIN_EMAIL}) not found!")
                print("   Please create admin account first.")
                print("   You can register at: POST /api/v1/auth/register")
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
                    work_duration=(
                        25 * 60 if i < 3 else 30 * 60
                    ),  # 25 or 30 minutes in seconds
                    break_duration=(
                        5 * 60 if i < 3 else 10 * 60
                    ),  # 5 or 10 minutes in seconds
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
                room_participants = await participant_repo.get_by_room_id(
                    room.id, active_only=False
                )
                admin_is_participant = any(
                    p.user_id == admin_user.id for p in room_participants
                )

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
                # Check if timer already exists
                existing_timer = await timer_repo.get_by_room_id(room.id)
                if existing_timer:
                    print(
                        f"   ⏭️  Timer for room '{room.name}' already exists, skipping..."
                    )
                    continue

                timer = Timer(
                    id=generate_uuid(),
                    room_id=room.id,
                    status=TimerStatus.IDLE.value,
                    phase=TimerPhase.WORK.value,
                    duration=room.work_duration,
                    remaining_seconds=room.work_duration,
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
                print(
                    f"   ✅ Created reservation for {scheduled_at.strftime('%Y-%m-%d %H:%M')}"
                )

            # Create sample session history (for statistics)
            print("\n📊 Creating sample session history...")
            now = datetime.now(timezone.utc)
            session_types = ["work", "break"]
            for i in range(20):  # Create 20 past sessions
                session_date = now - timedelta(days=i // 2, hours=i % 12)
                session = SessionHistory(
                    id=generate_uuid(),
                    user_id=admin_user.id,
                    room_id=(
                        sample_rooms[i % len(sample_rooms)].id
                        if sample_rooms
                        else generate_uuid()
                    ),
                    session_type=session_types[i % 2],
                    duration_minutes=25 if session_types[i % 2] == "work" else 5,
                    completed_at=session_date,
                )
                await session_history_repo.create(session)
            print(f"   ✅ Created 20 session history records")

            # Update user statistics
            admin_user.total_sessions = 20
            admin_user.total_focus_time = 20 * 25  # 20 work sessions * 25 minutes
            await user_repo.update(admin_user)
            print(f"   ✅ Updated admin user statistics")

            # Create sample achievements
            print("\n🏆 Creating sample achievements...")
            achievement_definitions = [
                {
                    "name": "첫 집중",
                    "description": "첫 번째 집중 세션 완료",
                    "category": "sessions",
                    "requirement_type": "total_sessions",
                    "requirement_value": 1,
                    "points": 10,
                },
                {
                    "name": "열정의 시작",
                    "description": "10회 집중 세션 완료",
                    "category": "sessions",
                    "requirement_type": "total_sessions",
                    "requirement_value": 10,
                    "points": 50,
                },
                {
                    "name": "집중 마스터",
                    "description": "50회 집중 세션 완료",
                    "category": "sessions",
                    "requirement_type": "total_sessions",
                    "requirement_value": 50,
                    "points": 200,
                },
                {
                    "name": "시간의 주인",
                    "description": "총 100분 집중",
                    "category": "time",
                    "requirement_type": "total_focus_time",
                    "requirement_value": 100,
                    "points": 100,
                },
                {
                    "name": "불굴의 의지",
                    "description": "총 500분 집중",
                    "category": "time",
                    "requirement_type": "total_focus_time",
                    "requirement_value": 500,
                    "points": 500,
                },
            ]

            created_achievements = []
            for ach_def in achievement_definitions:
                existing = await achievement_repo.get_by_name(ach_def["name"])
                if existing:
                    created_achievements.append(existing)
                    continue

                achievement = Achievement(
                    id=generate_uuid(),
                    name=ach_def["name"],
                    description=ach_def["description"],
                    icon="trophy",
                    category=ach_def["category"],
                    requirement_type=ach_def["requirement_type"],
                    requirement_value=ach_def["requirement_value"],
                    points=ach_def["points"],
                    is_active=True,
                )
                created_achievement = await achievement_repo.create(achievement)
                created_achievements.append(created_achievement)
            print(f"   ✅ Created {len(created_achievements)} achievements")

            # Unlock some achievements for admin
            print("\n🎖️  Unlocking achievements for admin...")
            unlocked_count = 0
            for achievement in created_achievements[:3]:  # Unlock first 3
                existing = await user_achievement_repo.get_by_user_and_achievement(
                    admin_user.id, achievement.id
                )
                if not existing:
                    user_achievement = UserAchievement(
                        id=generate_uuid(),
                        user_id=admin_user.id,
                        achievement_id=achievement.id,
                        unlocked_at=now - timedelta(days=unlocked_count),
                        progress=achievement.requirement_value,
                    )
                    await user_achievement_repo.create(user_achievement)
                    unlocked_count += 1
            print(f"   ✅ Unlocked {unlocked_count} achievements for admin")

            # Create sample community posts
            print("\n📝 Creating sample community posts...")
            post_categories = ["일반", "질문", "팁", "후기"]
            post_titles = [
                "포모도로 기법으로 생산성 향상하기",
                "집중 시간 설정은 어떻게 하시나요?",
                "팀과 함께하는 집중 세션 추천",
                "30일 챌린지 후기",
                "새로운 기능 제안",
            ]
            post_contents = [
                "포모도로 기법을 사용한 지 한 달이 되었는데 정말 효과적입니다!",
                "25분 집중, 5분 휴식이 가장 적합한 것 같아요.",
                "친구들과 함께 하니 더 집중이 잘 되네요.",
                "30일 동안 매일 집중 세션을 완료했습니다!",
                "다크 모드 기능이 추가되면 좋을 것 같습니다.",
            ]

            created_posts = []
            for i, (title, content) in enumerate(zip(post_titles, post_contents)):
                post = Post(
                    id=generate_uuid(),
                    user_id=admin_user.id,
                    title=title,
                    content=content,
                    category=post_categories[i % len(post_categories)],
                    likes=0,
                    comment_count=0,
                    is_pinned=i == 0,  # First post is pinned
                    is_deleted=False,
                )
                created_post = await post_repo.create(post)
                created_posts.append(created_post)
            print(f"   ✅ Created {len(created_posts)} community posts")

            # Create sample comments
            print("\n💬 Creating sample comments...")
            comment_texts = [
                "정말 좋은 글 감사합니다!",
                "저도 같은 경험이 있어요.",
                "추천합니다!",
                "도움이 많이 되었습니다.",
            ]
            for i, post in enumerate(
                created_posts[:3]
            ):  # Add comments to first 3 posts
                for j, comment_text in enumerate(
                    comment_texts[:2]
                ):  # 2 comments per post
                    comment = Comment(
                        id=generate_uuid(),
                        post_id=post.id,
                        user_id=admin_user.id,
                        content=comment_text,
                        parent_comment_id=None,
                        likes=0,
                        is_deleted=False,
                    )
                    await comment_repo.create(comment)
                    # Update post comment count
                    post.comment_count += 1
                    await post_repo.update(post)
            print(f"   ✅ Created comments for posts")

            # Create sample post likes
            print("\n👍 Creating sample post likes...")
            for post in created_posts[:2]:  # Like first 2 posts
                post_like = PostLike(
                    id=generate_uuid(),
                    post_id=post.id,
                    user_id=admin_user.id,
                    created_at=now - timedelta(hours=1),
                )
                await post_like_repo.create(post_like)
                post.likes += 1
                await post_repo.update(post)
            print(f"   ✅ Created post likes")

            # Create sample ranking team
            print("\n🏅 Creating sample ranking team...")
            team_data = {
                "team_id": uuid4(),
                "team_name": "Focus Masters",
                "team_type": "general",
                "verification_status": "verified",
                "leader_id": admin_user.id,
                "mini_game_enabled": True,
            }
            team = await ranking_repo.create_team(team_data)
            print(f"   ✅ Created ranking team: {team.team_name}")

            # Add admin as team member
            member_data = {
                "member_id": uuid4(),
                "team_id": team.team_id,
                "user_id": admin_user.id,
                "role": "leader",
                "joined_at": now - timedelta(days=7),
            }
            await ranking_repo.add_team_member(member_data)
            print(f"   ✅ Added admin as team member")

            # Create sample ranking sessions
            print("\n⏱️  Creating sample ranking sessions...")
            for i in range(5):
                session_data = {
                    "session_id": uuid4(),
                    "team_id": team.team_id,
                    "user_id": admin_user.id,
                    "duration_minutes": 25,
                    "session_type": "work",
                    "success": True,
                    "completed_at": now - timedelta(days=i),
                }
                await ranking_repo.create_session(session_data)
            print(f"   ✅ Created 5 ranking sessions")

            # Create sample mini-game records
            print("\n🎮 Creating sample mini-game records...")
            game_types = ["dino_jump", "dot_collector", "snake"]
            for i, game_type in enumerate(game_types):
                game_data = {
                    "game_id": uuid4(),
                    "team_id": team.team_id,
                    "user_id": admin_user.id,
                    "game_type": game_type,
                    "score": 100 + (i * 50),
                    "success": True,
                    "played_at": now - timedelta(hours=i * 2),
                }
                await ranking_repo.create_mini_game(game_data)
            print(f"   ✅ Created {len(game_types)} mini-game records")

            await session.commit()
            print("\n✅ Seed data creation completed!")
            print(f"\n📊 Summary:")
            print(f"   - Rooms: {len(sample_rooms)}")
            print(f"   - Participants: ~{len(participant_names[:3]) * 3}")
            print(f"   - Timers: 2")
            print(f"   - Reservations: {len(reservation_times)}")
            print(f"   - Session History: 20")
            print(f"   - Achievements: {len(created_achievements)}")
            print(f"   - Unlocked Achievements: {unlocked_count}")
            print(f"   - Community Posts: {len(created_posts)}")
            print(f"   - Ranking Team: 1")
            print(f"   - Ranking Sessions: 5")
            print(f"   - Mini-Games: {len(game_types)}")
            print(f"\n💡 You can now test with admin account: {settings.ADMIN_EMAIL}")

        except Exception as e:
            await session.rollback()
            print(f"\n❌ Error creating seed data: {e}")
            import traceback

            traceback.print_exc()


def seed():
    """Generate test data"""
    print_banner("Seeding Test Data")
    asyncio.run(_seed_data())
    print("\nTest data seeded successfully")


def shell():
    """Start Python shell"""
    import code

    print_banner("Python Shell")
    print("Available imports:")
    print("  - AsyncSessionLocal")
    print("  - settings")
    print("  - models (User, Room, Timer, etc.)")
    print()

    # Import commonly used modules
    from app.infrastructure.database.session import AsyncSessionLocal
    from app.core.config import settings
    import app.infrastructure.database.models as models

    local_vars = {
        "AsyncSessionLocal": AsyncSessionLocal,
        "settings": settings,
        "models": models,
    }

    code.interact(local=local_vars)


def check():
    """Code quality check"""
    import subprocess

    print_banner("Code Quality Check")

    checks = [
        ("Running Ruff linter", ["ruff", "check", "app"]),
        ("Running MyPy type checker", ["mypy", "app"]),
    ]

    failed = []

    for name, cmd in checks:
        print(f"\n{name}...")
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            failed.append(name)
            print(f"{name} failed")
        else:
            print(f"{name} passed")

    if failed:
        print(f"\n{len(failed)} check(s) failed:")
        for check in failed:
            print(f"  - {check}")
        sys.exit(1)
    else:
        print("\nAll checks passed!")


def health():
    """Server health check"""
    import httpx

    print_banner("Health Check")

    url = "http://localhost:8000/health"
    print(f"Checking: {url}")

    try:
        response = httpx.get(url, timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            print("\nServer is healthy")
            print(f"   Service: {data.get('service')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Environment: {data.get('environment')}")
        else:
            print(f"\nServer returned status code: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"\nHealth check failed: {e}")
        print("Make sure the server is running: python manage.py runserver")
        sys.exit(1)


def show_help():
    """Show help"""
    print(__doc__)


def main():
    """Main function"""
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "runserver": lambda: runserver(
            host=args[args.index("--host") + 1] if "--host" in args else "0.0.0.0",
            port=int(args[args.index("--port") + 1]) if "--port" in args else 8000,
            reload="--no-reload" not in args,
        ),
        "test": lambda: test(
            path=args[0] if args else "tests/",
            verbose="-v" in args or "--verbose" in args,
        ),
        "migrate": lambda: migrate(args[0] if args else ""),
        "upgrade": lambda: upgrade(args[0] if args else "head"),
        "downgrade": lambda: downgrade(args[0] if args else "-1"),
        "reset-db": lambda: reset_db(confirm="--yes" in args),
        "seed": seed,
        "shell": shell,
        "check": check,
        "health": health,
        "help": show_help,
        "--help": show_help,
        "-h": show_help,
    }

    if command not in commands:
        print(f"Unknown command: {command}")
        print(f"Run 'python manage.py help' for usage information")
        sys.exit(1)

    try:
        commands[command]()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
