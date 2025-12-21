"""Notification domain service."""

import logging
from datetime import UTC, datetime

from app.domain.notification.schemas import (
    NotificationCreate,
    NotificationResponse,
)
from app.infrastructure.database.models.notification import Notification
from app.infrastructure.email.email_service import EmailService
from app.infrastructure.repositories.notification_repository import (
    NotificationRepository,
)
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.user_settings_repository import (
    UserSettingsRepository,
)
from app.infrastructure.websocket.notification_manager import notification_ws_manager
from app.shared.utils.uuid import generate_uuid


logger = logging.getLogger(__name__)


class NotificationService:
    """Notification service for managing user notifications."""

    def __init__(
        self,
        repository: NotificationRepository,
        settings_repository: UserSettingsRepository | None = None,
        user_repository: UserRepository | None = None,
        email_service: EmailService | None = None,
    ) -> None:
        """Initialize service.

        Args:
            repository: Notification repository
            settings_repository: User settings repository (optional)
            user_repository: User repository (optional)
            email_service: Email service (optional)
        """
        self.repository = repository
        self.settings_repository = settings_repository
        self.user_repository = user_repository
        self.email_service = email_service or EmailService()

    async def _check_notification_allowed(
        self, user_id: str, notification_type: str
    ) -> bool:
        """Check if notification is allowed based on user settings.

        Args:
            user_id: User identifier
            notification_type: Type of notification (session, achievement, message, etc.)

        Returns:
            True if notification is allowed, False otherwise
        """
        if not self.settings_repository:
            # If settings repository is not available, allow all notifications
            logger.warning(f"Settings repository not available, allowing notification for user {user_id}")
            return True

        try:
            settings = await self.settings_repository.get_by_user_id(user_id)
            if not settings:
                # Default to allowing notifications if settings don't exist
                logger.debug(f"No settings found for user {user_id}, allowing notification")
                return True

            # Check type-specific settings
            type_mapping = {
                "session": settings.notification_session,
                "achievement": settings.notification_achievement,
                "message": settings.notification_message,
                "friend_request": settings.notification_message,  # Use message setting
                "team_invitation": settings.notification_message,  # Use message setting
                "post_comment": settings.notification_message,  # Use message setting
                "post_like": settings.notification_message,  # Use message setting
            }

            # Check if this notification type has a specific setting
            if notification_type in type_mapping:
                allowed = type_mapping[notification_type]
                logger.debug(
                    f"Notification type '{notification_type}' for user {user_id}: {'allowed' if allowed else 'blocked'}"
                )
                return allowed

            # For other types (system, etc.), allow by default
            logger.debug(f"Notification type '{notification_type}' for user {user_id}: allowed (default)")
            return True

        except Exception as e:
            logger.error(f"Error checking notification settings for user {user_id}: {e}")
            # On error, allow notification to avoid blocking legitimate notifications
            return True

    async def create_notification(
        self, data: NotificationCreate
    ) -> NotificationResponse | None:
        """Create a new notification with user settings check.

        Args:
            data: Notification data

        Returns:
            Created notification, or None if notification is blocked by user settings

        Raises:
            ValidationException: If validation fails
        """
        # Check if notification is allowed based on user settings
        if not await self._check_notification_allowed(data.user_id, data.type):
            logger.info(
                f"Notification blocked for user {data.user_id} (type: {data.type}) due to user settings"
            )
            return None

        notification = Notification(
            notification_id=generate_uuid(),
            user_id=data.user_id,
            type=data.type,
            title=data.title,
            message=data.message,
            data=data.data,
            is_read=False,
        )

        created = await self.repository.create(notification)
        notification_response = NotificationResponse.model_validate(created)

        # Send email notification if enabled
        await self._send_email_notification(created)

        # Send push notification via WebSocket if enabled
        await self._send_push_notification(created)

        return notification_response

    async def _send_email_notification(self, notification: Notification) -> None:
        """Send email notification if user has email notifications enabled.

        Args:
            notification: Notification to send
        """
        if not self.settings_repository:
            return

        try:
            settings = await self.settings_repository.get_by_user_id(notification.user_id)
            if not settings or not settings.notification_email:
                logger.debug(f"Email notifications disabled for user {notification.user_id}")
                return

            # Get user email
            user_email = None
            if self.user_repository:
                user = await self.user_repository.get_by_id(notification.user_id)
                if user:
                    user_email = user.email

            if not user_email:
                logger.warning(f"User email not found for user {notification.user_id}")
                return

            # Send email
            subject = f"[FocusMate] {notification.title}"
            body = f"{notification.message}\n\n"
            if notification.data and "routing" in notification.data:
                routing = notification.data.get("routing", {})
                if "path" in routing:
                    # In production, this would be the actual app URL
                    body += f"자세히 보기: https://focusmate.app{routing['path']}\n"

            success = await self.email_service._send_email(
                user_email, subject, body
            )
            if success:
                logger.info(f"Email notification sent to {user_email} for notification {notification.notification_id}")
            else:
                logger.warning(f"Failed to send email notification to {user_email}")

        except Exception as e:
            logger.error(f"Error sending email notification: {e}")

    async def _send_push_notification(self, notification: Notification) -> None:
        """Send push notification via WebSocket if user has push notifications enabled.

        Args:
            notification: Notification to send
        """
        if not self.settings_repository:
            # If settings repository is not available, send push notification
            await self._send_websocket_notification(notification)
            return

        try:
            settings = await self.settings_repository.get_by_user_id(notification.user_id)
            if not settings or not settings.notification_push:
                logger.debug(f"Push notifications disabled for user {notification.user_id}")
                return

            await self._send_websocket_notification(notification)

        except Exception as e:
            logger.error(f"Error checking push notification settings: {e}")
            # On error, send notification to avoid blocking
            await self._send_websocket_notification(notification)

    async def _send_websocket_notification(self, notification: Notification) -> None:
        """Send notification via WebSocket.

        Args:
            notification: Notification to send
        """
        try:
            await notification_ws_manager.send_notification(
                {
                    "type": "notification",
                    "data": {
                        "notification_id": notification.notification_id,
                        "type": notification.type,
                        "title": notification.title,
                        "message": notification.message,
                        "data": notification.data,
                        "created_at": notification.created_at.isoformat(),
                    },
                },
                notification.user_id,
            )
            logger.debug(f"WebSocket notification sent to user {notification.user_id}")
        except Exception as e:
            logger.error(f"Error sending WebSocket notification: {e}")

    async def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> list[NotificationResponse]:
        """Get notifications for a user.

        Args:
            user_id: User identifier
            unread_only: Whether to return only unread notifications
            limit: Maximum number of notifications to return
            offset: Number of notifications to skip

        Returns:
            List of notifications
        """
        notifications = await self.repository.get_by_user(
            user_id, unread_only, limit, offset
        )
        return [NotificationResponse.model_validate(n) for n in notifications]

    async def mark_as_read(self, notification_ids: list[str]) -> int:
        """Mark notifications as read.

        Args:
            notification_ids: List of notification IDs to mark as read

        Returns:
            Number of notifications marked as read
        """
        count = 0
        for notification_id in notification_ids:
            notification = await self.repository.get_by_id(notification_id)
            if notification and not notification.is_read:
                notification.is_read = True
                notification.read_at = datetime.now(UTC)
                await self.repository.update(notification)
                count += 1
        return count

    async def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications for a user as read.

        Args:
            user_id: User identifier

        Returns:
            Number of notifications marked as read
        """
        return await self.repository.mark_all_as_read(user_id)

    async def delete_notification(self, notification_id: str) -> bool:
        """Delete a notification.

        Args:
            notification_id: Notification identifier

        Returns:
            True if deleted successfully
        """
        notification = await self.repository.get_by_id(notification_id)
        if not notification:
            return False

        await self.repository.delete(notification)
        return True

    async def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications for a user.

        Args:
            user_id: User identifier

        Returns:
            Count of unread notifications
        """
        return await self.repository.get_unread_count(user_id)
