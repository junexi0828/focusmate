"""Notification helper functions for creating notifications with routing metadata."""


from app.domain.notification.schemas import NotificationCreate


class NotificationHelper:
    """Helper class for creating notifications with proper routing metadata."""

    @staticmethod
    def create_friend_request_notification(
        user_id: str,
        sender_name: str,
        request_id: str,
    ) -> NotificationCreate:
        """Create a friend request notification.

        Args:
            user_id: User ID to receive notification
            sender_name: Name of user who sent friend request
            request_id: Friend request ID

        Returns:
            NotificationCreate with routing metadata
        """
        return NotificationCreate(
            user_id=user_id,
            type="friend_request",
            title="New Friend Request",
            message=f"{sender_name} sent you a friend request",
            data={
                "request_id": request_id,
                "sender_name": sender_name,
                "routing": {
                    "type": "friend_requests",
                    "path": "/friends/requests",
                    "params": {"request_id": request_id},
                },
            },
        )

    @staticmethod
    def create_friend_request_accepted_notification(
        user_id: str,
        accepter_name: str,
        friend_id: str,
    ) -> NotificationCreate:
        """Create a notification when friend request is accepted.

        Args:
            user_id: User ID to receive notification
            accepter_name: Name of user who accepted request
            friend_id: Friend user ID

        Returns:
            NotificationCreate with routing metadata
        """
        return NotificationCreate(
            user_id=user_id,
            type="friend_request_accepted",
            title="Friend Request Accepted",
            message=f"{accepter_name} accepted your friend request",
            data={
                "friend_id": friend_id,
                "accepter_name": accepter_name,
                "routing": {
                    "type": "friends",
                    "path": "/friends",
                    "params": {"friend_id": friend_id},
                },
            },
        )

    @staticmethod
    def create_team_invitation_notification(
        user_id: str,
        team_name: str,
        inviter_name: str,
        invitation_id: str,
        team_id: str,
    ) -> NotificationCreate:
        """Create a team invitation notification.

        Args:
            user_id: User ID to receive notification
            team_name: Name of the team
            inviter_name: Name of user who sent invitation
            invitation_id: Team invitation ID
            team_id: Team ID

        Returns:
            NotificationCreate with routing metadata
        """
        return NotificationCreate(
            user_id=user_id,
            type="team_invitation",
            title="Team Invitation",
            message=f"{inviter_name} invited you to join {team_name}",
            data={
                "invitation_id": invitation_id,
                "team_id": team_id,
                "team_name": team_name,
                "inviter_name": inviter_name,
                "routing": {
                    "type": "team_invitation",
                    "path": f"/ranking/invitations/{invitation_id}",
                    "params": {
                        "invitation_id": invitation_id,
                        "team_id": team_id,
                    },
                },
            },
        )

    @staticmethod
    def create_new_message_notification(
        user_id: str,
        sender_name: str,
        message_preview: str,
        conversation_id: str,
    ) -> NotificationCreate:
        """Create a new message notification.

        Args:
            user_id: User ID to receive notification
            sender_name: Name of message sender
            message_preview: Preview of message content
            conversation_id: Conversation ID

        Returns:
            NotificationCreate with routing metadata
        """
        return NotificationCreate(
            user_id=user_id,
            type="new_message",
            title=f"New message from {sender_name}",
            message=message_preview[:100],
            data={
                "conversation_id": conversation_id,
                "sender_name": sender_name,
                "routing": {
                    "type": "conversation",
                    "path": f"/messages/conversations/{conversation_id}",
                    "params": {"conversation_id": conversation_id},
                },
            },
        )

    @staticmethod
    def create_post_comment_notification(
        user_id: str,
        commenter_name: str,
        post_id: str,
        post_title: str,
        comment_preview: str,
    ) -> NotificationCreate:
        """Create a notification when someone comments on user's post.

        Args:
            user_id: User ID to receive notification
            commenter_name: Name of user who commented
            post_id: Post ID
            post_title: Title of the post
            comment_preview: Preview of comment content

        Returns:
            NotificationCreate with routing metadata
        """
        return NotificationCreate(
            user_id=user_id,
            type="post_comment",
            title="New Comment",
            message=f"{commenter_name} commented on your post: {comment_preview[:50]}",
            data={
                "post_id": post_id,
                "post_title": post_title,
                "commenter_name": commenter_name,
                "routing": {
                    "type": "post",
                    "path": f"/community/posts/{post_id}",
                    "params": {"post_id": post_id},
                },
            },
        )

    @staticmethod
    def create_post_like_notification(
        user_id: str,
        liker_name: str,
        post_id: str,
        post_title: str,
    ) -> NotificationCreate:
        """Create a notification when someone likes user's post.

        Args:
            user_id: User ID to receive notification
            liker_name: Name of user who liked
            post_id: Post ID
            post_title: Title of the post

        Returns:
            NotificationCreate with routing metadata
        """
        return NotificationCreate(
            user_id=user_id,
            type="post_like",
            title="Post Liked",
            message=f"{liker_name} liked your post: {post_title}",
            data={
                "post_id": post_id,
                "post_title": post_title,
                "liker_name": liker_name,
                "routing": {
                    "type": "post",
                    "path": f"/community/posts/{post_id}",
                    "params": {"post_id": post_id},
                },
            },
        )

    @staticmethod
    def create_achievement_notification(
        user_id: str,
        achievement_name: str,
        achievement_description: str,
        achievement_id: str,
    ) -> NotificationCreate:
        """Create an achievement unlock notification.

        Args:
            user_id: User ID to receive notification
            achievement_name: Name of the achievement
            achievement_description: Description of the achievement
            achievement_id: Achievement ID

        Returns:
            NotificationCreate with routing metadata
        """
        return NotificationCreate(
            user_id=user_id,
            type="achievement",
            title=f"Achievement Unlocked: {achievement_name}",
            message=achievement_description,
            data={
                "achievement_id": achievement_id,
                "achievement_name": achievement_name,
                "routing": {
                    "type": "achievements",
                    "path": "/achievements",
                    "params": {"achievement_id": achievement_id},
                },
            },
        )

    @staticmethod
    def create_system_notification(
        user_id: str,
        title: str,
        message: str,
        routing_path: str | None = None,
    ) -> NotificationCreate:
        """Create a system notification.

        Args:
            user_id: User ID to receive notification
            title: Notification title
            message: Notification message
            routing_path: Optional path to navigate to

        Returns:
            NotificationCreate with routing metadata
        """
        data = {}
        if routing_path:
            data["routing"] = {
                "type": "custom",
                "path": routing_path,
            }

        return NotificationCreate(
            user_id=user_id,
            type="system",
            title=title,
            message=message,
            data=data if data else None,
        )
