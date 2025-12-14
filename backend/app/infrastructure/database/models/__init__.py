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
from app.infrastructure.database.models.message import Conversation, Message
from app.infrastructure.database.models.participant import Participant
from app.infrastructure.database.models.room import Room
from app.infrastructure.database.models.room_reservation import RoomReservation
from app.infrastructure.database.models.notification import Notification
from app.infrastructure.database.models.session_history import SessionHistory
from app.infrastructure.database.models.timer import Timer
from app.infrastructure.database.models.user import User
from app.infrastructure.database.models.verification import UserVerification
from app.infrastructure.database.models.matching import (
    MatchingPool,
    MatchingProposal,
    MatchingChatRoom,
    MatchingChatMember,
    MatchingMessage,
)

__all__ = [
    "Room",
    "Timer",
    "Participant",
    "User",
    "SessionHistory",
    "Achievement",
    "UserAchievement",
    "Post",
    "Comment",
    "PostLike",
    "CommentLike",
    "PostRead",
    "Conversation",
    "Message",
    "RoomReservation",
    "ChatRoom",
    "ChatMember",
    "ChatMessage",
    "Notification",
    "UserVerification",
    "MatchingPool",
    "MatchingProposal",
    "MatchingChatRoom",
    "MatchingChatMember",
    "MatchingMessage",
]
