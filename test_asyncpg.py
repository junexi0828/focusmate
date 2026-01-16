import asyncio
import asyncpg
from sqlalchemy.engine.url import make_url

async def main():
    url = "postgresql://postgres:postgres@localhost:5432/postgres?statement_cache_size=0"
    try:
        # This simulates how asyncpg might be called
        conn = await asyncpg.connect(url)
        print("Connected!")
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
