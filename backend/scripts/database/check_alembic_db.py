import asyncio
import sys
import ssl
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from app.core.config import settings

async def check_version():
    print(f"📊 Checking Alembic version from DB...")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    connect_args = {"ssl": ctx, "statement_cache_size": 0}
    engine = create_async_engine(settings.DATABASE_URL, connect_args=connect_args)
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version_num FROM alembic_version;"))
            row = result.fetchone()
            if row:
                print(f"✅ Current Alembic version in DB: {row[0]}")
            else:
                print("⚠️  No version found in alembic_version table.")
    except Exception as e:
        print(f"❌ Error checking version: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_version())
