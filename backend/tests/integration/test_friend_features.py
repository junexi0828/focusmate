"""Comprehensive test for friend and chat features."""

import asyncio
import sys

import httpx


BASE_URL = "http://localhost:8000/api/v1"

# Test users from database
USERS = {
    "user1": {
        "email": "user1@test.com",
        "password": "password123",
        "id": "86532628-606d-4016-82d8-ef0b1c555f50"
    },
    "user2": {
        "email": "user2@test.com",
        "password": "password123",
        "id": "848e2d13-3cc1-40de-a68f-fac1b2879b18"
    },
    "user3": {
        "email": "user3@test.com",
        "password": "password123",
        "id": "ac9fb748-c8ca-4fea-8fa3-0abdac101b79"
    }
}

tokens = {}


async def login_user(email: str, password: str) -> str:
    """Login and get JWT token."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/auth/login",
                json={"email": email, "password": password}
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("access_token")
            print(f"Login failed for {email}: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Login error for {email}: {e}")
    return None


async def setup_test_data():
    """Login all test users."""
    print("=" * 60)
    print("Setting up test data")
    print("=" * 60)

    for key, user in USERS.items():
        token = await login_user(user["email"], user["password"])
        if token:
            tokens[key] = token
            print(f"✓ Logged in {key} ({user['email']})")
        else:
            print(f"✗ Failed to login {key}")

    print(f"\n✓ Logged in {len(tokens)}/{len(USERS)} users")


async def test_friend_requests():
    """Test sending, accepting friend requests."""
    print("\n" + "=" * 60)
    print("Test: Friend Requests")
    print("=" * 60)

    if len(tokens) < 2:
        print("✗ Need at least 2 users logged in")
        return

    async with httpx.AsyncClient() as client:
        # user1 sends friend request to user2
        print("\n1. user1 sends friend request to user2")
        response = await client.post(
            f"{BASE_URL}/friends/requests",
            headers={"Authorization": f"Bearer {tokens['user1']}"},
            json={"receiver_id": USERS["user2"]["id"]}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            request_data = response.json()
            request_id = request_data.get("id")
            print(f"   ✓ Friend request created: {request_id}")

            # user2 accepts the request
            print("\n2. user2 accepts friend request")
            response = await client.post(
                f"{BASE_URL}/friends/requests/{request_id}/accept",
                headers={"Authorization": f"Bearer {tokens['user2']}"}
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✓ Friend request accepted")
            else:
                print(f"   ✗ Failed: {response.text}")
        else:
            print(f"   ✗ Failed: {response.text}")

        # user1 sends friend request to user3
        if "user3" in tokens:
            print("\n3. user1 sends friend request to user3")
            response = await client.post(
                f"{BASE_URL}/friends/requests",
                headers={"Authorization": f"Bearer {tokens['user1']}"},
                json={"receiver_id": USERS["user3"]["id"]}
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 201:
                request_data = response.json()
                request_id = request_data.get("id")
                print(f"   ✓ Friend request created: {request_id}")

                # user3 accepts
                print("\n4. user3 accepts friend request")
                response = await client.post(
                    f"{BASE_URL}/friends/requests/{request_id}/accept",
                    headers={"Authorization": f"Bearer {tokens['user3']}"}
                )
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    print("   ✓ Friend request accepted")
                else:
                    print(f"   ✗ Failed: {response.text}")


async def test_get_friends():
    """Test getting friends list."""
    print("\n" + "=" * 60)
    print("Test: Get Friends List")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/friends",
            headers={"Authorization": f"Bearer {tokens['user1']}"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            friends = data.get("friends", [])
            print(f"✓ user1 has {len(friends)} friends")
            for friend in friends:
                print(f"  - {friend.get('friend_username')}")
                print(f"    Online: {friend.get('friend_is_online', False)}")
                print(f"    Last seen: {friend.get('friend_last_seen_at', 'N/A')}")
        else:
            print(f"✗ Failed: {response.text}")


async def test_presence_endpoints():
    """Test presence endpoints."""
    print("\n" + "=" * 60)
    print("Test: Presence Endpoints")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        # Get all friends' presence
        response = await client.get(
            f"{BASE_URL}/friends/presence",
            headers={"Authorization": f"Bearer {tokens['user1']}"}
        )
        print(f"\nGET /friends/presence: {response.status_code}")
        if response.status_code == 200:
            presences = response.json()
            print(f"✓ Found {len(presences)} friend presences")
            for pres in presences:
                status = "ONLINE" if pres.get("is_online") else "OFFLINE"
                print(f"  - User {pres.get('user_id')[:8]}...: {status}")
        else:
            print(f"✗ Failed: {response.text}")

        # Get specific friend's presence
        if "user2" in USERS:
            response = await client.get(
                f"{BASE_URL}/friends/{USERS['user2']['id']}/presence",
                headers={"Authorization": f"Bearer {tokens['user1']}"}
            )
            print(f"\nGET /friends/{{user2_id}}/presence: {response.status_code}")
            if response.status_code == 200:
                pres = response.json()
                status = "ONLINE" if pres.get("is_online") else "OFFLINE"
                print(f"✓ user2 is {status}")
            else:
                print(f"✗ Failed: {response.text}")


async def test_friend_search():
    """Test friend search and filter."""
    print("\n" + "=" * 60)
    print("Test: Friend Search and Filter")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        # Search by query
        response = await client.get(
            f"{BASE_URL}/friends/search?query=김",
            headers={"Authorization": f"Bearer {tokens['user1']}"}
        )
        print(f"\nGET /friends/search?query=김: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Found {data.get('total_count', 0)} matching friends")
        else:
            print(f"✗ Failed: {response.text}")

        # Filter online friends
        response = await client.get(
            f"{BASE_URL}/friends/search?filter_type=online",
            headers={"Authorization": f"Bearer {tokens['user1']}"}
        )
        print(f"\nGET /friends/search?filter_type=online: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Found {data.get('total_count', 0)} online friends")
        else:
            print(f"✗ Failed: {response.text}")


async def test_invitation_codes():
    """Test invitation code generation and joining."""
    print("\n" + "=" * 60)
    print("Test: Invitation Codes")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        # Get a room first
        response = await client.get(
            f"{BASE_URL}/chats/rooms",
            headers={"Authorization": f"Bearer {tokens['user1']}"}
        )

        if response.status_code != 200:
            print("✗ Could not get rooms")
            return

        rooms = response.json()
        if not rooms:
            print("✗ No rooms available")
            return

        room_id = rooms[0]["room_id"]
        print(f"\nUsing room: {room_id}")

        # Generate invitation code
        response = await client.post(
            f"{BASE_URL}/chats/rooms/{room_id}/invitation",
            headers={"Authorization": f"Bearer {tokens['user1']}"},
            json={"expires_hours": 24, "max_uses": 10}
        )
        print(f"\nPOST /rooms/{{room_id}}/invitation: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            code = data.get("code")
            print(f"✓ Generated invitation code: {code}")
            print(f"  Expires at: {data.get('expires_at')}")
            print(f"  Max uses: {data.get('max_uses')}")

            # Get invitation info
            response = await client.get(
                f"{BASE_URL}/chats/invitations/{code}",
                headers={"Authorization": f"Bearer {tokens['user1']}"}
            )
            print(f"\nGET /invitations/{{code}}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print("✓ Code info retrieved")
                print(f"  Valid: {data.get('is_valid')}")
                print(f"  Uses: {data.get('current_uses')}/{data.get('max_uses')}")
            else:
                print(f"✗ Failed: {response.text}")

            # user2 joins by code
            if "user2" in tokens:
                response = await client.post(
                    f"{BASE_URL}/chats/rooms/join",
                    headers={"Authorization": f"Bearer {tokens['user2']}"},
                    json={"invitation_code": code}
                )
                print(f"\nPOST /rooms/join (user2): {response.status_code}")
                if response.status_code == 200:
                    print("✓ user2 joined room via invitation code")
                else:
                    print(f"✗ Failed: {response.text}")
        else:
            print(f"✗ Failed: {response.text}")


async def test_friend_room_creation():
    """Test creating room with friends."""
    print("\n" + "=" * 60)
    print("Test: Create Room with Friends")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/chats/rooms/friends",
            headers={"Authorization": f"Bearer {tokens['user1']}"},
            json={
                "friend_ids": [USERS["user2"]["id"]],
                "room_name": "Test Study Group",
                "description": "Testing friend room creation",
                "generate_invitation": True,
                "invitation_expires_hours": 48
            }
        )
        print(f"\nPOST /rooms/friends: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✓ Created room with friend")
            print(f"  Room ID: {data.get('room_id')}")
            print(f"  Room name: {data.get('room_name')}")
            print(f"  Invitation code: {data.get('invitation_code')}")
        else:
            print(f"✗ Failed: {response.text}")


async def test_quick_chat():
    """Test creating/getting direct chat with friend."""
    print("\n" + "=" * 60)
    print("Test: Quick Chat with Friend")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/friends/{USERS['user2']['id']}/chat",
            headers={"Authorization": f"Bearer {tokens['user1']}"}
        )
        print(f"\nPOST /friends/{{friend_id}}/chat: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✓ Chat created/retrieved")
            print(f"  Data: {data}")
        else:
            print(f"✗ Failed: {response.text}")


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Friend & Chat Features - Comprehensive Test")
    print("=" * 60)

    # Setup
    await setup_test_data()

    if not tokens:
        print("\n✗ No users logged in, cannot proceed with tests")
        sys.exit(1)

    # Run all tests
    await test_friend_requests()
    await test_get_friends()
    await test_presence_endpoints()
    await test_friend_search()
    await test_invitation_codes()
    await test_friend_room_creation()
    await test_quick_chat()

    print("\n" + "=" * 60)
    print("All Tests Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
