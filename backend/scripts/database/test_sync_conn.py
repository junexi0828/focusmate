import psycopg2
import sys
import os
from urllib.parse import urlparse

def test_sync_conn():
    # Construct sync URL from env or setting
    # postgresql+asyncpg://user:pass@host:port/db -> postgresql://user:pass@host:port/db
    raw_url = "postgresql://postgres.xevhqwaxxlcsqzhmawjr:focusmate202230262@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"
    print(f"🔍 Testing synchronous connection to: {raw_url.split('@')[1]}")

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
    test_sync_conn()
