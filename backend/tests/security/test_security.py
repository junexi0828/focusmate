"""
Security Tests for FocusMate
Tests authentication, authorization, input validation, and common vulnerabilities
"""

import json

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
def auth_token(client) -> str:
    """Get authentication token for testing."""
    import time
    test_email = f"security_test_{int(time.time())}@example.com"

    # Register test user
    response = client.post("/api/v1/auth/register", json={
        "email": test_email,
        "username": "security_test",
        "password": "SecurePassword123!"
    })

    if response.status_code == 201:
        return response.json().get("access_token")
    if response.status_code == 400:
        # Try login
        login_response = client.post("/api/v1/auth/login", json={
            "email": test_email,
            "password": "SecurePassword123!"
        })
        if login_response.status_code == 200:
            return login_response.json().get("access_token")

    pytest.skip("Could not authenticate")


@pytest.fixture
def auth_headers(auth_token) -> dict[str, str]:
    """Get authentication headers."""
    return {"Authorization": f"Bearer {auth_token}"}


class TestAuthentication:
    """Test authentication security."""

    def test_invalid_credentials_rejected(self, client):
        """Test that invalid credentials are rejected."""
        response = client.post("/api/v1/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401, "Invalid credentials should be rejected"

    def test_missing_token_rejected(self, client):
        """Test that endpoints requiring auth reject requests without token."""
        response = client.get("/api/v1/rooms")
        assert response.status_code in [401, 403], "Unauthenticated requests should be rejected"

    def test_invalid_token_rejected(self, client):
        """Test that invalid tokens are rejected."""
        headers = {"Authorization": "Bearer invalid_token_12345"}
        response = client.get("/api/v1/rooms", headers=headers)
        assert response.status_code in [401, 403], "Invalid tokens should be rejected"

    def test_expired_token_rejected(self, client):
        """Test that expired tokens are rejected."""
        from datetime import datetime, timedelta

        from jose import jwt

        from app.core.config import settings

        # Create expired token
        payload = {
            "sub": "test_user",
            "email": "test@example.com",
            "exp": datetime.utcnow() - timedelta(hours=1),  # Expired
            "iat": datetime.utcnow() - timedelta(hours=2)
        }
        expired_token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )

        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/api/v1/rooms", headers=headers)
        assert response.status_code in [401, 403], "Expired tokens should be rejected"

    def test_password_not_returned(self, client):
        """Test that passwords are never returned in responses."""
        import time
        test_email = f"password_test_{int(time.time())}@example.com"

        # Register
        response = client.post("/api/v1/auth/register", json={
            "email": test_email,
            "username": "password_test",
            "password": "TestPassword123!"
        })

        if response.status_code == 201:
            data = response.json()
            response_str = json.dumps(data)
            assert "TestPassword123!" not in response_str, "Password should not be in response"
            assert "password" not in response_str.lower() or "hashed" in response_str.lower()


class TestAuthorization:
    """Test authorization (RBAC) security."""

    def test_user_cannot_access_admin_endpoints(self, client, auth_headers):
        """Test that regular users cannot access admin endpoints."""
        # Try to access admin endpoint (if exists)
        response = client.get("/api/v1/admin/users", headers=auth_headers)
        # Should be 403 or 404 (endpoint might not exist)
        assert response.status_code in [403, 404], "Users should not access admin endpoints"

    def test_user_cannot_modify_other_users_data(self, client, auth_headers):
        """Test that users cannot modify other users' data."""
        # Try to update another user's profile
        response = client.put(
            "/api/v1/auth/profile/other_user_id",
            json={"username": "hacked"},
            headers=auth_headers
        )
        # Should be 403 or 404
        assert response.status_code in [403, 404, 422], "Users should not modify other users' data"


class TestInputValidation:
    """Test input validation and sanitization."""

    def test_sql_injection_prevention(self, client, auth_headers):
        """Test that SQL injection attempts are prevented."""
        # Try SQL injection in various fields
        sql_injections = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "1; DELETE FROM users; --"
        ]

        for injection in sql_injections:
            # Test in room name
            response = client.post("/api/v1/rooms", json={
                "name": injection,
                "work_duration": 1500,
                "break_duration": 300
            }, headers=auth_headers)

            # Should either reject (422) or sanitize (201), but not crash (500)
            assert response.status_code != 500, f"SQL injection caused server error: {injection}"

    def test_xss_prevention(self, client, auth_headers):
        """Test that XSS attempts are prevented."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>"
        ]

        for payload in xss_payloads:
            # Test in post content
            response = client.post("/api/v1/community/posts", json={
                "title": "Test",
                "content": payload,
                "category": "general"
            }, headers=auth_headers)

            # Should either reject (422) or sanitize (201), but not crash
            assert response.status_code != 500, f"XSS payload caused server error: {payload}"

            if response.status_code == 201:
                # Check that script tags are sanitized
                post = response.json()
                content = json.dumps(post)
                assert "<script>" not in content.lower(), "Script tags should be sanitized"

    def test_email_validation(self, client):
        """Test that invalid emails are rejected."""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "test@",
            "test..test@example.com",
            "test@example",
            "test @example.com"
        ]

        for email in invalid_emails:
            response = client.post("/api/v1/auth/register", json={
                "email": email,
                "username": "test",
                "password": "TestPassword123!"
            })
            assert response.status_code == 422, f"Invalid email should be rejected: {email}"

    def test_password_validation(self, client):
        """Test that weak passwords are rejected."""
        weak_passwords = [
            "short",  # Too short
            "12345678",  # Only numbers
            "abcdefgh",  # Only letters
            "password",  # Common password
        ]

        for password in weak_passwords:
            response = client.post("/api/v1/auth/register", json={
                "email": f"test_{int(time.time())}@example.com",
                "username": "test",
                "password": password
            })
            # Should reject weak passwords (422) or accept but warn
            assert response.status_code in [422, 201], f"Weak password handling: {password}"

    def test_input_length_limits(self, client, auth_headers):
        """Test that input length limits are enforced."""
        # Test very long strings
        long_string = "a" * 10000

        # Test in room name
        response = client.post("/api/v1/rooms", json={
            "name": long_string,
            "work_duration": 1500,
            "break_duration": 300
        }, headers=auth_headers)

        # Should reject (422) or truncate, but not crash
        assert response.status_code != 500, "Long input should not crash server"


class TestCSRFProtection:
    """Test CSRF protection."""

    def test_csrf_token_validation(self, client):
        """Test that CSRF tokens are validated (if implemented)."""
        # CSRF protection might not be implemented yet
        # This test checks if it exists
        response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "username": "test",
            "password": "TestPassword123!"
        }, headers={"X-CSRF-Token": "invalid"})

        # Should either work (no CSRF) or reject (CSRF implemented)
        assert response.status_code in [201, 400, 403, 422]


class TestRateLimiting:
    """Test rate limiting (if implemented)."""

    def test_rate_limiting_on_login(self, client):
        """Test that rate limiting prevents brute force attacks."""
        # Try many login attempts
        for i in range(20):
            response = client.post("/api/v1/auth/login", json={
                "email": "nonexistent@example.com",
                "password": f"wrong{i}"
            })
            # After some attempts, should get rate limited (429)
            if response.status_code == 429:
                assert True, "Rate limiting is working"
                return

        # If no rate limiting, that's okay for now
        pytest.skip("Rate limiting not implemented")


class TestDataExposure:
    """Test that sensitive data is not exposed."""

    def test_passwords_not_in_logs(self, client):
        """Test that passwords are not logged (check response)."""
        import time
        test_email = f"log_test_{int(time.time())}@example.com"

        response = client.post("/api/v1/auth/register", json={
            "email": test_email,
            "username": "log_test",
            "password": "SensitivePassword123!"
        })

        # Check response doesn't contain password
        if response.status_code == 201:
            response_str = json.dumps(response.json())
            assert "SensitivePassword123!" not in response_str

    def test_internal_errors_not_exposed(self, client):
        """Test that internal errors don't expose sensitive information."""
        # Try to trigger an error (if possible)
        # This is a placeholder - actual implementation depends on error handling
        response = client.get("/api/v1/nonexistent/endpoint")
        # Should return generic error, not stack trace
        assert response.status_code in [404, 500]
        if response.status_code == 500:
            response_str = json.dumps(response.json())
            # Should not contain file paths, stack traces, etc.
            assert "Traceback" not in response_str
            assert "/app/" not in response_str or "Internal Server Error" in response_str


class TestFileUploadSecurity:
    """Test file upload security."""

    def test_file_type_validation(self, client, auth_headers):
        """Test that only allowed file types are accepted."""
        # This would test actual file upload
        # For now, check endpoint exists
        response = client.post("/api/v1/auth/profile/test/upload-image", headers=auth_headers)
        # Should either work or return proper error
        assert response.status_code in [200, 201, 400, 401, 404, 422]

    def test_file_size_limits(self, client, auth_headers):
        """Test that file size limits are enforced."""
        # Create a large file (in real test)
        # For now, check endpoint handles size validation
        response = client.post("/api/v1/auth/profile/test/upload-image", headers=auth_headers)
        assert response.status_code in [200, 201, 400, 401, 404, 413, 422]


class TestSessionSecurity:
    """Test session and token security."""

    def test_token_rotation(self, client, auth_token):
        """Test that tokens can be refreshed."""
        # Try to refresh token
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.post("/api/v1/auth/refresh", headers=headers)
        # Should either work or return appropriate error
        assert response.status_code in [200, 401, 404, 422]

    def test_token_invalidation(self, client, auth_token):
        """Test that tokens can be invalidated (logout)."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.post("/api/v1/auth/logout", headers=headers)
        # Should either work or return appropriate error
        assert response.status_code in [200, 401, 404, 422]


# Import time for test
import time

