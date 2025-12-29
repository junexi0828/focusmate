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
        to_email: str,
        team_name: str,
        username: str,
        admin_note: Optional[str] = None,
    ) -> bool:
        """Send verification approval email with HTML template."""
        subject = f"[Focus Mate] {team_name} 팀 인증 승인"

        reason_html = f"<p><strong>관리자 메모:</strong> {admin_note}</p>" if admin_note else ""
        reason_text = f"\n관리자 메모: {admin_note}\n" if admin_note else ""

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px 10px 0 0;
                    text-align: center;
                }}
                .content {{
                    background: #f9fafb;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .success-badge {{
                    display: inline-block;
                    background: #10b981;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-weight: bold;
                    margin: 20px 0;
                }}
                .button {{
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    color: #6b7280;
                    font-size: 14px;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e5e7eb;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎉 인증이 승인되었습니다!</h1>
            </div>
            <div class="content">
                <p>안녕하세요, {username}님!</p>

                <div class="success-badge">✅ 승인 완료</div>

                <p><strong>{team_name}</strong> 팀의 인증 요청이 승인되었습니다.</p>
                {reason_html}

                <p>이제 다음 기능을 사용하실 수 있습니다:</p>
                <ul>
                    <li>🏆 랭킹전 참여</li>
                    <li>👥 팀 활동 기록</li>
                    <li>📊 팀 통계 확인</li>
                    <li>🎯 명예의 전당 등재</li>
                </ul>

                <p>팀원들과 함께 집중력을 높이고 목표를 달성하세요!</p>

                <div style="text-align: center;">
                    <a href="https://focusmate.com/ranking" class="button">랭킹 확인하기</a>
                </div>
            </div>
            <div class="footer">
                <p>Focus Mate - 함께 집중하는 힘</p>
                <p>이 이메일은 자동으로 발송되었습니다.</p>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        안녕하세요, {username}님!

        {team_name} 팀의 인증 요청이 승인되었습니다.
        {reason_text}
        이제 랭킹전에 참여하실 수 있습니다.

        Focus Mate - 함께 집중하는 힘
        """
        return await self._send_email(to_email, subject, text_content, html_content)

    async def send_verification_rejected_email(
        self,
        to_email: str,
        team_name: str,
        username: str,
        admin_note: Optional[str] = None,
    ) -> bool:
        """Send verification rejection email with HTML template."""
        subject = f"[Focus Mate] {team_name} 팀 인증 거부"

        reason_html = f"<p><strong>거부 사유:</strong> {admin_note}</p>" if admin_note else ""
        reason_text = f"\n거부 사유: {admin_note}\n" if admin_note else ""

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px 10px 0 0;
                    text-align: center;
                }}
                .content {{
                    background: #f9fafb;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .warning-badge {{
                    display: inline-block;
                    background: #ef4444;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-weight: bold;
                    margin: 20px 0;
                }}
                .button {{
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    color: #6b7280;
                    font-size: 14px;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e5e7eb;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>❌ 인증이 거부되었습니다</h1>
            </div>
            <div class="content">
                <p>안녕하세요, {username}님!</p>

                <div class="warning-badge">거부됨</div>

                <p><strong>{team_name}</strong> 팀의 인증 요청이 거부되었습니다.</p>

                {reason_html}

                <p>다음 사항을 확인하신 후 다시 신청해주세요:</p>
                <ul>
                    <li>📸 인증 사진이 명확한지 확인</li>
                    <li>👥 모든 팀원이 포함되었는지 확인</li>
                    <li>📝 팀 정보가 정확한지 확인</li>
                </ul>

                <p>문의사항이 있으시면 관리자에게 연락해주세요.</p>

                <div style="text-align: center;">
                    <a href="https://focusmate.com/ranking/verification" class="button">다시 신청하기</a>
                </div>
            </div>
            <div class="footer">
                <p>Focus Mate - 함께 집중하는 힘</p>
                <p>이 이메일은 자동으로 발송되었습니다.</p>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        안녕하세요, {username}님!

        {team_name} 팀의 인증 요청이 거부되었습니다.
        {reason_text}
        다시 신청해주세요.

        Focus Mate - 함께 집중하는 힘
        """
        return await self._send_email(to_email, subject, text_content, html_content)

    async def send_team_invitation_email(
        self,
        team_name: str,
        invitee_email: str,
        invite_link: str,
        inviter_name: str = "FocusMate",
    ) -> bool:
        """Send team invitation email with HTML template."""
        subject = f"[Focus Mate] {inviter_name}님이 {team_name} 팀에 초대했습니다"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px 10px 0 0;
                    text-align: center;
                }}
                .content {{
                    background: #f9fafb;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .invite-badge {{
                    display: inline-block;
                    background: #3b82f6;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-weight: bold;
                    margin: 20px 0;
                }}
                .button {{
                    display: inline-block;
                    background: #10b981;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                    font-weight: bold;
                }}
                .button:hover {{
                    background: #059669;
                }}
                .footer {{
                    text-align: center;
                    color: #6b7280;
                    font-size: 14px;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e5e7eb;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎊 팀 초대장이 도착했습니다!</h1>
            </div>
            <div class="content">
                <p>안녕하세요!</p>

                <div class="invite-badge">📨 초대</div>

                <p><strong>{inviter_name}</strong>님이 <strong>{team_name}</strong> 팀에 초대했습니다.</p>

                <p>팀에 참여하면 다음을 할 수 있습니다:</p>
                <ul>
                    <li>🏆 팀원들과 함께 랭킹전 참여</li>
                    <li>📊 팀 통계 및 성과 확인</li>
                    <li>💬 팀 채팅으로 소통</li>
                    <li>🎯 공동 목표 달성</li>
                </ul>

                <p>아래 버튼을 클릭하여 초대를 수락하세요!</p>

                <div style="text-align: center;">
                    <a href="{invite_link}" class="button">초대 수락하기</a>
                </div>

                <p style="font-size: 14px; color: #6b7280; margin-top: 20px;">
                    초대 링크: <a href="{invite_link}">{invite_link}</a>
                </p>
            </div>
            <div class="footer">
                <p>Focus Mate - 함께 집중하는 힘</p>
                <p>이 이메일은 자동으로 발송되었습니다.</p>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        안녕하세요!

        {inviter_name}님이 {team_name} 팀에 초대했습니다.

        초대를 수락하려면 아래 링크를 클릭하세요:
        {invite_link}

        Focus Mate - 함께 집중하는 힘
        """
        return await self._send_email(invitee_email, subject, text_content, html_content)

    async def _send_email(
        self,
        to_email: str,
        subject: str,
        text_content: str,
        html_content: Optional[str] = None,
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

            # Attach plain text
            msg.attach(MIMEText(text_content, "plain", "utf-8"))

            # Attach HTML if provided
            if html_content:
                msg.attach(MIMEText(html_content, "html", "utf-8"))

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
