"""Notification helper functions for creating notifications with routing metadata."""


from app.domain.notification.schemas import NotificationCreate, NotificationPriority


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
            group_key=f"friend_req:{request_id}",
            routing={
                "type": "friend_requests",
                "path": "/friends/requests",
                "params": {"request_id": request_id},
            },
            data={
                "request_id": request_id,
                "sender_name": sender_name,
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
            group_key=f"friend:{friend_id}",
            routing={
                "type": "friends",
                "path": "/friends",
                "params": {"friend_id": friend_id},
            },
            data={
                "friend_id": friend_id,
                "accepter_name": accepter_name,
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
            group_key=f"team_invite:{invitation_id}",
            routing={
                "type": "team_invitation",
                "path": f"/ranking/invitations/{invitation_id}",
                "params": {
                    "invitation_id": invitation_id,
                    "team_id": team_id,
                },
            },
            data={
                "invitation_id": invitation_id,
                "team_id": team_id,
                "team_name": team_name,
                "inviter_name": inviter_name,
            },
        )

    @staticmethod
    def create_team_invitation_response_notification(
        user_id: str,
        team_name: str,
        responder_name: str,
        accepted: bool,
    ) -> NotificationCreate:
        """Create a notification when a team invitation is accepted or rejected.

        Args:
            user_id: User ID to receive notification (usually team leader)
            team_name: Name of the team
            responder_name: Name of user who responded
            accepted: Whether invitation was accepted or rejected

        Returns:
            NotificationCreate with routing metadata
        """
        action = "accepted" if accepted else "rejected"
        title = f"Invitation {action.capitalize()}"
        message = f"{responder_name} {action} your invitation to join {team_name}",

        return NotificationCreate(
            user_id=user_id,
            type=f"team_invitation_{action}",
            title=title,
            message=message,
            routing={
                "type": "team",
                "path": "/teams",
            },
            data={
                "team_name": team_name,
                "responder_name": responder_name,
                "accepted": accepted,
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
            priority=NotificationPriority.HIGH,
            title=f"New message from {sender_name}",
            message=message_preview[:100],
            group_key=f"message:{conversation_id}",
            routing={
                "type": "conversation",
                "path": f"/messages/conversations/{conversation_id}",
                "params": {"conversation_id": conversation_id},
            },
            data={
                "conversation_id": conversation_id,
                "sender_name": sender_name,
            },
        )

    @staticmethod
    def create_comment_like_notification(
        user_id: str,
        liker_name: str,
        post_id: str,
        post_title: str,
        comment_content: str,
    ) -> NotificationCreate:
        """Create a notification when someone likes user's comment.

        Args:
            user_id: User ID to receive notification
            liker_name: Name of user who liked
            post_id: Post ID
            post_title: Title of the post
            comment_content: Content of the comment

        Returns:
            NotificationCreate with routing metadata
        """
        return NotificationCreate(
            user_id=user_id,
            type="comment_like",
            title="Comment Liked",
            message=f"{liker_name} liked your comment: {comment_content[:50]}",
            group_key=f"post:{post_id}", # Group by post so multiple likes on same post's comments don't spam? or group by comment?
            # Let's group by post for now to capture activity on the same thread
            routing={
                "type": "post",
                "path": f"/community/posts/{post_id}",
                "params": {"post_id": post_id},
            },
            data={
                "post_id": post_id,
                "post_title": post_title,
                "liker_name": liker_name,
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
            group_key=f"post_comment:{post_id}",
            routing={
                "type": "post",
                "path": f"/community/posts/{post_id}",
                "params": {"post_id": post_id},
            },
            data={
                "post_id": post_id,
                "post_title": post_title,
                "commenter_name": commenter_name,
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
            group_key=f"post_like:{post_id}",
            routing={
                "type": "post",
                "path": f"/community/posts/{post_id}",
                "params": {"post_id": post_id},
            },
            data={
                "post_id": post_id,
                "post_title": post_title,
                "liker_name": liker_name,
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
            priority=NotificationPriority.MEDIUM,
            title=f"Achievement Unlocked: {achievement_name}",
            message=achievement_description,
            group_key=f"achievement:{achievement_id}",
            routing={
                "type": "achievements",
                "path": "/achievements",
                "params": {"achievement_id": achievement_id},
            },
            data={
                "achievement_id": achievement_id,
                "achievement_name": achievement_name,
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
        routing = None
        if routing_path:
            routing = {
                "type": "custom",
                "path": routing_path,
            }

        return NotificationCreate(
            user_id=user_id,
            type="system",
            priority=NotificationPriority.HIGH, # System notifications are high priority
            title=title,
            message=message,
            routing=routing,
            data={},
        )

    @staticmethod
    def create_match_proposal_notification(
        user_id: str,
        proposal_id: str,
        partner_department: str,
    ) -> NotificationCreate:
        """Create a notification for a new matching proposal.

        Args:
            user_id: User ID to receive notification
            proposal_id: Proposal ID
            partner_department: Department of the potential match

        Returns:
            NotificationCreate with routing metadata
        """
        return NotificationCreate(
            user_id=user_id,
            type="match_proposal",
            title="New Match Proposal",
            message=f"A new match proposal from {partner_department} is waiting!",
            group_key=f"proposal:{proposal_id}",
            routing={
                "type": "proposal",
                "path": f"/matching/proposals/{proposal_id}",
                "params": {"proposal_id": proposal_id},
            },
            data={
                "proposal_id": proposal_id,
                "partner_department": partner_department,
            },
        )

    @staticmethod
    def create_match_success_notification(
        user_id: str,
        proposal_id: str,
        chat_room_id: str,
        partner_department: str,
    ) -> NotificationCreate:
        """Create a notification when a match is successfully connected.

        Args:
            user_id: User ID to receive notification
            proposal_id: Proposal ID
            chat_room_id: Created chat room ID
            partner_department: Department of the matched group

        Returns:
            NotificationCreate with routing metadata
        """
        return NotificationCreate(
            user_id=user_id,
            type="match_success",
            title="It's a Match!",
            message=f"You are matched with {partner_department}! Chat room created.",
            group_key=f"match:{proposal_id}",
            routing={
                "type": "chat_room",
                "path": f"/messages/rooms/{chat_room_id}",
                "params": {"room_id": chat_room_id},
            },
            data={
                "proposal_id": proposal_id,
                "chat_room_id": chat_room_id,
                "partner_department": partner_department,
            },
        )
