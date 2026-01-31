"""User domain service."""

from secrets import token_urlsafe

from app.core.config import settings
from app.core.exceptions import UnauthorizedException, ValidationException
from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.domain.user.schemas import (
    NaverOAuthCallback,
    PasswordResetComplete,
    PasswordResetRequest,
    PasswordResetVerify,
    TokenResponse,
    UserLogin,
    UserProfileUpdate,
    UserRegister,
    UserResponse,
)
from app.infrastructure.database.models.user import User
from app.infrastructure.repositories.refresh_token_repository import RefreshTokenRepository
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.redis.session_helpers import store_token_mapping
from app.shared.utils.uuid import generate_uuid
from datetime import UTC, datetime, timedelta
from uuid import uuid4


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
            ValidationException: If email already exists or password is weak
        """
        # SECURITY: Validate password strength
        from app.shared.utils.password_validator import validate_password_strength

        password_validation = validate_password_strength(data.password)
        if not password_validation.is_valid:
            raise ValidationException(
                "password",
                " ".join(password_validation.errors)
            )

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

        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.now(UTC):
            minutes_left = int(
                (user.locked_until - datetime.now(UTC)).total_seconds() / 60
            )
            raise UnauthorizedException(
                f"Account is locked. Please try again in {max(1, minutes_left)} minutes."
            )

        # Verify password
        if not verify_password(data.password, user.hashed_password):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.now(UTC) + timedelta(minutes=15)
                await self.repository.update(user)
                # Commit to persist lockout even if exception is raised
                await self.repository.db.commit()
                raise UnauthorizedException(
                    "Too many failed attempts. Account locked for 15 minutes."
                )

            await self.repository.update(user)
            # Commit to persist failed attempts even if exception is raised
            await self.repository.db.commit()
            raise UnauthorizedException("Invalid email or password")

        # Check if user is active
        if not user.is_active:
            raise UnauthorizedException("Account is deactivated")

        # Reset failed attempts on successful login
        if user.failed_login_attempts > 0 or user.locked_until:
            user.failed_login_attempts = 0
            user.locked_until = None
            await self.repository.update(user)

        # Generate JWT token
        access_token = create_access_token({"sub": user.id})

        # Generate refresh token
        family_id = str(uuid4())
        refresh_token_repo = RefreshTokenRepository(self.repository.db)
        refresh_token = await refresh_token_repo.create(
            user_id=user.id,
            family_id=family_id,
            expires_at=datetime.now(UTC) + timedelta(days=7),
            absolute_expires_at=datetime.now(UTC) + timedelta(days=30),
        )
        refresh_token_str = create_refresh_token(
            user.id, refresh_token.token_id, family_id
        )

        # Store mapping for WebSocket use (non-critical)
        try:
            await store_token_mapping(user.id, refresh_token.token_id)
        except Exception:
            pass

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
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
        if data.school is not None:
            user.school = data.school
        if data.profile_image is not None:
            user.profile_image = data.profile_image

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

    async def request_password_reset(self, data: PasswordResetRequest) -> dict:
        """Request password reset.

        Args:
            data: Password reset request with email

        Returns:
            Success message (always returns success to prevent email enumeration)

        Raises:
            ValidationException: If email format is invalid
        """
        from app.infrastructure.email.email_service import EmailService

        # Get user by email
        user = await self.repository.get_by_email(data.email)

        # Always return success to prevent email enumeration
        # Only send email if user exists
        if user:
            # Generate reset token
            reset_token = token_urlsafe(32)
            expires_at = datetime.now(UTC) + timedelta(hours=1)

            # Update user with reset token
            user.password_reset_token = reset_token
            user.password_reset_expires = expires_at
            await self.repository.update(user)

            # Send email with reset link
            email_service = EmailService()
            reset_url = f"{settings.FRONTEND_URL or 'http://localhost:3000'}/auth/reset-password?token={reset_token}"
            subject = "[FocusMate] 비밀번호 재설정 요청"
            body = f"""
안녕하세요, {user.username}님

비밀번호 재설정을 요청하셨습니다.
아래 링크를 클릭하여 새 비밀번호를 설정해주세요.

{reset_url}

이 링크는 1시간 동안만 유효합니다.
만약 비밀번호 재설정을 요청하지 않으셨다면, 이 이메일을 무시하셔도 됩니다.

감사합니다.
FocusMate 팀
"""
            await email_service._send_email(user.email, subject, body)

        return {"message": "If the email exists, a password reset link has been sent."}

    async def verify_password_reset_token(self, data: PasswordResetVerify) -> dict:
        """Verify password reset token.

        Args:
            data: Token verification data

        Returns:
            Token validity status

        Raises:
            ValidationException: If token is invalid or expired
        """
        # Find user by reset token
        user = await self.repository.get_by_password_reset_token(data.token)
        if not user:
            raise ValidationException("token", "Invalid or expired reset token")

        # Check if token is expired
        if not user.password_reset_expires or user.password_reset_expires < datetime.now(UTC):
            raise ValidationException("token", "Reset token has expired")

        return {"valid": True, "message": "Token is valid"}

    async def complete_password_reset(self, data: PasswordResetComplete) -> dict:
        """Complete password reset.

        Args:
            data: Password reset completion data

        Returns:
            Success message

        Raises:
            ValidationException: If token is invalid, expired, or password is weak
        """
        # SECURITY: Validate password strength
        from app.shared.utils.password_validator import validate_password_strength

        password_validation = validate_password_strength(data.new_password)
        if not password_validation.is_valid:
            raise ValidationException(
                "password",
                " ".join(password_validation.errors)
            )

        # Find user by reset token
        user = await self.repository.get_by_password_reset_token(data.token)
        if not user:
            raise ValidationException("token", "Invalid or expired reset token")

        # Check if token is expired
        if not user.password_reset_expires or user.password_reset_expires < datetime.now(UTC):
            raise ValidationException("token", "Reset token has expired")

        # Update password
        user.hashed_password = hash_password(data.new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        await self.repository.update(user)

        return {"message": "Password has been reset successfully"}

    async def naver_oauth_login(self, data: NaverOAuthCallback) -> TokenResponse:
        """Login or register user via Naver OAuth.

        Args:
            data: Naver OAuth callback data

        Returns:
            Token response with user data

        Raises:
            ValidationException: If OAuth authentication fails
        """
        import httpx

        # Exchange code for access token
        token_url = "https://nid.naver.com/oauth2.0/token"
        token_params = {
            "grant_type": "authorization_code",
            "client_id": settings.NAVER_CLIENT_ID,
            "client_secret": settings.NAVER_CLIENT_SECRET,
            "code": data.code,
            "state": data.state or "",
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                token_response = await client.post(token_url, params=token_params)
                token_response.raise_for_status()
                token_data = token_response.json()

                if "error" in token_data:
                    raise ValidationException("oauth", f"Naver OAuth error: {token_data.get('error_description', 'Unknown error')}")

                access_token = token_data.get("access_token")
                if not access_token:
                    raise ValidationException("oauth", "Failed to get access token from Naver")

                # Get user info from Naver
                userinfo_url = "https://openapi.naver.com/v1/nid/me"
                headers = {"Authorization": f"Bearer {access_token}"}
                userinfo_response = await client.get(userinfo_url, headers=headers)
                userinfo_response.raise_for_status()
                userinfo_data = userinfo_response.json()

                if userinfo_data.get("resultcode") != "00":
                    raise ValidationException("oauth", f"Failed to get user info from Naver: {userinfo_data.get('message', 'Unknown error')}")

                naver_user = userinfo_data.get("response", {})
                naver_id = naver_user.get("id")
                email = naver_user.get("email")
                nickname = naver_user.get("nickname") or naver_user.get("name") or "네이버 사용자"

                if not naver_id or not email:
                    raise ValidationException("oauth", "이메일 정보 제공 동의가 필요합니다. 네이버 로그인 시 이메일 정보 제공에 동의해주세요.")

                # Check if user exists by naver_id
                user = await self.repository.get_by_naver_id(naver_id)

                if not user:
                    # Check if email already exists
                    existing_user = await self.repository.get_by_email(email)
                    if existing_user:
                        # SECURITY: Check if another user already has this naver_id
                        # This prevents naver_id conflicts during account linking
                        if existing_user.naver_id and existing_user.naver_id != naver_id:
                            raise ValidationException(
                                "oauth",
                                "이 계정은 이미 다른 네이버 계정과 연동되어 있습니다. "
                                "기존 연동을 해제한 후 다시 시도해주세요."
                            )

                        # Link Naver account to existing user
                        existing_user.naver_id = naver_id
                        existing_user.is_verified = True  # Naver verified
                        user = await self.repository.update(existing_user)
                    else:
                        # Create new user
                        user = User(
                            id=generate_uuid(),
                            email=email,
                            username=nickname,
                            hashed_password=hash_password(token_urlsafe(32)),  # Random password for OAuth users
                            is_active=True,
                            is_verified=True,  # Naver verified email
                            is_admin=False,
                            naver_id=naver_id,
                            total_focus_time=0,
                            total_sessions=0,
                        )
                        user = await self.repository.create(user)
                else:
                    # Update user info if needed (with security checks)
                    # SECURITY: Only update email if it's not already taken by another user
                    if not user.email or user.email != email:
                        # Check if the new email is already taken by a different user
                        email_conflict = await self.repository.get_by_email(email)
                        if email_conflict and email_conflict.id != user.id:
                            # CRITICAL: Another user already has this email - don't update!
                            # This prevents account hijacking via email change on Naver
                            raise ValidationException(
                                "oauth",
                                f"이메일 충돌: {email}은(는) 이미 다른 계정에서 사용 중입니다. "
                                f"네이버 계정의 이메일을 변경하신 경우, 기존 이메일로 되돌려주세요."
                            )
                        user.email = email

                    # Update username if it's default or empty
                    if not user.username or user.username == "네이버 사용자":
                        user.username = nickname

                    user.naver_id = naver_id
                    user.is_verified = True
                    user = await self.repository.update(user)

                # Generate JWT token
                jwt_token = create_access_token({"sub": user.id})

                return TokenResponse(
                    access_token=jwt_token,
                    user=UserResponse.model_validate(user),
                )

            except httpx.HTTPError as e:
                raise ValidationException("oauth", f"Naver OAuth HTTP error: {e!s}")
            except ValidationException:
                raise
            except Exception as e:
                raise ValidationException("oauth", f"Naver OAuth error: {e!s}")

    async def naver_oauth_unlink(self, naver_id: str) -> dict:
        """Unlink Naver OAuth account.

        Args:
            naver_id: Naver OAuth ID

        Returns:
            Success message
        """
        user = await self.repository.get_by_naver_id(naver_id)
        if user:
            # Unlink Naver account (set naver_id to None)
            user.naver_id = None
            await self.repository.update(user)
            return {"message": "Naver account unlinked successfully"}
        return {"message": "User not found or already unlinked"}

    async def delete_account(self, user_id: str, password: str) -> dict:
        """Delete user account.

        Args:
            user_id: User identifier
            password: Password for confirmation

        Returns:
            Success message

        Raises:
            UnauthorizedException: If user not found or password incorrect
        """
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UnauthorizedException("User not found")

        # Verify password
        if not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Invalid password")

        # Delete user
        await self.repository.delete(user)

        return {"message": "Account deleted successfully"}
