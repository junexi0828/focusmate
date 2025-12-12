"""Enhanced seed data script for development.

Creates comprehensive sample data for all implemented features:
- Users (admin + test users)
- Stats (goals, sessions)
- Community (posts, comments, likes)
- Ranking (teams, members, invitations, verifications)
- Chat (rooms, messages)
- Achievements
- Mini Games scores

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
from app.infrastructure.database.models.chat import ChatRoom, ChatMessage
from app.infrastructure.database.models.achievement import Achievement, UserAchievement
from app.shared.utils.uuid import generate_uuid


async def seed_comprehensive_data():
    """Create comprehensive seed data for all features."""
    print("🌱 Starting comprehensive seed data creation...")

    async for db in get_db():
        try:
            # 1. Create test users
            print("\n👥 Creating test users...")
            users = []

            # Admin user (should already exist)
            from app.infrastructure.repositories.user_repository import UserRepository
            user_repo = UserRepository(db)
            admin = await user_repo.get_by_email(settings.ADMIN_EMAIL)

            if not admin:
                print(f"❌ Admin user ({settings.ADMIN_EMAIL}) not found!")
                print("   Creating admin user...")
                admin = User(
                    id=generate_uuid(),
                    email=settings.ADMIN_EMAIL,
                    username="admin",
                    hashed_password=hash_password("admin123"),
                    is_active=True,
                    is_verified=True,
                    role="admin",
                )
                db.add(admin)
                await db.flush()
                print(f"   ✅ Created admin user: {admin.email}")
            else:
                print(f"✅ Found admin user: {admin.email}")

            users.append(admin)

            # Test users
            test_users_data = [
                ("user1@test.com", "김철수", "user"),
                ("user2@test.com", "이영희", "user"),
                ("user3@test.com", "박민수", "user"),
                ("user4@test.com", "최지은", "user"),
                ("user5@test.com", "정대현", "user"),
            ]

            for email, username, role in test_users_data:
                existing = await user_repo.get_by_email(email)
                if existing:
                    users.append(existing)
                    print(f"   ⏭️  User '{email}' already exists")
                    continue

                user = User(
                    id=generate_uuid(),
                    email=email,
                    username=username,
                    hashed_password=hash_password("password123"),
                    is_active=True,
                    is_verified=True,
                    role=role,
                    total_sessions=random.randint(10, 100),
                    total_focus_time=random.randint(1000, 5000),
                )
                db.add(user)
                await db.flush()
                users.append(user)
                print(f"   ✅ Created user: {email}")

            # 2. Create user goals
            print("\n🎯 Creating user goals...")
            for user in users[:4]:  # First 4 users
                goal = UserGoal(
                    id=generate_uuid(),
                    user_id=user.id,
                    daily_goal_minutes=random.choice([60, 90, 120, 180]),
                    weekly_goal_sessions=random.choice([5, 10, 15, 20]),
                    created_at=datetime.now(timezone.utc),
                )
                db.add(goal)
                print(f"   ✅ Created goal for {user.username}")

            # 3. Create manual sessions
            print("\n📝 Creating manual sessions...")
            for user in users[:4]:
                for i in range(random.randint(3, 8)):
                    session = ManualSession(
                        id=generate_uuid(),
                        user_id=user.id,
                        room_name=random.choice(["Study Room", "Focus Zone", "Deep Work", "Team Session"]),
                        duration_minutes=random.choice([25, 30, 45, 60]),
                        completed_at=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 7)),
                        created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 7)),
                    )
                    db.add(session)
                print(f"   ✅ Created sessions for {user.username}")

            # 4. Create community posts
            print("\n📰 Creating community posts...")
            post_data = [
                ("공부 팁 공유", "효과적인 집중 방법을 공유합니다!", "tips", admin.id),
                ("오늘의 목표", "오늘 3시간 집중하기!", "general", users[1].id),
                ("질문있어요", "포모도로 타이머 사용법 알려주세요", "question", users[2].id),
                ("성공 후기", "한 달 동안 매일 2시간씩 공부했어요!", "success", users[3].id),
                ("스터디 모집", "함께 공부할 팀원 모집합니다", "recruitment", users[4].id),
            ]

            posts = []
            for title, content, category, user_id in post_data:
                post = Post(
                    id=generate_uuid(),
                    user_id=user_id,
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
                posts.append(post)
                print(f"   ✅ Created post: {title}")

            await db.flush()

            # 5. Create comments
            print("\n💬 Creating comments...")
            for post in posts[:3]:  # First 3 posts
                for i in range(random.randint(1, 3)):
                    comment = Comment(
                        id=generate_uuid(),
                        post_id=post.id,
                        user_id=users[i + 1].id,
                        content=f"좋은 글이네요! 댓글 {i + 1}",
                        likes=random.randint(0, 10),
                        is_deleted=False,
                        created_at=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 24)),
                    )
                    db.add(comment)
                print(f"   ✅ Created comments for post: {post.title}")

            # 6. Create post likes
            print("\n❤️  Creating post likes...")
            for post in posts:
                for user in users[:3]:  # First 3 users like posts
                    if random.random() > 0.5:  # 50% chance
                        like = PostLike(
                            id=generate_uuid(),
                            post_id=post.id,
                            user_id=user.id,
                            created_at=datetime.now(timezone.utc),
                        )
                        db.add(like)
            print("   ✅ Created post likes")

            # 7. Create teams
            print("\n🏆 Creating teams...")
            team_data = [
                ("Study Warriors", "열심히 공부하는 팀", admin.id),
                ("Focus Masters", "집중력 마스터들", users[1].id),
                ("Deep Work Team", "딥워크 실천팀", users[2].id),
            ]

            teams = []
            for name, description, leader_id in team_data:
                team = Team(
                    id=generate_uuid(),
                    name=name,
                    description=description,
                    leader_id=leader_id,
                    total_score=random.randint(500, 2000),
                    member_count=random.randint(3, 8),
                    is_active=True,
                    created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(10, 30)),
                )
                db.add(team)
                teams.append(team)
                print(f"   ✅ Created team: {name}")

            await db.flush()

            # 8. Create team members
            print("\n👥 Creating team members...")
            for team in teams:
                # Leader
                leader_member = TeamMember(
                    id=generate_uuid(),
                    team_id=team.id,
                    user_id=team.leader_id,
                    role="leader",
                    total_sessions=random.randint(20, 50),
                    total_focus_time=random.randint(2000, 5000),
                    joined_at=team.created_at,
                )
                db.add(leader_member)

                # Other members
                for user in users[3:5]:  # Add 2 members to each team
                    member = TeamMember(
                        id=generate_uuid(),
                        team_id=team.id,
                        user_id=user.id,
                        role="member",
                        total_sessions=random.randint(10, 30),
                        total_focus_time=random.randint(1000, 3000),
                        joined_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 20)),
                    )
                    db.add(member)
                print(f"   ✅ Created members for team: {team.name}")

            # 9. Create team invitations
            print("\n📧 Creating team invitations...")
            for team in teams[:2]:  # First 2 teams
                invitation = TeamInvitation(
                    id=generate_uuid(),
                    team_id=team.id,
                    inviter_id=team.leader_id,
                    invitee_email=f"newuser{random.randint(1, 100)}@test.com",
                    status="pending",
                    created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 5)),
                    expires_at=datetime.now(timezone.utc) + timedelta(days=7),
                )
                db.add(invitation)
                print(f"   ✅ Created invitation for team: {team.name}")

            # 10. Create verifications
            print("\n🎓 Creating verifications...")
            verification_data = [
                (users[1].id, "서울대학교", "pending"),
                (users[2].id, "연세대학교", "approved"),
                (users[3].id, "고려대학교", "rejected"),
            ]

            for user_id, school_name, status in verification_data:
                verification = Verification(
                    id=generate_uuid(),
                    user_id=user_id,
                    school_name=school_name,
                    student_id_encrypted=None,  # Encrypted data
                    document_path="/uploads/verifications/sample.pdf",
                    status=status,
                    submitted_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 10)),
                    reviewed_at=datetime.now(timezone.utc) if status != "pending" else None,
                    reviewer_id=admin.id if status != "pending" else None,
                    admin_note="검토 완료" if status != "pending" else None,
                )
                db.add(verification)
                print(f"   ✅ Created verification for {school_name}: {status}")

            # 11. Create chat rooms
            print("\n💬 Creating chat rooms...")
            chat_rooms = []
            room_names = ["General", "Study Tips", "Q&A", "Team Chat"]

            for name in room_names:
                room = ChatRoom(
                    id=generate_uuid(),
                    name=name,
                    description=f"{name} 채팅방",
                    is_active=True,
                    created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(5, 20)),
                )
                db.add(room)
                chat_rooms.append(room)
                print(f"   ✅ Created chat room: {name}")

            await db.flush()

            # 12. Create chat messages
            print("\n💬 Creating chat messages...")
            for room in chat_rooms[:2]:  # First 2 rooms
                for i in range(random.randint(5, 10)):
                    message = ChatMessage(
                        id=generate_uuid(),
                        room_id=room.id,
                        user_id=users[i % len(users)].id,
                        content=f"안녕하세요! 메시지 {i + 1}",
                        is_read=random.choice([True, False]),
                        created_at=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 48)),
                    )
                    db.add(message)
                print(f"   ✅ Created messages for room: {room.name}")

            # 13. Create achievements
            print("\n🏅 Creating achievements...")
            achievement_data = [
                ("First Session", "첫 세션 완료", "total_sessions", 1),
                ("10 Sessions", "10개 세션 완료", "total_sessions", 10),
                ("Focus Master", "100시간 집중", "total_focus_time", 6000),
                ("Week Streak", "7일 연속 출석", "streak_days", 7),
                ("Community Star", "10개 게시글 작성", "community_posts", 10),
            ]

            achievements = []
            for name, description, req_type, req_value in achievement_data:
                achievement = Achievement(
                    id=generate_uuid(),
                    name=name,
                    description=description,
                    requirement_type=req_type,
                    requirement_value=req_value,
                    is_active=True,
                )
                db.add(achievement)
                achievements.append(achievement)
                print(f"   ✅ Created achievement: {name}")

            await db.flush()

            # 14. Create user achievements
            print("\n🎖️  Creating user achievements...")
            for user in users[:3]:  # First 3 users
                for achievement in achievements[:2]:  # First 2 achievements
                    user_achievement = UserAchievement(
                        id=generate_uuid(),
                        user_id=user.id,
                        achievement_id=achievement.id,
                        unlocked_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 10)),
                    )
                    db.add(user_achievement)
                print(f"   ✅ Created achievements for {user.username}")

            await db.commit()

            # Summary
            print("\n" + "="*60)
            print("✅ Comprehensive seed data creation completed!")
            print("="*60)
            print(f"\n📊 Summary:")
            print(f"   - Users: {len(users)} (1 admin + {len(users)-1} test users)")
            print(f"   - Goals: {len(users[:4])}")
            print(f"   - Sessions: ~{len(users[:4]) * 5}")
            print(f"   - Posts: {len(posts)}")
            print(f"   - Comments: ~{len(posts[:3]) * 2}")
            print(f"   - Teams: {len(teams)}")
            print(f"   - Team Members: ~{len(teams) * 3}")
            print(f"   - Invitations: 2")
            print(f"   - Verifications: 3 (pending, approved, rejected)")
            print(f"   - Chat Rooms: {len(chat_rooms)}")
            print(f"   - Chat Messages: ~{len(chat_rooms[:2]) * 7}")
            print(f"   - Achievements: {len(achievements)}")
            print(f"   - User Achievements: ~{len(users[:3]) * 2}")

            print(f"\n💡 Test Accounts:")
            print(f"   Admin: {settings.ADMIN_EMAIL} / admin123")
            print(f"   User1: user1@test.com / password123")
            print(f"   User2: user2@test.com / password123")
            print(f"   User3: user3@test.com / password123")

            print(f"\n🎯 You can now test all 15 implemented features!")
            print("="*60)

        except Exception as e:
            await db.rollback()
            print(f"\n❌ Error creating seed data: {e}")
            import traceback
            traceback.print_exc()
        finally:
            break


if __name__ == "__main__":
    asyncio.run(seed_comprehensive_data())
