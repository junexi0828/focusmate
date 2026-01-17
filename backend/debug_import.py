
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Starting debug import...")

try:
    logger.info("Importing redis_timer_listener...")
    from app.infrastructure.tasks import redis_timer_listener
    logger.info("✅ redis_timer_listener imported")
except Exception as e:
    logger.error(f"❌ Failed to import redis_timer_listener: {e}")

try:
    logger.info("Importing reservation_notification_worker...")
    from app.infrastructure.tasks import reservation_notification_worker
    logger.info("✅ reservation_notification_worker imported")
except Exception as e:
    logger.error(f"❌ Failed to import reservation_notification_worker: {e}")

logger.info("Debug import complete.")
