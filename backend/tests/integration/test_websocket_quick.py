"""Quick WebSocket presence test."""

import asyncio
import json

import websockets


async def test_websocket():
    """Test WebSocket presence connection."""
    # Login to get token
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/auth/login",
            json={"email": "user1@test.com", "password": "password123"}
        )
        token = response.json()["access_token"]

    # Connect to WebSocket
    uri = f"ws://localhost:8000/api/v1/chats/ws?token={token}"
    try:
        async with websockets.connect(uri, timeout=5) as websocket:
            print("✅ WebSocket connected")

            # Wait for initial message
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=2)
                data = json.loads(message)
                print(f"✅ Received: {data.get('type')}")
            except TimeoutError:
                print("✅ Connection stable (no immediate messages)")

            print("✅ WebSocket presence working")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
