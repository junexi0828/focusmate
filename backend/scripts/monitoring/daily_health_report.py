#!/usr/bin/env python3
"""
FocusMate Daily Health Report
Aggregates daily statistics and system health for Slack notification.
"""

import os
import sys
import asyncio
import logging
import psutil
from datetime import datetime, timedelta, UTC
from sqlalchemy import select, func, text
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.core.config import settings
from app.infrastructure.database.session import get_db_session
from app.infrastructure.database.models.user import User
from app.core.notify import send_slack_notification

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("health_report")

async def get_daily_stats():
    """Query database for last 24h statistics."""
    stats = {}
    async with get_db_session() as session:
        # 1. Total Users
        stats['total_users'] = await session.scalar(select(func.count(User.id)))

        # 2. New Users (Last 24h)
        yesterday = datetime.now(UTC) - timedelta(days=1)
        stats['new_users'] = await session.scalar(
            select(func.count(User.id)).where(User.created_at >= yesterday)
        )

        # 3. Active Users & Focus Time (from session_history)
        # Assuming session_history table exists as mentioned in RLS report
        try:
            result = await session.execute(text("""
                SELECT
                    COUNT(DISTINCT user_id) as active_users,
                    SUM(duration_minutes) as total_focus_minutes
                FROM session_history
                WHERE created_at >= NOW() - INTERVAL '1 day'
            """))
            row = result.fetchone()
            stats['active_users'] = row[0] or 0
            stats['total_focus_hours'] = round((row[1] or 0) / 60, 1)
        except Exception as e:
            logger.error(f"Error fetching session stats: {e}")
            stats['active_users'] = "N/A"
            stats['total_focus_hours'] = "N/A"

    return stats

def get_system_stats():
    """Get NAS system resource status."""
    return {
        'cpu_usage': psutil.cpu_percent(interval=1),
        'memory_usage': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent
    }

async def send_report():
    """Generate and send the report to Slack."""
    logger.info("Generating daily health report...")

    db_stats = await get_daily_stats()
    sys_stats = get_system_stats()

    report_message = (
        f"📊 *{settings.APP_NAME} Daily Health Report*\n"
        f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        f"*User Statistics (Last 24h):*\n"
        f"• Total Users: {db_stats['total_users']}\n"
        f"• New Users: +{db_stats['new_users']}\n"
        f"• Active Users: {db_stats['active_users']}\n"
        f"• Global Focus Time: {db_stats['total_focus_hours']} hours\n\n"
        f"*System Health (NAS):*\n"
        f"• CPU Usage: {sys_stats['cpu_usage']}%\n"
        f"• Memory Usage: {sys_stats['memory_usage']}%\n"
        f"• Disk Usage: {sys_stats['disk_usage']}%"
    )

    # Use info level for daily report
    send_slack_notification(
        message=report_message,
        level="info"
    )
    logger.info("Daily health report sent to Slack.")

if __name__ == "__main__":
    asyncio.run(send_report())
