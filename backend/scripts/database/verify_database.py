#!/usr/bin/env python3
"""종합 데이터베이스 검증 스크립트

데이터베이스 구성, 테이블 존재, CRUD 작업, 제약조건 등을 확인합니다.
"""

import asyncio
import sys
from pathlib import Path
from uuid import uuid4
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text, select, inspect
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.infrastructure.database.session import engine, AsyncSessionLocal
from app.infrastructure.database.models import (
    User,
    Room,
    Participant,
    Timer,
    SessionHistory,
    Post,
    Comment,
    ChatRoom,
    ChatMember,
    ChatMessage,
    Friend,
    FriendRequest,
    Notification,
    Achievement,
    UserAchievement,
    RankingTeam,
    RankingTeamMember,
    UserVerification,
    UserSettings,
    UserGoal,
    ManualSession,
    RoomReservation,
    MatchingPool,
    MatchingProposal,
    MatchingChatRoom,
    MatchingChatMember,
    MatchingMessage,
    Conversation,
    Message,
    UserPresence,
    RankingSession,
    RankingLeaderboard,
    RankingMiniGame,
    RankingTeamInvitation,
    RankingVerificationRequest,
    PostLike,
    CommentLike,
    PostRead,
    Report,
)


class DatabaseVerifier:
    """데이터베이스 검증 클래스"""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success_count = 0

    def log_error(self, message: str):
        """에러 로그"""
        self.errors.append(message)
        print(f"❌ {message}")

    def log_warning(self, message: str):
        """경고 로그"""
        self.warnings.append(message)
        print(f"⚠️  {message}")

    def log_success(self, message: str):
        """성공 로그"""
        self.success_count += 1
        print(f"✅ {message}")

    async def verify_connection(self) -> bool:
        """데이터베이스 연결 확인"""
        print("\n" + "=" * 70)
        print("1. 데이터베이스 연결 확인")
        print("=" * 70)

        try:
            async with engine.begin() as conn:
                result = await conn.execute(text("SELECT version()"))
                version = result.scalar()
                self.log_success(f"데이터베이스 연결 성공: {version[:60]}...")
                return True
        except Exception as e:
            self.log_error(f"데이터베이스 연결 실패: {e}")
            return False

    async def verify_tables(self) -> bool:
        """모든 테이블 존재 확인"""
        print("\n" + "=" * 70)
        print("2. 테이블 존재 확인")
        print("=" * 70)

        # 예상되는 모든 테이블 목록 (실제 데이터베이스 테이블 이름과 일치)
        expected_tables = {
            "user",
            "room",
            "participant",
            "timer",
            "session_history",
            "post",
            "comment",
            "post_like",
            "comment_like",
            "post_read",
            "chat_rooms",
            "chat_members",
            "chat_messages",
            "friend",
            "friend_request",
            "notifications",
            "achievement",
            "user_achievement",
            "ranking_teams",
            "ranking_team_members",
            "ranking_team_invitations",
            "ranking_verification_requests",
            "user_verification",
            "user_settings",
            "user_goals",
            "manual_sessions",
            "room_reservations",
            "matching_pools",
            "matching_proposals",
            "matching_chat_rooms",
            "matching_chat_members",
            "matching_messages",
            "conversation",
            "message",
            "user_presence",
            "ranking_sessions",
            "ranking_leaderboard",
            "ranking_mini_games",
            "reports",
            "alembic_version",
        }

        try:
            async with engine.begin() as conn:
                result = await conn.execute(
                    text(
                        """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """
                    )
                )
                existing_tables = {row[0] for row in result.fetchall()}

                # 누락된 테이블 확인
                missing_tables = expected_tables - existing_tables
                if missing_tables:
                    self.log_error(
                        f"누락된 테이블: {', '.join(sorted(missing_tables))}"
                    )
                    return False

                # 예상치 못한 테이블 확인 (경고)
                unexpected_tables = existing_tables - expected_tables
                if unexpected_tables:
                    self.log_warning(
                        f"예상치 못한 테이블: {', '.join(sorted(unexpected_tables))}"
                    )

                self.log_success(
                    f"모든 테이블 존재 확인 완료 ({len(existing_tables)}개 테이블)"
                )
                return True

        except Exception as e:
            self.log_error(f"테이블 확인 실패: {e}")
            return False

    async def verify_foreign_keys(self) -> bool:
        """외래키 제약조건 확인"""
        print("\n" + "=" * 70)
        print("3. 외래키 제약조건 확인")
        print("=" * 70)

        try:
            async with engine.begin() as conn:
                result = await conn.execute(
                    text(
                        """
                    SELECT
                        tc.table_name,
                        kcu.column_name,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                    ORDER BY tc.table_name, kcu.column_name
                """
                    )
                )
                foreign_keys = result.fetchall()

                if foreign_keys:
                    self.log_success(
                        f"외래키 제약조건 확인 완료 ({len(foreign_keys)}개)"
                    )
                    return True
                else:
                    self.log_warning("외래키 제약조건이 없습니다")
                    return True

        except Exception as e:
            self.log_error(f"외래키 확인 실패: {e}")
            return False

    async def verify_indexes(self) -> bool:
        """인덱스 확인"""
        print("\n" + "=" * 70)
        print("4. 인덱스 확인")
        print("=" * 70)

        try:
            async with engine.begin() as conn:
                result = await conn.execute(
                    text(
                        """
                    SELECT
                        tablename,
                        indexname
                    FROM pg_indexes
                    WHERE schemaname = 'public'
                    ORDER BY tablename, indexname
                """
                    )
                )
                indexes = result.fetchall()

                # 주요 테이블의 필수 인덱스 확인
                required_indexes = {
                    ("user", "ix_user_email"),
                    ("user", "ix_user_username"),
                    ("room", "ix_room_host_id"),
                    ("friend", "idx_friend_user_friend"),
                }

                existing_indexes = {(row[0], row[1]) for row in indexes}
                missing_indexes = required_indexes - existing_indexes

                if missing_indexes:
                    self.log_warning(
                        f"권장 인덱스 누락: {', '.join([f'{t}.{i}' for t, i in missing_indexes])}"
                    )
                else:
                    self.log_success(f"주요 인덱스 확인 완료 ({len(indexes)}개 인덱스)")

                return True

        except Exception as e:
            self.log_error(f"인덱스 확인 실패: {e}")
            return False

    async def test_crud_operations(self) -> bool:
        """CRUD 작업 테스트"""
        print("\n" + "=" * 70)
        print("5. CRUD 작업 테스트")
        print("=" * 70)

        async with AsyncSessionLocal() as session:
            try:
                # 테스트용 사용자 생성
                test_user_id = str(uuid4())
                test_user = User(
                    id=test_user_id,
                    email=f"test_{uuid4().hex[:8]}@test.com",
                    username=f"testuser_{uuid4().hex[:8]}",
                    hashed_password="test_hash",
                    is_active=True,
                    is_verified=False,
                )

                # CREATE 테스트
                session.add(test_user)
                await session.flush()
                self.log_success("CREATE: 사용자 생성 성공")

                # READ 테스트
                result = await session.execute(
                    select(User).where(User.id == test_user_id)
                )
                retrieved_user = result.scalar_one_or_none()
                if retrieved_user and retrieved_user.id == test_user_id:
                    self.log_success("READ: 사용자 조회 성공")
                else:
                    self.log_error("READ: 사용자 조회 실패")
                    await session.rollback()
                    return False

                # UPDATE 테스트
                retrieved_user.username = "updated_username"
                await session.flush()
                await session.refresh(retrieved_user)
                if retrieved_user.username == "updated_username":
                    self.log_success("UPDATE: 사용자 업데이트 성공")
                else:
                    self.log_error("UPDATE: 사용자 업데이트 실패")
                    await session.rollback()
                    return False

                # DELETE 테스트
                await session.delete(retrieved_user)
                await session.flush()
                result = await session.execute(
                    select(User).where(User.id == test_user_id)
                )
                deleted_user = result.scalar_one_or_none()
                if deleted_user is None:
                    self.log_success("DELETE: 사용자 삭제 성공")
                else:
                    self.log_error("DELETE: 사용자 삭제 실패")
                    await session.rollback()
                    return False

                await session.commit()
                return True

            except Exception as e:
                await session.rollback()
                self.log_error(f"CRUD 작업 테스트 실패: {e}")
                import traceback

                traceback.print_exc()
                return False

    async def verify_model_relationships(self) -> bool:
        """모델 관계 확인"""
        print("\n" + "=" * 70)
        print("6. 모델 관계 확인")
        print("=" * 70)

        try:
            # 모든 모델이 Base에 등록되어 있는지 확인
            from app.infrastructure.database.base import Base
            import app.infrastructure.database.models  # noqa: F401

            # 비동기 엔진에서 동기 엔진 가져오기
            registered_tables = set(Base.metadata.tables.keys())

            # 모델 클래스 목록
            model_classes = [
                User,
                Room,
                Participant,
                Timer,
                SessionHistory,
                Post,
                Comment,
                ChatRoom,
                ChatMember,
                ChatMessage,
                Friend,
                FriendRequest,
                Notification,
                Achievement,
                UserAchievement,
                RankingTeam,
                RankingTeamMember,
                UserVerification,
                UserSettings,
                UserGoal,
                ManualSession,
                RoomReservation,
                MatchingPool,
                MatchingProposal,
                MatchingChatRoom,
                MatchingChatMember,
                MatchingMessage,
                Conversation,
                Message,
                UserPresence,
                RankingSession,
                RankingLeaderboard,
                RankingMiniGame,
                RankingTeamInvitation,
                RankingVerificationRequest,
                PostLike,
                CommentLike,
                PostRead,
                Report,
            ]

            missing_models = []
            for model in model_classes:
                if model.__tablename__ not in registered_tables:
                    missing_models.append(f"{model.__name__} ({model.__tablename__})")

            if missing_models:
                self.log_error(f"등록되지 않은 모델: {', '.join(missing_models)}")
                return False

            self.log_success(
                f"모델 관계 확인 완료 ({len(model_classes)}개 모델, {len(registered_tables)}개 테이블)"
            )
            return True

        except Exception as e:
            self.log_error(f"모델 관계 확인 실패: {e}")
            import traceback

            traceback.print_exc()
            return False

    async def verify_data_integrity(self) -> bool:
        """데이터 무결성 확인"""
        print("\n" + "=" * 70)
        print("7. 데이터 무결성 확인")
        print("=" * 70)

        try:
            async with AsyncSessionLocal() as session:
                # NULL 제약조건 확인
                result = await session.execute(
                    text(
                        """
                    SELECT
                        table_name,
                        column_name,
                        is_nullable
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                        AND is_nullable = 'NO'
                        AND column_name NOT IN ('created_at', 'updated_at')
                    ORDER BY table_name, column_name
                """
                    )
                )
                not_null_columns = result.fetchall()

                if not_null_columns:
                    self.log_success(
                        f"NOT NULL 제약조건 확인 완료 ({len(not_null_columns)}개 컬럼)"
                    )

                # 고유 제약조건 확인
                result = await session.execute(
                    text(
                        """
                    SELECT
                        tc.table_name,
                        kcu.column_name
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.constraint_type = 'UNIQUE'
                        AND tc.table_schema = 'public'
                    ORDER BY tc.table_name, kcu.column_name
                """
                    )
                )
                unique_constraints = result.fetchall()

                if unique_constraints:
                    self.log_success(
                        f"UNIQUE 제약조건 확인 완료 ({len(unique_constraints)}개)"
                    )

                return True

        except Exception as e:
            self.log_error(f"데이터 무결성 확인 실패: {e}")
            return False

    async def run_all_checks(self) -> bool:
        """모든 검증 실행"""
        print("\n" + "=" * 70)
        print("🔍 Focus Mate 데이터베이스 종합 검증 시작")
        print("=" * 70)
        print(
            f"📍 데이터베이스: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}"
        )
        print(f"📍 환경: {settings.APP_ENV}")

        checks = [
            ("연결 확인", self.verify_connection),
            ("테이블 존재 확인", self.verify_tables),
            ("외래키 제약조건", self.verify_foreign_keys),
            ("인덱스 확인", self.verify_indexes),
            ("CRUD 작업", self.test_crud_operations),
            ("모델 관계", self.verify_model_relationships),
            ("데이터 무결성", self.verify_data_integrity),
        ]

        results = []
        for name, check_func in checks:
            try:
                result = await check_func()
                results.append((name, result))
            except Exception as e:
                self.log_error(f"{name} 검증 중 예외 발생: {e}")
                results.append((name, False))

        # 결과 요약
        print("\n" + "=" * 70)
        print("📊 검증 결과 요약")
        print("=" * 70)

        for name, result in results:
            status = "✅ 통과" if result else "❌ 실패"
            print(f"{status}: {name}")

        print("\n" + "=" * 70)
        print(f"✅ 성공: {self.success_count}개")
        if self.warnings:
            print(f"⚠️  경고: {len(self.warnings)}개")
        if self.errors:
            print(f"❌ 에러: {len(self.errors)}개")
        print("=" * 70)

        all_passed = all(result for _, result in results)
        if all_passed:
            print("\n🎉 모든 검증을 통과했습니다!")
        else:
            print("\n⚠️  일부 검증에 실패했습니다. 위의 에러 메시지를 확인하세요.")

        return all_passed


async def main():
    """메인 함수"""
    verifier = DatabaseVerifier()
    success = await verifier.run_all_checks()

    # 연결 정리
    await engine.dispose()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
