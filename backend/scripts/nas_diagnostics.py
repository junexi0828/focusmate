
import sys
import os
import asyncio
import logging
from datetime import datetime

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def check_redis():
    logger.info("--- Checking Redis Connection ---")
    try:
        redis = await aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
        await redis.ping()
        await redis.set("diagnostics_test", "passed", ex=10)
        await redis.close()
        logger.info("✅ Redis connection successful!")
        return True
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        return False

async def check_db():
    logger.info("--- Checking Database Connection ---")
    try:
        logger.info(f"Database URL: {settings.DATABASE_URL.split('@')[-1]}") # Hide credentials
        engine = create_async_engine(str(settings.DATABASE_URL))
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            value = result.scalar()
            if value == 1:
                logger.info("✅ Database connection successful!")

                # Check active connections if possible (requires permissions)
                # try:
                #     result = await conn.execute(text("SELECT count(*) FROM pg_stat_activity"))
                #     count = result.scalar()
                #     logger.info(f"ℹ️  Current active connections on DB: {count}")
                # except:
                #     pass
                return True
            else:
                logger.error("❌ Database query returned unexpected result.")
                return False
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def check_env():
    logger.info("--- Checking Environment Variables ---")

    # Check WORKERS
    workers = os.getenv("WORKERS", "Not Set")
    pool_size = os.getenv("DATABASE_POOL_SIZE", "Not Set")
    overflow = os.getenv("DATABASE_MAX_OVERFLOW", "Not Set")

    logger.info(f"WORKERS: {workers}")
    logger.info(f"DATABASE_POOL_SIZE: {pool_size}")
    logger.info(f"DATABASE_MAX_OVERFLOW: {overflow}")

    issues = []

    if workers == "Not Set" or int(workers) > 2:
        issues.append("⚠️  WORKERS is high (>2) or not set. Recommended: 1 for NAS/Supabase.")

    if pool_size == "Not Set" or int(pool_size) > 5:
        issues.append("⚠️  DATABASE_POOL_SIZE is high (>5) or not set. Recommended: 5.")

    if overflow == "Not Set" or int(overflow) > 0:
        issues.append("⚠️  DATABASE_MAX_OVERFLOW is high (>0) or not set. Recommended: 0.")

    if not issues:
        logger.info("✅ Environment configuration looks optimal for weak network/NAS.")
    else:
        for issue in issues:
            logger.warning(issue)

    return len(issues) == 0

async def main():
    print(f"Starting NAS Diagnostics at {datetime.now()}")
    print("="*50)

    env_ok = check_env()
    print("-" * 30)

    redis_ok = await check_redis()
    print("-" * 30)

    db_ok = await check_db()
    print("="*50)

    if env_ok and redis_ok and db_ok:
        print("\n✅ ALL CHECKS PASSED. System should be stable.\n")
    else:
        print("\n❌ SOME CHECKS FAILED. See logs above for details.\n")

if __name__ == "__main__":
    asyncio.run(main())
