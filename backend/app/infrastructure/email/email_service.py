"""Email notification service using aiosmtplib for asynchronous operations."""

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from app.core.config import settings


class EmailService:
    """Service for sending email notifications asynchronously."""

    def __init__(self):
        """Initialize email service with settings from config."""
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.from_name = settings.SMTP_FROM_NAME
        self.from_email = settings.SMTP_FROM_EMAIL
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.use_tls = settings.SMTP_USE_TLS
        self.is_enabled = settings.SMTP_ENABLED

    async def send_verification_submitted_email(
        self,
        team_name: str,
        leader_email: str,
    ) -> bool:
        """Send email notification when verification is submitted."""
        subject = f"[FocusMate] {team_name} 인증 요청이 제출되었습니다"
        body = f"""
안녕하세요,

{team_name}의 학교 인증 요청이 성공적으로 제출되었습니다.

관리자 검토 후 결과를 이메일로 안내드리겠습니다.
검토는 영업일 기준 1-3일 소요됩니다.

감사합니다.
FocusMate 팀
"""
        return await self._send_email(leader_email, subject, body)

    async def send_verification_submitted_to_admin_email(
        self,
        admin_email: str,
        user_email: str,
        username: str,
        school_name: str,
        department: str,
        grade: int,
    ) -> bool:
        """Send email notification to admin when verification is submitted."""
        subject = f"[FocusMate] 새로운 인증 신청: {school_name} - {username}"
        body = f"""
새로운 인증 신청이 제출되었습니다.

사용자 정보:
- 이메일: {user_email}
- 사용자명: {username}
- 학교: {school_name}
- 학과: {department}
- 학년: {grade}

관리자 대시보드에서 검토해주세요.

감사합니다.
FocusMate 시스템
"""
        return await self._send_email(admin_email, subject, body)

    async def send_verification_approved_email(
        self,
        team_name: str = "",
        leader_email: str = "",
        admin_note: str | None = None,
    ) -> bool:
        """Send email notification when verification is approved."""
        subject = f"[FocusMate] {team_name} 인증이 승인되었습니다 ✅"
        body = f"""안녕하세요,

축하합니다! {team_name}의 학교 인증이 승인되었습니다.

이제 인증된 팀으로 랭킹전에 참여하실 수 있습니다.
"""
        if admin_note:
            body += f"\n관리자 메모: {admin_note}\n"

        body += """감사합니다.
FocusMate 팀
"""
        return await self._send_email(leader_email, subject, body)

    async def send_verification_rejected_email(
        self,
        team_name: str,
        leader_email: str,
        admin_note: str | None = None,
    ) -> bool:
        """Send email notification when verification is rejected."""
        subject = f"[FocusMate] {team_name} 인증이 반려되었습니다"
        body = f"""안녕하세요,

{team_name}의 학교 인증 요청이 반려되었습니다.
"""
        if admin_note:
            body += f"\n반려 사유: {admin_note}\n\n"

        body += """서류를 보완하여 다시 신청하실 수 있습니다.

감사합니다.
FocusMate 팀
"""
        return await self._send_email(leader_email, subject, body)

    async def send_team_invitation_email(
        self,
        team_name: str,
        invitee_email: str,
        invite_link: str,
    ) -> bool:
        """Send team invitation email."""
        subject = f"[FocusMate] {team_name}에서 초대했습니다"
        body = f"""
안녕하세요,

{team_name}에서 회원님을 팀원으로 초대했습니다.

아래 링크를 클릭하여 초대를 수락하세요:
{invite_link}

초대는 7일 후 만료됩니다.

감사합니다.
FocusMate 팀
"""
        return await self._send_email(invitee_email, subject, body)

    async def _send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
    ) -> bool:
        """Send email using aiosmtplib.

        Returns:
            True if email was successfully sent, False otherwise.
            Note: Returns False if SMTP is disabled or misconfigured.
        """
        import logging

        logger = logging.getLogger(__name__)

        # Log SMTP configuration status
        logger.info(f"[EMAIL] 📧 Email send attempt - To: {to_email}, Subject: {subject}")
        logger.info(f"[EMAIL] SMTP Status - Enabled: {self.is_enabled}, Host: {self.smtp_host}, Port: {self.smtp_port}")
        logger.info(f"[EMAIL] SMTP Auth - User: {self.smtp_user[:10] + '...' if self.smtp_user else 'NOT SET'}, Password: {'SET' if self.smtp_password else 'NOT SET'}")

        if not self.is_enabled:
            logger.warning(f"[EMAIL DISABLED] 📧 SMTP is disabled. Email not sent to {to_email}, Subject: {subject}")
            return False

        if not (self.smtp_user and self.smtp_password):
            logger.error(
                f"[EMAIL MISCONFIGURED] ❌ SMTP_USER or SMTP_PASSWORD not set. "
                f"SMTP_USER={bool(self.smtp_user)}, SMTP_PASSWORD={bool(self.smtp_password)}. "
                f"To: {to_email}, Subject: {subject}"
            )
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            # Gmail requires From to match authenticated user or use authenticated user's email
            # Use SMTP_USER as From if it's a Gmail account, otherwise use configured from_email
            if "@gmail.com" in self.smtp_user.lower():
                from_email = (
                    self.smtp_user
                )  # Gmail requires From to match authenticated user
            else:
                from_email = self.from_email
            msg["From"] = f"{self.from_name} <{from_email}>"
            msg["To"] = to_email
            msg.attach(MIMEText(body, "plain", "utf-8"))

            logger.info(
                f"[EMAIL] 📤 Attempting to send email to {to_email} via {self.smtp_host}:{self.smtp_port}"
            )
            logger.info(
                f"[EMAIL] From: {from_email}, To: {to_email}, Subject: {subject}"
            )
            logger.debug(
                f"[EMAIL] SMTP Config: host={self.smtp_host}, port={self.smtp_port}, user={self.smtp_user[:10]}..., tls={self.use_tls}"
            )

            await aiosmtplib.send(
                msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=self.use_tls,
                timeout=30.0,  # Increased timeout to 30 seconds
            )
            logger.info(f"[EMAIL] ✅ Successfully sent to {to_email}: {subject}")
            return True
        except aiosmtplib.SMTPAuthenticationError as e:
            logger.error(
                f"[EMAIL ERROR] 🔐 SMTP Authentication failed sending to {to_email}: {e}",
                exc_info=True,
            )
            logger.error("[EMAIL ERROR] Check SMTP_USER and SMTP_PASSWORD are correct")
            return False
        except aiosmtplib.SMTPException as e:
            logger.error(
                f"[EMAIL ERROR] 📧 SMTP Exception sending to {to_email}: {type(e).__name__}: {e}",
                exc_info=True,
            )
            return False
        except TimeoutError as e:
            logger.error(f"[EMAIL ERROR] ⏱️ Timeout sending to {to_email}: {e}")
            return False
        except Exception as e:
            logger.error(
                f"[EMAIL ERROR] ❌ Failed to send to {to_email}: {type(e).__name__}: {e}",
                exc_info=True,
            )
            return False


# Singleton instance for dependency injection
email_service = EmailService()
