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

Run with: python scripts/database/seed_comprehensive.py
"""

import asyncio
import random
import sys
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path


# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


from app.core.config import settings
from app.core.security import hash_password
from app.infrastructure.database.models import Participant, Room, Timer
from app.infrastructure.database.models.achievement import Achievement, UserAchievement
from app.infrastructure.database.models.chat import ChatMember, ChatMessage, ChatRoom
from app.infrastructure.database.models.community import Comment, Post, PostLike
from app.infrastructure.database.models.friend import Friend, FriendRequest
from app.infrastructure.database.models.matching import (
    MatchingPool,
    MatchingProposal,
)
from app.infrastructure.database.models.message import Conversation, Message
from app.infrastructure.database.models.ranking import (
    RankingMiniGame,
    RankingSession,
    RankingTeam,
    RankingTeamInvitation,
    RankingTeamMember,
    RankingVerificationRequest,
)
from app.infrastructure.database.models.session_history import SessionHistory
from app.infrastructure.database.models.user import User
from app.infrastructure.database.models.user_stats import ManualSession, UserGoal
from app.infrastructure.database.models.verification import UserVerification
from app.infrastructure.database.session import get_db
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
                (settings.ADMIN_EMAIL, "admin", True),
                ("admin2@example.com", "admin2", True),
            ]

            for email, username, is_admin in admin_data:
                existing = await user_repo.get_by_email(email)
                if existing:
                    users.append(existing)
                    print(f"   ⏭️  Admin '{username}' already exists")
                else:
                    user = User(
                        id=str(uuid.uuid4()),
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
                    "user1@example.com",
                    "김도윤",
                    "부경대학교",
                    "컴퓨터공학과 3학년입니다. 함께 공부해요!",
                ),
                (
                    "user2@example.com",
                    "김지운",
                    "부경대학교",
                    "산업경영공학과 2학년입니다.",
                ),
                ("user3@example.com", "심동혁", "부경대학교", "전자공학과 4학년입니다."),
                ("user4@example.com", "유재성", "부경대학교", "기계공학과 1학년입니다."),
                ("user5@example.com", "김시은", "부경대학교", "화학공학과 3학년입니다."),
                ("user6@example.com", "이민수", "부경대학교", "경영학과 2학년입니다."),
                ("user7@example.com", "박지현", "부경대학교", "컴퓨터공학과 4학년입니다."),
                (
                    "user8@example.com",
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
                user = User(
                    id=str(uuid.uuid4()),
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

            # 2. Create comprehensive user goals (모든 사용자)
            print("\n🎯 Creating comprehensive user goals...")
            goals_created = 0
            for user in users:
                # 각 사용자마다 여러 목표 생성 (과거 목표 포함)
                num_goals = random.randint(2, 5)
                for i in range(num_goals):
                    days_ago = random.randint(0, 60)  # 과거 60일간의 목표
                    goal = UserGoal(
                        id=uuid.uuid4(),
                        user_id=str(user.id),
                        daily_goal_minutes=random.choice([60, 90, 120, 150, 180, 240]),
                        weekly_goal_sessions=random.choice([5, 7, 10, 14, 15, 20]),
                        created_at=datetime.now(UTC)
                        - timedelta(days=days_ago),
                    )
                    db.add(goal)
                    goals_created += 1
                await db.commit()
            print(f"   ✅ Created {goals_created} goals for all users")

            # 3. Create comprehensive manual sessions (모든 사용자)
            print("\n📝 Creating comprehensive manual sessions...")
            manual_sessions_created = 0
            for user_idx, user in enumerate(users):
                # 활성 사용자는 더 많은 수동 세션
                if user.is_admin or user_idx < 4:
                    num_sessions = random.randint(15, 30)
                else:
                    num_sessions = random.randint(5, 15)

                for i in range(num_sessions):
                    days_ago = random.randint(0, 30)
                    session = ManualSession(
                        id=uuid.uuid4(),
                        user_id=str(user.id),
                        session_type=random.choice(["focus", "study", "work", "break"]),
                        duration_minutes=random.choice([15, 25, 30, 45, 60, 90]),
                        completed_at=datetime.now(UTC)
                        - timedelta(days=days_ago, hours=random.randint(0, 23)),
                        created_at=datetime.now(UTC)
                        - timedelta(days=days_ago),
                    )
                    db.add(session)
                    manual_sessions_created += 1

                if (user_idx + 1) % 3 == 0:  # 배치 커밋
                    await db.commit()

            await db.commit()
            print(f"   ✅ Created {manual_sessions_created} manual sessions")

            # 4. Create comprehensive community posts (더 많은 게시글)
            print("\n📰 Creating comprehensive community posts...")
            post_templates = [
                ("공부 팁 공유", "효과적인 집중 방법을 공유합니다!", "tips"),
                ("오늘의 목표", "오늘 3시간 집중하기!", "general"),
                ("질문있어요", "포모도로 타이머 사용법 알려주세요", "question"),
                ("성공 후기", "한 달 동안 매일 2시간씩 공부했어요!", "success"),
                ("스터디 모집", "함께 공부할 팀원 모집합니다", "recruitment"),
                ("시험 준비 팁", "중간고사 대비 방법 공유합니다", "tips"),
                ("집중력 향상", "집중력 높이는 방법 알려드려요", "tips"),
                ("타이머 활용법", "포모도로 기법으로 생산성 높이기", "tips"),
                ("동기부여", "공부 동기부여 받는 방법", "general"),
                ("시간 관리", "효과적인 시간 관리 전략", "tips"),
                ("시험 후기", "시험 잘 본 후기 공유합니다", "success"),
                ("스터디 그룹 후기", "함께 공부한 경험 공유", "success"),
                ("질문", "이 기능은 어떻게 사용하나요?", "question"),
                ("질문", "랭킹전 참여 방법 알려주세요", "question"),
                ("질문", "매칭 풀은 어떻게 만드나요?", "question"),
                ("모집", "프로젝트 팀원 모집합니다", "recruitment"),
                ("모집", "같이 공부할 스터디 그룹 찾아요", "recruitment"),
            ]

            posts = []
            # 각 사용자마다 2-5개의 게시글 생성
            for user in users:
                num_posts = random.randint(2, 5)
                for i in range(num_posts):
                    title, content, category = random.choice(post_templates)
                    days_ago = random.randint(0, 30)
                    post = Post(
                        id=str(generate_uuid()),
                        user_id=str(user.id),
                        title=f"{title} ({user.username})",
                        content=f"{content}\n\n- {user.username}",
                        category=category,
                        likes=random.randint(0, 50),
                        comment_count=0,  # 나중에 댓글 생성 시 업데이트
                        is_pinned=(
                            i == 0 and user.is_admin
                        ),  # 첫 번째 관리자 게시글 고정
                        is_deleted=False,
                        created_at=datetime.now(UTC)
                        - timedelta(days=days_ago, hours=random.randint(0, 23)),
                    )
                    db.add(post)
                    posts.append(post)

            await db.commit()
            print(f"   ✅ Created {len(posts)} community posts")

            # 5. Create comprehensive comments (각 게시글마다 여러 댓글)
            print("\n💬 Creating comprehensive comments...")
            comments_created = 0
            comment_templates = [
                "좋은 글이네요!",
                "도움이 많이 되었어요",
                "저도 같은 경험이 있어요",
                "추가 정보 감사합니다",
                "궁금한 점이 있어요",
                "저도 시도해볼게요",
                "좋은 팁이에요!",
                "응원합니다!",
            ]

            for post in posts:
                # 각 게시글마다 2-8개의 댓글
                num_comments = random.randint(2, 8)
                comment_users = random.sample(users, min(num_comments, len(users)))

                for i, comment_user in enumerate(comment_users):
                    hours_ago = random.randint(
                        0,
                        min(
                            24 * 7,
                            int(
                                (
                                    datetime.now(UTC) - post.created_at
                                ).total_seconds()
                                / 3600
                            ),
                        ),
                    )
                    comment = Comment(
                        id=str(uuid.uuid4()),
                        post_id=str(post.id),
                        user_id=str(comment_user.id),
                        content=f"{random.choice(comment_templates)} - {comment_user.username}",
                        likes=random.randint(0, 15),
                        is_deleted=False,
                        created_at=post.created_at + timedelta(hours=hours_ago),
                    )
                    db.add(comment)
                    comments_created += 1

                    # 댓글 수 업데이트
                    post.comment_count = (post.comment_count or 0) + 1

                if (posts.index(post) + 1) % 10 == 0:  # 배치 커밋
                    await db.commit()

            await db.commit()
            print(f"   ✅ Created {comments_created} comments")

            # 6. Create comprehensive post likes
            print("\n❤️  Creating comprehensive post likes...")
            likes_created = 0
            for post in posts:
                # 각 게시글마다 3-15명이 좋아요
                num_likes = random.randint(3, 15)
                like_users = random.sample(users, min(num_likes, len(users)))

                for like_user in like_users:
                    like = PostLike(
                        id=str(generate_uuid()),
                        post_id=str(post.id),
                        user_id=str(like_user.id),
                        created_at=post.created_at
                        + timedelta(
                            hours=random.randint(
                                0,
                                int(
                                    (
                                        datetime.now(UTC) - post.created_at
                                    ).total_seconds()
                                    / 3600
                                ),
                            )
                        ),
                    )
                    db.add(like)
                    likes_created += 1

                    # 좋아요 수 업데이트
                    post.likes = (post.likes or 0) + 1

                if (posts.index(post) + 1) % 10 == 0:  # 배치 커밋
                    await db.commit()

            await db.commit()
            print(f"   ✅ Created {likes_created} post likes")

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
                        team_id=uuid.uuid4(),
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
                        member_id=uuid.uuid4(),
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
                            member_id=uuid.uuid4(),
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

            # 8.5. Create comprehensive ranking sessions (랭킹 세션 데이터)
            print("\n🏆 Creating comprehensive ranking sessions...")
            ranking_sessions_created = 0
            now = datetime.now(UTC)

            for team in teams:
                # 각 팀의 멤버들 가져오기
                team_members_result = await db.execute(
                    select(RankingTeamMember).where(
                        RankingTeamMember.team_id == team.team_id
                    )
                )
                team_members = team_members_result.scalars().all()

                if not team_members:
                    continue

                # 각 팀 멤버마다 20-50개의 랭킹 세션 생성 (과거 60일간)
                for member in team_members:
                    num_sessions = random.randint(20, 50)

                    for i in range(num_sessions):
                        days_ago = random.randint(0, 60)
                        session = RankingSession(
                            session_id=uuid.uuid4(),
                            team_id=team.team_id,
                            user_id=member.user_id,
                            duration_minutes=random.choice([25, 30, 45, 50, 60]),
                            session_type=random.choice(["work", "break"]),
                            success=random.random() > 0.1,  # 90% 성공률
                            completed_at=now
                            - timedelta(
                                days=days_ago,
                                hours=random.randint(0, 23),
                                minutes=random.randint(0, 59),
                            ),
                        )
                        db.add(session)
                        ranking_sessions_created += 1

                    if ranking_sessions_created % 100 == 0:  # 배치 커밋
                        await db.commit()

            await db.commit()
            print(f"   ✅ Created {ranking_sessions_created} ranking sessions")

            # 8.6. Create comprehensive mini-game records (미니게임 기록)
            print("\n🎮 Creating comprehensive mini-game records...")
            mini_games_created = 0
            game_types = [
                "dino_jump",
                "dot_collector",
                "snake",
                "memory_game",
                "reaction_test",
            ]

            for team in teams:
                if not team.mini_game_enabled:
                    continue

                team_members_result = await db.execute(
                    select(RankingTeamMember).where(
                        RankingTeamMember.team_id == team.team_id
                    )
                )
                team_members = team_members_result.scalars().all()

                if not team_members:
                    continue

                # 각 팀 멤버마다 10-30개의 미니게임 기록 생성
                for member in team_members:
                    num_games = random.randint(10, 30)

                    for i in range(num_games):
                        game_type = random.choice(game_types)
                        days_ago = random.randint(0, 30)

                        # 게임 타입별 점수 범위
                        score_ranges = {
                            "dino_jump": (100, 5000),
                            "dot_collector": (50, 3000),
                            "snake": (200, 8000),
                            "memory_game": (500, 10000),
                            "reaction_test": (100, 2000),
                        }

                        score = random.randint(
                            *score_ranges.get(game_type, (100, 5000))
                        )
                        completion_time = (
                            random.uniform(10.0, 300.0)
                            if game_type in ["reaction_test", "memory_game"]
                            else None
                        )

                        mini_game = RankingMiniGame(
                            game_id=uuid.uuid4(),
                            team_id=team.team_id,
                            user_id=member.user_id,
                            game_type=game_type,
                            score=score,
                            success=random.random() > 0.15,  # 85% 성공률
                            completion_time=completion_time,
                            game_data={
                                "level": random.randint(1, 10),
                                "difficulty": random.choice(["easy", "medium", "hard"]),
                            },
                            played_at=now
                            - timedelta(
                                days=days_ago,
                                hours=random.randint(0, 23),
                                minutes=random.randint(0, 59),
                            ),
                        )
                        db.add(mini_game)
                        mini_games_created += 1

                    if mini_games_created % 100 == 0:  # 배치 커밋
                        await db.commit()

            await db.commit()
            print(f"   ✅ Created {mini_games_created} mini-game records")

            # 9. Create team invitations
            print("\n📧 Creating team invitations...")
            for team in teams[:2]:  # First 2 teams
                invitation = RankingTeamInvitation(
                    invitation_id=uuid.uuid4(),
                    team_id=team.team_id,
                    email=f"newuser{random.randint(1, 100)}@test.com",
                    invited_by=team.leader_id,
                    status="pending",
                    expires_at=datetime.now(UTC) + timedelta(days=7),
                )
                db.add(invitation)
                await db.commit()
                print(f"   ✅ Created invitation for team: {team.team_name}")

            # 10. Create verification requests
            print("\n🎓 Creating verification requests...")
            for team in teams:
                verification = RankingVerificationRequest(
                    request_id=uuid.uuid4(),
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

            # 10.5. Create comprehensive session history for statistics
            print("\n📊 Creating comprehensive session history for statistics...")
            sessions_created = 0
            now = datetime.now(UTC)

            for user_idx, user in enumerate(users):
                # 각 사용자마다 60-120개의 세션 생성 (과거 90일간)
                # 활성 사용자는 더 많은 세션, 덜 활성 사용자는 적은 세션
                if user.is_admin:
                    num_sessions = random.randint(80, 120)  # 관리자는 더 활성
                elif user_idx < 3:
                    num_sessions = random.randint(70, 100)  # 처음 3명은 활성
                elif user_idx < 6:
                    num_sessions = random.randint(50, 80)  # 중간 사용자
                else:
                    num_sessions = random.randint(30, 60)  # 나머지는 보통

                # 시간대별 패턴 생성 (아침, 점심, 저녁, 밤)
                time_patterns = [
                    (6, 12, 0.3),  # 아침 (6-12시, 30% 확률)
                    (12, 18, 0.25),  # 점심 (12-18시, 25% 확률)
                    (18, 22, 0.3),  # 저녁 (18-22시, 30% 확률)
                    (22, 6, 0.15),  # 밤 (22-6시, 15% 확률)
                ]

                for i in range(num_sessions):
                    # 과거 90일간 분산
                    days_ago = random.randint(0, 90)

                    # 시간대 패턴 적용
                    pattern = random.choices(
                        time_patterns, weights=[p[2] for p in time_patterns]
                    )[0]

                    if pattern[0] < pattern[1]:  # 일반적인 시간대
                        hour = random.randint(pattern[0], pattern[1] - 1)
                    else:  # 밤 시간대 (22-6시)
                        hour = random.choice(
                            list(range(pattern[0], 24)) + list(range(pattern[1]))
                        )

                    minute = random.randint(0, 59)

                    # 요일별 패턴 (주말보다 평일이 더 활성)
                    day_of_week = (now - timedelta(days=days_ago)).weekday()
                    if day_of_week >= 5:  # 주말
                        if random.random() < 0.3:  # 주말에는 30% 확률로 스킵
                            continue

                    # 세션 타입 (work가 80%, break가 20%)
                    session_type = random.choices(
                        ["work", "break"], weights=[0.8, 0.2]
                    )[0]

                    # 세션 길이 (work는 25-60분, break는 5-15분)
                    if session_type == "work":
                        duration_minutes = random.choice([25, 30, 45, 50, 60])
                    else:
                        duration_minutes = random.choice([5, 10, 15])

                    session = SessionHistory(
                        id=str(generate_uuid()),
                        user_id=user.id,
                        room_id=str(generate_uuid()),
                        session_type=session_type,
                        duration_minutes=duration_minutes,
                        completed_at=(now - timedelta(days=days_ago)).replace(
                            hour=hour, minute=minute, second=0, microsecond=0
                        ),
                    )
                    db.add(session)

                    # 배치 커밋 (100개마다)
                    if (i + 1) % 100 == 0:
                        await db.commit()

                    sessions_created += 1

                await db.commit()  # 사용자별로 커밋
                print(f"   ✅ Created {num_sessions} sessions for {user.username}")

            print(f"✅ Created {sessions_created} total session records")

            # 11. Create chat rooms
            print("\n💬 Creating chat rooms...")
            chat_rooms = []

            # Create team/public chat rooms
            room_names = [
                ("General", "team"),
                ("Study Tips", "team"),
                ("Q&A", "team"),
                ("Team Chat", "team"),
            ]

            for name, room_type in room_names:
                room = ChatRoom(
                    room_id=str(generate_uuid()),
                    room_type=room_type,
                    room_name=name,
                    description=f"{name} 채팅방",
                    is_active=True,
                    room_metadata={"type": room_type},
                )
                db.add(room)
                await db.commit()
                await db.refresh(room)
                chat_rooms.append(room)
                print(f"   ✅ Created chat room: {name}")

            # 11.2. Create direct chat rooms between friends
            print("\n💬 Creating direct chat rooms...")
            direct_rooms_created = 0
            regular_users = [u for u in users if not u.is_admin]

            # Create direct chats between pairs of regular users
            for i in range(min(3, len(regular_users) - 1)):
                user1 = regular_users[i]
                user2 = regular_users[i + 1]

                # Create direct chat room
                direct_room = ChatRoom(
                    room_id=uuid.uuid4(),
                    room_type="direct",
                    room_name=None,  # Direct chats don't have names
                    description=None,
                    is_active=True,
                    room_metadata={
                        "type": "direct",
                        "user_ids": sorted([user1.id, user2.id]),
                    },
                )
                db.add(direct_room)
                await db.commit()
                await db.refresh(direct_room)
                chat_rooms.append(direct_room)
                direct_rooms_created += 1

                # Add both users as members
                for user in [user1, user2]:
                    member = ChatMember(
                        room_id=direct_room.room_id,
                        user_id=user.id,
                        role="member",
                        is_active=True,
                        is_muted=False,
                        unread_count=0,
                    )
                    db.add(member)
                    await db.commit()

                print(
                    f"   ✅ Created direct chat between {user1.username} and {user2.username}"
                )

            print(f"   ✅ Created {direct_rooms_created} direct chat rooms")

            # 11.5. Add chat members to team rooms
            print("\n👥 Adding chat members to team rooms...")
            members_created = 0

            for i, user in enumerate(users[:5]):  # First 5 users join first team room
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
            print(f"   ✅ Added {members_created} chat members to team rooms")

            # 12. Create chat messages
            print("\n💬 Creating chat messages...")
            for room in chat_rooms[:4]:  # First 4 rooms (including direct chats)
                # Get room members to determine sender
                result = await db.execute(
                    select(ChatMember).where(ChatMember.room_id == room.room_id)
                )
                room_members = [m for m in result.scalars().all() if m.is_active]

                if not room_members:
                    continue

                for i in range(random.randint(3, 8)):
                    # Pick a random member from this room
                    sender = random.choice(room_members)
                    message = ChatMessage(
                        message_id=uuid.uuid4(),
                        room_id=room.room_id,
                        sender_id=sender.user_id,
                        message_type="text",
                        content=f"메시지 {i+1}: 안녕하세요!",
                        created_at=datetime.now(UTC)
                        - timedelta(hours=random.randint(1, 48)),
                    )
                    db.add(message)
                    await db.commit()

                room_display = room.room_name or f"Direct Chat ({room.room_id[:8]})"
                print(f"   ✅ Created messages for room: {room_display}")

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
                        unlocked_at=datetime.now(UTC)
                        - timedelta(days=random.randint(1, 30)),
                        progress=achievement.requirement_value,
                    )
                    db.add(user_achievement)
                    await db.commit()
            print("   ✅ Created user achievements")

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
                    id=str(uuid.uuid4()),
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
                        joined_at=datetime.now(UTC),
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
                        notification_id=str(uuid.uuid4()),
                        user_id=str(user.id),
                        title=title,
                        message=message,
                        type=notif_type,
                        is_read=random.choice([True, False, False]),
                        created_at=datetime.now(UTC)
                        - timedelta(hours=random.randint(1, 48)),
                    )
                    db.add(notification)
                    notifications_count += 1

            await db.commit()
            print(f"✅ Created {notifications_count} notifications")

            # MATCHING POOLS (핑크캠퍼스) - 모든 사용자 참여
            print("\n💕 Creating Matching Pools (핑크캠퍼스)...")

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
                    "경제학과",
                    "심리학과",
                    "국어국문학과",
                    "영어영문학과",
                ]
                grades = ["1", "2", "3", "4"]

                # 더 현실적인 메시지들
                pool_messages = [
                    "같은 전공 친구들과 함께 공부하고 싶어요! 📚",
                    "시험 기간 같이 집중해서 공부할 분들 모집합니다 ✨",
                    "프로젝트 팀원 구해요! 열정적인 분들 환영합니다 🚀",
                    "매일 꾸준히 공부하는 습관 만들고 싶어요 💪",
                    "같은 목표를 가진 친구들과 함께 성장하고 싶습니다 🌱",
                    "스터디 그룹 만들어서 서로 도와가며 공부해요! 🤝",
                    "조용한 분위기에서 집중해서 공부하고 싶어요 📖",
                    "같이 모여서 공부하면 더 집중이 잘 될 것 같아요 🎯",
                ]

                # 모든 사용자를 여러 풀로 분배
                # 각 풀은 3-6명의 멤버를 가질 수 있음
                pool_size = random.randint(3, 6)  # 더 다양한 크기
                num_pools = min(
                    8,  # 최대 8개의 풀
                    (len(regular_users_for_matching) + pool_size - 1) // pool_size,
                )

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
                        datetime.now(UTC)
                        + timedelta(days=random.randint(3, 14))
                    ).replace(tzinfo=None)

                    # 성별 분배 (더 현실적으로)
                    if i % 4 == 0:
                        gender = "male"
                    elif i % 4 == 1:
                        gender = "female"
                    elif i % 4 == 2:
                        gender = "mixed"
                    else:
                        gender = random.choice(["male", "female", "mixed"])

                    # 학과와 학년을 더 현실적으로 분배
                    department = random.choice(departments)
                    grade = random.choice(grades)

                    # 매칭 타입도 다양하게
                    matching_type = random.choice(["open", "blind"])
                    preferred_match_type = random.choice(["study", "project", "both"])

                    pool = MatchingPool(
                        pool_id=uuid.uuid4(),
                        creator_id=pool_users[0].id,
                        member_count=len(pool_users),
                        member_ids=[u.id for u in pool_users],
                        department=department,
                        grade=grade,
                        gender=gender,
                        preferred_match_type=preferred_match_type,
                        preferred_categories=random.sample(
                            ["study", "project", "exam", "assignment"],
                            k=random.randint(1, 3),
                        ),
                        matching_type=matching_type,
                        message=random.choice(pool_messages),
                        status="waiting",
                        expires_at=expires_at_naive,
                    )
                    db.add(pool)
                    await db.commit()
                    await db.refresh(pool)
                    matching_pools.append(pool)
                    print(
                        f"   ✅ Created matching pool {i+1} ({gender}, {department}, {grade}학년, {len(pool_users)}명)"
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
                # Create proposals between different pools with various statuses
                # 서로 다른 성별의 풀들 간에 제안 생성
                num_proposals = min(5, len(matching_pools) - 1)  # 최대 5개의 제안

                for i in range(num_proposals):
                    pool_a = matching_pools[i]
                    pool_b = matching_pools[(i + 1) % len(matching_pools)]

                    # 서로 다른 성별의 풀 간에만 제안 생성
                    if (
                        pool_a.gender != pool_b.gender
                        or pool_a.gender == "mixed"
                        or pool_b.gender == "mixed"
                    ):
                        expires_at_naive = (
                            datetime.now(UTC)
                            + timedelta(hours=random.randint(12, 48))
                        ).replace(tzinfo=None)

                        # 다양한 상태의 제안 생성 (일부는 matched, 일부는 pending)
                        if i < 2:  # 처음 2개는 matched 상태
                            group_a_status = "accepted"
                            group_b_status = "accepted"
                            final_status = "matched"
                            matched_at_naive = (
                                datetime.now(UTC)
                                - timedelta(hours=random.randint(1, 12))
                            ).replace(tzinfo=None)
                        elif i < 4:  # 다음 2개는 pending 상태
                            group_a_status = "pending"
                            group_b_status = "pending"
                            final_status = "pending"
                            matched_at_naive = None
                        elif random.random() < 0.3:  # 30% 확률로 rejected
                            group_a_status = random.choice(["accepted", "rejected"])
                            group_b_status = (
                                "rejected"
                                if group_a_status == "accepted"
                                else "rejected"
                            )
                            final_status = "rejected"
                            matched_at_naive = None
                        else:
                            group_a_status = "pending"
                            group_b_status = "pending"
                            final_status = "pending"
                            matched_at_naive = None

                        proposal = MatchingProposal(
                            proposal_id=uuid.uuid4(),
                            pool_id_a=pool_a.pool_id,
                            pool_id_b=pool_b.pool_id,
                            group_a_status=group_a_status,
                            group_b_status=group_b_status,
                            final_status=final_status,
                            expires_at=expires_at_naive,
                            matched_at=matched_at_naive,
                        )
                        db.add(proposal)
                        await db.commit()
                        proposals_created += 1
                        print(
                            f"   ✅ Created matching proposal ({final_status}) between pool {i+1} and {i+2}"
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
                            datetime.now(UTC)
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
                    datetime.now(UTC) - timedelta(days=random.randint(1, 30))
                ).replace(tzinfo=None)
                verified_at_naive = None
                if random.random() > 0.3:
                    verified_at_naive = (
                        datetime.now(UTC)
                        - timedelta(days=random.randint(1, 20))
                    ).replace(tzinfo=None)

                verification = UserVerification(
                    verification_id=uuid.uuid4(),
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
                    last_message_at=datetime.now(UTC)
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
                        created_at=datetime.now(UTC)
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
            print("\n📊 Summary:")
            print(f"   - Users: {len(users)} (2 admins + {len(users)-2} regular users)")
            print(f"   - Goals: {goals_created}")
            print(f"   - Manual Sessions: {manual_sessions_created}")
            print(f"   - Session History: {sessions_created}")
            print(f"   - Ranking Sessions: {ranking_sessions_created}")
            print(f"   - Mini-Game Records: {mini_games_created}")
            print(f"   - Posts: {len(posts)}")
            print(f"   - Comments: {comments_created}")
            print(f"   - Post Likes: {likes_created}")
            print(f"   - Teams: {len(teams)}")
            print("   - Team Members: ~9")
            print("   - Invitations: 2")
            print("   - Verifications: 3")
            print(f"   - Chat Rooms: {len(chat_rooms)}")
            print(f"   - Chat Members: {members_created}")
            print("   - Chat Messages: ~14")
            print("   - Achievements: 5")
            print("   - User Achievements: ~6")
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

            print("\n💡 Test Accounts:")
            print("   Admins:")
            print(f"   - {settings.ADMIN_EMAIL} / admin123 (admin)")
            print("   - admin2@example.com / admin123 (admin2)")
            print("\n   Users (all passwords: password123):")
            for user in users[2:]:  # Skip admins
                if not user.is_admin:
                    school_info = f" ({user.school})" if user.school else ""
                    print(
                        f"   - {user.email} / password123 ({user.username}{school_info})"
                    )

            print("\n🎯 You can now test all features with realistic data!")
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
