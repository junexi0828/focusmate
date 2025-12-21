"""Simple test for friend request to debug the issue."""

import asyncio

import httpx


BASE_URL = "http://localhost:8000/api/v1"

async def test():
    """Test simple friend request."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Login user1
        print("1. Logging in user1...")
        response = await client.post(
            f"{BASE_URL}/auth/login",
            json={"email": "user1@test.com", "password": "password123"}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text}")
            return

        token1 = response.json()["access_token"]
        print("   ✓ Got token")

        # Login user2
        print("\n2. Logging in user2...")
        response = await client.post(
            f"{BASE_URL}/auth/login",
            json={"email": "user2@test.com", "password": "password123"}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text}")
            return

        user2_id = "848e2d13-3cc1-40de-a68f-fac1b2879b18"
        print(f"   ✓ user2 ID: {user2_id}")

        # Send friend request
        print("\n3. Sending friend request from user1 to user2...")
        try:
            response = await client.post(
                f"{BASE_URL}/friends/requests",
                headers={"Authorization": f"Bearer {token1}"},
                json={"receiver_id": user2_id}
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   ✗ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test())
