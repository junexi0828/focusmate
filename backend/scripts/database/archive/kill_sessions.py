import asyncio
import sys
import ssl
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Add parent directory to path to find app.core.config
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from app.core.config import settings

async def kill_stale_sessions():
    print(f"🧹 Scanning for stale sessions (idle in transaction > 5m)...")

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    connect_args = {"ssl": ctx, "statement_cache_size": 0}
    engine = create_async_engine(settings.DATABASE_URL, connect_args=connect_args)
    try:
        async with engine.begin() as conn:
            # Check for any others are idle in transaction for a long time
            query = text("""
                SELECT pid, state, now() - xact_start AS duration
                FROM pg_stat_activity
                WHERE state = 'idle in transaction'
                AND now() - xact_start > interval '5 minutes';
            """)
            result = await conn.execute(query)
            rows = result.fetchall()

            if not rows:
                print("✅ No stale sessions found.")
            else:
                for row in rows:
                    print(f"⚠️  Stale session found: PID {row.pid} (Duration: {row.duration})")
                    print(f"🚀 Terminating PID {row.pid}...")
                    term_result = await conn.execute(text(f"SELECT pg_terminate_backend({row.pid});"))
                    success = term_result.scalar()
                    print(f"   Result for {row.pid}: {'✅ Terminated' if success else '❌ Failed'}")

    except Exception as e:
        print(f"❌ Error terminating sessions: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(kill_stale_sessions())
