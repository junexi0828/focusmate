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
from app.infrastructure.database.models.matching import (
    MatchingPool,
    MatchingProposal,
    MatchingChatRoom,
    MatchingChatMember,
    MatchingMessage,
)
from app.infrastructure.database.models.friend import Friend, FriendRequest
from app.infrastructure.database.models.message import Conversation, Message
from app.infrastructure.database.models.verification import UserVerification
from app.infrastructure.repositories.room_repository import RoomRepository
from app.infrastructure.repositories.participant_repository import ParticipantRepository
from app.infrastructure.repositories.timer_repository import TimerRepository
from app.infrastructure.repositories.room_reservation_repository import (
    RoomReservationRepository,
)
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

            # Regular users (extended for comprehensive testing)
            regular_users_data = [
                (
                    "user1@test.com",
                    "김도윤",
                    "부경대학교",
                    "컴퓨터공학과 3학년입니다. 함께 공부해요!",
                ),
                (
                    "user2@test.com",
                    "김지운",
                    "부경대학교",
                    "산업경영공학과 2학년입니다.",
                ),
                ("user3@test.com", "심동혁", "부경대학교", "전자공학과 4학년입니다."),
                ("user4@test.com", "유재성", "부경대학교", "기계공학과 1학년입니다."),
                ("user5@test.com", "김시은", "부경대학교", "화학공학과 3학년입니다."),
                ("user6@test.com", "이민수", "부경대학교", "경영학과 2학년입니다."),
                ("user7@test.com", "박지현", "부경대학교", "컴퓨터공학과 4학년입니다."),
                (
                    "user8@test.com",
                    "최영희",
                    "부경대학교",
                    "산업경영공학과 1학년입니다.",
                ),
            ]

            for user_data in regular_users_data:
                # All user_data entries have 4 elements: (email, username, school, bio)
                email, username, school, bio = user_data

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
                        school=school,
                        bio=bio,
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
                        completed_at=datetime.now(timezone.utc)
                        - timedelta(days=random.randint(0, 7)),
                        created_at=datetime.now(timezone.utc)
                        - timedelta(days=random.randint(0, 7)),
                    )
                    db.add(session)
                    await db.commit()
                print(f"   ✅ Created sessions for {user.username}")

            # 4. Create community posts
            print("\n📰 Creating community posts...")
            post_data = [
                (
                    "공부 팁 공유",
                    "효과적인 집중 방법을 공유합니다!",
                    "tips",
                    users[0].id,
                ),
                ("오늘의 목표", "오늘 3시간 집중하기!", "general", users[2].id),
                (
                    "질문있어요",
                    "포모도로 타이머 사용법 알려주세요",
                    "question",
                    users[3].id,
                ),
                (
                    "성공 후기",
                    "한 달 동안 매일 2시간씩 공부했어요!",
                    "success",
                    users[4].id,
                ),
                (
                    "스터디 모집",
                    "함께 공부할 팀원 모집합니다",
                    "recruitment",
                    users[5].id,
                ),
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
                    created_at=datetime.now(timezone.utc)
                    - timedelta(days=random.randint(0, 5)),
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
                        created_at=datetime.now(timezone.utc)
                        - timedelta(hours=random.randint(1, 24)),
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

            # 7. Create teams (랭킹전)
            print("\n🏆 Creating teams (랭킹전)...")
            # Use regular users (not admins) as team leaders
            regular_users = [u for u in users if not u.is_admin]
            team_data = [
                (
                    "Study Warriors",
                    "general",
                    regular_users[0].id if len(regular_users) > 0 else users[2].id,
                ),
                (
                    "Focus Masters",
                    "department",
                    regular_users[1].id if len(regular_users) > 1 else users[3].id,
                ),
                (
                    "Deep Work Team",
                    "lab",
                    regular_users[2].id if len(regular_users) > 2 else users[4].id,
                ),
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
                    # Generate invite code
                    import secrets
                    import string

                    invite_code = "".join(
                        secrets.choice(string.ascii_uppercase + string.digits)
                        for _ in range(8)
                    )

                    team = RankingTeam(
                        team_name=name,
                        team_type=team_type,
                        leader_id=leader_id,
                        verification_status="none",
                        mini_game_enabled=True,
                        invite_code=invite_code,
                        affiliation_info=(
                            {"school": "부경대학교", "department": team_type}
                            if team_type != "general"
                            else None
                        ),
                    )
                    db.add(team)
                    await db.commit()
                    await db.refresh(team)
                    teams.append(team)
                    print(f"   ✅ Created team: {name} (invite_code: {invite_code})")

            await db.commit()

            # 8. Create team members (모든 사용자를 팀에 참여시키기)
            print("\n👥 Creating team members (랭킹전)...")
            members_created = 0

            # 모든 일반 사용자를 팀에 분배 (각 팀에 최소 4명, 최대 8명)
            for idx, team in enumerate(teams):
                # Add leader as member (if not already added)
                existing_leader_result = await db.execute(
                    select(RankingTeamMember).where(
                        RankingTeamMember.team_id == team.team_id,
                        RankingTeamMember.user_id == team.leader_id,
                    )
                )
                existing_leader = existing_leader_result.scalars().first()
                if not existing_leader:
                    leader_member = RankingTeamMember(
                        team_id=team.team_id,
                        user_id=team.leader_id,
                        role="leader",
                    )
                    db.add(leader_member)
                    members_created += 1

                # Add other members - distribute all regular users across teams
                # 각 팀에 최소 3명 추가 (리더 포함 최소 4명)
                regular_members = [u for u in regular_users if u.id != team.leader_id]

                # 팀별로 사용자 분배 (각 팀에 최대 7명의 추가 멤버, 총 8명까지)
                # 첫 번째 팀: 처음 7명, 두 번째 팀: 다음 7명, 세 번째 팀: 나머지
                start_idx = idx * 7
                end_idx = min(start_idx + 7, len(regular_members))
                members_to_add = regular_members[start_idx:end_idx]

                for user in members_to_add:
                    # Check if member already exists
                    existing_member_result = await db.execute(
                        select(RankingTeamMember).where(
                            RankingTeamMember.team_id == team.team_id,
                            RankingTeamMember.user_id == user.id,
                        )
                    )
                    existing_member = existing_member_result.scalars().first()
                    if not existing_member:
                        member = RankingTeamMember(
                            team_id=team.team_id,
                            user_id=user.id,
                            role="member",
                        )
                        db.add(member)
                        members_created += 1

                await db.commit()
                team_member_count = 1 + len(members_to_add)  # leader + members
                print(
                    f"   ✅ Created {team_member_count} members for team: {team.team_name}"
                )

            print(f"✅ Created {members_created} team members total")

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
                    documents={
                        "school_name": f"학교{random.randint(1,3)}",
                        "document_url": "https://example.com/doc.pdf",
                    },
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
                        completed_at=now
                        - timedelta(days=days_ago, hours=random.randint(0, 23)),
                    )
                    db.add(session)
                    await db.commit()
                    sessions_created += 1
            print(f"   ✅ Created {sessions_created} session records")

            # 11. Create chat rooms
            print("\n💬 Creating chat rooms...")
            chat_rooms = []
            room_names = [
                ("General", "public"),
                ("Study Tips", "public"),
                ("Q&A", "public"),
                ("Team Chat", "private"),
            ]

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
                        sender_id=users[random.randint(0, len(users) - 1)].id,
                        message_type="text",
                        content=f"메시지 {i+1}: 안녕하세요!",
                    )
                    db.add(message)
                    await db.commit()
                print(f"   ✅ Created messages for room: {room.room_name}")

            # 13. Create achievements
            print("\n🏅 Creating achievements...")
            achievement_data = [
                (
                    "First Session",
                    "첫 세션 완료",
                    "sessions",
                    "total_sessions",
                    1,
                    "🎯",
                ),
                (
                    "10 Sessions",
                    "10개 세션 완료",
                    "sessions",
                    "total_sessions",
                    10,
                    "🔥",
                ),
                ("Focus Master", "100시간 집중", "time", "total_focus_time", 6000, "⏱️"),
                ("Week Streak", "7일 연속 출석", "streak", "streak_days", 7, "📅"),
                (
                    "Community Star",
                    "10개 게시글 작성",
                    "social",
                    "community_posts",
                    10,
                    "⭐",
                ),
            ]

            achievements = []
            for (
                name,
                description,
                category,
                req_type,
                req_value,
                icon,
            ) in achievement_data:
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
                        unlocked_at=datetime.now(timezone.utc)
                        - timedelta(days=random.randint(1, 30)),
                        progress=achievement.requirement_value,
                    )
                    db.add(user_achievement)
                    await db.commit()
            print(f"   ✅ Created user achievements")

            await db.commit()

            # ============================================================
            # ADDITIONAL DATA: Rooms, Participants, Timers, Notifications
            # ============================================================

            print("\n" + "=" * 60)
            print("🔧 Adding additional data...")
            print("=" * 60)

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
                existing_result = await db.execute(
                    select(Room).where(Room.name == name, Room.is_active == True)
                )
                if existing_result.scalars().first():
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
            all_rooms_result = await db.execute(
                select(Room).where(Room.is_active == True)
            )
            all_rooms = all_rooms_result.scalars().all()
            print(f"✅ Total rooms: {len(all_rooms)}")

            # PARTICIPANTS
            print("\n👥 Creating Participants...")
            participants_count = 0
            for room in all_rooms:
                num_participants = random.randint(2, 4)
                selected_users = random.sample(users, min(num_participants, len(users)))

                for user in selected_users:
                    existing_result = await db.execute(
                        select(Participant).where(
                            Participant.room_id == room.id,
                            Participant.user_id == user.id,
                        )
                    )
                    if existing_result.scalars().first():
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
                existing_result = await db.execute(
                    select(Timer).where(Timer.room_id == room.id)
                )
                if existing_result.scalars().first():
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
                        created_at=datetime.now(timezone.utc)
                        - timedelta(hours=random.randint(1, 48)),
                    )
                    db.add(notification)
                    notifications_count += 1

            await db.commit()
            print(f"✅ Created {notifications_count} notifications")

            # MATCHING POOLS (핑크캠퍼스) - 모든 사용자 참여
            print("\n💕 Creating Matching Pools (핑크캠퍼스)...")
            from uuid import UUID

            matching_pools = []
            regular_users_for_matching = [u for u in users if not u.is_admin]

            if len(regular_users_for_matching) >= 4:
                departments = [
                    "컴퓨터공학과",
                    "산업경영공학과",
                    "전자공학과",
                    "기계공학과",
                    "화학공학과",
                    "경영학과",
                ]
                grades = ["1학년", "2학년", "3학년", "4학년"]

                # 모든 사용자를 여러 풀로 분배
                # 각 풀은 4-8명의 멤버를 가질 수 있음
                pool_size = 4  # 각 풀의 기본 크기
                num_pools = (
                    len(regular_users_for_matching) + pool_size - 1
                ) // pool_size  # 올림 계산

                for i in range(num_pools):
                    start_idx = i * pool_size
                    end_idx = min(
                        start_idx + pool_size, len(regular_users_for_matching)
                    )
                    pool_users = regular_users_for_matching[start_idx:end_idx]

                    if len(pool_users) < 2:  # 최소 2명 필요
                        break

                    # Convert timezone-aware datetime to naive datetime for database
                    expires_at_naive = (
                        datetime.now(timezone.utc) + timedelta(days=7)
                    ).replace(tzinfo=None)

                    # 성별 분배 (홀수 인덱스는 male, 짝수 인덱스는 female, 마지막은 mixed)
                    if i % 3 == 0:
                        gender = "male"
                    elif i % 3 == 1:
                        gender = "female"
                    else:
                        gender = "mixed"

                    pool = MatchingPool(
                        creator_id=pool_users[0].id,
                        member_count=len(pool_users),
                        member_ids=[u.id for u in pool_users],
                        department=random.choice(departments),
                        grade=random.choice(grades),
                        gender=gender,
                        preferred_match_type=random.choice(
                            ["study", "project", "both"]
                        ),
                        preferred_categories=["study", "project"],
                        matching_type="open",
                        message=f"함께 공부하고 싶어요! (풀 {i+1})",
                        status="waiting",
                        expires_at=expires_at_naive,
                    )
                    db.add(pool)
                    await db.commit()
                    await db.refresh(pool)
                    matching_pools.append(pool)
                    print(
                        f"   ✅ Created matching pool {i+1} ({gender}, {len(pool_users)} members)"
                    )
            else:
                print(
                    f"   ⚠️  Not enough users for matching pools (need 4+, have {len(regular_users_for_matching)})"
                )

            print(f"✅ Created {len(matching_pools)} matching pools")

            # MATCHING PROPOSALS
            print("\n💌 Creating Matching Proposals...")
            proposals_created = 0
            if len(matching_pools) >= 2:
                # Create proposals between different pools
                # 서로 다른 성별의 풀들 간에 제안 생성
                for i in range(min(3, len(matching_pools) - 1)):  # 최대 3개의 제안
                    pool_a = matching_pools[i]
                    pool_b = matching_pools[(i + 1) % len(matching_pools)]

                    # 서로 다른 성별의 풀 간에만 제안 생성
                    if (
                        pool_a.gender != pool_b.gender
                        or pool_a.gender == "mixed"
                        or pool_b.gender == "mixed"
                    ):
                        expires_at_naive = (
                            datetime.now(timezone.utc) + timedelta(hours=24)
                        ).replace(tzinfo=None)
                        proposal = MatchingProposal(
                            pool_id_a=pool_a.pool_id,
                            pool_id_b=pool_b.pool_id,
                            group_a_status="pending",
                            group_b_status="pending",
                            final_status="pending",
                            expires_at=expires_at_naive,
                        )
                        db.add(proposal)
                        await db.commit()
                        proposals_created += 1
                        print(
                            f"   ✅ Created matching proposal between pool {i+1} and {i+2}"
                        )
            print(f"✅ Created {proposals_created} matching proposals")

            # FRIENDS & FRIEND REQUESTS
            print("\n👥 Creating Friends & Friend Requests...")
            friends_created = 0
            friend_requests_created = 0

            # Create friend relationships
            for i in range(min(5, len(users) - 1)):
                user1 = users[i]
                user2 = users[i + 1]
                if user1.is_admin or user2.is_admin:
                    continue

                # Create friend relationship (bidirectional)
                friend1 = Friend(
                    id=str(generate_uuid()),
                    user_id=user1.id,
                    friend_id=user2.id,
                    is_blocked=False,
                )
                friend2 = Friend(
                    id=str(generate_uuid()),
                    user_id=user2.id,
                    friend_id=user1.id,
                    is_blocked=False,
                )
                db.add(friend1)
                db.add(friend2)
                friends_created += 2
                print(
                    f"   ✅ Created friendship: {user1.username} <-> {user2.username}"
                )

            # Create friend requests
            if len(users) >= 4:
                for i in range(2, min(5, len(users))):
                    sender = users[i]
                    receiver = users[(i + 1) % len(users)]
                    if sender.is_admin or receiver.is_admin:
                        continue

                    friend_request = FriendRequest(
                        id=str(generate_uuid()),
                        sender_id=sender.id,
                        receiver_id=receiver.id,
                        status=random.choice(["pending", "accepted", "rejected"]),
                        responded_at=(
                            datetime.now(timezone.utc)
                            - timedelta(days=random.randint(1, 7))
                            if random.random() > 0.3
                            else None
                        ),
                    )
                    db.add(friend_request)
                    friend_requests_created += 1

            await db.commit()
            print(f"✅ Created {friends_created} friend relationships")
            print(f"✅ Created {friend_requests_created} friend requests")

            # USER VERIFICATIONS (학교 인증)
            print("\n🎓 Creating User Verifications...")
            verifications_created = 0
            departments_list = [
                "컴퓨터공학과",
                "산업경영공학과",
                "전자공학과",
                "기계공학과",
                "화학공학과",
                "경영학과",
            ]
            grades_list = ["1학년", "2학년", "3학년", "4학년"]

            for user in users[2:6]:  # First 4 regular users
                if user.is_admin:
                    continue

                # Check if verification already exists
                existing_result = await db.execute(
                    select(UserVerification).where(UserVerification.user_id == user.id)
                )
                if existing_result.scalars().first():
                    continue

                # Convert timezone-aware datetime to naive datetime
                submitted_at_naive = (
                    datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30))
                ).replace(tzinfo=None)
                verified_at_naive = None
                if random.random() > 0.3:
                    verified_at_naive = (
                        datetime.now(timezone.utc)
                        - timedelta(days=random.randint(1, 20))
                    ).replace(tzinfo=None)

                verification = UserVerification(
                    user_id=user.id,
                    school_name=user.school or "부경대학교",
                    department=random.choice(departments_list),
                    major_category=random.choice(["공학", "경영", "자연과학"]),
                    grade=random.choice(grades_list),
                    student_id_encrypted=None,  # Optional
                    gender=random.choice(["male", "female"]),
                    verification_status=random.choice(
                        ["pending", "approved", "rejected"]
                    ),
                    submitted_documents=None,  # Optional
                    admin_note=None,  # Optional
                    badge_visible=True,
                    department_visible=True,
                    submitted_at=submitted_at_naive,
                    verified_at=verified_at_naive,
                )
                db.add(verification)
                verifications_created += 1
            await db.commit()
            print(f"✅ Created {verifications_created} user verifications")

            # CONVERSATIONS & MESSAGES (1:1 메시지)
            print("\n💬 Creating Conversations & Messages...")
            conversations_created = 0
            messages_created = 0

            # Create conversations between friends
            for i in range(min(3, len(users) - 1)):
                user1 = users[i]
                user2 = users[i + 1]
                if user1.is_admin or user2.is_admin:
                    continue

                conversation = Conversation(
                    id=str(generate_uuid()),
                    user1_id=user1.id,
                    user2_id=user2.id,
                    last_message_at=datetime.now(timezone.utc)
                    - timedelta(hours=random.randint(1, 48)),
                )
                db.add(conversation)
                await db.commit()
                await db.refresh(conversation)
                conversations_created += 1

                # Create messages in conversation
                for j in range(random.randint(3, 8)):
                    sender = user1 if j % 2 == 0 else user2
                    message = Message(
                        id=str(generate_uuid()),
                        conversation_id=conversation.id,
                        sender_id=sender.id,
                        receiver_id=user2.id if sender.id == user1.id else user1.id,
                        content=f"안녕하세요! 메시지 {j+1}입니다.",
                        is_read=random.choice([True, False]),
                        created_at=datetime.now(timezone.utc)
                        - timedelta(hours=random.randint(1, 48)),
                    )
                    db.add(message)
                    messages_created += 1

                print(
                    f"   ✅ Created conversation between {user1.username} and {user2.username}"
                )

            await db.commit()
            print(f"✅ Created {conversations_created} conversations")
            print(f"✅ Created {messages_created} messages")

            # Summary
            print("\n" + "=" * 60)
            print("✅ Comprehensive seed data creation completed!")
            print("=" * 60)
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
            print(f"   - Matching Pools: {len(matching_pools)}")
            print(f"   - Matching Proposals: {proposals_created}")
            print(f"   - Friends: {friends_created // 2}")
            print(f"   - Friend Requests: {friend_requests_created}")
            print(f"   - User Verifications: {verifications_created}")
            print(f"   - Conversations: {conversations_created}")
            print(f"   - Messages: {messages_created}")

            print(f"\n💡 Test Accounts:")
            print(f"   Admins:")
            print(f"   - junexi@naver.com / admin123 (juns)")
            print(f"   - sc82.choi@pknu.ac.kr / admin123 (sc82)")
            print(f"\n   Users (all passwords: password123):")
            for user in users[2:]:  # Skip admins
                if not user.is_admin:
                    school_info = f" ({user.school})" if user.school else ""
                    print(
                        f"   - {user.email} / password123 ({user.username}{school_info})"
                    )

            print(f"\n🎯 You can now test all features with realistic data!")
            print("=" * 60)

            return  # Exit successfully

        except Exception as e:
            await db.rollback()
            print(f"\n❌ Error creating seed data: {e}")
            import traceback

            traceback.print_exc()
            return  # Exit with error


if __name__ == "__main__":
    asyncio.run(seed_comprehensive_data())
