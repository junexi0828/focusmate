"""Test script for new friend and chat API endpoints."""

import asyncio

import httpx


# Base URL - adjust if needed
BASE_URL = "http://localhost:8000/api/v1"

# Test credentials - adjust based on your test data
TEST_USER_1_TOKEN = None  # Will be set after login
TEST_USER_2_TOKEN = None


async def login_test_users():
    """Login test users and get tokens."""
    global TEST_USER_1_TOKEN, TEST_USER_2_TOKEN

    async with httpx.AsyncClient() as client:
        # Try to login with test users
        # You'll need to adjust these based on your actual test users
        try:
            response = await client.post(
                f"{BASE_URL}/auth/login",
                json={"email": "test1@example.com", "password": "password123"}
            )
            if response.status_code == 200:
                TEST_USER_1_TOKEN = response.json()["access_token"]
                print("✓ Logged in as test user 1")
        except Exception as e:
            print(f"✗ Could not login test user 1: {e}")

        try:
            response = await client.post(
                f"{BASE_URL}/auth/login",
                json={"email": "test2@example.com", "password": "password123"}
            )
            if response.status_code == 200:
                TEST_USER_2_TOKEN = response.json()["access_token"]
                print("✓ Logged in as test user 2")
        except Exception as e:
            print(f"✗ Could not login test user 2: {e}")


async def test_presence_endpoints():
    """Test presence-related endpoints."""
    print("\n" + "=" * 60)
    print("Testing Presence Endpoints")
    print("=" * 60)

    if not TEST_USER_1_TOKEN:
        print("✗ No authentication token, skipping presence tests")
        return

    headers = {"Authorization": f"Bearer {TEST_USER_1_TOKEN}"}

    async with httpx.AsyncClient() as client:
        # Test: Get friends presence
        try:
            response = await client.get(
                f"{BASE_URL}/friends/presence",
                headers=headers
            )
            print(f"\nGET /friends/presence: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ Success: Found {len(data)} friends with presence data")
                if data:
                    print(f"  Sample: {data[0]}")
            else:
                print(f"  ✗ Error: {response.text}")
        except Exception as e:
            print(f"  ✗ Exception: {e}")


async def test_friend_search():
    """Test friend search and filter endpoints."""
    print("\n" + "=" * 60)
    print("Testing Friend Search/Filter Endpoints")
    print("=" * 60)

    if not TEST_USER_1_TOKEN:
        print("✗ No authentication token, skipping search tests")
        return

    headers = {"Authorization": f"Bearer {TEST_USER_1_TOKEN}"}

    async with httpx.AsyncClient() as client:
        # Test: Search friends
        try:
            response = await client.get(
                f"{BASE_URL}/friends/search?query=test&limit=10",
                headers=headers
            )
            print(f"\nGET /friends/search: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ Success: Found {data.get('total_count', 0)} results")
            else:
                print(f"  ✗ Error: {response.text}")
        except Exception as e:
            print(f"  ✗ Exception: {e}")

        # Test: Filter online friends
        try:
            response = await client.get(
                f"{BASE_URL}/friends/search?filter_type=online",
                headers=headers
            )
            print(f"\nGET /friends/search?filter_type=online: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ Success: Found {data.get('total_count', 0)} online friends")
            else:
                print(f"  ✗ Error: {response.text}")
        except Exception as e:
            print(f"  ✗ Exception: {e}")


async def test_invitation_endpoints():
    """Test invitation code endpoints."""
    print("\n" + "=" * 60)
    print("Testing Invitation Code Endpoints")
    print("=" * 60)

    if not TEST_USER_1_TOKEN:
        print("✗ No authentication token, skipping invitation tests")
        return

    headers = {"Authorization": f"Bearer {TEST_USER_1_TOKEN}"}
    invitation_code = None
    room_id = None

    async with httpx.AsyncClient() as client:
        # First, get user's rooms
        try:
            response = await client.get(
                f"{BASE_URL}/chats/rooms",
                headers=headers
            )
            if response.status_code == 200:
                rooms = response.json()
                if rooms:
                    room_id = rooms[0]["room_id"]
                    print(f"\n✓ Using room: {room_id}")
        except Exception as e:
            print(f"  ✗ Could not get rooms: {e}")

        if room_id:
            # Test: Generate invitation code
            try:
                response = await client.post(
                    f"{BASE_URL}/chats/rooms/{room_id}/invitation",
                    headers=headers,
                    json={"expires_hours": 24, "max_uses": 10}
                )
                print(f"\nPOST /chats/rooms/{room_id}/invitation: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    invitation_code = data.get("code")
                    print(f"  ✓ Success: Generated code: {invitation_code}")
                    print(f"  Expires at: {data.get('expires_at')}")
                    print(f"  Max uses: {data.get('max_uses')}")
                else:
                    print(f"  ✗ Error: {response.text}")
            except Exception as e:
                print(f"  ✗ Exception: {e}")

            # Test: Get invitation info
            if invitation_code:
                try:
                    response = await client.get(
                        f"{BASE_URL}/chats/invitations/{invitation_code}",
                        headers=headers
                    )
                    print(f"\nGET /chats/invitations/{invitation_code}: {response.status_code}")
                    if response.status_code == 200:
                        data = response.json()
                        print(f"  ✓ Success: Code is valid: {data.get('is_valid')}")
                        print(f"  Current uses: {data.get('current_uses')}")
                    else:
                        print(f"  ✗ Error: {response.text}")
                except Exception as e:
                    print(f"  ✗ Exception: {e}")


async def test_friend_room_creation():
    """Test creating room with friends."""
    print("\n" + "=" * 60)
    print("Testing Friend Room Creation")
    print("=" * 60)

    if not TEST_USER_1_TOKEN:
        print("✗ No authentication token, skipping room creation test")
        return

    headers = {"Authorization": f"Bearer {TEST_USER_1_TOKEN}"}

    async with httpx.AsyncClient() as client:
        # First, get friends list
        try:
            response = await client.get(
                f"{BASE_URL}/friends",
                headers=headers
            )
            if response.status_code == 200:
                friends_data = response.json()
                friends = friends_data.get("friends", [])
                if friends:
                    friend_id = friends[0]["friend_id"]
                    print(f"\n✓ Using friend: {friend_id}")

                    # Test: Create room with friend
                    try:
                        response = await client.post(
                            f"{BASE_URL}/chats/rooms/friends",
                            headers=headers,
                            json={
                                "friend_ids": [friend_id],
                                "room_name": "Test Room with Friends",
                                "description": "Testing friend room creation",
                                "generate_invitation": True,
                                "invitation_expires_hours": 24
                            }
                        )
                        print(f"\nPOST /chats/rooms/friends: {response.status_code}")
                        if response.status_code == 200:
                            data = response.json()
                            print(f"  ✓ Success: Created room: {data.get('room_id')}")
                            print(f"  Room name: {data.get('room_name')}")
                            print(f"  Invitation code: {data.get('invitation_code')}")
                        else:
                            print(f"  ✗ Error: {response.text}")
                    except Exception as e:
                        print(f"  ✗ Exception: {e}")
                else:
                    print("  ✗ No friends found to test with")
        except Exception as e:
            print(f"  ✗ Could not get friends: {e}")


async def check_server_health():
    """Check if the server is running."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/../health")
            if response.status_code == 200:
                print("✓ Server is running")
                return True
    except Exception:
        pass

    print("✗ Server is not running or not accessible")
    print(f"  Expected at: {BASE_URL}")
    print("  Please start the server with: uvicorn app.main:app --reload")
    return False


async def main():
    """Main test runner."""
    print("=" * 60)
    print("API Endpoint Testing")
    print("=" * 60)

    # Check if server is running
    if not await check_server_health():
        return

    # Try to login
    await login_test_users()

    # Run tests
    await test_presence_endpoints()
    await test_friend_search()
    await test_invitation_endpoints()
    await test_friend_room_creation()

    print("\n" + "=" * 60)
    print("Testing Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
