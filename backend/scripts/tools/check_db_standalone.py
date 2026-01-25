import asyncio
import os
import sys
from urllib.parse import urlparse

# Try to load .env manually if dotenv is missing
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Loaded .env file via python-dotenv")
except ImportError:
    print("python-dotenv not installed, attempting manual parsing of backend/.env...")
    try:
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip().strip("'").strip('"')
            print(f"Loaded {env_path} manually")
        else:
            print(f"Could not find .env at {env_path}")
    except Exception as e:
        print(f"Manual parsing failed: {e}")

DATABASE_URL = os.getenv("DATABASE_URL")

async def check_connection():
    if not DATABASE_URL:
        print("❌ Error: DATABASE_URL environment variable is not set.")
        print("Make sure you are running this from the backend directory with a valid .env file.")
        return

    print(f"Checking connection to: {DATABASE_URL.split('@')[-1]}")  # masking password

    try:
        # Initial check regarding protocol
        if DATABASE_URL.startswith("postgresql+asyncpg"):
            import asyncpg

            # Parse URL manually for asyncpg if needed, or use create_pool
            # asyncpg expects dsn
            dsn = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

            print("⏳ Attempting to connect via asyncpg...")
            try:
                conn = await asyncpg.connect(dsn, timeout=5)
                version = await conn.fetchval("SELECT version()")
                print(f"✅ Connection Successful!")
                print(f"   Server Version: {version}")

                # Check active connections count just in case
                active = await conn.fetchval("SELECT count(*) FROM pg_stat_activity")
                print(f"   Active Connections on server: {active}")

                await conn.close()
            except Exception as e:
                print(f"❌ Connection Failed:")
                print(f"   Type: {type(e).__name__}")
                print(f"   Message: {str(e)}")

                if "password authentication failed" in str(e):
                    print("\n💡 Tip: Check your username or password in DATABASE_URL.")
                elif "timeout" in str(e).lower() or "connection refused" in str(e).lower():
                    print("\n💡 Tip: Check if the database server is running, the port is correct, and firewalls allow traffic.")
                    print("   If using Supabase, check if the project is paused.")

        else:
            print("⚠️  This script is optimized for 'postgresql+asyncpg' driver.")
            print("   Your URL uses a different driver. Please check manually.")

    except ImportError:
        print("❌ 'asyncpg' library is missing. Install it with: pip install asyncpg")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        asyncio.run(check_connection())
    except KeyboardInterrupt:
        print("\nCancelled.")
