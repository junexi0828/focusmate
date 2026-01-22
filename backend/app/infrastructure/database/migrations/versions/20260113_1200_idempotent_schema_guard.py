"""Harden schema creation for presence/settings/invitations (idempotent)

Revision ID: c5e1d5af0c8a
Revises: 31f2a346119d
Create Date: 2026-01-13 12:00:00

Purpose:
- Make earlier schema additions (user profile/settings, presence, room invitations) resilient
  to partially-applied/hand-edited states on NAS by using IF NOT EXISTS guards.
- This avoids migration crashes on environments where some columns/indexes already exist.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "c5e1d5af0c8a"
down_revision: Union[str, None] = "31f2a346119d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- user profile fields -------------------------------------------------
    op.execute('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS school VARCHAR(100)')
    op.execute("COMMENT ON COLUMN \"user\".school IS 'User school/university'")

    op.execute('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS profile_image VARCHAR(500)')
    op.execute("COMMENT ON COLUMN \"user\".profile_image IS 'Profile image URL'")

    # --- user_settings table (idempotent create) -----------------------------
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT FROM pg_tables
                WHERE schemaname = 'public' AND tablename = 'user_settings'
            ) THEN
                CREATE TABLE user_settings (
                    id VARCHAR(36) NOT NULL,
                    user_id VARCHAR(36) NOT NULL,
                    theme VARCHAR(20) DEFAULT 'system' NOT NULL,
                    language VARCHAR(10) DEFAULT 'ko' NOT NULL,
                    notification_email BOOLEAN DEFAULT true NOT NULL,
                    notification_push BOOLEAN DEFAULT true NOT NULL,
                    notification_session BOOLEAN DEFAULT true NOT NULL,
                    notification_achievement BOOLEAN DEFAULT true NOT NULL,
                    notification_message BOOLEAN DEFAULT true NOT NULL,
                    do_not_disturb_start VARCHAR(5),
                    do_not_disturb_end VARCHAR(5),
                    session_reminder BOOLEAN DEFAULT true NOT NULL,
                    custom_settings JSON,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
                    CONSTRAINT pk_user_settings PRIMARY KEY (id),
                    CONSTRAINT fk_user_settings_user_id_user FOREIGN KEY(user_id)
                        REFERENCES "user" (id) ON DELETE CASCADE,
                    CONSTRAINT uq_user_settings_user_id UNIQUE (user_id)
                );
                CREATE INDEX ix_user_settings_user_id ON user_settings (user_id);
            END IF;
        END
        $$;
        """
    )

    # --- user_presence table (idempotent create) ----------------------------
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT FROM pg_tables
                WHERE schemaname = 'public' AND tablename = 'user_presence'
            ) THEN
                CREATE TABLE user_presence (
                    id VARCHAR(36) NOT NULL,
                    is_online BOOLEAN DEFAULT false NOT NULL,
                    last_seen_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
                    connection_count INTEGER DEFAULT 0 NOT NULL,
                    status_message VARCHAR(200),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
                    CONSTRAINT pk_user_presence PRIMARY KEY (id),
                    CONSTRAINT fk_user_presence_id_user FOREIGN KEY(id)
                        REFERENCES "user" (id) ON DELETE CASCADE
                );
                CREATE INDEX ix_user_presence_is_online ON user_presence (is_online);
            END IF;
        END
        $$;
        """
    )

    # --- chat_rooms invitation fields (idempotent) --------------------------
    op.execute(
        "ALTER TABLE chat_rooms ADD COLUMN IF NOT EXISTS invitation_code VARCHAR(8)"
    )
    op.execute(
        "COMMENT ON COLUMN chat_rooms.invitation_code IS 'Room invitation code'"
    )

    op.execute(
        "ALTER TABLE chat_rooms ADD COLUMN IF NOT EXISTS invitation_expires_at TIMESTAMP WITH TIME ZONE"
    )
    op.execute(
        "COMMENT ON COLUMN chat_rooms.invitation_expires_at IS 'Invitation code expiration timestamp'"
    )

    op.execute(
        "ALTER TABLE chat_rooms ADD COLUMN IF NOT EXISTS invitation_max_uses INTEGER"
    )
    op.execute(
        "COMMENT ON COLUMN chat_rooms.invitation_max_uses IS 'Maximum number of invitation uses'"
    )

    op.execute(
        "ALTER TABLE chat_rooms ADD COLUMN IF NOT EXISTS invitation_use_count INTEGER DEFAULT 0 NOT NULL"
    )
    op.execute(
        "COMMENT ON COLUMN chat_rooms.invitation_use_count IS 'Current invitation use count'"
    )

    # Recreate invitation indexes idempotently (drop if exists to avoid duplicates)
    op.execute("DROP INDEX IF EXISTS ix_chat_rooms_invitation_code")
    op.create_index(
        "ix_chat_rooms_invitation_code",
        "chat_rooms",
        ["invitation_code"],
        unique=True,
        postgresql_where=sa.text("invitation_code IS NOT NULL"),
    )

    op.execute("DROP INDEX IF EXISTS ix_chat_rooms_invitation_expires_at")
    op.create_index(
        op.f("ix_chat_rooms_invitation_expires_at"),
        "chat_rooms",
        ["invitation_expires_at"],
        unique=False,
    )


def downgrade() -> None:
    # Drop indexes first (if they exist)
    op.execute("DROP INDEX IF EXISTS ix_chat_rooms_invitation_expires_at")
    op.execute("DROP INDEX IF EXISTS ix_chat_rooms_invitation_code")

    # Remove chat_rooms columns
    op.execute("ALTER TABLE chat_rooms DROP COLUMN IF EXISTS invitation_use_count")
    op.execute("ALTER TABLE chat_rooms DROP COLUMN IF EXISTS invitation_max_uses")
    op.execute("ALTER TABLE chat_rooms DROP COLUMN IF EXISTS invitation_expires_at")
    op.execute("ALTER TABLE chat_rooms DROP COLUMN IF EXISTS invitation_code")

    # Drop user_presence table
    op.execute("DROP INDEX IF EXISTS ix_user_presence_is_online")
    op.execute("DROP TABLE IF EXISTS user_presence")

    # Drop user_settings table
    op.execute("DROP INDEX IF EXISTS ix_user_settings_user_id")
    op.execute("DROP TABLE IF EXISTS user_settings")

    # Remove user profile columns
    op.execute('ALTER TABLE "user" DROP COLUMN IF EXISTS profile_image')
    op.execute('ALTER TABLE "user" DROP COLUMN IF EXISTS school')
