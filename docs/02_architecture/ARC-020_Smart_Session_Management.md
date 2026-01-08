---
id: ARC-020
title: Smart Session Management Architecture
version: 1.0
status: Approved
date: 2026-01-08
author: Focus Mate Team
iso_standard: ISO/IEC 42010 Architecture Description
---

# ARC-020: 스마트 세션 관리 아키텍처 (Smart Session Management Architecture)

**문서 ID**: ARC-020
**작성일**: 2026-01-08
**작성자**: Focus Mate Team
**상태**: Approved
**카테고리**: Architecture / Security

---

## 1. 개요 (Overview)

### 1.1 목적
스마트 세션 관리(Smart Session Management)는 Notion과 같이 사용자 친화적인 "세션 유지(Keep-alive)" 경험을 제공하면서도 엔터프라이즈급 보안을 유지하는 것을 목적으로 합니다. 사용자의 활동을 감지하여 세션을 지능적으로 연장하고, 다중 기기 환경을 지원하며 강력한 보안 기능을 제공합니다.

### 1.2 핵심 기능
1. **보안 (Security)**
    - **HttpOnly Cookies**: XSS 공격 방지
    - **Token Rotation**: 24시간 주기의 자동 토큰 교체
    - **Reuse Detection**: 토큰 탈취 감지 시 즉시 해당 토큰 패밀리 전체 무효화
    - **Absolute Expiry**: 30일 경과 시 강제 재로그인 (보안 캡)
    - **Per-Device Sessions**: 기기별 독립적인 세션 관리

2. **사용자 경험 (UX)**
    - **Activity-Based Extension**: 룸 내 활동 감지 시 세션 자동 연장
    - **Seamless Refresh**: 사용자 개입 없는 백그라운드 토큰 갱신
    - **Fail-open Policy**: Redis 장애 시에도 서비스가 중단되지 않도록 설계

3. **성능 (Performance)**
    - **Lightweight**: Redis를 활용한 고빈도 작업 처리
    - **Optimized Writes**: 활동 추적은 Redis TTL 연장으로만 처리 (1시간 슬라이딩 윈도우)
    - **Minimal DB Load**: DB 쓰기는 토큰 교체(Rotation) 시에만 발생

---

## 2. 시스템 아키텍처 (System Architecture)

### 2.1 데이터베이스 스키마
**Table**: `user_refresh_tokens`
*(Supabase의 `auth.refresh_tokens`와의 충돌 방지를 위해 이름 변경됨)*

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

-- 인덱스 구성
CREATE INDEX idx_user_refresh_tokens_user_id ON user_refresh_tokens(user_id);
CREATE UNIQUE INDEX idx_user_refresh_tokens_token_id ON user_refresh_tokens(token_id);
CREATE INDEX idx_user_refresh_tokens_family_id ON user_refresh_tokens(family_id);
```

### 2.2 Redis 키 구조
- **Session Activity**: `session:active:{user_id}:{token_id}` (TTL: 1 hour)
- **Token Mapping**: `session:token_mapping:{user_id}` → `token_id`

### 2.3 토큰 구조 (JWT Claims)
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

## 3. 핵심 비즈니스 로직 (Core Logic)

### 3.1 토큰 교체 (Rotation)
- **주기**: 24시간
- **로직**:
    1. 토큰이 24시간 이상 경과했는지 확인
    2. 기존 토큰 무효화 (`expires_at` = NOW)
    3. 새 토큰 발급 (기존 `expires_at`, `absolute_expires_at` 유지)
    4. 쿠키 업데이트

### 3.2 재사용 감지 (Reuse Detection)
- **트리거**: 이미 사용되었거나 무효화된 토큰으로 Refresh 요청 시
- **대응**:
    1. 보안 이벤트 로그 기록 (`Revoked token reused`)
    2. 해당 `family_id`에 속한 **모든 토큰 즉시 폐기**
    3. 401 Unauthorized 응답 (해킹 시도 차단)

### 3.3 스마트 세션 연장 (Activity Extension)
- **트리거**: WebSocket 메시지 또는 API 호출 활동 감지
- **로직**:
    1. Redis에 활동 플래그(`session:active:...`)가 있는지 확인
    2. 활동 중이고 토큰 만료가 24시간 이내로 남았다면 만료일 7일 연장
    3. 단, `absolute_expires_at` (30일)을 초과할 수 없음

---

## 4. API 명세 (API Specification)

### 4.1 로그인 (Login)
- **Endpoint**: `POST /api/v1/auth/login`
- **Response**: JWT Access Token (Body), Refresh Token (HttpOnly Cookie)
- **Cookie Settings**: `HttpOnly`, `Secure`, `SameSite=Lax`, `Path=/`, `Max-Age=7 days`

### 4.2 토큰 갱신 (Refresh)
- **Endpoint**: `POST /api/v1/auth/refresh`
- **Input**: Refresh Token Cookie
- **Behavior**: 토큰 검증 → 재사용 감지 → 활동 기반 연장? → 교체(Rotation)? → 새 Access Token 발급

### 4.3 로그아웃 (Logout)
- **Endpoint**: `POST /api/v1/auth/logout`
- **Behavior**:
    1. DB에서 토큰 즉시 만료 처리
    2. Redis 활동 정보 제거
    3. 쿠키 삭제

---

## 5. 보안 및 모니터링 (Security & Monitoring)

### 5.1 보안 기능 요약
| 기능 | 설명 | 구현 위치 |
|------|------|-----------|
| **Token Type Check** | 토큰 타입이 'refresh'인지 확인 | `validate_refresh_token` |
| **Absolute Expiry** | 최대 세션 수명(30일) 강제 | Refresh Endpoint |
| **Family Revocation** | 토큰 탈취 시 해당 기기의 모든 세션 종료 | Reuse Detection Logic |
| **Fail-Open** | Redis 장애 시 로그인/갱신 차단하지 않음 | Exception Handler |

### 5.2 모니터링 메트릭
```sql
-- 현재 활성 세션 수
SELECT COUNT(*) FROM user_refresh_tokens WHERE expires_at > NOW();

-- 사용자별 멀티 디바이스 현황
SELECT user_id, COUNT(*) FROM user_refresh_tokens
WHERE expires_at > NOW() GROUP BY user_id;
```

---

## 6. 구현 환경 (Implementation Details)

### 6.1 관련 파일
- **Model**: `app/infrastructure/database/models/refresh_token.py`
- **Service**: `app/core/security.py`, `app/api/v1/endpoints/refresh.py`
- **Repository**: `app/infrastructure/repositories/refresh_token_repository.py`
- **Migration**: `20260108_1355_add_refresh_tokens.py`

### 6.2 환경 변수
- `ACCESS_TOKEN_EXPIRE_MINUTES`: 액세스 토큰 수명 (기본 30분)
- `REFRESH_TOKEN_EXPIRE_DAYS`: 리프레시 토큰 수명 (기본 7일)
- `ABSOLUTE_EXPIRE_DAYS`: 절대 만료 기간 (기본 30일)

---

## 7. 변경 이력

| 날짜 | 버전 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| 2026-01-08 | 1.0 | 초기 아키텍처 정의 및 구현 완료 | Focus Mate Team |
