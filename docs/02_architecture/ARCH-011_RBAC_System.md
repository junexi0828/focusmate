# RBAC (Role-Based Access Control) 시스템

## 개요

FocusMate의 역할 기반 접근 제어 시스템입니다.

## 역할 (Roles)

### USER
일반 사용자 역할입니다.

**권한**:
- 기본 기능 사용
- 자신의 데이터 조회/수정
- 채팅 참여
- 매칭 참여

### ADMIN
관리자 역할입니다.

**권한**:
- USER의 모든 권한
- 사용자 인증 승인/거부
- 인증 요청 조회
- 랭킹 시즌 생성/관리
- 전체 랭킹 조회
- 분석 데이터 조회

### SUPER_ADMIN
최고 관리자 역할입니다.

**권한**:
- ADMIN의 모든 권한
- 사용자 관리 (생성/수정/삭제)
- 사용자 차단/해제
- 시스템 설정 관리

## 권한 (Permissions)

| Permission | Description | USER | ADMIN | SUPER_ADMIN |
|------------|-------------|------|-------|-------------|
| `VERIFY_USERS` | 사용자 인증 승인 | ❌ | ✅ | ✅ |
| `VIEW_VERIFICATIONS` | 인증 요청 조회 | ❌ | ✅ | ✅ |
| `MANAGE_SEASONS` | 랭킹 시즌 관리 | ❌ | ✅ | ✅ |
| `VIEW_ALL_RANKINGS` | 전체 랭킹 조회 | ❌ | ✅ | ✅ |
| `MANAGE_USERS` | 사용자 관리 | ❌ | ❌ | ✅ |
| `BAN_USERS` | 사용자 차단 | ❌ | ❌ | ✅ |
| `VIEW_ANALYTICS` | 분석 데이터 조회 | ❌ | ✅ | ✅ |
| `MANAGE_SETTINGS` | 시스템 설정 관리 | ❌ | ❌ | ✅ |

## 구현

### 역할 확인

```python
from app.core.rbac import get_user_role, UserRole

user = {"id": "123", "role": "admin"}
role = get_user_role(user)  # UserRole.ADMIN
```

### 권한 확인

```python
from app.core.rbac import has_permission, Permission

user = {"id": "123", "role": "admin"}
can_verify = has_permission(user, Permission.VERIFY_USERS)  # True
can_ban = has_permission(user, Permission.BAN_USERS)  # False
```

### 엔드포인트 보호

#### require_admin 사용

```python
from fastapi import Depends
from app.core.rbac import require_admin

@router.get("/admin/verifications")
async def get_verifications(
    current_user: Annotated[dict, Depends(require_admin)],
):
    # Only ADMIN or SUPER_ADMIN can access
    pass
```

#### require_super_admin 사용

```python
from app.core.rbac import require_super_admin

@router.post("/admin/users/{user_id}/ban")
async def ban_user(
    user_id: str,
    current_user: Annotated[dict, Depends(require_super_admin)],
):
    # Only SUPER_ADMIN can access
    pass
```

#### 커스텀 권한 데코레이터

```python
from app.core.rbac import require_permission, Permission

@router.get("/analytics")
@require_permission(Permission.VIEW_ANALYTICS)
async def get_analytics(current_user: dict):
    # Only users with VIEW_ANALYTICS permission
    pass
```

## 보호된 엔드포인트

### 인증 관리

| Endpoint | Method | Required Role |
|----------|--------|---------------|
| `/api/v1/verification/admin/pending` | GET | ADMIN |
| `/api/v1/verification/admin/{id}/review` | POST | ADMIN |

### 랭킹 관리

| Endpoint | Method | Required Role |
|----------|--------|---------------|
| `/api/v1/ranking/seasons` | POST | ADMIN |
| `/api/v1/ranking/seasons/{id}` | PATCH | ADMIN |

### 사용자 관리

| Endpoint | Method | Required Role |
|----------|--------|---------------|
| `/api/v1/admin/users` | GET | SUPER_ADMIN |
| `/api/v1/admin/users/{id}` | PATCH | SUPER_ADMIN |
| `/api/v1/admin/users/{id}/ban` | POST | SUPER_ADMIN |

## 에러 처리

### 401 Unauthorized
인증되지 않은 사용자

```json
{
  "detail": "Authentication required"
}
```

### 403 Forbidden
권한이 없는 사용자

```json
{
  "detail": "Admin access required"
}
```

```json
{
  "detail": "Permission denied: verify_users required"
}
```

## 보안 고려사항

### 역할 할당
- 역할은 데이터베이스에 저장
- 기본 역할: USER
- 역할 변경은 SUPER_ADMIN만 가능

### JWT 토큰
- 토큰에 역할 정보 포함
- 토큰 갱신 시 역할 재확인

### 감사 로그
- 관리자 작업 모두 로깅
- 권한 변경 이력 추적

---

**작성일**: 2025-12-12
**버전**: 1.0.0
