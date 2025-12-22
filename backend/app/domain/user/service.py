"""User domain service."""

from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe

from app.core.config import settings
from app.core.exceptions import UnauthorizedException, ValidationException
from app.core.security import create_access_token, hash_password, verify_password
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
            ValidationException: If token is invalid or expired
        """
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

        async with httpx.AsyncClient() as client:
            try:
                import logging
                logger = logging.getLogger(__name__)

                token_response = await client.post(token_url, params=token_params)
                token_response.raise_for_status()
                token_data = token_response.json()

                logger.debug(f"Naver token response: {token_data}")

                if "error" in token_data:
                    error_msg = f"Naver OAuth error: {token_data.get('error_description', 'Unknown error')}"
                    logger.error(f"Naver OAuth token error: {error_msg}")
                    raise ValidationException("oauth", error_msg)

                access_token = token_data.get("access_token")
                if not access_token:
                    logger.error("Failed to get access token from Naver")
                    raise ValidationException("oauth", "Failed to get access token from Naver")

                # Get user info from Naver
                userinfo_url = "https://openapi.naver.com/v1/nid/me"
                headers = {"Authorization": f"Bearer {access_token}"}
                userinfo_response = await client.get(userinfo_url, headers=headers)
                userinfo_response.raise_for_status()
                userinfo_data = userinfo_response.json()
                
                logger.info(f"Naver userinfo full response: {userinfo_data}")

                if userinfo_data.get("resultcode") != "00":
                    error_msg = f"Failed to get user info from Naver: {userinfo_data.get('message', 'Unknown error')}"
                    logger.error(f"Naver userinfo error: {error_msg}")
                    raise ValidationException("oauth", error_msg)

                naver_user = userinfo_data.get("response", {})
                logger.info(f"Naver user response object: {naver_user}")
                
                naver_id = naver_user.get("id")
                email = naver_user.get("email")
                nickname = naver_user.get("nickname") or naver_user.get("name") or "네이버 사용자"
                
                logger.info(f"Naver user data extracted: id={naver_id}, email={email}, nickname={nickname}")

                if not naver_id or not email:
                    logger.error(f"Incomplete user information: id={naver_id}, email={email}, full response keys: {list(naver_user.keys())}")
                    raise ValidationException("oauth", "Incomplete user information from Naver. 이메일 정보가 필요합니다. 네이버 개발자 센터에서 '회원정보 조회' API 사용 설정과 이메일 정보 제공 동의를 확인해주세요.")

                # Check if user exists by naver_id
                user = await self.repository.get_by_naver_id(naver_id)

                if not user:
                    # Check if email already exists
                    existing_user = await self.repository.get_by_email(email)
                    if existing_user:
                        # Link Naver account to existing user
                        existing_user.naver_id = naver_id
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
                    # Update user info if needed
                    if not user.email or user.email != email:
                        user.email = email
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
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Naver OAuth HTTP error: {e!s}", exc_info=True)
                raise ValidationException("oauth", f"Naver OAuth HTTP error: {e!s}")
            except ValidationException:
                raise
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Naver OAuth error: {e!s}", exc_info=True)
                raise ValidationException("oauth", f"Naver OAuth error: {e!s}")
