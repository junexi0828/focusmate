"""Email service for sending notifications.

Handles email sending via SMTP with support for:
- Verification approval/rejection emails
- Team invitation emails
- HTML templates with inline CSS
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via SMTP."""

    def __init__(self):
        """Initialize email service with SMTP configuration."""
        self.enabled = settings.SMTP_ENABLED
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.user = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = settings.SMTP_FROM_NAME
        self.use_tls = settings.SMTP_USE_TLS

    def _send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """Send an email via SMTP.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email content
            text_content: Plain text fallback (optional)

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.enabled:
            logger.warning("SMTP is disabled. Email not sent.")
            return False

        if not self.user or not self.password:
            logger.error("SMTP credentials not configured. Email not sent.")
            return False

        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email
            msg["Subject"] = subject

            # Add plain text version if provided
            if text_content:
                part1 = MIMEText(text_content, "plain")
                msg.attach(part1)

            # Add HTML version
            part2 = MIMEText(html_content, "html")
            msg.attach(part2)

            # Send email
            with smtplib.SMTP(self.host, self.port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.user, self.password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    def send_verification_approved(
        self,
        to_email: str,
        team_name: str,
        username: str,
    ) -> bool:
        """Send verification approval email.

        Args:
            to_email: Recipient email address
            team_name: Name of the team
            username: User's name

        Returns:
            bool: True if email sent successfully
        """
        subject = f"[Focus Mate] {team_name} 팀 인증 승인"

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

        이제 랭킹전에 참여하실 수 있습니다.

        Focus Mate - 함께 집중하는 힘
        """

        return self._send_email(to_email, subject, html_content, text_content)

    def send_verification_rejected(
        self,
        to_email: str,
        team_name: str,
        username: str,
        reason: Optional[str] = None,
    ) -> bool:
        """Send verification rejection email.

        Args:
            to_email: Recipient email address
            team_name: Name of the team
            username: User's name
            reason: Rejection reason (optional)

        Returns:
            bool: True if email sent successfully
        """
        subject = f"[Focus Mate] {team_name} 팀 인증 거부"

        reason_html = f"<p><strong>거부 사유:</strong> {reason}</p>" if reason else ""
        reason_text = f"\n거부 사유: {reason}\n" if reason else ""

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

        return self._send_email(to_email, subject, html_content, text_content)

    def send_team_invitation(
        self,
        to_email: str,
        team_name: str,
        inviter_name: str,
        invitation_link: str,
    ) -> bool:
        """Send team invitation email.

        Args:
            to_email: Recipient email address
            team_name: Name of the team
            inviter_name: Name of the person sending the invitation
            invitation_link: Link to accept the invitation

        Returns:
            bool: True if email sent successfully
        """
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
                    <a href="{invitation_link}" class="button">초대 수락하기</a>
                </div>

                <p style="font-size: 14px; color: #6b7280; margin-top: 20px;">
                    초대 링크: <a href="{invitation_link}">{invitation_link}</a>
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
        {invitation_link}

        Focus Mate - 함께 집중하는 힘
        """

        return self._send_email(to_email, subject, html_content, text_content)


# Global email service instance
email_service = EmailService()
