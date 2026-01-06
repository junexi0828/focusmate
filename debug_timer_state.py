
import asyncio
import os
import sys
from uuid import UUID

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.app.infrastructure.database.session import AsyncSessionLocal
from backend.app.infrastructure.database.models import Timer
from sqlalchemy import select

async def check_timer(room_id: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Timer).where(Timer.room_id == UUID(room_id)))
        timer = result.scalar_one_or_none()

        if timer:
            print(f"Timer found for room {room_id}:")
            print(f"  ID: {timer.id}")
            print(f"  Status: {timer.status}")
            print(f"  Phase: {timer.phase}")
            print(f"  Remaining Seconds: {timer.remaining_seconds}")
            print(f"  Duration: {timer.duration}")
            print(f"  Started At: {timer.started_at}")
            print(f"  Paused At: {timer.paused_at}")
            print(f"  Completed At: {timer.completed_at}")
        else:
            print(f"No timer found for room {room_id}")

if __name__ == "__main__":
    room_id = "5b2a5f1b-75cf-48f3-b6f9-a5f89fd35e74"
    asyncio.run(check_timer(room_id))
