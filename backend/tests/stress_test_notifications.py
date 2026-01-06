import asyncio
import aiohttp
import uuid
import time
import random

# CONFIG
BASE_URL = "http://localhost:8000/api/v1"
TEST_USER_COUNT = 5
CONCURRENT_REQUESTS = 20

async def get_token(session, username):
    # Assuming a devout bypass or test login endpoint exists,
    # or we simulate it. For this script, we'll assume we can get tokens.
    # If not, we might need to mock or use existing known tokens.
    # Placeholder for logic.
    return f"mock_token_{username}"

async def simulate_user_behavior(user_id, session):
    """Simulate a user enabling WS and causing events."""
    print(f"User {user_id} starting...")
    # 1. Connect WS (Simulated) - In real test we'd use websockets library
    # 2. Trigger Events

    # Send Message
    target_user = f"user_{random.randint(0, TEST_USER_COUNT)}"
    while target_user == user_id:
        target_user = f"user_{random.randint(0, TEST_USER_COUNT)}"

    # POST /messages/send
    # await session.post(...)
    pass

async def stress_test_notifications():
    print(f"Starting Stress Test with {CONCURRENT_REQUESTS} concurrent ops...")
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(CONCURRENT_REQUESTS):
            user_id = f"user_{i % TEST_USER_COUNT}"
            tasks.append(simulate_user_behavior(user_id, session))

        start = time.time()
        await asyncio.gather(*tasks)
        end = time.time()

    print(f"Test Finished in {end - start:.2f}s")

if __name__ == "__main__":
    # asyncio.run(stress_test_notifications())
    print("This is a template. Actual execution requires running Backend.")
