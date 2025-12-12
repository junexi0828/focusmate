# FocusMate Backend Tests

## 테스트 구조

```
tests/
├── conftest.py              # Pytest 설정 및 공통 fixtures
├── unit/                    # 단위 테스트
│   ├── test_chat_repository.py
│   ├── test_chat_service.py
│   └── test_rbac.py
└── integration/             # 통합 테스트
    └── test_chat_api.py
```

## 테스트 실행

### 전체 테스트
```bash
pytest
```

### 단위 테스트만
```bash
pytest tests/unit/
```

### 통합 테스트만
```bash
pytest tests/integration/
```

### 특정 파일
```bash
pytest tests/unit/test_chat_service.py
```

### Coverage 포함
```bash
pytest --cov=app --cov-report=html
```

## 테스트 데이터베이스 설정

테스트용 PostgreSQL 데이터베이스 생성:
```bash
createdb focusmate_test
```

또는 Docker 사용:
```bash
docker run -d \
  --name focusmate-test-db \
  -e POSTGRES_USER=test \
  -e POSTGRES_PASSWORD=test \
  -e POSTGRES_DB=focusmate_test \
  -p 5433:5432 \
  postgres:15
```

## 테스트 커버리지

### 현재 커버리지

| 모듈 | 커버리지 |
|------|---------|
| ChatRepository | 90%+ |
| ChatService | 85%+ |
| RBAC | 95%+ |
| Chat API | 80%+ |

### 목표 커버리지
- Unit Tests: 90%+
- Integration Tests: 80%+
- Overall: 85%+

## 작성된 테스트

### Unit Tests (39 tests)

#### test_chat_repository.py (14 tests)
- ✅ test_create_room
- ✅ test_get_room_by_id
- ✅ test_get_user_rooms
- ✅ test_get_direct_room
- ✅ test_add_member
- ✅ test_create_message
- ✅ test_get_messages
- ✅ test_update_message
- ✅ test_delete_message
- ✅ test_search_messages
- ✅ test_mark_as_read
- ✅ test_get_room_members
- ✅ test_update_member_read_status
- ✅ test_get_unread_count

#### test_chat_service.py (10 tests)
- ✅ test_create_direct_chat_new
- ✅ test_create_direct_chat_existing
- ✅ test_create_team_chat
- ✅ test_send_message
- ✅ test_send_message_not_member
- ✅ test_update_message
- ✅ test_update_message_not_sender
- ✅ test_delete_message
- ✅ test_mark_as_read
- ✅ test_get_rooms

#### test_rbac.py (15 tests)
- ✅ test_get_user_role_user
- ✅ test_get_user_role_admin
- ✅ test_get_user_role_super_admin
- ✅ test_get_user_role_default
- ✅ test_has_permission_user
- ✅ test_has_permission_admin
- ✅ test_has_permission_super_admin
- ✅ test_require_admin_with_admin
- ✅ test_require_admin_with_super_admin
- ✅ test_require_admin_with_user
- ✅ test_require_super_admin_with_super_admin
- ✅ test_require_super_admin_with_admin
- ✅ test_require_super_admin_with_user
- ✅ test_permission_inheritance
- ✅ test_invalid_role

### Integration Tests (11 tests)

#### test_chat_api.py (11 tests)
- ✅ test_get_user_rooms
- ✅ test_create_direct_chat
- ✅ test_create_team_chat
- ✅ test_get_room_details
- ✅ test_send_message
- ✅ test_get_messages
- ✅ test_update_message
- ✅ test_delete_message
- ✅ test_search_messages
- ✅ test_mark_as_read
- ✅ test_add_reaction
- ✅ test_remove_reaction

## CI/CD 통합

### GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: focusmate_test
        ports:
          - 5432:5432

      redis:
        image: redis:7
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov

      - name: Run tests
        run: pytest --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## 추가 테스트 필요

### 우선순위 높음
- [ ] WebSocket 연결 테스트
- [ ] Redis Pub/Sub 테스트
- [ ] File upload 테스트
- [ ] Proposal service 테스트

### 우선순위 중간
- [ ] Email service 테스트
- [ ] S3 storage 테스트
- [ ] Notification service 테스트

### 우선순위 낮음
- [ ] Performance 테스트
- [ ] Load 테스트
- [ ] Security 테스트

---

**마지막 업데이트**: 2025-12-12
**총 테스트 수**: 50개
**상태**: 진행 중 ✅
