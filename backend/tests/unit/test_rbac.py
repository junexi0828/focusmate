"""Unit tests for RBAC system."""

import pytest
from fastapi import HTTPException

from app.core.rbac import (
    UserRole,
    Permission,
    get_user_role,
    has_permission,
    require_admin,
    require_super_admin,
)


class TestRBAC:
    """Test suite for RBAC system."""

    def test_get_user_role_user(self):
        """Test getting USER role."""
        user = {"id": "123", "role": "user"}
        role = get_user_role(user)
        assert role == UserRole.USER

    def test_get_user_role_admin(self):
        """Test getting ADMIN role."""
        user = {"id": "123", "role": "admin"}
        role = get_user_role(user)
        assert role == UserRole.ADMIN

    def test_get_user_role_super_admin(self):
        """Test getting SUPER_ADMIN role."""
        user = {"id": "123", "role": "super_admin"}
        role = get_user_role(user)
        assert role == UserRole.SUPER_ADMIN

    def test_get_user_role_default(self):
        """Test default role when not specified."""
        user = {"id": "123"}
        role = get_user_role(user)
        assert role == UserRole.USER

    def test_has_permission_user(self):
        """Test USER permissions."""
        user = {"id": "123", "role": "user"}

        # USER should not have any permissions
        assert not has_permission(user, Permission.VERIFY_USERS)
        assert not has_permission(user, Permission.MANAGE_SEASONS)

    def test_has_permission_admin(self):
        """Test ADMIN permissions."""
        user = {"id": "123", "role": "admin"}

        # ADMIN should have these permissions
        assert has_permission(user, Permission.VERIFY_USERS)
        assert has_permission(user, Permission.VIEW_VERIFICATIONS)
        assert has_permission(user, Permission.MANAGE_SEASONS)
        assert has_permission(user, Permission.VIEW_ALL_RANKINGS)
        assert has_permission(user, Permission.VIEW_ANALYTICS)

        # ADMIN should NOT have these permissions
        assert not has_permission(user, Permission.MANAGE_USERS)
        assert not has_permission(user, Permission.BAN_USERS)

    def test_has_permission_super_admin(self):
        """Test SUPER_ADMIN permissions."""
        user = {"id": "123", "role": "super_admin"}

        # SUPER_ADMIN should have all permissions
        assert has_permission(user, Permission.VERIFY_USERS)
        assert has_permission(user, Permission.VIEW_VERIFICATIONS)
        assert has_permission(user, Permission.MANAGE_SEASONS)
        assert has_permission(user, Permission.VIEW_ALL_RANKINGS)
        assert has_permission(user, Permission.MANAGE_USERS)
        assert has_permission(user, Permission.BAN_USERS)
        assert has_permission(user, Permission.VIEW_ANALYTICS)
        assert has_permission(user, Permission.MANAGE_SETTINGS)

    def test_require_admin_with_admin(self):
        """Test require_admin with admin user."""
        admin_user = {"id": "123", "role": "admin"}
        result = require_admin(admin_user)
        assert result == admin_user

    def test_require_admin_with_super_admin(self):
        """Test require_admin with super admin user."""
        super_admin_user = {"id": "123", "role": "super_admin"}
        result = require_admin(super_admin_user)
        assert result == super_admin_user

    def test_require_admin_with_user(self):
        """Test require_admin with regular user (should fail)."""
        regular_user = {"id": "123", "role": "user"}

        with pytest.raises(HTTPException) as exc_info:
            require_admin(regular_user)

        assert exc_info.value.status_code == 403
        assert "Admin access required" in str(exc_info.value.detail)

    def test_require_super_admin_with_super_admin(self):
        """Test require_super_admin with super admin user."""
        super_admin_user = {"id": "123", "role": "super_admin"}
        result = require_super_admin(super_admin_user)
        assert result == super_admin_user

    def test_require_super_admin_with_admin(self):
        """Test require_super_admin with admin user (should fail)."""
        admin_user = {"id": "123", "role": "admin"}

        with pytest.raises(HTTPException) as exc_info:
            require_super_admin(admin_user)

        assert exc_info.value.status_code == 403
        assert "Super admin access required" in str(exc_info.value.detail)

    def test_require_super_admin_with_user(self):
        """Test require_super_admin with regular user (should fail)."""
        regular_user = {"id": "123", "role": "user"}

        with pytest.raises(HTTPException) as exc_info:
            require_super_admin(regular_user)

        assert exc_info.value.status_code == 403
        assert "Super admin access required" in str(exc_info.value.detail)
