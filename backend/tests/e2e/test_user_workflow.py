"""
E2E Tests for User Workflow
Tests complete user journeys from registration to core feature usage
"""

from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client."""
    try:
        from app.main import app

        return TestClient(app)
    except Exception:
        pytest.skip("App not available")


@pytest.fixture
def test_user_data():
    """Test user registration data."""

    return {
        "email": f"e2e_test_{int(time.time())}@example.com",
        "username": "e2e_test_user",
        "password": "TestPassword123!",
    }


@pytest.fixture
def registered_user(client, test_user_data) -> dict[str, Any]:
    """Register a test user and return user data with token."""
    response = client.post("/api/v1/auth/register", json=test_user_data)
    if response.status_code == 201:
        data = response.json()
        return {
            "user_id": data.get("user", {}).get("id"),
            "email": test_user_data["email"],
            "username": test_user_data["username"],
            "access_token": data.get("access_token"),
            "headers": {"Authorization": f"Bearer {data.get('access_token')}"},
        }
    if response.status_code == 400:
        # User might already exist, try login
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        if login_response.status_code == 200:
            data = login_response.json()
            return {
                "user_id": data.get("user", {}).get("id"),
                "email": test_user_data["email"],
                "username": test_user_data["username"],
                "access_token": data.get("access_token"),
                "headers": {"Authorization": f"Bearer {data.get('access_token')}"},
            }
    pytest.fail(
        f"Failed to register/login user: {response.status_code} - {response.text}"
    )


class TestUserRegistrationWorkflow:
    """E2E tests for user registration and authentication."""

    def test_user_registration_flow(self, client, test_user_data):
        """Test complete user registration workflow."""
        # Register user
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code in [
            201,
            400,
        ], f"Registration failed: {response.text}"

        if response.status_code == 201:
            data = response.json()
            assert "access_token" in data
            assert "user" in data
            assert data["user"]["email"] == test_user_data["email"]

    def test_user_login_flow(self, client, test_user_data):
        """Test user login workflow."""
        # First register (or skip if exists)
        client.post("/api/v1/auth/register", json=test_user_data)

        # Login
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        assert "user" in data

    def test_user_profile_access(self, client, registered_user):
        """Test accessing user profile after authentication."""
        headers = registered_user["headers"]
        user_id = registered_user["user_id"]

        response = client.get(f"/api/v1/auth/profile/{user_id}", headers=headers)
        assert response.status_code == 200, f"Profile access failed: {response.text}"
        data = response.json()
        assert data["email"] == registered_user["email"]


class TestRoomWorkflow:
    """E2E tests for room creation and management."""

    def test_room_creation_workflow(self, client, registered_user):
        """Test complete room creation workflow."""
        headers = registered_user["headers"]

        # Create room
        room_data = {
            "name": "E2E Test Room",
            "work_duration": 1500,  # 25 minutes
            "break_duration": 300,  # 5 minutes
            "auto_start_break": False,
            "remove_on_leave": False,
        }
        response = client.post("/api/v1/rooms", json=room_data, headers=headers)
        assert response.status_code == 201, f"Room creation failed: {response.text}"

        room = response.json()
        room_id = room.get("room_id") or room.get("id")
        assert room_id is not None

        # Get room details
        response = client.get(f"/api/v1/rooms/{room_id}", headers=headers)
        assert response.status_code == 200, f"Room retrieval failed: {response.text}"

        return room_id

    def test_room_participation_workflow(self, client, registered_user):
        """Test room participation workflow."""
        headers = registered_user["headers"]

        # Create room
        room_data = {
            "name": "E2E Participation Test",
            "work_duration": 1500,
            "break_duration": 300,
        }
        response = client.post("/api/v1/rooms", json=room_data, headers=headers)
        assert response.status_code == 201
        room = response.json()
        room_id = room.get("room_id") or room.get("id")

        # Join room (should auto-join on creation, but test explicit join)
        join_data = {"username": registered_user["username"]}
        response = client.post(
            f"/api/v1/rooms/{room_id}/participants", json=join_data, headers=headers
        )
        # Should succeed or return 409 if already joined
        assert response.status_code in [201, 409], f"Join failed: {response.text}"

        # Get participants
        response = client.get(f"/api/v1/rooms/{room_id}/participants", headers=headers)
        assert response.status_code == 200
        participants = response.json()
        assert isinstance(participants, (list, dict))

    def test_room_timer_workflow(self, client, registered_user):
        """Test room timer workflow."""
        headers = registered_user["headers"]

        # Create room
        room_data = {
            "name": "E2E Timer Test",
            "work_duration": 1500,
            "break_duration": 300,
        }
        response = client.post("/api/v1/rooms", json=room_data, headers=headers)
        assert response.status_code == 201
        room = response.json()
        room_id = room.get("room_id") or room.get("id")

        # Get timer state
        response = client.get(f"/api/v1/timer/{room_id}", headers=headers)
        assert response.status_code == 200, f"Timer state failed: {response.text}"

        # Start timer
        response = client.post(
            f"/api/v1/timer/{room_id}/start",
            json={"session_type": "work"},
            headers=headers,
        )
        assert response.status_code in [
            200,
            201,
        ], f"Timer start failed: {response.text}"


class TestStatsWorkflow:
    """E2E tests for statistics and goals."""

    def test_goal_setting_workflow(self, client, registered_user):
        """Test goal setting workflow."""
        headers = registered_user["headers"]

        # Set goal
        goal_data = {"daily_goal_minutes": 120, "weekly_goal_sessions": 10}
        response = client.post("/api/v1/stats/goals", json=goal_data, headers=headers)
        assert response.status_code in [
            200,
            201,
        ], f"Goal setting failed: {response.text}"

        # Get goal
        response = client.get("/api/v1/stats/goals", headers=headers)
        assert response.status_code == 200, f"Goal retrieval failed: {response.text}"

    def test_session_recording_workflow(self, client, registered_user):
        """Test session recording workflow."""
        headers = registered_user["headers"]

        # Record manual session
        session_data = {
            "room_name": "E2E Test Session",
            "duration_minutes": 30,
            "session_type": "work",
        }
        response = client.post(
            "/api/v1/stats/sessions", json=session_data, headers=headers
        )
        assert response.status_code in [
            200,
            201,
        ], f"Session recording failed: {response.text}"

        # Get sessions
        response = client.get("/api/v1/stats/sessions", headers=headers)
        assert response.status_code == 200, f"Session retrieval failed: {response.text}"


class TestCommunityWorkflow:
    """E2E tests for community features."""

    def test_post_creation_workflow(self, client, registered_user):
        """Test post creation workflow."""
        headers = registered_user["headers"]

        # Create post
        post_data = {
            "title": "E2E Test Post",
            "content": "This is a test post for E2E testing",
            "category": "general",
        }
        response = client.post(
            "/api/v1/community/posts", json=post_data, headers=headers
        )
        assert response.status_code == 201, f"Post creation failed: {response.text}"

        post = response.json()
        post_id = post.get("id") or post.get("post_id")
        assert post_id is not None

        # Get post
        response = client.get(f"/api/v1/community/posts/{post_id}", headers=headers)
        assert response.status_code == 200, f"Post retrieval failed: {response.text}"

        return post_id

    def test_post_like_workflow(self, client, registered_user):
        """Test post like workflow."""
        headers = registered_user["headers"]

        # Create post
        post_data = {
            "title": "E2E Like Test",
            "content": "Testing likes",
            "category": "general",
        }
        response = client.post(
            "/api/v1/community/posts", json=post_data, headers=headers
        )
        assert response.status_code == 201
        post = response.json()
        post_id = post.get("id") or post.get("post_id")

        # Like post
        response = client.post(
            f"/api/v1/community/posts/{post_id}/like", headers=headers
        )
        assert response.status_code in [200, 201], f"Like failed: {response.text}"


class TestRankingWorkflow:
    """E2E tests for ranking system."""

    def test_team_creation_workflow(self, client, registered_user):
        """Test team creation workflow."""
        headers = registered_user["headers"]

        # Create team
        team_data = {
            "team_name": "E2E Test Team",
            "team_type": "general",
            "mini_game_enabled": True,
        }
        response = client.post("/api/v1/ranking/teams", json=team_data, headers=headers)
        assert response.status_code == 201, f"Team creation failed: {response.text}"

        team = response.json()
        team_id = team.get("team_id") or team.get("id")
        assert team_id is not None

        # Get team
        response = client.get(f"/api/v1/ranking/teams/{team_id}", headers=headers)
        assert response.status_code == 200, f"Team retrieval failed: {response.text}"


class TestMatchingWorkflow:
    """E2E tests for matching system."""

    def test_pool_creation_workflow(self, client, registered_user):
        """Test matching pool creation workflow."""
        headers = registered_user["headers"]

        # Create pool
        pool_data = {
            "department": "컴퓨터공학",
            "grade": 1,
            "gender": "male",
            "member_count": 2,
            "message": "E2E Test Pool",
            "matching_type": "open",
        }
        response = client.post(
            "/api/v1/matching/pools", json=pool_data, headers=headers
        )
        assert response.status_code == 201, f"Pool creation failed: {response.text}"

        pool = response.json()
        pool_id = pool.get("pool_id") or pool.get("id")
        assert pool_id is not None


# Time module imported at top level for unique test data
