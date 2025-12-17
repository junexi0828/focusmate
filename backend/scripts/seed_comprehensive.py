"""Enhanced comprehensive seed data script for beta testing.

Creates complete sample data for ALL implemented features:
- Users (2 admins + 5 regular users)
- Stats (goals, sessions, session history)
- Community (posts, comments, likes)
- Ranking (teams, members, invitations, verifications)
- Chat (rooms, members, messages)
- Achievements (definitions, user achievements)
- Room Management (rooms, participants, timers)
- Notifications (various types)

Run with: python scripts/seed_comprehensive.py
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
import random

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.security import hash_password
from app.infrastructure.database.session import get_db
from app.infrastructure.database.models.user import User
from app.infrastructure.database.models.user_stats import UserGoal, ManualSession
from app.infrastructure.database.models.community import Post, Comment, PostLike
from app.infrastructure.database.models.ranking import (
    RankingTeam,
    RankingTeamMember,
    RankingTeamInvitation,
    RankingVerificationRequest,
)
from app.infrastructure.database.models.chat import ChatRoom, ChatMessage, ChatMember
from app.infrastructure.database.models.achievement import Achievement, UserAchievement
from app.infrastructure.database.models.session_history import SessionHistory
from app.infrastructure.database.models import Room, Participant, Timer, RoomReservation
from app.infrastructure.repositories.room_repository import RoomRepository
from app.infrastructure.repositories.participant_repository import ParticipantRepository
from app.infrastructure.repositories.timer_repository import TimerRepository
from app.infrastructure.repositories.room_reservation_repository import RoomReservationRepository
from app.shared.utils.uuid import generate_uuid


async def seed_comprehensive_data():
    """Create comprehensive seed data for all features."""
    print("🌱 Starting comprehensive seed data creation...")

    async for db in get_db():
        try:
            # 1. Create test users
            print("\n👥 Creating test users...")
            users = []

            # Admin users
            from app.infrastructure.repositories.user_repository import UserRepository
            user_repo = UserRepository(db)

            admin_data = [
                ("junexi@naver.com", "juns", True),
                ("sc82.choi@pknu.ac.kr", "sc82", True),
            ]

            for email, username, is_admin in admin_data:
                existing = await user_repo.get_by_email(email)
                if existing:
                    users.append(existing)
                    print(f"   ⏭️  Admin '{username}' already exists")
                else:
                    user = User(
                        id=str(generate_uuid()),
                        email=email,
                        username=username,
                        hashed_password=hash_password("admin123"),
                        is_active=True,
                        is_verified=True,
                        is_admin=is_admin,
                        total_sessions=random.randint(20, 50),
                        total_focus_time=random.randint(800, 2000),
                    )
                    db.add(user)
                    await db.commit()
                    await db.refresh(user)
                    users.append(user)
                    print(f"   ✅ Created admin: {username} ({email})")

            # Regular users
            regular_users_data = [
                ("user1@test.com", "김도윤"),
                ("user2@test.com", "김지운"),
                ("user3@test.com", "심동혁"),
                ("user4@test.com", "유재성"),
                ("user5@test.com", "김시은"),
            ]

            for email, username in regular_users_data:
                existing = await user_repo.get_by_email(email)
                if existing:
                    users.append(existing)
                    print(f"   ⏭️  User '{username}' already exists")
                    continue
                else:
                    user = User(
                        id=str(generate_uuid()),
                        email=email,
                        username=username,
                        hashed_password=hash_password("password123"),
                        is_active=True,
                        is_verified=True,
                        is_admin=False,
                        total_sessions=random.randint(10, 40),
                        total_focus_time=random.randint(500, 1500),
                    )
                    db.add(user)
                    await db.commit()
                    await db.refresh(user)
                    users.append(user)
                    print(f"   ✅ Created user: {username} ({email})")

            # 2. Create user goals
            print("\n🎯 Creating user goals...")
            for user in users[:4]:  # First 4 users
                goal = UserGoal(
                    id=str(generate_uuid()),
                    user_id=str(user.id),
                    daily_goal_minutes=random.choice([60, 90, 120, 180]),
                    weekly_goal_sessions=random.choice([5, 10, 15, 20]),
                    created_at=datetime.now(timezone.utc),
                )
                db.add(goal)
                await db.commit()
                print(f"   ✅ Created goal for {user.username}")

            # 3. Create manual sessions
            print("\n📝 Creating manual sessions...")
            for user in users[:4]:
                for i in range(random.randint(3, 8)):
                    session = ManualSession(
                        id=str(generate_uuid()),
                        user_id=str(user.id),
                        session_type="focus",
                        duration_minutes=random.choice([25, 30, 45, 60]),
                        completed_at=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 7)),
                        created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 7)),
                    )
                    db.add(session)
                    await db.commit()
                print(f"   ✅ Created sessions for {user.username}")

            # 4. Create community posts
            print("\n📰 Creating community posts...")
            post_data = [
                ("공부 팁 공유", "효과적인 집중 방법을 공유합니다!", "tips", users[0].id),
                ("오늘의 목표", "오늘 3시간 집중하기!", "general", users[2].id),
                ("질문있어요", "포모도로 타이머 사용법 알려주세요", "question", users[3].id),
                ("성공 후기", "한 달 동안 매일 2시간씩 공부했어요!", "success", users[4].id),
                ("스터디 모집", "함께 공부할 팀원 모집합니다", "recruitment", users[5].id),
            ]

            posts = []
            for title, content, category, user_id in post_data:
                post = Post(
                    id=str(generate_uuid()),  # Convert UUID to string
                    user_id=str(user_id),  # Convert UUID to string
                    title=title,
                    content=content,
                    category=category,
                    likes=random.randint(0, 20),
                    comment_count=random.randint(0, 5),
                    is_pinned=False,
                    is_deleted=False,
                    created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 5)),
                )
                db.add(post)
                await db.commit()
                posts.append(post)
                print(f"   ✅ Created post: {title}")

            await db.commit()

            # 5. Create comments
            print("\n💬 Creating comments...")
            for post in posts[:3]:  # First 3 posts
                for i in range(random.randint(1, 3)):
                    comment = Comment(
                        id=str(generate_uuid()),
                        post_id=str(post.id),
                        user_id=str(users[i + 1].id),
                        content=f"좋은 글이네요! 댓글 {i + 1}",
                        likes=random.randint(0, 10),
                        is_deleted=False,
                        created_at=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 24)),
                    )
                    db.add(comment)
                await db.commit()
                print(f"   ✅ Created comments for post: {post.title}")

            # 6. Create post likes
            print("\n❤️  Creating post likes...")
            for post in posts:
                for user in users[:3]:  # First 3 users like posts
                    if random.random() > 0.5:  # 50% chance
                        like = PostLike(
                            id=str(generate_uuid()),
                            post_id=str(post.id),
                            user_id=str(user.id),
                            created_at=datetime.now(timezone.utc),
                        )
                        db.add(like)
            print("   ✅ Created post likes")

            # 7. Create teams
            print("\n🏆 Creating teams...")
            team_data = [
                ("Study Warriors", "general", users[0].id),
                ("Focus Masters", "department", users[2].id),
                ("Deep Work Team", "lab", users[3].id),
            ]

            teams = []
            from sqlalchemy import select
            for name, team_type, leader_id in team_data:
                # Check if team already exists
                existing_team = await db.execute(
                    select(RankingTeam).where(RankingTeam.team_name == name)
                )
                existing = existing_team.scalar_one_or_none()

                if existing:
                    teams.append(existing)
                    print(f"   ⏭️  Team '{name}' already exists")
                else:
                    team = RankingTeam(
                        team_name=name,
                        team_type=team_type,
                        leader_id=leader_id,
                        verification_status="none",
                        mini_game_enabled=True,
                    )
                    db.add(team)
                    await db.commit()
                    await db.refresh(team)
                    teams.append(team)
                    print(f"   ✅ Created team: {name}")

            await db.commit()


            # 8. Create team members
            print("\n👥 Creating team members...")
            for team in teams:
                # Add leader as member
                leader_member = RankingTeamMember(
                    team_id=team.team_id,
                    user_id=team.leader_id,
                    role="leader",
                )
                db.add(leader_member)
                await db.commit()

                # Add other members
                for user in users[3:5]:  # Add 2 members to each team
                    member = RankingTeamMember(
                        team_id=team.team_id,
                        user_id=user.id,
                        role="member",
                    )
                    db.add(member)
                    await db.commit()
                print(f"   ✅ Created members for team: {team.team_name}")

            # 9. Create team invitations
            print("\n📧 Creating team invitations...")
            for team in teams[:2]:  # First 2 teams
                invitation = RankingTeamInvitation(
                    team_id=team.team_id,
                    email=f"newuser{random.randint(1, 100)}@test.com",
                    invited_by=team.leader_id,
                    status="pending",
                    expires_at=datetime.now(timezone.utc) + timedelta(days=7),
                )
                db.add(invitation)
                await db.commit()
                print(f"   ✅ Created invitation for team: {team.team_name}")

            # 10. Create verification requests
            print("\n🎓 Creating verification requests...")
            for team in teams:
                verification = RankingVerificationRequest(
                    team_id=team.team_id,
                    documents={"school_name": f"학교{random.randint(1,3)}", "document_url": "https://example.com/doc.pdf"},
                    status="pending",
                )
                db.add(verification)
                await db.commit()
            print(f"   ✅ Created {len(teams)} verification requests")

            # 10.5. Create session history
            print("\n📊 Creating session history...")
            sessions_created = 0
            now = datetime.now(timezone.utc)

            for user in users:
                # Create 5-15 sessions per user over the past 30 days
                num_sessions = random.randint(5, 15)
                for i in range(num_sessions):
                    days_ago = random.randint(0, 30)
                    session = SessionHistory(
                        id=str(generate_uuid()),
                        user_id=user.id,
                        room_id=str(generate_uuid()),  # Dummy room ID
                        session_type=random.choice(["work", "break"]),
                        duration_minutes=random.choice([25, 30, 45, 50, 60]),
                        completed_at=now - timedelta(days=days_ago, hours=random.randint(0, 23)),
                    )
                    db.add(session)
                    await db.commit()
                    sessions_created += 1
            print(f"   ✅ Created {sessions_created} session records")

            # 11. Create chat rooms
            print("\n💬 Creating chat rooms...")
            chat_rooms = []
            room_names = [("General", "public"), ("Study Tips", "public"), ("Q&A", "public"), ("Team Chat", "private")]

            for name, room_type in room_names:
                room = ChatRoom(
                    room_type=room_type,
                    room_name=name,
                    description=f"{name} 채팅방",
                    is_active=True,
                )
                db.add(room)
                await db.commit()
                await db.refresh(room)
                chat_rooms.append(room)
                print(f"   ✅ Created chat room: {name}")

            # 11.5. Add chat members
            print("\n👥 Adding chat members...")
            members_created = 0

            for i, user in enumerate(users[:5]):  # First 5 users join first chat room
                member = ChatMember(
                    room_id=chat_rooms[0].room_id,
                    user_id=user.id,
                    role="admin" if i == 0 else "member",
                    is_active=True,
                    is_muted=False,
                    unread_count=0,
                )
                db.add(member)
                await db.commit()
                members_created += 1
            print(f"   ✅ Added {members_created} chat members")

            # 12. Create chat messages
            print("\n💬 Creating chat messages...")
            for room in chat_rooms[:2]:  # First 2 rooms
                for i in range(random.randint(5, 10)):
                    message = ChatMessage(
                        room_id=room.room_id,
                        sender_id=users[random.randint(0, len(users)-1)].id,
                        message_type="text",
                        content=f"메시지 {i+1}: 안녕하세요!",
                    )
                    db.add(message)
                    await db.commit()
                print(f"   ✅ Created messages for room: {room.room_name}")

            # 13. Create achievements
            print("\n🏅 Creating achievements...")
            achievement_data = [
                ("First Session", "첫 세션 완료", "sessions", "total_sessions", 1, "🎯"),
                ("10 Sessions", "10개 세션 완료", "sessions", "total_sessions", 10, "🔥"),
                ("Focus Master", "100시간 집중", "time", "total_focus_time", 6000, "⏱️"),
                ("Week Streak", "7일 연속 출석", "streak", "streak_days", 7, "📅"),
                ("Community Star", "10개 게시글 작성", "social", "community_posts", 10, "⭐"),
            ]

            achievements = []
            for name, description, category, req_type, req_value, icon in achievement_data:
                # Check if achievement already exists
                from sqlalchemy import select
                existing = await db.execute(
                    select(Achievement).where(Achievement.name == name)
                )
                existing_achievement = existing.scalar_one_or_none()

                if existing_achievement:
                    achievements.append(existing_achievement)
                    print(f"   ⏭️  Achievement '{name}' already exists")
                    continue

                achievement = Achievement(
                    id=str(generate_uuid()),
                    name=name,
                    description=description,
                    icon=icon,
                    category=category,
                    requirement_type=req_type,
                    requirement_value=req_value,
                    points=10,
                    is_active=True,
                )
                db.add(achievement)
                await db.commit()
                await db.refresh(achievement)
                achievements.append(achievement)
                print(f"   ✅ Created achievement: {name}")

            await db.commit()

            # 14. Create user achievements
            print("\n🎖️  Creating user achievements...")
            for user in users[:3]:  # First 3 users
                for achievement in achievements[:2]:  # First 2 achievements
                    user_achievement = UserAchievement(
                        id=str(generate_uuid()),
                        user_id=user.id,
                        achievement_id=achievement.id,
                        unlocked_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30)),
                        progress=achievement.requirement_value,
                    )
                    db.add(user_achievement)
                    await db.commit()
            print(f"   ✅ Created user achievements")

            await db.commit()

            # ============================================================
            # ADDITIONAL DATA: Rooms, Participants, Timers, Notifications
            # ============================================================

            print("\n" + "="*60)
            print("🔧 Adding additional data...")
            print("="*60)

            # ROOMS
            print("\n🏠 Creating Rooms...")
            from sqlalchemy import select

            sample_rooms = []
            room_data = [
                ("아침 집중방", 25 * 60, 5 * 60, True),
                ("점심 스터디", 30 * 60, 10 * 60, False),
                ("저녁 공부방", 45 * 60, 15 * 60, True),
                ("심야 집중", 50 * 60, 10 * 60, False),
                ("주말 특별방", 60 * 60, 20 * 60, True),
            ]

            for name, work_dur, break_dur, auto_start in room_data:
                existing = await db.execute(
                    select(Room).where(Room.name == name, Room.is_active == True)
                )
                if existing.scalar_one_or_none():
                    print(f"   ⏭️  Room '{name}' already exists")
                    continue

                room = Room(
                    id=str(generate_uuid()),
                    name=name,
                    work_duration=work_dur,
                    break_duration=break_dur,
                    auto_start_break=auto_start,
                )
                db.add(room)
                await db.commit()
                await db.refresh(room)
                sample_rooms.append(room)
                print(f"   ✅ Created room: {name}")

            # Get all rooms for participants
            all_rooms_result = await db.execute(select(Room).where(Room.is_active == True))
            all_rooms = all_rooms_result.scalars().all()
            print(f"✅ Total rooms: {len(all_rooms)}")

            # PARTICIPANTS
            print("\n👥 Creating Participants...")
            participants_count = 0
            for room in all_rooms:
                num_participants = random.randint(2, 4)
                selected_users = random.sample(users, min(num_participants, len(users)))

                for user in selected_users:
                    existing = await db.execute(
                        select(Participant).where(
                            Participant.room_id == room.id,
                            Participant.user_id == user.id
                        )
                    )
                    if existing.scalar_one_or_none():
                        continue

                    participant = Participant(
                        id=str(generate_uuid()),
                        username=user.username,
                        room_id=str(room.id),
                        user_id=str(user.id),
                        joined_at=datetime.now(timezone.utc),
                    )
                    db.add(participant)
                    participants_count += 1

            await db.commit()
            print(f"✅ Created {participants_count} participants")

            # TIMERS
            print("\n⏱️  Creating Timers...")
            timers_count = 0
            for room in all_rooms:
                existing = await db.execute(
                    select(Timer).where(Timer.room_id == room.id)
                )
                if existing.scalar_one_or_none():
                    continue

                timer = Timer(
                    id=str(generate_uuid()),
                    room_id=str(room.id),
                    status="idle",
                    phase="work",
                    duration=room.work_duration,
                    remaining_seconds=room.work_duration,
                    is_auto_start=room.auto_start_break,
                )
                db.add(timer)
                timers_count += 1

            await db.commit()
            print(f"✅ Created {timers_count} timers")

            # NOTIFICATIONS
            print("\n🔔 Creating Notifications...")
            from app.infrastructure.database.models.notification import Notification

            notification_templates = [
                ("새 댓글", "회원님의 게시글에 새 댓글이 달렸습니다", "comment"),
                ("좋아요", "회원님의 게시글을 좋아합니다", "like"),
                ("팀 초대", "새로운 팀에 초대되었습니다", "team_invite"),
                ("업적 달성", "새로운 업적을 달성했습니다!", "achievement"),
                ("예약 알림", "예약한 세션이 곧 시작됩니다", "reservation"),
            ]

            notifications_count = 0
            for user in users:
                num_notifications = random.randint(3, 8)
                for i in range(num_notifications):
                    title, message, notif_type = random.choice(notification_templates)
                    notification = Notification(
                        notification_id=str(generate_uuid()),
                        user_id=str(user.id),
                        title=title,
                        message=message,
                        type=notif_type,
                        is_read=random.choice([True, False, False]),
                        created_at=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 48)),
                    )
                    db.add(notification)
                    notifications_count += 1

            await db.commit()
            print(f"✅ Created {notifications_count} notifications")

            # Summary
            print("\n" + "="*60)
            print("✅ Comprehensive seed data creation completed!")
            print("="*60)
            print(f"\n📊 Summary:")
            print(f"   - Users: {len(users)} (2 admins + {len(users)-2} regular users)")
            print(f"   - Goals: 4")
            print(f"   - Manual Sessions: ~20")
            print(f"   - Session History: {sessions_created}")
            print(f"   - Posts: {len(posts)}")
            print(f"   - Comments: ~6")
            print(f"   - Post Likes: ~10")
            print(f"   - Teams: {len(teams)}")
            print(f"   - Team Members: ~9")
            print(f"   - Invitations: 2")
            print(f"   - Verifications: 3")
            print(f"   - Chat Rooms: {len(chat_rooms)}")
            print(f"   - Chat Members: {members_created}")
            print(f"   - Chat Messages: ~14")
            print(f"   - Achievements: 5")
            print(f"   - User Achievements: ~6")
            print(f"   - Rooms: {len(all_rooms)}")
            print(f"   - Participants: {participants_count}")
            print(f"   - Timers: {timers_count}")
            print(f"   - Notifications: {notifications_count}")

            print(f"\n💡 Test Accounts:")
            print(f"   Admins:")
            print(f"   - junexi@naver.com / admin123 (juns)")
            print(f"   - sc82.choi@pknu.ac.kr / admin123 (sc82)")
            print(f"\n   Users:")
            print(f"   - user1@test.com / password123 (김도윤)")
            print(f"   - user2@test.com / password123 (김지운)")
            print(f"   - user3@test.com / password123 (심동혁)")
            print(f"   - user4@test.com / password123 (유재성)")
            print(f"   - user5@test.com / password123 (김시은)")

            print(f"\n🎯 You can now test all features with realistic data!")
            print("="*60)

            return  # Exit successfully

        except Exception as e:
            await db.rollback()
            print(f"\n❌ Error creating seed data: {e}")
            import traceback
            traceback.print_exc()
            return  # Exit with error


if __name__ == "__main__":
    asyncio.run(seed_comprehensive_data())
