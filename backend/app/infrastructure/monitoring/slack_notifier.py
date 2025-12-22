"""Slack webhook notifier for monitoring and alerts.

Sends notifications to Slack channels for critical events, errors, and alerts.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class SlackNotifier:
    """Slack webhook notifier for sending alerts and notifications."""

    def __init__(self, webhook_url: str | None = None):
        """Initialize Slack notifier.

        Args:
            webhook_url: Slack webhook URL (defaults to settings)
        """
        self.webhook_url = webhook_url or getattr(settings, "SLACK_WEBHOOK_URL", None)
        self.enabled = bool(self.webhook_url)

    async def send_message(
        self,
        text: str,
        blocks: list[dict[str, Any]] | None = None,
        level: str = "info",
    ) -> bool:
        """Send message to Slack.

        Args:
            text: Plain text message (fallback)
            blocks: Rich message blocks (Slack Block Kit)
            level: Severity level (info, warning, error, critical)

        Returns:
            True if message sent successfully
        """
        if not self.enabled:
            logger.debug("Slack notifications disabled - no webhook URL configured")
            return False

        # Prepare payload
        payload = {"text": text}
        if blocks:
            payload["blocks"] = blocks

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )
                response.raise_for_status()
                logger.debug(f"Slack message sent: {text[:50]}...")
                return True

        except httpx.HTTPError as e:
            logger.error(f"Failed to send Slack message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending Slack message: {e}")
            return False

    async def notify_error(
        self,
        error: Exception,
        context: dict[str, Any] | None = None,
    ) -> bool:
        """Send error notification to Slack.

        Args:
            error: Exception object
            context: Additional context information

        Returns:
            True if notification sent successfully
        """
        context = context or {}
        error_type = type(error).__name__
        error_message = str(error)

        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🚨 Error Alert", "emoji": True},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Type:*\n{error_type}"},
                    {
                        "type": "mrkdwn",
                        "text": f"*Time:*\n{datetime.utcnow().isoformat()}",
                    },
                    {"type": "mrkdwn", "text": f"*Environment:*\n{settings.APP_ENV}"},
                    {"type": "mrkdwn", "text": f"*Service:*\n{settings.APP_NAME}"},
                ],
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Error:*\n```{error_message}```"},
            },
        ]

        # Add context if provided
        if context:
            context_text = "\n".join([f"• *{k}:* {v}" for k, v in context.items()])
            blocks.append(
                {"type": "section", "text": {"type": "mrkdwn", "text": context_text}}
            )

        return await self.send_message(
            text=f"Error: {error_type} - {error_message}",
            blocks=blocks,
            level="error",
        )

    async def notify_service_status(
        self,
        service: str,
        status: str,
        details: dict[str, Any] | None = None,
    ) -> bool:
        """Send service status notification.

        Args:
            service: Service name
            status: Status (up, down, degraded)
            details: Additional details

        Returns:
            True if notification sent successfully
        """
        emoji_map = {"up": "✅", "down": "🔴", "degraded": "⚠️"}
        emoji = emoji_map.get(status.lower(), "ℹ️")

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} Service Status Update",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Service:*\n{service}"},
                    {"type": "mrkdwn", "text": f"*Status:*\n{status.upper()}"},
                    {
                        "type": "mrkdwn",
                        "text": f"*Time:*\n{datetime.utcnow().isoformat()}",
                    },
                    {"type": "mrkdwn", "text": f"*Environment:*\n{settings.APP_ENV}"},
                ],
            },
        ]

        if details:
            details_text = "\n".join([f"• *{k}:* {v}" for k, v in details.items()])
            blocks.append(
                {"type": "section", "text": {"type": "mrkdwn", "text": details_text}}
            )

        return await self.send_message(
            text=f"{service} is {status}",
            blocks=blocks,
            level="warning" if status == "down" else "info",
        )

    async def notify_deployment(
        self,
        version: str,
        environment: str,
        status: str = "success",
    ) -> bool:
        """Send deployment notification.

        Args:
            version: Deployment version
            environment: Target environment
            status: Deployment status (success, failed, in_progress)

        Returns:
            True if notification sent successfully
        """
        emoji_map = {"success": "🚀", "failed": "❌", "in_progress": "⏳"}
        emoji = emoji_map.get(status, "ℹ️")

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} Deployment {status.title()}",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Version:*\n{version}"},
                    {"type": "mrkdwn", "text": f"*Environment:*\n{environment}"},
                    {
                        "type": "mrkdwn",
                        "text": f"*Time:*\n{datetime.utcnow().isoformat()}",
                    },
                    {"type": "mrkdwn", "text": f"*Service:*\n{settings.APP_NAME}"},
                ],
            },
        ]

        return await self.send_message(
            text=f"Deployment {status}: {version} to {environment}",
            blocks=blocks,
            level="error" if status == "failed" else "info",
        )


# Global Slack notifier instance
slack_notifier = SlackNotifier()


# Convenience functions
async def notify_error(error: Exception, context: dict[str, Any] | None = None):
    """Send error notification (convenience function)."""
    await slack_notifier.notify_error(error, context)


async def notify_service_status(
    service: str, status: str, details: dict[str, Any] | None = None
):
    """Send service status notification (convenience function)."""
    await slack_notifier.notify_service_status(service, status, details)


async def notify_deployment(version: str, environment: str, status: str = "success"):
    """Send deployment notification (convenience function)."""
    await slack_notifier.notify_deployment(version, environment, status)
