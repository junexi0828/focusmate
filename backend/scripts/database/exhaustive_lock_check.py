import asyncio
import sys
import ssl
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from app.core.config import settings

async def exhaustive_check():
    print(f"🕵️  Exhaustive lock check...")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    connect_args = {"ssl": ctx, "statement_cache_size": 0}
    engine = create_async_engine(settings.DATABASE_URL, connect_args=connect_args)
    try:
        async with engine.begin() as conn:
            # Query from Postgres Wiki for lock detection
            query = text("""
                SELECT
                    blocked_locks.pid AS blocked_pid,
                    blocked_activity.query AS blocked_query,
                    blocking_locks.pid AS blocking_pid,
                    blocking_activity.query AS blocking_query,
                    blocking_activity.state AS blocking_state
                FROM pg_catalog.pg_locks blocked_locks
                JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_locks.pid = blocked_activity.pid
                JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
                    AND blocking_locks.DATABASE IS NOT DISTINCT FROM blocked_locks.DATABASE
                    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
                    AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
                    AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
                    AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
                    AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
                    AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
                    AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
                    AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
                    AND blocking_locks.pid != blocked_locks.pid
                JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_locks.pid = blocking_activity.pid
                WHERE NOT blocked_locks.granted;
            """)
            result = await conn.execute(query)
            rows = result.fetchall()

            if not rows:
                print("✅ No blocked processes found.")
            else:
                for row in rows:
                    print(f"❌ BLOCKED: PID {row.blocked_pid} is waiting for PID {row.blocking_pid}")
                    print(f"   Blocked Query: {row.blocked_query[:100]}...")
                    print(f"   Blocking Query: {row.blocking_query[:100]}...")
                    print(f"   Blocking State: {row.blocking_state}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(exhaustive_check())
