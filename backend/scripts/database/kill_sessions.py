import asyncio
import sys
import ssl
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Add parent directory to path to find app.core.config
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from app.core.config import settings

async def kill_stale_sessions():
    # PIDs found in previous check
    stale_pids = [20820, 20816]
    print(f"🧹 Attempting to terminate stale PIDs: {stale_pids}")

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    connect_args = {"ssl": ctx, "statement_cache_size": 0}
    engine = create_async_engine(settings.DATABASE_URL, connect_args=connect_args)
    try:
        async with engine.begin() as conn:
            for pid in stale_pids:
                print(f"🚀 Terminating PID {pid}...")
                # pg_terminate_backend is the standard way to kill a session
                result = await conn.execute(text(f"SELECT pg_terminate_backend({pid});"))
                success = result.scalar()
                print(f"   Result for {pid}: {'✅ Terminated' if success else '❌ Failed or already gone'}")

            # Double check if any others are idle in transaction for a long time
            print("\n🔍 Checking for any remaining stale sessions...")
            query = text("""
                SELECT pid, state, now() - xact_start AS duration
                FROM pg_stat_activity
                WHERE state = 'idle in transaction'
                AND now() - xact_start > interval '5 minutes';
            """)
            result = await conn.execute(query)
            rows = result.fetchall()
            for row in rows:
                print(f"⚠️  New stale session found: PID {row.pid} (Duration: {row.duration})")
                await conn.execute(text(f"SELECT pg_terminate_backend({row.pid});"))
                print(f"   ✅ PID {row.pid} terminated")

    except Exception as e:
        print(f"❌ Error terminating sessions: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(kill_stale_sessions())
