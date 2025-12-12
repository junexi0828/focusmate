"""Email notification service for ranking system."""

from typing import Optional
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailService:
    """Service for sending email notifications."""

    def __init__(
        self,
        smtp_host: str = "localhost",
        smtp_port: int = 587,
        from_name: str = "FocusMate",
        from_email: str = "noreply@focusmate.com",
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
    ):
        """Initialize email service."""
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.from_name = from_name
        self.from_email = from_email
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password

    async def send_verification_submitted_email(
        self, team_name: str, leader_email: str
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

    async def send_verification_approved_email(
        self, team_name: str, leader_email: str, admin_note: Optional[str] = None
    ) -> bool:
        """Send email notification when verification is approved."""
        subject = f"[FocusMate] {team_name} 인증이 승인되었습니다 ✅"
        body = f"""
안녕하세요,

축하합니다! {team_name}의 학교 인증이 승인되었습니다.

이제 인증된 팀으로 랭킹전에 참여하실 수 있습니다.

"""
        if admin_note:
            body += f"\n관리자 메모: {admin_note}\n"

        body += """
감사합니다.
FocusMate 팀
"""
        return await self._send_email(leader_email, subject, body)

    async def send_verification_rejected_email(
        self, team_name: str, leader_email: str, admin_note: Optional[str] = None
    ) -> bool:
        """Send email notification when verification is rejected."""
        subject = f"[FocusMate] {team_name} 인증이 반려되었습니다"
        body = f"""
안녕하세요,

{team_name}의 학교 인증 요청이 반려되었습니다.

"""
        if admin_note:
            body += f"반려 사유: {admin_note}\n\n"

        body += """
서류를 보완하여 다시 신청하실 수 있습니다.

감사합니다.
FocusMate 팀
"""
        return await self._send_email(leader_email, subject, body)

    async def send_team_invitation_email(
        self, team_name: str, invitee_email: str, invite_link: str
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
        self, to_email: str, subject: str, body: str
    ) -> bool:
        """Send email using SMTP."""
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email

            # Attach plain text content
            text_part = MIMEText(body, "plain")
            msg.attach(text_part)

            # Send email
            if self.smtp_user and self.smtp_password:
                # Production mode - actual SMTP sending
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.starttls()  # Enable TLS
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(msg)
                print(f"[EMAIL] ✅ Sent to {to_email}: {subject}")
            else:
                # Development mode - just log
                print(f"[EMAIL] 📧 To: {to_email}")
                print(f"[EMAIL] 📝 Subject: {subject}")
                print(f"[EMAIL] 📄 Body: {body[:100]}...")

            return True

        except Exception as e:
            print(f"[EMAIL ERROR] ❌ Failed to send to {to_email}: {e}")
            return False


# Singleton instance
email_service = EmailService()
