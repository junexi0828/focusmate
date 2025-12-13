"""Simple seed data script - creates realistic test data for 7 users.

Creates:
- 2 Admin users (juns, sc82)
- 5 Regular users (김도윤, 김지운, 심동혁, 유재성, 김시은)
- Realistic usage data: sessions, goals, posts, comments, chats

Run with: python scripts/seed_simple.py
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
import random
import uuid

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.security import hash_password
from app.infrastructure.database.session import get_db
from app.infrastructure.database.models.user import User
from app.infrastructure.database.models.user_stats import UserGoal, ManualSession
from app.infrastructure.database.models.community import Post, Comment, PostLike, CommentLike
from app.infrastructure.database.models.chat import ChatRoom, ChatMember, ChatMessage
from app.infrastructure.database.models.achievement import Achievement, UserAchievement
from app.infrastructure.database.models.session_history import SessionHistory
from app.infrastructure.repositories.user_repository import UserRepository


async def seed_simple_data():
    """Create simple but realistic seed data."""
    print("🌱 Starting simple seed data creation...\n")

    async for db in get_db():
        try:
            user_repo = UserRepository(db)

            # ==================== 1. CREATE USERS ====================
            print("👥 Creating users...")
            users = []

            # Admin users
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
                else:
                    user = User(
                        id=str(uuid.uuid4()),
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
                    users.append(user)
                    print(f"   ✅ Created user: {username} ({email})")

            await db.commit()
            print(f"✅ Created {len(users)} users\n")


            # ==================== 2. CREATE GOALS ====================
            print("🎯 Creating user goals...")
            goals_created = 0
            for user in users:
                goal = UserGoal(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    daily_goal_minutes=random.choice([60, 90, 120, 180]),
                    weekly_goal_sessions=random.choice([5, 7, 10, 14]),
                )
                db.add(goal)
                goals_created += 1

            await db.commit()
            print(f"✅ Created {goals_created} goals\n")


            # ==================== 3. CREATE SESSION HISTORY ====================
            print("📊 Creating session history...")
            sessions_created = 0
            now = datetime.now(timezone.utc)

            for user in users:
                # Create 5-15 sessions per user over the past 30 days
                num_sessions = random.randint(5, 15)
                for i in range(num_sessions):
                    days_ago = random.randint(0, 30)
                    session = SessionHistory(
                        id=str(uuid.uuid4()),
                        user_id=user.id,
                        room_id=str(uuid.uuid4()),  # Dummy room ID
                        session_type=random.choice(["work", "break"]),
                        duration_minutes=random.choice([25, 30, 45, 50, 60]),
                        completed_at=now - timedelta(days=days_ago, hours=random.randint(0, 23)),
                    )
                    db.add(session)
                    sessions_created += 1

            await db.commit()
            print(f"✅ Created {sessions_created} session records\n")


            # ==================== 4. CREATE MANUAL SESSIONS ====================
            print("✍️  Creating manual sessions...")
            manual_sessions_created = 0

            for user in users[:4]:  # Only some users have manual sessions
                num_manual = random.randint(1, 3)
                for _ in range(num_manual):
                    days_ago = random.randint(0, 14)
                    manual_session = ManualSession(
                        id=uuid.uuid4(),
                        user_id=user.id,
                        duration_minutes=random.choice([30, 45, 60, 90]),
                        session_type=random.choice(["focus", "break"]),
                        completed_at=now - timedelta(days=days_ago),
                    )
                    db.add(manual_session)
                    manual_sessions_created += 1

            await db.commit()
            print(f"✅ Created {manual_sessions_created} manual sessions\n")


            # ==================== 5. CREATE ACHIEVEMENTS ====================
            print("🏆 Creating achievements...")
            achievements = []
            achievements_data = [
                ("first_session", "첫 세션 완료", "첫 번째 집중 세션을 완료했습니다", "🎯", "milestone", "session_count", 1, 10),
                ("session_streak_3", "3일 연속", "3일 연속으로 세션을 완료했습니다", "🔥", "streak", "streak_days", 3, 20),
                ("total_time_10h", "10시간 달성", "총 집중 시간 10시간을 달성했습니다", "⏱️", "time", "total_minutes", 600, 30),
                ("early_bird", "얼리버드", "오전 6시 이전에 세션을 시작했습니다", "🌅", "special", "early_sessions", 1, 15),
            ]

            for ach_id, name, desc, icon, category, req_type, req_value, points in achievements_data:
                achievement = Achievement(
                    id=ach_id,
                    name=name,
                    description=desc,
                    icon=icon,
                    category=category,
                    requirement_type=req_type,
                    requirement_value=req_value,
                    points=points,
                    is_active=True,
                )
                db.add(achievement)
                achievements.append(achievement)

            await db.commit()
            print(f"✅ Created {len(achievements)} achievements\n")


            # ==================== 6. UNLOCK SOME ACHIEVEMENTS ====================
            print("🎖️  Unlocking user achievements...")
            unlocks_created = 0

            # First 4 users get some achievements
            for user in users[:4]:
                num_unlocks = random.randint(1, 3)
                unlocked = random.sample(achievements, num_unlocks)

                for achievement in unlocked:
                    user_achievement = UserAchievement(
                        id=str(uuid.uuid4()),
                        user_id=user.id,
                        achievement_id=achievement.id,
                        unlocked_at=now - timedelta(days=random.randint(1, 20)),
                        progress=achievement.requirement_value,  # Fully completed
                    )
                    db.add(user_achievement)
                    unlocks_created += 1

            await db.commit()
            print(f"✅ Created {unlocks_created} achievement unlocks\n")


            # ==================== 7. CREATE COMMUNITY POSTS ====================
            print("📝 Creating community posts...")
            posts = []
            posts_data = [
                (users[0].id, "집중력을 높이는 5가지 방법", "포모도로 테크닉을 사용하면서 느낀 점을 공유합니다. 25분 집중, 5분 휴식의 사이클이 정말 효과적이에요!", "study_tips"),
                (users[1].id, "오늘 3시간 달성!", "드디어 하루 목표인 3시간 집중 시간을 달성했어요! 다들 화이팅!", "achievements"),
                (users[2].id, "함께 공부하실 분 구합니다", "평일 저녁 8시-10시 정기적으로 같이 공부하실 분 찾아요. 관심 있으신 분은 댓글 주세요!", "study_group"),
                (users[3].id, "시험 준비 어떻게 하시나요?", "다음 주 시험인데 집중이 잘 안되네요. 여러분의 시험 준비 팁 공유해주세요!", "questions"),
                (users[0].id, "FocusMate 사용 후기", "이 앱 사용한 지 한 달 됐는데, 생산성이 확실히 올랐어요. 추천합니다!", "general"),
            ]

            for user_id, title, content, category in posts_data:
                days_ago = random.randint(1, 14)
                post = Post(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    title=title,
                    content=content,
                    category=category,
                    likes=random.randint(0, 10),
                    comment_count=random.randint(0, 5),
                    is_pinned=False,
                    is_deleted=False,
                    created_at=now - timedelta(days=days_ago),
                )
                db.add(post)
                posts.append(post)

            await db.commit()
            print(f"✅ Created {len(posts)} posts\n")


            # ==================== 8. CREATE COMMENTS ====================
            print("💬 Creating comments...")
            comments = []
            comments_data = [
                (posts[0].id, users[2].id, "정말 유용한 정보네요! 저도 포모도로 써보겠습니다."),
                (posts[0].id, users[3].id, "25분도 긴 것 같은데 어떻게 집중하시나요?"),
                (posts[1].id, users[0].id, "축하드려요! 저도 열심히 해야겠어요 ㅎㅎ"),
                (posts[2].id, users[4].id, "저도 관심 있어요! 어떻게 참여하나요?"),
                (posts[3].id, users[1].id, "저는 아침 일찍 일어나서 공부하는 게 도움이 됐어요."),
                (posts[3].id, users[0].id, "시험 범위를 나눠서 하루에 조금씩 하는 게 좋아요!"),
            ]

            for post_id, user_id, content in comments_data:
                comment = Comment(
                    id=str(uuid.uuid4()),
                    post_id=post_id,
                    user_id=user_id,
                    content=content,
                    parent_comment_id=None,
                    likes=random.randint(0, 5),
                    is_deleted=False,
                )
                db.add(comment)
                comments.append(comment)

            await db.commit()
            print(f"✅ Created {len(comments)} comments\n")


            # ==================== 9. CREATE LIKES ====================
            print("❤️  Creating likes...")
            likes_created = 0

            # Some users like some posts
            for post in posts[:3]:
                likers = random.sample(users, random.randint(2, 4))
                for user in likers:
                    like = PostLike(
                        id=str(uuid.uuid4()),
                        post_id=post.id,
                        user_id=user.id,
                        created_at=now - timedelta(days=random.randint(1, 10)),
                    )
                    db.add(like)
                    likes_created += 1

            # Some users like some comments
            for comment in comments[:3]:
                likers = random.sample(users, random.randint(1, 3))
                for user in likers:
                    like = CommentLike(
                        id=str(uuid.uuid4()),
                        comment_id=comment.id,
                        user_id=user.id,
                        created_at=now - timedelta(days=random.randint(1, 10)),
                    )
                    db.add(like)
                    likes_created += 1

            await db.commit()
            print(f"✅ Created {likes_created} likes\n")


            # ==================== 10. CREATE CHAT ROOM ====================
            print("💬 Creating chat room...")
            chat_room = ChatRoom(
                room_id=uuid.uuid4(),
                room_type="group",
                room_name="스터디 그룹",
                description="함께 공부하는 그룹 채팅방",
                is_active=True,
                is_archived=False,
            )
            db.add(chat_room)
            await db.commit()
            print(f"✅ Created chat room\n")


            # ==================== 11. ADD CHAT MEMBERS ====================
            print("👥 Adding chat members...")
            members_created = 0

            for i, user in enumerate(users[:5]):  # First 5 users join chat
                member = ChatMember(
                    member_id=uuid.uuid4(),
                    room_id=chat_room.room_id,
                    user_id=user.id,
                    role="admin" if i == 0 else "member",
                    is_active=True,
                    is_muted=False,
                    unread_count=0,
                )
                db.add(member)
                members_created += 1

            await db.commit()
            print(f"✅ Added {members_created} chat members\n")


            # ==================== 12. CREATE CHAT MESSAGES ====================
            print("💬 Creating chat messages...")
            messages_data = [
                (users[0].id, "안녕하세요! 스터디 그룹에 오신 것을 환영합니다."),
                (users[1].id, "반갑습니다! 열심히 공부해봐요!"),
                (users[2].id, "오늘 목표는 2시간 집중입니다 ㅎㅎ"),
                (users[3].id, "저도 같이 열심히 하겠습니다!"),
                (users[0].id, "다들 화이팅! 🔥"),
            ]

            messages_created = 0
            for i, (user_id, content) in enumerate(messages_data):
                message = ChatMessage(
                    message_id=uuid.uuid4(),
                    room_id=chat_room.room_id,
                    sender_id=user_id,
                    message_type="text",
                    content=content,
                    is_edited=False,
                    is_deleted=False,
                    created_at=now - timedelta(hours=24-i),
                )
                db.add(message)
                messages_created += 1

            await db.commit()
            print(f"✅ Created {messages_created} chat messages\n")


            # ==================== SUMMARY ====================
            print("\n" + "="*60)
            print("✅ Seed data creation completed!")
            print("="*60)
            print("\n📊 Summary:")
            print(f"   👥 Users: {len(users)} (2 admins + 5 regular)")
            print(f"   🎯 Goals: {goals_created}")
            print(f"   📊 Sessions: {sessions_created}")
            print(f"   ✍️  Manual Sessions: {manual_sessions_created}")
            print(f"   🏆 Achievements: {len(achievements)}")
            print(f"   🎖️  Unlocks: {unlocks_created}")
            print(f"   📝 Posts: {len(posts)}")
            print(f"   💬 Comments: {len(comments)}")
            print(f"   ❤️  Likes: {likes_created}")
            print(f"   💬 Chat Messages: {messages_created}")

            print("\n🔐 Login Credentials:")
            print("   Admins:")
            print("   - junexi@naver.com / admin123 (juns)")
            print("   - sc82.choi@pknu.ac.kr / admin123 (sc82)")
            print("\n   Users:")
            print("   - user1@test.com / password123 (김도윤)")
            print("   - user2@test.com / password123 (김지운)")
            print("   - user3@test.com / password123 (심동혁)")
            print("   - user4@test.com / password123 (유재성)")
            print("   - user5@test.com / password123 (김시은)")

            print("\n💡 The data simulates realistic usage by 7 users!")
            print("   Ready for testing all features.\n")

        except Exception as e:
            await db.rollback()
            print(f"\n❌ Error creating seed data: {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    asyncio.run(seed_simple_data())
