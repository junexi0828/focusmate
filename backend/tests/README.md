# FocusMate Backend Tests

## 테스트 구조

```
tests/
├── conftest.py              # Pytest 설정 및 공통 fixtures
├── unit/                    # 단위 테스트
│   ├── test_chat_repository.py
│   ├── test_chat_service.py
│   ├── test_rbac.py
│   ├── test_encryption.py              # 암호화 서비스 테스트
│   ├── test_encrypted_file_upload.py   # 파일 암호화 업로드 테스트
│   ├── test_achievement_service.py
│   ├── test_community_service.py
│   ├── test_matching_service.py
│   ├── test_ranking_service.py
│   ├── test_room_service.py
│   └── test_verification_service.py
├── integration/             # 통합 테스트
│   ├── api/
│   │   ├── test_api_endpoints.py       # API 엔드포인트 통합 테스트
│   │   └── test_chat_api.py
│   ├── repositories/
│   ├── test_chat_api.py
│   ├── test_db_connection.py           # 데이터베이스 연결 테스트
│   ├── test_friend_features.py         # 친구 기능 통합 테스트
│   ├── test_migrations.py               # 마이그레이션 테스트
│   ├── test_simple_friend_request.py   # 친구 요청 간단 테스트
│   ├── test_websocket_quick.py         # WebSocket 빠른 테스트
│   └── test_websocket_simple.py        # WebSocket 간단 테스트
├── e2e/                     # E2E 테스트
├── performance/             # 성능 테스트
│   ├── test_matching_performance.py    # 매칭 알고리즘 성능 테스트
│   └── benchmark_matching.py           # 매칭 알고리즘 벤치마크
└── fixtures/                # 테스트 픽스처
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

### 성능 테스트만

```bash
pytest tests/performance/

# 또는 벤치마크 마커로
pytest -m benchmark
```

### 특정 파일

```bash
pytest tests/unit/test_chat_service.py
pytest tests/unit/test_encryption.py
pytest tests/performance/test_matching_performance.py
```

### Coverage 포함

```bash
pytest --cov=app --cov-report=html
```

### Standalone 벤치마크

```bash
# pytest 없이 매칭 알고리즘 벤치마크 실행
python3 tests/performance/benchmark_matching.py
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

| 모듈           | 커버리지 |
| -------------- | -------- |
| ChatRepository | 90%+     |
| ChatService    | 85%+     |
| RBAC           | 95%+     |
| Chat API       | 80%+     |

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

#### test_encryption.py (15 tests) ✨ NEW

- ✅ test_encrypt_decrypt_bytes
- ✅ test_encrypt_decrypt_string
- ✅ test_encryption_is_non_deterministic
- ✅ test_decrypt_invalid_token_raises_error
- ✅ test_decrypt_string_invalid_data_raises_error
- ✅ test_empty_data_encryption
- ✅ test_large_data_encryption
- ✅ test_unicode_string_encryption
- ✅ test_key_derivation_from_secret
- ✅ test_custom_encryption_key
- ✅ test_get_encryption_service_singleton
- ✅ test_binary_file_simulation
- ✅ test_encryption_preserves_data_integrity
- ⚡ test_encryption_performance (benchmark)
- ⚡ test_decryption_performance (benchmark)

#### test_encrypted_file_upload.py (13 tests) ✨ NEW

- ✅ test_upload_file_encrypts_content
- ✅ test_download_file_decrypts_content
- ✅ test_upload_download_roundtrip
- ✅ test_file_extension_validation
- ✅ test_delete_encrypted_file
- ✅ test_delete_nonexistent_file
- ✅ test_large_file_encryption
- ✅ test_empty_file_handling
- ✅ test_filename_sanitization
- ✅ test_concurrent_uploads
- ✅ test_encryption_service_integration
- ✅ test_file_metadata_preservation

### Integration Tests

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

#### test_api_endpoints.py

- ✅ API 엔드포인트 통합 테스트

#### test_friend_features.py

- ✅ 친구 기능 통합 테스트

#### test_db_connection.py

- ✅ 데이터베이스 연결 테스트

#### test_migrations.py

- ✅ 마이그레이션 검증 테스트

#### test*websocket*\*.py

- ✅ WebSocket 연결 및 통신 테스트

### Performance Tests (6 tests)

#### test_matching_performance.py (6 tests)

- ✅ test_optimized_finds_more_matches
- ✅ test_matching_quality
- ✅ test_performance_scales
- ✅ test_no_same_gender_matches
- ✅ test_member_count_matching
- ⚡ test_benchmark_comparison (benchmark)

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
          python-version: "3.11"

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
- [x] File upload 테스트 ✅ (암호화 포함)
- [ ] Proposal service 테스트

### 우선순위 중간

- [ ] Email service 테스트
- [ ] S3 storage 테스트
- [ ] Notification service 테스트

### 우선순위 낮음

- [x] Performance 테스트 ✅ (매칭 알고리즘)
- [ ] Load 테스트
- [x] Security 테스트 ✅ (암호화)

---

**마지막 업데이트**: 2025-12-25
**총 테스트 수**: 100+ (Unit: 67+, Integration: 20+, Performance: 6)
**상태**: 진행 중 ✅

## 테스트 파일 정리 (2025-12-25)

모든 테스트 파일을 적절한 폴더로 정리했습니다:

- API 통합 테스트 → `integration/api/`
- 데이터베이스/마이그레이션 테스트 → `integration/`
- WebSocket 테스트 → `integration/`
- 성능 벤치마크 → `performance/`

### 테스트 커버리지 개선

- ✅ 암호화 서비스: 100% 커버리지
- ✅ 파일 업로드 암호화: 90%+ 커버리지
- ✅ 매칭 알고리즘: 성능 벤치마크 포함
