import asyncio
import sys
import ssl
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Add parent directory to path to find app.core.config
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from app.core.config import settings

async def check_locks():
    print(f"🔍 Checking for locks on database (with SSL, no-verify)...")

    # Create an SSL context that does not verify certificates
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Add statement_cache_size=0 for PgBouncer/Supabase Pooler safety
    connect_args = {"ssl": ctx, "statement_cache_size": 0}
    engine = create_async_engine(settings.DATABASE_URL, connect_args=connect_args)
    try:
        async with engine.begin() as conn:
            query = text("""
                SELECT pid, state, wait_event_type, wait_event, query,
                       now() - xact_start AS xact_duration
                FROM pg_stat_activity
                WHERE state != 'idle'
                AND pid != pg_backend_pid();
            """)
            result = await conn.execute(query)
            rows = result.fetchall()

            if not rows:
                print("✅ No active (non-idle) transactions found.")
            else:
                print(f"⚠️  Found {len(rows)} active transactions:")
                for row in rows:
                    print(f"--- PID: {row.pid} ---")
                    print(f"State: {row.state}")
                    print(f"Wait Event: {row.wait_event_type} - {row.wait_event}")
                    print(f"Duration: {row.xact_duration}")
                    print(f"Query: {row.query[:150]}...")
                    print("-" * 20)
    except Exception as e:
        print(f"❌ Error checking locks: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_locks())
