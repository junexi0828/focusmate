# Smart Session Management

## Overview

Smart Session Management is a secure, user-friendly session system that provides Notion-like "keep alive" behavior while maintaining robust security. The system balances seamless user experience with enterprise-grade security features.

## Key Features

### 🔒 Security
- **HttpOnly Cookies**: XSS protection for refresh tokens
- **Token Rotation**: 24-hour automatic rotation cycle
- **Reuse Detection**: Immediate family revocation on theft detection
- **Absolute Expiry**: Hard 30-day re-login requirement
- **Per-Device Sessions**: Independent session management per device

### 🚀 User Experience
- **Activity-Based Extension**: Sessions extend while user is active in rooms
- **Seamless Refresh**: Automatic access token renewal
- **Multi-Device Support**: Independent sessions across devices
- **Graceful Degradation**: Fail-open Redis policy for reliability

### ⚡ Performance
- **Lightweight Design**: Redis for high-frequency operations, DB for security
- **Optimized Writes**: Activity tracking only extends Redis TTL (1-hour sliding window)
- **Minimal DB Load**: Database writes only on rotation or explicit extension

---

## Architecture

### Database Schema

**Table**: `user_refresh_tokens` (renamed to avoid Supabase `auth.refresh_tokens` conflict)

```sql
CREATE TABLE user_refresh_tokens (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id VARCHAR(36) NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    token_id VARCHAR(36) NOT NULL UNIQUE,
    family_id VARCHAR(36) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    absolute_expires_at TIMESTAMPTZ NOT NULL,
    last_rotated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    device_info VARCHAR(255),
    ip_address VARCHAR(45),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_user_refresh_tokens_user_id ON user_refresh_tokens(user_id);
CREATE UNIQUE INDEX idx_user_refresh_tokens_token_id ON user_refresh_tokens(token_id);
CREATE INDEX idx_user_refresh_tokens_family_id ON user_refresh_tokens(family_id);
```

### Redis Keys

- **Session Activity**: `session:active:{user_id}:{token_id}` (TTL: 1 hour)
- **Token Mapping**: `session:token_mapping:{user_id}` → `token_id`

### Token Structure

**Refresh Token JWT Claims**:
```json
{
  "sub": "user_id",
  "jti": "token_id",
  "family_id": "family_id",
  "token_type": "refresh",
  "exp": 1234567890,
  "absolute_exp": 1234567890
}
```

---

## API Endpoints

### POST /api/v1/auth/login

**Request**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": { ... }
}
```

**Cookies Set**:
- `refresh_token`: HttpOnly, Secure, SameSite=Lax, Path=/, Max-Age=7 days

---

### POST /api/v1/auth/refresh

**Request**: Cookie or `Authorization: Bearer <refresh_token>`

**Response**:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

**Behavior**:
1. Validates refresh token (type, expiry, absolute expiry)
2. Checks for reuse (revokes family if detected)
3. Extends expiry if user is active (Redis check)
4. Rotates token if > 24 hours old
5. Issues new access token

**Error Responses**:
- `401`: No refresh token, invalid token, expired, or revoked
- `401`: "Token revoked - security event" (reuse detected)

---

### POST /api/v1/auth/logout

**Request**: Cookie or `Authorization: Bearer <refresh_token>`

**Response**:
```json
{
  "message": "Logged out successfully"
}
```

**Behavior**:
1. Revokes refresh token (sets `expires_at = NOW()`)
2. Clears Redis activity
3. Removes refresh_token cookie

---

## WebSocket Integration

### Connection
```python
# On WebSocket connect
token_id = await get_token_id(user_id)
await track_user_activity(user_id, token_id, room_id)
```

### Message Handling
```python
# On every WebSocket message (heartbeat, timer events, chat)
await track_user_activity(user_id, token_id, room_id)
```

**Heartbeat Frequency**: 3 minutes (client-side)

---

## Security Features

### 1. Token Type Enforcement
```python
if payload.get("token_type") != "refresh":
    raise ValueError("Invalid token type")
```

### 2. Absolute Expiry Check
```python
if datetime.now(UTC) > datetime.fromtimestamp(payload["absolute_exp"], UTC):
    raise ValueError("Token expired (absolute limit)")
```

### 3. Reuse Detection
```python
if db_token.expires_at < datetime.now(UTC):
    logger.warning(f"Revoked token reused: {token_id}")
    await refresh_token_repo.revoke_family(family_id)
    raise HTTPException(401, "Token revoked - security event")
```

### 4. Token Rotation
```python
if (datetime.now(UTC) - db_token.last_rotated_at) > timedelta(hours=24):
    # Preserve expiry before revoking
    preserved_expiry = db_token.expires_at
    preserved_absolute_expiry = db_token.absolute_expires_at

    # Revoke old token
    db_token.expires_at = datetime.now(UTC)
    await refresh_token_repo.update(db_token)

    # Create new token with preserved expiry
    new_db_token = await refresh_token_repo.create(
        user_id=user_id,
        family_id=family_id,
        expires_at=preserved_expiry,
        absolute_expires_at=preserved_absolute_expiry,
        ...
    )
```

### 5. Activity-Based Extension
```python
is_active = await check_user_activity(user_id, token_id)
should_extend = is_active and (db_token.expires_at - datetime.now(UTC)) < timedelta(hours=24)

if should_extend:
    new_expiry = min(
        datetime.now(UTC) + timedelta(days=7),
        db_token.absolute_expires_at
    )
    db_token.expires_at = new_expiry
```

---

## Implementation Files

### Core Files
- **Model**: `app/infrastructure/database/models/refresh_token.py`
- **Repository**: `app/infrastructure/repositories/refresh_token_repository.py`
- **Security**: `app/core/security.py` (token creation/validation)
- **Endpoint**: `app/api/v1/endpoints/refresh.py`
- **Redis Helpers**: `app/infrastructure/redis/session_helpers.py`

### Modified Files
- **Login**: `app/api/v1/endpoints/auth.py` (sets refresh token cookie)
- **WebSocket**: `app/api/v1/endpoints/websocket.py` (activity tracking)
- **User Service**: `app/domain/user/service.py` (generates refresh token)
- **Schemas**: `app/domain/user/schemas.py` (TokenResponse)

### Migration
- **File**: `app/infrastructure/database/migrations/versions/20260108_1355_add_refresh_tokens.py`
- **Revision**: `20260108_1355`
- **Parent**: `20260105_0009`

---

## Configuration

### Environment Variables
```bash
# Existing variables (no new env vars needed)
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=redis://localhost:6379
```

### Token Expiry Settings
- **Access Token**: 30 minutes (configurable)
- **Refresh Token**: 7 days (rolling, extendable)
- **Absolute Expiry**: 30 days (hard limit, never extended)
- **Rotation Cycle**: 24 hours

---

## Monitoring

### Key Metrics

**Refresh Token Usage**:
```sql
-- Active tokens
SELECT COUNT(*) FROM user_refresh_tokens
WHERE expires_at > NOW();

-- Tokens by user
SELECT user_id, COUNT(*) as token_count
FROM user_refresh_tokens
WHERE expires_at > NOW()
GROUP BY user_id;
```

**Redis Session Activity**:
```bash
# Active sessions
redis-cli KEYS "session:active:*" | wc -l

# User's active sessions
redis-cli KEYS "session:active:user_123:*"
```

### Security Events

**Monitor Logs** for:
```
"Revoked token reused" - Theft attempt detected
"Redis unavailable during refresh" - Redis failure (fail-open)
"No token_id found for user" - Token mapping issue
```

### Maintenance

**Cleanup Expired Tokens** (optional cron job):
```python
# Run daily
await refresh_token_repo.delete_expired()
```

---

## Testing

### Test Scenarios

#### 1. Login/Refresh/Logout Flow
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}' \
  -c cookies.txt

# Refresh
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -b cookies.txt

# Logout
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -b cookies.txt
```

#### 2. Reuse Detection
```bash
# 1. Login and save cookie
# 2. Logout (revokes token)
# 3. Try to refresh with old cookie
# Expected: 401 "Token revoked - security event"
```

#### 3. Redis Failure
```bash
# 1. Stop Redis: redis-cli shutdown
# 2. Try to refresh
# Expected: 200 (fail-open, access token issued)
# 3. Restart Redis
```

#### 4. WebSocket Activity
```bash
# 1. Login
# 2. Join room (WebSocket connection)
# 3. Check Redis: redis-cli GET session:active:user_id:token_id
# 4. Send messages
# 5. Verify TTL extends
```

### Test Results (Verified ✅)
- ✅ Login → 200
- ✅ Refresh → 200
- ✅ Logout → 200
- ✅ Reuse Detection → 401 (with "Revoked token reused" log)
- ✅ Redis Failure → 200 (with "Redis unavailable" log)

---

## Troubleshooting

### Issue: "relation 'refresh_tokens' does not exist"

**Cause**: Migration not applied or wrong table name

**Solution**:
```bash
cd backend
./venv/bin/alembic upgrade head
```

**Verify**:
```sql
SELECT table_name FROM information_schema.tables
WHERE table_name = 'user_refresh_tokens';
```

---

### Issue: 19 duplicate columns

**Cause**: Supabase `auth.refresh_tokens` conflict

**Solution**: Table renamed to `user_refresh_tokens` (already fixed)

**Verify**:
```sql
SELECT COUNT(*) FROM information_schema.columns
WHERE table_name = 'user_refresh_tokens';
-- Should return 10
```

---

### Issue: Refresh returns 401

**Possible Causes**:
1. Cookie not sent (check browser DevTools)
2. Token expired (check `expires_at` in DB)
3. Token revoked (check `expires_at < NOW()`)
4. Token type mismatch (check JWT claims)

**Debug**:
```python
# Check token in DB
SELECT * FROM user_refresh_tokens WHERE token_id = 'your-token-id';

# Check Redis activity
redis-cli GET session:active:user_id:token_id
```

---

### Issue: WebSocket activity not extending session

**Possible Causes**:
1. `token_id` mapping not stored
2. Redis connection issue
3. WebSocket not calling `track_user_activity`

**Debug**:
```python
# Check token mapping
redis-cli GET session:token_mapping:user_id

# Check activity tracking
redis-cli GET session:active:user_id:token_id
redis-cli TTL session:active:user_id:token_id
```

---

## Rollback Plan

### Emergency Disable

**Option 1**: Comment out refresh endpoint
```python
# app/api/v1/router.py
# router.include_router(refresh.router)
```

**Option 2**: Revert migration
```bash
cd backend
./venv/bin/alembic downgrade -1
```

**Option 3**: Drop table
```sql
DROP TABLE user_refresh_tokens CASCADE;
UPDATE alembic_version SET version_num = '20260105_0009';
```

---

## Future Enhancements

### Potential Improvements
1. **Device Management UI**: Allow users to view/revoke active sessions
2. **Suspicious Activity Alerts**: Email notifications on reuse detection
3. **Geographic Tracking**: Store/validate IP location
4. **Rate Limiting**: Limit refresh attempts per user
5. **Token Blacklist**: Redis-based revocation list for immediate invalidation

### Performance Optimizations
1. **Batch Cleanup**: Bulk delete expired tokens
2. **Connection Pooling**: Optimize Redis connection usage
3. **Caching**: Cache frequently accessed token data

---

## References

### Related Documentation
- [API.md](./API.md) - General API documentation
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture
- [DEVELOPMENT.md](./DEVELOPMENT.md) - Development guide

### External Resources
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [OWASP Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [Supabase Auth](https://supabase.com/docs/guides/auth)

---

## Changelog

### v1.0.0 (2026-01-08)
- ✅ Initial implementation
- ✅ HttpOnly cookie support
- ✅ Token rotation (24h cycle)
- ✅ Reuse detection with family revocation
- ✅ Activity-based session extension
- ✅ WebSocket integration
- ✅ Fail-open Redis policy
- ✅ Per-device session isolation
- ✅ Renamed to `user_refresh_tokens` (Supabase conflict fix)
- ✅ Production deployment ready

---

**Status**: ✅ Production Ready
**Last Updated**: 2026-01-08
**Maintainer**: FocusMate Team
