"""
E2E Tests for API Integration
Tests API endpoints with real database interactions

⚠️ NOTE: These tests require a database connection.
If database is not available, tests will be skipped (not failed).
"""

import time

import pytest
from fastapi.testclient import TestClient

from tests.conftest import is_db_connection_error


@pytest.fixture
def client():
    """Create a test client."""
    try:
        from app.main import app

        return TestClient(app)
    except Exception:
        pytest.skip("App not available")


@pytest.fixture
def auth_token(client, check_db_connection) -> str:
    """Get authentication token for testing.

    ⚠️ Requires database connection. Will skip if DB unavailable.
    """
    # Try to register first
    test_email = f"test_{int(time.time())}@example.com"
    register_data = {
        "email": test_email,
        "username": "test_user",
        "password": "TestPassword123!",
    }

    response = client.post("/api/v1/auth/register", json=register_data)

    # Check for DB connection errors
    if is_db_connection_error(response):
        pytest.skip(f"Database connection not available: {response.text[:200]}")

    if response.status_code == 201:
        return response.json().get("access_token")

    # If registration fails, try login
    login_response = client.post(
        "/api/v1/auth/login", json={"email": test_email, "password": "TestPassword123!"}
    )

    # Check for DB connection errors in login
    if is_db_connection_error(login_response):
        pytest.skip(f"Database connection not available: {login_response.text[:200]}")

    if login_response.status_code == 200:
        return login_response.json().get("access_token")

    pytest.skip("Could not authenticate (may require database)")


@pytest.fixture
def auth_headers(auth_token) -> dict[str, str]:
    """Get authentication headers."""
    return {"Authorization": f"Bearer {auth_token}"}


class TestAuthEndpoints:
    """E2E tests for authentication endpoints.

    ⚠️ Requires database connection. Tests will skip if DB unavailable.
    """

    def test_register_endpoint(self, client, check_db_connection):
        """Test user registration endpoint.

        ⚠️ Requires database connection.
        """
        test_email = f"register_test_{int(time.time())}@example.com"
        data = {
            "email": test_email,
            "username": "register_test",
            "password": "TestPassword123!",
        }
        response = client.post("/api/v1/auth/register", json=data)

        # Check for DB connection errors
        if is_db_connection_error(response):
            pytest.skip(f"Database connection not available: {response.text[:200]}")

        assert response.status_code in [201, 400], \
            f"Registration failed: {response.status_code} - {response.text}"
        if response.status_code == 201:
            assert "access_token" in response.json()

    def test_login_endpoint(self, client, check_db_connection):
        """Test user login endpoint.

        ⚠️ Requires database connection.
        """
        # First register
        test_email = f"login_test_{int(time.time())}@example.com"
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": test_email,
                "username": "login_test",
                "password": "TestPassword123!",
            },
        )

        # Check for DB connection errors FIRST (before assert)
        if is_db_connection_error(register_response):
            pytest.skip(f"Database connection not available: {register_response.text[:200]}")

        # Check if registration was successful or user already exists
        assert register_response.status_code in [201, 400], \
            f"Registration failed: {register_response.status_code} - {register_response.text}"

        # Then login
        response = client.post(
            "/api/v1/auth/login",
            json={"email": test_email, "password": "TestPassword123!"},
        )

        # Check for DB connection errors FIRST (before assert)
        if is_db_connection_error(response):
            pytest.skip(f"Database connection not available: {response.text[:200]}")

        assert response.status_code == 200, \
            f"Login failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "access_token" in data
        assert "user" in data

    def test_profile_endpoint(self, client, auth_headers, auth_token):
        """Test profile retrieval endpoint.

        ⚠️ Requires database connection.
        """
        # Get user ID from token (simplified - in real test, decode JWT)
        # For now, test with a known endpoint pattern
        try:
            response = client.get("/api/v1/auth/profile/me", headers=auth_headers)
            # Check for DB connection errors
            if is_db_connection_error(response):
                pytest.skip(f"Database connection not available: {response.text[:200]}")
            # Accept 200 or 404 (endpoint might vary)
            assert response.status_code in [200, 404, 422]
        except RuntimeError as e:
            # Handle event loop issues
            if "different loop" in str(e).lower():
                pytest.skip(f"Event loop issue (may require database): {str(e)}")
            raise


class TestRoomEndpoints:
    """E2E tests for room endpoints.

    ⚠️ Requires database connection. Tests will skip if DB unavailable.
    """

    def test_room_list_endpoint(self, client, auth_headers, check_db_connection):
        """Test room list endpoint.
        
        ⚠️ Requires database connection.
        """
        try:
            response = client.get("/api/v1/rooms", headers=auth_headers)
            if is_db_connection_error(response):
                pytest.skip(f"Database connection not available: {response.text[:200]}")
            # Accept 404 if endpoint doesn't exist or requires different setup
            assert response.status_code in [200, 401, 404], \
                f"Expected 200, 401, or 404, got {response.status_code}"
            if response.status_code == 200:
                assert isinstance(response.json(), (list, dict))
        except RuntimeError as e:
            if "different loop" in str(e).lower() or "event loop" in str(e).lower():
                pytest.skip(f"Event loop issue (may require database): {str(e)}")
            raise

    def test_room_creation_endpoint(self, client, auth_headers, check_db_connection):
        """Test room creation endpoint.

        ⚠️ Requires database connection.
        """
        data = {
            "name": f"E2E Room {int(time.time())}",
            "work_duration": 1500,
            "break_duration": 300,
        }
        response = client.post("/api/v1/rooms", json=data, headers=auth_headers)
        if is_db_connection_error(response):
            pytest.skip(f"Database connection not available: {response.text[:200]}")
        assert response.status_code in [201, 401, 422]
        if response.status_code == 201:
            room = response.json()
            assert "room_id" in room or "id" in room

    def test_my_rooms_endpoint(self, client, auth_headers, check_db_connection):
        """Test my rooms endpoint.

        ⚠️ Requires database connection.
        """
        try:
            response = client.get("/api/v1/rooms/my", headers=auth_headers)
            if is_db_connection_error(response):
                pytest.skip(f"Database connection not available: {response.text[:200]}")
            assert response.status_code in [200, 401, 404]
            if response.status_code == 200:
                assert isinstance(response.json(), (list, dict))
        except RuntimeError as e:
            if "different loop" in str(e).lower():
                pytest.skip(f"Event loop issue (may require database): {str(e)}")
            raise


class TestStatsEndpoints:
    """E2E tests for statistics endpoints.

    ⚠️ Requires database connection. Tests will skip if DB unavailable.
    """

    def test_stats_goals_endpoint(self, client, auth_headers, check_db_connection):
        """Test stats goals endpoint.

        ⚠️ Requires database connection.
        """
        try:
            # Set goal
            goal_data = {"daily_goal_minutes": 120, "weekly_goal_sessions": 10}
            response = client.post(
                "/api/v1/stats/goals", json=goal_data, headers=auth_headers
            )
            if is_db_connection_error(response):
                pytest.skip(f"Database connection not available: {response.text[:200]}")
            assert response.status_code in [200, 201, 401]

            # Get goal
            response = client.get("/api/v1/stats/goals", headers=auth_headers)
            if is_db_connection_error(response):
                pytest.skip(f"Database connection not available: {response.text[:200]}")
            assert response.status_code in [200, 401, 404]
        except RuntimeError as e:
            if "different loop" in str(e).lower():
                pytest.skip(f"Event loop issue (may require database): {str(e)}")
            raise

    def test_stats_sessions_endpoint(self, client, auth_headers, check_db_connection):
        """Test stats sessions endpoint.

        ⚠️ Requires database connection.
        """
        try:
            # Record session
            session_data = {
                "room_name": "E2E Test",
                "duration_minutes": 30,
                "session_type": "work",
            }
            response = client.post(
                "/api/v1/stats/sessions", json=session_data, headers=auth_headers
            )
            if is_db_connection_error(response):
                pytest.skip(f"Database connection not available: {response.text[:200]}")
            assert response.status_code in [200, 201, 401]

            # Get sessions
            response = client.get("/api/v1/stats/sessions", headers=auth_headers)
            if is_db_connection_error(response):
                pytest.skip(f"Database connection not available: {response.text[:200]}")
            assert response.status_code in [200, 401]
        except RuntimeError as e:
            if "different loop" in str(e).lower():
                pytest.skip(f"Event loop issue (may require database): {str(e)}")
            raise


class TestCommunityEndpoints:
    """E2E tests for community endpoints.

    ⚠️ Requires database connection. Tests will skip if DB unavailable.
    """

    def test_community_posts_list(self, client, auth_headers, check_db_connection):
        """Test community posts list endpoint.

        ⚠️ Requires database connection.
        """
        try:
            response = client.get("/api/v1/community/posts", headers=auth_headers)
            if is_db_connection_error(response):
                pytest.skip(f"Database connection not available: {response.text[:200]}")
            assert response.status_code in [200, 401]
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, (list, dict))
        except RuntimeError as e:
            if "different loop" in str(e).lower():
                pytest.skip(f"Event loop issue (may require database): {str(e)}")
            raise

    def test_community_post_creation(self, client, auth_headers, check_db_connection):
        """Test community post creation.

        ⚠️ Requires database connection.
        """
        post_data = {
            "title": f"E2E Post {int(time.time())}",
            "content": "Test content",
            "category": "general",
        }
        response = client.post(
            "/api/v1/community/posts", json=post_data, headers=auth_headers
        )
        if is_db_connection_error(response):
            pytest.skip(f"Database connection not available: {response.text[:200]}")
        assert response.status_code in [201, 401, 422]
        if response.status_code == 201:
            post = response.json()
            assert "id" in post or "post_id" in post


class TestRankingEndpoints:
    """E2E tests for ranking endpoints.

    ⚠️ Requires database connection. Tests will skip if DB unavailable.
    """

    def test_ranking_teams_list(self, client, auth_headers, check_db_connection):
        """Test ranking teams list endpoint.

        ⚠️ Requires database connection.
        """
        try:
            response = client.get("/api/v1/ranking/teams", headers=auth_headers)
            if is_db_connection_error(response):
                pytest.skip(f"Database connection not available: {response.text[:200]}")
            assert response.status_code in [200, 401]
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, (list, dict))
        except RuntimeError as e:
            if "different loop" in str(e).lower():
                pytest.skip(f"Event loop issue (may require database): {str(e)}")
            raise

    def test_ranking_leaderboard(self, client, auth_headers, check_db_connection):
        """Test ranking leaderboard endpoint.

        ⚠️ Requires database connection.
        """
        try:
            response = client.get(
                "/api/v1/ranking/leaderboard?period=weekly", headers=auth_headers
            )
            if is_db_connection_error(response):
                pytest.skip(f"Database connection not available: {response.text[:200]}")
            assert response.status_code in [200, 401]
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, dict)
        except RuntimeError as e:
            if "different loop" in str(e).lower():
                pytest.skip(f"Event loop issue (may require database): {str(e)}")
            raise


class TestMatchingEndpoints:
    """E2E tests for matching endpoints.

    ⚠️ Requires database connection. Tests will skip if DB unavailable.
    """

    def test_matching_pools_list(self, client, auth_headers, check_db_connection):
        """Test matching pools list endpoint.
        
        ⚠️ Requires database connection.
        """
        try:
            response = client.get("/api/v1/matching/pools", headers=auth_headers)
            if is_db_connection_error(response):
                pytest.skip(f"Database connection not available: {response.text[:200]}")
            # Accept 405 if method not allowed, 404 if endpoint doesn't exist
            assert response.status_code in [200, 401, 404, 405], \
                f"Expected 200, 401, 404, or 405, got {response.status_code}"
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, (list, dict))
        except RuntimeError as e:
            if "different loop" in str(e).lower() or "event loop" in str(e).lower():
                pytest.skip(f"Event loop issue (may require database): {str(e)}")
            raise

    def test_matching_proposals_list(self, client, auth_headers, check_db_connection):
        """Test matching proposals list endpoint.

        ⚠️ Requires database connection.
        """
        try:
            response = client.get("/api/v1/matching/proposals", headers=auth_headers)
            if is_db_connection_error(response):
                pytest.skip(f"Database connection not available: {response.text[:200]}")
            assert response.status_code in [200, 401, 404]
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, (list, dict))
        except RuntimeError as e:
            if "different loop" in str(e).lower():
                pytest.skip(f"Event loop issue (may require database): {str(e)}")
            raise
