import psycopg2
import sys
import os
from pathlib import Path

def check_version_sync():
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from app.core.config import settings
        raw_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    except Exception:
        raw_url = os.environ.get("DATABASE_URL", "").replace("+asyncpg", "")

    if not raw_url:
        print("❌ DATABASE_URL not found.")
        return

    print(f"🔍 Testing synchronous version check...")

    try:
        conn = psycopg2.connect(raw_url, sslmode='require')
        cur = conn.cursor()
        cur.execute("SELECT version_num FROM alembic_version;")
        row = cur.fetchone()
        if row:
            print(f"✅ Current version in DB: {row[0]}")
        else:
            print("⚠️  No version found in alembic_version table.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Check failed: {e}")

if __name__ == "__main__":
    check_version_sync()
