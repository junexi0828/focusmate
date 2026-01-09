# Enterprise Notification System

## Overview

The Enterprise Notification System is a scalable, real-time notification infrastructure designed to handle high-volume user interactions across distributed server instances. It leverages Redis Pub/Sub for cross-server message delivery and utilizes a smart database schema for efficient querying, grouping, and routing of notifications.

## Key Features

### 🚀 Scalability & Real-Time Delivery
- **Redis Pub/Sub**: Decouples notification production from delivery, enabling scaling to multiple backend instances.
- **WebSocket Streaming**: Delivers notifications instantly to connected clients.
- **Fail-Safe Backfill**: Ensures users receive notifications generated while they were offline via a dedicated backfill API.

### 🧠 Smart Management
- **Notification Helper**: Centralized factory pattern (`NotificationHelper`) for consistent notification creation.
- **Priority System**: Supports `high` (alerts), `medium` (messages), and `low` (promotions) priorities.
- **Event Grouping**: Intelligent `group_key` logic (e.g., `friend_req:{id}`) prevents duplicate or spammy notifications.
- **Smart Routing**: Structured `routing` JSON metadata directs the frontend exactly where to go (e.g., specific chat room, post, or profile).

### 🔔 Core Notification Channels
1.  **Messages**: Real-time chat messages (intelligent online status checking to avoid redundancy).
2.  **Community**: Post likes and comments.
3.  **Friends**: Friend requests and acceptances.
4.  **Teams**: Team invitations and join/reject responses.
5.  **Matching**: New match proposals and successful match events.

---

## Architecture

### Database Schema

**Table**: `notification`

```sql
CREATE TABLE notification (
    id VARCHAR(36) PRIMARY KEY,
    recipient_id VARCHAR(36) NOT NULL REFERENCES "user"(id),
    sender_id VARCHAR(36) REFERENCES "user"(id),
    type VARCHAR(50) NOT NULL,      -- e.g., 'new_message', 'friend_request'
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,

    -- Enterprise Features
    priority VARCHAR(20) DEFAULT 'medium',  -- 'high', 'medium', 'low'
    global BOOLEAN DEFAULT FALSE,           -- For system-wide announcements
    group_key VARCHAR(100),                 -- For grouping (e.g., 'post:123')
    routing JSONB,                          -- Frontend navigation data
    data JSONB,                             -- Additional payload

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_notification_recipient ON notification(recipient_id);
CREATE INDEX idx_notification_created_at ON notification(created_at);
CREATE INDEX idx_notification_group_key ON notification(group_key);
```

### Data Flow

1.  **Event Trigger**: A service (e.g., `FriendService`) identifies an event.
2.  **Creation**: The service calls `NotificationHelper.create_X_notification()` to generate a standardized `NotificationCreate` object.
3.  **Persistence**: `NotificationService` saves the notification to PostgreSQL.
4.  **Broadcasting**: `NotificationService` publishes the standardized event to Redis channel `system:notifications`.
5.  **Delivery**: `WebSocketManager` (subscribing to Redis) receives the event and pushes it to the specific user's active WebSocket connection.
6.  **Offline Handling**: If the user is not connected, the notification remains in the DB. Next time the user connects, the frontend hook `useNotificationBackfill` fetches pending items.

---

## API Endpoints

### GET /api/v1/notifications
Retrieves a paginated list of notifications for the current user.

**Response**:
```json
{
  "items": [
    {
      "id": "uuid",
      "type": "friend_request",
      "title": "New Friend Request",
      "message": "User123 wants to be friends.",
      "priority": "medium",
      "routing": { "type": "profile", "path": "/users/user123" },
      "is_read": false,
      "created_at": "2026-01-10T..."
    }
  ],
  "total": 15,
  "page": 1,
  "size": 20
}
```

### PATCH /api/v1/notifications/{notification_id}/read
Marks a specific notification as read.

### POST /api/v1/notifications/backfill [New]
Batch retrieval endpoint optimized for client reconnection. Sends the client's last known notification ID to fetch only what was missed.

**Request**:
```json
{
  "last_notification_id": "uuid-of-last-received"
}
```

---

## Implementation Details

### Key Files

*   **Helper**: `app/domain/notification/notification_helper.py`
    *   *The "Brain"*. Contains static factory methods for every notification type. Usage ensures schema triggers are always correct.
*   **Service**: `app/domain/notification/service.py`
    *   *The "Engine"*. Handles DB persistence and Redis broadcasting.
*   **Listener**: `app/infrastructure/timer/redis_timer_listener.py`
    *   (Related) Handles timer events but shares the Redis Pub/Sub infrastructure.
*   **Socket**: `app/api/v1/endpoints/websocket.py`
    *   Handles final delivery to the client socket.

### Usage Example (Backend)

```python
from app.domain.notification.notification_helper import NotificationHelper

# Inside a domain service
if self.notification_service:
    notification = NotificationHelper.create_friend_request_notification(
        user_id=receiver_id,
        sender_name="Alice",
        request_id=request.id
    )
    await self.notification_service.create_notification(notification)
```

### Usage Example (Frontend)

The frontend uses a custom hook to manage backfill automatically.

```typescript
// hooks/useNotifications.ts
// Automatically syncs when socket reconnects
useNotificationBackfill(socket.connected, lastNotificationId);
```

---

## Testing & Verification

### Integration Tests
We maintain specific integration tests for each notification domain to ensure triggers work as expected.

*   `tests/integration/test_community_notification.py`: Verifies post likes/comments.
*   `tests/integration/test_friend_notification.py`: Verifies friend requests/accepts.
*   `tests/integration/test_matching_notification.py`: Verifies matching proposals/success.

### Stress Testing
A dedicated script `tests/stress_test_notifications.py` is available to simulate high load.

```bash
# Run stress test
python -m tests.stress_test_notifications
```

---

## Troubleshooting

### Issue: Notification not received
1.  **Check Redis**: Ensure Redis is running and reachable.
2.  **Check Connection**: Verify user's WebSocket connection in browser DevTools.
3.  **Check Database**: Query `notification` table for the user ID. If it exists in DB but didn't pop up, it's a delivery/socket issue. If not in DB, it's a trigger logic issue.

### Issue: Duplicate Notifications
1.  **Check `group_key`**: Ensure the trigger is setting a unique `group_key` (e.g., `friend_req:{id}`). The service logic typically checks for existing notifications with the same key before creating a new one (idempotency).

---

## Changelog

### v2.0.0 (2026-01-10)
- ✅ **Complete Enterprise Overhaul**: Replaced legacy system with `NotificationHelper` and Redis Pub/Sub.
- ✅ **New Triggers**: Added Matching, Team, and Friend interaction triggers.
- ✅ **Backfill API**: Added offline synchronization.
- ✅ **Schema Update**: Added `routing`, `priority`, and `group_key`.

**Status**: ✅ Production Ready
**Last Updated**: 2026-01-10
**Maintainer**: Backend Team
