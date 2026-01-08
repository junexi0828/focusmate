"""RefreshToken ORM Model."""

from datetime import datetime
from sqlalchemy import DateTime, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class RefreshToken(Base):
    """Refresh token model for session management.

    Attributes:
        id: Unique token record identifier (UUID)
        user_id: User who owns this token
        token_id: JWT jti claim (unique identifier)
        family_id: Token family for rotation tracking
        expires_at: Rolling expiry (7 days, extendable)
        absolute_expires_at: Hard limit (30 days, never extended)
        last_rotated_at: Last rotation timestamp
        device_info: Device/browser information
        ip_address: IP address at token creation
        created_at: Token creation timestamp
    """

    __tablename__ = "refresh_tokens"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        server_default="gen_random_uuid()",
        comment="Unique token record identifier",
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who owns this token",
    )

    token_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        unique=True,
        index=True,
        comment="JWT jti claim",
    )

    family_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
        comment="Token family for rotation tracking",
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Rolling expiry (extendable)",
    )

    absolute_expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Hard limit (never extended)",
    )

    last_rotated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="NOW()",
        comment="Last rotation timestamp",
    )

    device_info: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Device/browser information",
    )

    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
        comment="IP address at creation",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="NOW()",
        comment="Token creation timestamp",
    )

    def __repr__(self) -> str:
        """String representation of RefreshToken."""
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, token_id={self.token_id})>"
