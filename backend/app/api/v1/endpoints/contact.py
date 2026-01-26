"""Contact form endpoint."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from app.core.config import settings
from email.message import EmailMessage
import aiosmtplib

router = APIRouter(prefix="/contact", tags=["contact"])


class ContactSchema(BaseModel):
    """Contact form schema."""
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    type: str
    subject: str = Field(..., min_length=2, max_length=100)
    message: str = Field(..., min_length=10, max_length=2000)


@router.post("", status_code=status.HTTP_200_OK)
async def send_contact_email(data: ContactSchema):
    """Send contact email to support."""

    # 1. Log the inquiry (Essential for backup)
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Contact Form: {data.model_dump()}")

    # 2. Check if SMTP is enabled
    if not settings.SMTP_ENABLED:
        logger.warning("SMTP is disabled. Email not sent.")
        # We verify "sending" was successful even if SMTP is off (for dev)
        return {"message": "Inquiry received (Dev mode: email not sent)"}

    # 3. Construct Email
    message = EmailMessage()
    message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    message["To"] = settings.ADMIN_EMAIL
    message["Reply-To"] = data.email
    message["Subject"] = f"[FocusMate 문의] {data.subject} ({data.type})"

    body = f"""
    [FocusMate 접수된 문의]

    - 이름: {data.name}
    - 이메일: {data.email}
    - 유형: {data.type}

    [내용]
    {data.message}
    """
    message.set_content(body)

    # 4. Send via SMTP
    # Determine security settings based on port
    use_tls = settings.SMTP_USE_TLS and settings.SMTP_PORT == 465
    start_tls = settings.SMTP_USE_TLS and settings.SMTP_PORT == 587

    # Log attempt details (masking password)
    logger.info(
        f"Sending email via {settings.SMTP_HOST}:{settings.SMTP_PORT} "
        f"(use_tls={use_tls}, start_tls={start_tls})"
    )

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=use_tls,
            start_tls=start_tls,
        )
        logger.info("Email sent successfully")
        return {"message": "Email sent successfully"}
    except Exception as e:
        logger.exception("Failed to send email") # Log full stack trace
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email. Please try again later."
        ) from e
