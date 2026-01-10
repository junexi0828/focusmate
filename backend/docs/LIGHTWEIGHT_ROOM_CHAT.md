# Lightweight Focus Room Chat

## Overview

Lightweight Focus Room Chat is an ephemeral, in-room chat stream designed to support "focus companionship" without turning FocusMate into a collaboration tool. The chat exists only while users are inside a focus room and intentionally avoids read receipts, notifications, and long-term storage.

---

## Product Framing

### Purpose
- **Primary**: Encourage short, real-time check-ins that reinforce focus.
- **Not**: Work tracking, task coordination, or durable knowledge capture.

### Core Principles
1. **Ephemeral by default**: Short-lived messages that do not become a record.
2. **Low-friction**: Simple text only; no reactions, read states, or threads.
3. **Focus-first**: Minimize UI/UX that encourages long conversations.

### Non-Goals
- Read receipts or notifications
- Presence indicators (reuses existing presence system)
- File uploads, reactions, threads, or search
- Cross-room history or user inbox

---

## Experience Design

### UX Constraints
- Show only recent messages while inside the room.
- No guarantee of historical backfill after leaving.
- Provide a short guidance line near the input (e.g., "Keep it brief. This chat is only for this room session.").

### Example Use Cases
- "Starting 25-minute focus now."
- "Halfway done, staying on track."

---

## Architecture

### High-Level Flow
1. Client connects to the existing room WebSocket: `GET /api/v1/ws/{room_id}?token=...`.
2. Server sends a short backfill list (last N messages).
3. Client sends chat messages over the same WebSocket.
4. Server validates membership, stamps server time, stores ephemeral message, and broadcasts.

### Why Shared Room WebSocket
The room WebSocket already handles real-time room events (timer, participant updates). Adding a `chat_message` event keeps the runtime footprint low and avoids a separate socket connection per feature.

---

## Data Storage (Ephemeral)

### Redis Message Cache
We store a small sliding window in Redis for room backfill.

**Key Pattern**:
- `focus:room:{room_id}:chat`

**Data**:
- Redis List of JSON messages (newest first)

**Retention Policy**:
- `LTRIM` to keep the most recent N messages (default: 50).
- Set `EXPIRE` to a short TTL (default: 2 hours).

**Fallback**:
- If Redis is unavailable, chat still works in-session but no backfill is provided.

---

## Message Schema

```json
{
  "id": "uuid",
  "room_id": "uuid",
  "sender_id": "uuid",
  "sender_name": "string",
  "content": "string",
  "created_at": "2026-01-10T12:00:00Z"
}
```

### Validation Rules
- `content`: 1..300 characters
- ASCII or UTF-8 text only (no attachments)
- Trim whitespace on both ends

---

## WebSocket Events

### Client → Server
```json
{
  "type": "chat_message",
  "data": {
    "content": "string"
  }
}
```

### Server → Client (Backfill)
```json
{
  "event": "chat_backfill",
  "data": {
    "messages": [ ... ]
  }
}
```

### Server → Client (Broadcast)
```json
{
  "event": "chat_message",
  "data": {
    "message": { ... }
  }
}
```

---

## Backend Implementation Plan

### Entry Point
- `app/api/v1/endpoints/websocket.py` (room WebSocket)
  - Add `chat_message` handling inside the main loop.
  - Send `chat_backfill` after connection success.

### New Components
- `app/domain/room_chat/schemas.py`
  - `RoomChatMessage`, `RoomChatSend`
- `app/domain/room_chat/service.py`
  - Validation + message creation
- `app/infrastructure/redis/room_chat_cache.py`
  - `append_message(room_id, message)`
  - `get_recent_messages(room_id, limit)`

### Redis Pub/Sub
- Add `publish_focus_room_event(room_id, event_type, data)` to `RedisPubSubManager`
  - Channel: `focus:room:{room_id}`
  - Keep separate from chat-room channel (`chat:room:{room_id}`)

### Room WebSocket Changes
1. After connection:
   - Fetch backfill from Redis
   - Send `chat_backfill`
2. On `chat_message`:
   - Validate content and membership
   - Create `RoomChatMessage` with server timestamp
   - Append to Redis list + publish event
   - Broadcast to local connections

---

## Rate Limits

- 1 message per 2 seconds per user (soft limit)
- Hard limit: 30 messages per 5 minutes
- Reuse existing rate-limit middleware where possible

---

## Security

- Require valid JWT (already enforced on room WebSocket).
- Verify user is a room participant (reuse `ParticipantRepository`).
- No file uploads or external URLs processed server-side.

---

## Observability

- Log entry on message validation failures (debug level).
- Redis errors should be logged but not fail the room experience.
- Track message count per room for basic usage metrics.

---

## Testing & Verification

### Unit Tests
- `RoomChatService` validation (length, empty content).
- Redis cache wrapper (append, trim, TTL).

### Integration Tests
- WebSocket flow for backfill and broadcast.
- Redis down scenario: chat works in-session without backfill.

---

## Rollout Plan

1. Feature flag `room_chat_enabled` (default: off).
2. Enable for internal rooms only.
3. Expand to all rooms after stability review.

---

## Changelog

### v1.0.0 (2026-01-10)
- Initial design document for lightweight focus room chat.
