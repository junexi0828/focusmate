#!/usr/bin/env python3
"""Test SMTP connection and email sending."""

import asyncio
import sys
from pathlib import Path


# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.infrastructure.email.email_service import EmailService


async def test_smtp_connection():
    """Test SMTP connection and send a test email."""
    print("=" * 60)
    print("SMTP Connection Test")
    print("=" * 60)
    print()

    # Check configuration
    print("📋 SMTP Configuration:")
    print(f"   Enabled: {settings.SMTP_ENABLED}")
    print(f"   Host: {settings.SMTP_HOST}")
    print(f"   Port: {settings.SMTP_PORT}")
    print(f"   Use TLS: {settings.SMTP_USE_TLS}")
    print(f"   From Email: {settings.SMTP_FROM_EMAIL}")
    print(f"   From Name: {settings.SMTP_FROM_NAME}")
    print(f"   User: {settings.SMTP_USER}")
    print(
        f"   Password: {'*' * len(settings.SMTP_PASSWORD) if settings.SMTP_PASSWORD else 'NOT SET'}"
    )
    print()

    if not settings.SMTP_ENABLED:
        print("⚠️  SMTP is disabled. Set SMTP_ENABLED=true to enable.")
        return False

    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print("❌ SMTP_USER or SMTP_PASSWORD is not set.")
        return False

    # Create email service
    email_service = EmailService()

    # Test email
    test_email = settings.SMTP_USER  # Send to the same email as SMTP_USER
    test_subject = "[FocusMate] SMTP 테스트"
    test_body = """
안녕하세요,

이것은 SMTP 연결 테스트 이메일입니다.

SMTP 서비스가 정상적으로 작동하고 있습니다.

감사합니다.
FocusMate 팀
"""

    print(f"📧 Sending test email to: {test_email}")
    print(f"📝 Subject: {test_subject}")
    print()

    try:
        success = await email_service._send_email(test_email, test_subject, test_body)

        if success:
            print("✅ Email sent successfully!")
            print(f"   Please check your inbox: {test_email}")
            return True
        print("❌ Failed to send email. Check the logs above for details.")
        return False

    except Exception as e:
        print(f"❌ Error sending email: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_smtp_connection())
    sys.exit(0 if result else 1)
