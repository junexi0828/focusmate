"""User ORM Model."""

from typing import Optional

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """User model for authentication and profile.

    Attributes:
        id: Unique user identifier (UUID)
        email: User email (unique)
        username: Display name
        hashed_password: Bcrypt hashed password
        is_active: Account active status
        is_verified: Email verification status
        bio: User bio/description (optional)
        school: User school/university (optional)
        profile_image: Profile image URL (optional)
        total_focus_time: Total focus time in minutes
        total_sessions: Total completed sessions
    """

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        comment="Unique user identifier (UUID)",
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="User email",
    )

    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Display name",
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Bcrypt hashed password",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Account active status",
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Email verification status",
    )

    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Admin user status",
    )

    bio: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="User bio",
    )

    school: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="User school/university",
    )

    profile_image: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Profile image URL",
    )

    total_focus_time: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        comment="Total focus time in minutes",
    )

    total_sessions: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        comment="Total completed sessions",
    )

    # Relationships
    verification: Mapped[Optional["UserVerification"]] = relationship(
        "UserVerification", back_populates="user", uselist=False
    )

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"
