"""Service for lightweight room chat."""

from datetime import UTC, datetime
from uuid import uuid4

from app.domain.room_chat.schemas import RoomChatMessage


class RoomChatService:
    """Builds and validates room chat messages."""

    def __init__(self, max_length: int = 300) -> None:
        self.max_length = max_length

    def build_message(
        self,
        *,
        room_id: str,
        sender_id: str,
        sender_name: str,
        content: str,
    ) -> RoomChatMessage:
        """Validate content and build a message payload."""
        trimmed = content.strip()
        if not trimmed:
            raise ValueError("Message content cannot be empty")
        if len(trimmed) > self.max_length:
            raise ValueError("Message content exceeds max length")

        return RoomChatMessage(
            id=str(uuid4()),
            room_id=room_id,
            sender_id=sender_id,
            sender_name=sender_name,
            content=trimmed,
            created_at=datetime.now(UTC),
        )

