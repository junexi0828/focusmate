"""Admin role-based access control (RBAC) system."""

from enum import Enum
from functools import wraps
from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.api.deps import get_current_user


class UserRole(str, Enum):
    """User roles."""

    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class Permission(str, Enum):
    """System permissions."""

    # Verification permissions
    VERIFY_USERS = "verify_users"
    VIEW_VERIFICATIONS = "view_verifications"

    # Ranking permissions
    MANAGE_SEASONS = "manage_seasons"
    VIEW_ALL_RANKINGS = "view_all_rankings"

    # User management
    MANAGE_USERS = "manage_users"
    BAN_USERS = "ban_users"

    # System
    VIEW_ANALYTICS = "view_analytics"
    MANAGE_SETTINGS = "manage_settings"


# Role-Permission mapping
ROLE_PERMISSIONS = {
    UserRole.USER: set(),
    UserRole.ADMIN: {
        Permission.VERIFY_USERS,
        Permission.VIEW_VERIFICATIONS,
        Permission.MANAGE_SEASONS,
        Permission.VIEW_ALL_RANKINGS,
        Permission.VIEW_ANALYTICS,
    },
    UserRole.SUPER_ADMIN: {
        Permission.VERIFY_USERS,
        Permission.VIEW_VERIFICATIONS,
        Permission.MANAGE_SEASONS,
        Permission.VIEW_ALL_RANKINGS,
        Permission.MANAGE_USERS,
        Permission.BAN_USERS,
        Permission.VIEW_ANALYTICS,
        Permission.MANAGE_SETTINGS,
    },
}


def get_user_role(user: dict) -> UserRole:
    """Get user role from user dict."""
    role_str = user.get("role", "user")
    try:
        return UserRole(role_str)
    except ValueError:
        return UserRole.USER


def has_permission(user: dict, permission: Permission) -> bool:
    """Check if user has specific permission."""
    role = get_user_role(user)
    return permission in ROLE_PERMISSIONS.get(role, set())


def require_permission(permission: Permission):
    """Decorator to require specific permission."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            if not has_permission(current_user, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission.value} required",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_admin(current_user: Annotated[dict, Depends(get_current_user)]) -> dict:
    """Dependency to require admin role."""
    role = get_user_role(current_user)
    if role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


def require_super_admin(
    current_user: Annotated[dict, Depends(get_current_user)]
) -> dict:
    """Dependency to require super admin role."""
    role = get_user_role(current_user)
    if role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required",
        )
    return current_user
