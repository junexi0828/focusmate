"""Database ORM Models.

This package contains all SQLAlchemy ORM models.
Models are independent and avoid direct relationships to maintain modularity.
"""

from app.infrastructure.database.models.achievement import Achievement, UserAchievement
from app.infrastructure.database.models.chat import ChatMember, ChatMessage, ChatRoom
from app.infrastructure.database.models.community import (
    Comment,
    CommentLike,
    Post,
    PostLike,
    PostRead,
)
from app.infrastructure.database.models.friend import Friend, FriendRequest
from app.infrastructure.database.models.matching import (
    MatchingChatMember,
    MatchingChatRoom,
    MatchingMessage,
    MatchingPool,
    MatchingProposal,
)
from app.infrastructure.database.models.message import Conversation, Message
from app.infrastructure.database.models.notification import Notification
from app.infrastructure.database.models.participant import Participant
from app.infrastructure.database.models.ranking import (
    RankingLeaderboard,
    RankingTeam,
    RankingTeamInvitation,
    RankingTeamMember,
    RankingVerificationRequest,
)
from app.infrastructure.database.models.report import Report
from app.infrastructure.database.models.room import Room
from app.infrastructure.database.models.room_reservation import RoomReservation
from app.infrastructure.database.models.session_history import SessionHistory
from app.infrastructure.database.models.timer import Timer
from app.infrastructure.database.models.user import User
from app.infrastructure.database.models.user_settings import UserSettings
from app.infrastructure.database.models.user_stats import (
    ManualSession,
    UserGoal,
)
from app.infrastructure.database.models.verification import UserVerification


__all__ = [
    "Achievement",
    "ChatMember",
    "ChatMessage",
    "ChatRoom",
    "Comment",
    "CommentLike",
    "Conversation",
    "Friend",
    "FriendRequest",
    "ManualSession",
    "MatchingChatMember",
    "MatchingChatRoom",
    "MatchingMessage",
    "MatchingPool",
    "MatchingProposal",
    "Message",
    "Notification",
    "Participant",
    "Post",
    "PostLike",
    "PostRead",
    "RankingLeaderboard",
    "RankingMember",
    "RankingMiniGame",
    "RankingSession",
    "RankingTeam",
    "Report",
    "Room",
    "RoomReservation",
    "SessionHistory",
    "Timer",
    "User",
    "UserAchievement",
    "UserGoal",
    "UserSettings",
    "UserVerification",
]
