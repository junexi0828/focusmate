#!/usr/bin/env python3
"""Simple WebSocket test - no authentication."""

import asyncio

import websockets


async def test_websocket():
    # First, let's just try to connect without a token to see what happens
    uri = "ws://localhost:8000/api/v1/chats/ws?token=invalid"

    print(f"Connecting to {uri}")
    try:
        async with websockets.connect(uri, timeout=5) as websocket:
            print("✅ Connected!")

            # Try to receive a message
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=2)
                print(f"Received: {message}")
            except TimeoutError:
                print("No message received within 2 seconds")

    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ Connection rejected with status code: {e.status_code}")
    except TimeoutError:
        print("❌ Connection timeout")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
