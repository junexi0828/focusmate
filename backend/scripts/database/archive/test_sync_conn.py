import psycopg2
import sys
import os
from urllib.parse import urlparse

def test_sync_conn():
    # Construct sync URL from environment
    # Note: Requires DATABASE_URL in environment or hardcoded mapping
    try:
        from app.core.config import settings
        raw_url = settings.DATABASE_URL
        if raw_url.startswith("postgresql+asyncpg://"):
            raw_url = raw_url.replace("postgresql+asyncpg://", "postgresql://")
    except ImportError:
        # Fallback for standalone use
        raw_url = os.environ.get("DATABASE_URL", "").replace("+asyncpg", "")

    if not raw_url:
        print("❌ DATABASE_URL not found.")
        return

    print(f"🔍 Testing synchronous connection to: {raw_url.split('@')[1] if '@' in raw_url else raw_url}")

    try:
        # Supabase requires SSL
        conn = psycopg2.connect(raw_url, sslmode='require')
        print("✅ Connection successful!")
        cur = conn.cursor()
        cur.execute("SELECT version();")
        print(f"📊 PostgreSQL Version: {cur.fetchone()[0]}")
        cur.close()
        conn.close()
        print("✅ Connection closed cleanly.")
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    # Add parent path to find app.core.config
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
    test_sync_conn()
