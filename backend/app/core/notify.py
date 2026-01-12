import httpx
import logging
import asyncio
from typing import Any

from app.core.config import settings

logger = logging.getLogger("app.notify")

async def send_slack_notification(
    message: str,
    level: str = "info",
    details: dict[str, Any] | None = None
) -> None:
    """Send a notification to Slack via Webhook.

    Args:
        message: The main message text
        level: Severity level (info, warning, error)
        details: Optional dictionary of extra fields to display
    """
    if not settings.SLACK_WEBHOOK_URL:
        logger.debug("Slack webhook not configured, skipping notification")
        return

    # Determine color based on level
    color_map = {
        "info": "#36a64f",      # Green
        "warning": "#ecb22e",   # Yellow
        "error": "#e01e5a",     # Red
        "critical": "#5c1025"   # Dark Red
    }
    color = color_map.get(level, "#36a64f")

    # Build payload
    payload = {
        "attachments": [
            {
                "color": color,
                "title": f"[{settings.APP_ENV.upper()}] {level.upper()}: FocusMate Backend",
                "text": message,
                "fields": [],
                "footer": settings.APP_NAME,
                "ts": asyncio.get_event_loop().time() # timestamp approximation or just omit
            }
        ]
    }

    if details:
        for k, v in details.items():
            payload["attachments"][0]["fields"].append({
                "title": k,
                "value": str(v),
                "short": True
            })

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.SLACK_WEBHOOK_URL,
                json=payload,
                timeout=5.0
            )
            response.raise_for_status()
    except Exception as e:
        logger.warning(f"Failed to send Slack notification: {e}")
