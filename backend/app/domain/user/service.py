"""User domain service."""

from app.core.config import settings
from app.core.exceptions import UnauthorizedException, ValidationException
from app.core.security import create_access_token, hash_password, verify_password
from app.domain.user.schemas import (
    TokenResponse,
    UserLogin,
    UserProfileUpdate,
    UserRegister,
    UserResponse,
)
from app.infrastructure.database.models.user import User
from app.infrastructure.repositories.user_repository import UserRepository
from app.shared.utils.uuid import generate_uuid


class UserService:
    """User authentication and profile management service."""

    def __init__(self, repository: UserRepository) -> None:
        """Initialize service."""
        self.repository = repository

    async def register(self, data: UserRegister) -> TokenResponse:
        """Register new user.

        Args:
            data: Registration data

        Returns:
            Token response with user data

        Raises:
            ValidationException: If email already exists
        """
        # Check if email already exists
        existing = await self.repository.get_by_email(data.email)
        if existing:
            raise ValidationException("email", "Email already registered")

        # Create user
        # Check if admin email (development only)
        is_admin = (
            settings.APP_ENV == "development"
            and data.email.lower() == settings.ADMIN_EMAIL.lower()
        )

        user = User(
            id=generate_uuid(),
            email=data.email,
            username=data.username,
            hashed_password=hash_password(data.password),
            is_active=True,
            is_verified=False,
            is_admin=is_admin,
            total_focus_time=0,
            total_sessions=0,
        )

        created_user = await self.repository.create(user)

        # Generate JWT token
        access_token = create_access_token({"sub": created_user.id})

        return TokenResponse(
            access_token=access_token,
            user=UserResponse.model_validate(created_user),
        )

    async def login(self, data: UserLogin) -> TokenResponse:
        """Login user.

        Args:
            data: Login credentials

        Returns:
            Token response with user data

        Raises:
            UnauthorizedException: If credentials invalid
        """
        # Get user by email
        user = await self.repository.get_by_email(data.email)
        if not user:
            raise UnauthorizedException("Invalid email or password")

        # Verify password
        if not verify_password(data.password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")

        # Check if user is active
        if not user.is_active:
            raise UnauthorizedException("Account is deactivated")

        # Generate JWT token
        access_token = create_access_token({"sub": user.id})

        return TokenResponse(
            access_token=access_token,
            user=UserResponse.model_validate(user),
        )

    async def get_profile(self, user_id: str) -> UserResponse:
        """Get user profile.

        Args:
            user_id: User identifier

        Returns:
            User profile

        Raises:
            UnauthorizedException: If user not found
        """
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UnauthorizedException("User not found")

        return UserResponse.model_validate(user)

    async def update_profile(
        self, user_id: str, data: UserProfileUpdate
    ) -> UserResponse:
        """Update user profile.

        Args:
            user_id: User identifier
            data: Update data

        Returns:
            Updated user profile

        Raises:
            UnauthorizedException: If user not found
        """
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UnauthorizedException("User not found")

        # Update fields
        if data.username is not None:
            user.username = data.username
        if data.bio is not None:
            user.bio = data.bio

        updated_user = await self.repository.update(user)
        return UserResponse.model_validate(updated_user)

    async def increment_stats(self, user_id: str, focus_minutes: int) -> UserResponse:
        """Increment user statistics after session completion.

        Args:
            user_id: User identifier
            focus_minutes: Minutes focused in session

        Returns:
            Updated user profile
        """
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UnauthorizedException("User not found")

        user.total_focus_time += focus_minutes
        user.total_sessions += 1

        updated_user = await self.repository.update(user)
        return UserResponse.model_validate(updated_user)
