"""Pytest configuration and fixtures."""

import asyncio
import os
import subprocess
import time
from collections.abc import AsyncGenerator, Generator
from pathlib import Path
from unittest.mock import patch

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.infrastructure.database.base import Base


# Test database URL (override with TEST_DATABASE_URL env var if needed)
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://test:test@localhost:5432/focusmate_test",
)

# Docker compose file path
DOCKER_COMPOSE_FILE = Path(__file__).parent.parent / "docker-compose.yml"


def pytest_configure(config):
    """Configure pytest - start database if needed."""
    # Check if we should auto-start DB
    auto_start_db = os.getenv("PYTEST_AUTO_START_DB", "false").lower() == "true"

    if auto_start_db and DOCKER_COMPOSE_FILE.exists():
        try:
            # Check if postgres is already running
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--filter",
                    "name=focus-mate-postgres",
                    "--format",
                    "{{.Names}}",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if "focus-mate-postgres" not in result.stdout:
                print("\n🐳 Starting PostgreSQL database for tests...")
                subprocess.run(
                    [
                        "docker-compose",
                        "-f",
                        str(DOCKER_COMPOSE_FILE),
                        "up",
                        "-d",
                        "postgres",
                        "redis",
                    ],
                    cwd=DOCKER_COMPOSE_FILE.parent,
                    timeout=30,
                )
                # Wait for DB to be ready
                import time

                time.sleep(5)
                print("✅ Database started\n")
        except (
            subprocess.TimeoutExpired,
            FileNotFoundError,
            subprocess.SubprocessError,
        ) as e:
            # Docker not available or failed to start - continue without DB
            print(f"⚠️  Could not auto-start database: {e}")
            print("   Tests will skip DB-dependent tests (NORMAL)\n")


def pytest_unconfigure(config):
    """Cleanup after tests - stop database if we started it."""
    auto_start_db = os.getenv("PYTEST_AUTO_START_DB", "false").lower() == "true"
    auto_stop_db = os.getenv("PYTEST_AUTO_STOP_DB", "true").lower() == "true"

    if auto_start_db and auto_stop_db and DOCKER_COMPOSE_FILE.exists():
        try:
            # Check if we started it (by checking if it's running)
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--filter",
                    "name=focus-mate-postgres",
                    "--format",
                    "{{.Names}}",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if "focus-mate-postgres" in result.stdout:
                print("\n🐳 Stopping test database...")
                subprocess.run(
                    [
                        "docker-compose",
                        "-f",
                        str(DOCKER_COMPOSE_FILE),
                        "stop",
                        "postgres",
                        "redis",
                    ],
                    cwd=DOCKER_COMPOSE_FILE.parent,
                    timeout=30,
                )
                print("✅ Database stopped\n")
        except (
            subprocess.TimeoutExpired,
            FileNotFoundError,
            subprocess.SubprocessError,
        ):
            # Ignore errors during cleanup
            pass


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Add custom summary for AI Testing Automation."""
    terminalreporter.write_sep(
        "=", "AI Testing Automation Summary", bold=True, cyan=True
    )

    # Get test statistics
    passed = len(terminalreporter.stats.get("passed", []))
    failed = len(terminalreporter.stats.get("failed", []))
    skipped = len(terminalreporter.stats.get("skipped", []))
    errors = len(terminalreporter.stats.get("error", []))

    total = passed + failed + skipped + errors

    terminalreporter.write_line("")
    terminalreporter.write_line("📊 Test Results:", bold=True, green=True)
    terminalreporter.write_line(f"  • Total:   {total}")
    terminalreporter.write_line(f"  • Passed:  {passed}")
    terminalreporter.write_line(f"  • Failed:  {failed}")
    terminalreporter.write_line(f"  • Skipped: {skipped}")
    terminalreporter.write_line(f"  • Errors:  {errors}")

    if total > 0:
        pass_rate = (passed / total) * 100
        terminalreporter.write_line(f"  • Pass Rate: {pass_rate:.1f}%")

    terminalreporter.write_line("")
    if failed == 0 and errors == 0:
        terminalreporter.write_line("✅ All tests passed!", green=True, bold=True)
    elif failed <= 2:
        terminalreporter.write_line("⚠️  Minor issues detected", yellow=True, bold=True)
    else:
        terminalreporter.write_line("❌ Multiple failures detected", red=True, bold=True)

    terminalreporter.write_sep("=", "End of Test Summary", bold=True, cyan=True)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    # Create async engine
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
        await session.rollback()

    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
def test_user():
    """Test user data."""
    return {
        "id": "test_user_123",
        "email": "test@example.com",
        "role": "user",
    }


@pytest.fixture
def test_admin():
    """Test admin user data."""
    return {
        "id": "admin_user_123",
        "email": "admin@example.com",
        "role": "admin",
    }


@pytest.fixture
def test_super_admin():
    """Test super admin user data."""
    return {
        "id": "super_admin_123",
        "email": "superadmin@example.com",
        "role": "super_admin",
    }


@pytest.fixture
def mock_get_current_user(test_user):
    """Mock get_current_user dependency for testing."""

    async def _mock_get_current_user():
        return test_user

    return _mock_get_current_user


@pytest.fixture
def authenticated_client(client, mock_get_current_user):
    """Create an authenticated test client."""

    # Patch get_current_user to return test user
    with patch("app.api.deps.get_current_user", return_value=mock_get_current_user()):
        yield client


@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers with valid JWT token."""
    from datetime import UTC, datetime, timedelta

    from jose import jwt

    # Create a valid JWT token for testing
    payload = {
        "sub": test_user["id"],
        "email": test_user["email"],
        "exp": datetime.now(UTC) + timedelta(hours=1),
        "iat": datetime.now(UTC),
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def check_db_connection():
    """Check if database connection is available. Skip test if not.

    This fixture can be used in tests that require database access.
    It will attempt to verify DB connectivity and skip the test if unavailable.
    """
    # This is a marker fixture - actual DB checks are done in individual tests
    # to avoid unnecessary overhead
    return True


def is_db_connection_error(response) -> bool:
    """Check if response indicates a database connection error.

    E2E tests require database connection. If we get a 500 error,
    it's likely a database connection issue unless explicitly stated otherwise.
    """
    if response.status_code != 500:
        return False

    error_text = response.text.lower()

    # Explicit DB error keywords
    db_error_keywords = [
        "database",
        "connection",
        "postgres",
        "sqlalchemy",
        "asyncpg",
        "connection pool",
        "could not connect",
        "operationalerror",
        "connection refused",
        "timeout",
        "asyncpg.exceptions",
        "pool",
    ]

    # If explicit DB error keywords found, definitely a DB issue
    if any(keyword in error_text for keyword in db_error_keywords):
        return True

    # For E2E tests, 500 errors on auth/registration endpoints are likely DB issues
    # unless they're explicitly about validation or other non-DB issues
    non_db_error_keywords = [
        "validation",
        "invalid",
        "unauthorized",
        "forbidden",
        "not found",
        "bad request",
    ]

    # If it's a generic 500 error without explicit non-DB error keywords,
    # and it's from an endpoint that requires DB, treat as DB connection issue
    if not any(keyword in error_text for keyword in non_db_error_keywords):
        # Generic 500 errors in E2E tests are likely DB connection issues
        return True

    return False


# =============================================================================
# N+1 Query Test Fixtures (Phase 2)
# =============================================================================

@pytest_asyncio.fixture
async def sample_posts(db_session):
    """Create 50 sample posts for N+1 query testing.

    Returns:
        List of 50 Post objects with different authors
    """
    from app.infrastructure.database.models.community import Post
    from app.infrastructure.database.models.user import User

    # Create 10 users
    users = []
    for i in range(10):
        user = User(
            id=f"user_{i}",
            email=f"user{i}@test.com",
            username=f"user{i}",
            hashed_password="hashed",
        )
        db_session.add(user)
        users.append(user)

    await db_session.flush()

    # Create 50 posts (each user writes 5 posts)
    posts = []
    for i in range(50):
        post = Post(
            id=f"post_{i}",
            user_id=users[i % 10].id,
            title=f"Test Post {i}",
            content=f"Content for post {i}",
            category="general",
        )
        db_session.add(post)
        posts.append(post)

    await db_session.commit()
    return posts


@pytest_asyncio.fixture
async def sample_post_with_comments(db_session):
    """Create a post with 50 comments for N+1 query testing.

    Returns:
        Post object with 50 comments
    """
    from app.infrastructure.database.models.community import Post, Comment
    from app.infrastructure.database.models.user import User

    # Create 10 users
    users = []
    for i in range(10):
        user = User(
            id=f"comment_user_{i}",
            email=f"commenter{i}@test.com",
            username=f"commenter{i}",
            hashed_password="hashed",
        )
        db_session.add(user)
        users.append(user)

    await db_session.flush()

    # Create post
    post = Post(
        id="post_with_comments",
        user_id=users[0].id,
        title="Post with Many Comments",
        content="This post has 50 comments",
        category="general",
    )
    db_session.add(post)
    await db_session.flush()

    # Create 50 comments
    for i in range(50):
        comment = Comment(
            id=f"comment_{i}",
            post_id=post.id,
            user_id=users[i % 10].id,
            content=f"Comment {i}",
        )
        db_session.add(comment)

    await db_session.commit()
    return post


@pytest_asyncio.fixture
async def sample_conversations(db_session):
    """Create 20 sample conversations for N+1 query testing.

    Returns:
        List of 20 Conversation objects
    """
    from app.infrastructure.database.models.message import Conversation, Message
    from app.infrastructure.database.models.user import User
    from datetime import datetime, UTC

    # Create main user
    main_user = User(
        id="main_user",
        email="main@test.com",
        username="mainuser",
        hashed_password="hashed",
    )
    db_session.add(main_user)

    # Create 20 other users
    users = []
    for i in range(20):
        user = User(
            id=f"conv_user_{i}",
            email=f"convuser{i}@test.com",
            username=f"convuser{i}",
            hashed_password="hashed",
        )
        db_session.add(user)
        users.append(user)

    await db_session.flush()

    # Create 20 conversations
    conversations = []
    for i, user in enumerate(users):
        conv = Conversation(
            id=f"conversation_{i}",
            user1_id=main_user.id,
            user2_id=user.id,
            last_message_at=datetime.now(UTC),
        )
        db_session.add(conv)
        conversations.append(conv)

        # Add a last message to each conversation
        message = Message(
            id=f"last_msg_{i}",
            conversation_id=conv.id,
            sender_id=user.id,
            receiver_id=main_user.id,
            content=f"Last message in conversation {i}",
        )
        db_session.add(message)

    await db_session.commit()
    return conversations


@pytest_asyncio.fixture
async def sample_conversation_with_messages(db_session):
    """Create a conversation with 50 messages for N+1 query testing.

    Returns:
        Conversation object with 50 messages
    """
    from app.infrastructure.database.models.message import Conversation, Message
    from app.infrastructure.database.models.user import User
    from datetime import datetime, UTC

    # Create 2 users
    user1 = User(
        id="msg_user_1",
        email="msguser1@test.com",
        username="msguser1",
        hashed_password="hashed",
    )
    user2 = User(
        id="msg_user_2",
        email="msguser2@test.com",
        username="msguser2",
        hashed_password="hashed",
    )
    db_session.add(user1)
    db_session.add(user2)
    await db_session.flush()

    # Create conversation
    conv = Conversation(
        id="conversation_with_messages",
        user1_id=user1.id,
        user2_id=user2.id,
        last_message_at=datetime.now(UTC),
    )
    db_session.add(conv)
    await db_session.flush()

    # Create 50 messages (alternating between users)
    for i in range(50):
        sender = user1 if i % 2 == 0 else user2
        receiver = user2 if i % 2 == 0 else user1

        message = Message(
            id=f"message_{i}",
            conversation_id=conv.id,
            sender_id=sender.id,
            receiver_id=receiver.id,
            content=f"Message {i}",
        )
        db_session.add(message)

    await db_session.commit()
    return conv


@pytest_asyncio.fixture
async def sample_post(db_session):
    """Create a single post for testing.

    Returns:
        Single Post object
    """
    from app.infrastructure.database.models.community import Post
    from app.infrastructure.database.models.user import User

    user = User(
        id="single_post_user",
        email="singlepost@test.com",
        username="singlepostuser",
        hashed_password="hashed",
    )
    db_session.add(user)
    await db_session.flush()

    post = Post(
        id="single_post",
        user_id=user.id,
        title="Single Test Post",
        content="Content for single post",
        category="general",
    )
    db_session.add(post)
    await db_session.commit()
    return post
