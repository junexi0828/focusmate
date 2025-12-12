# Test Scripts

## test-all.sh

포괄적인 시스템 테스트 스크립트입니다.

### 사용법

```bash
# 전체 테스트 실행
./scripts/test-all.sh

# 또는
cd scripts
./test-all.sh
```

### 테스트 항목

#### 1. Backend - Python Syntax & Compilation (8 tests)
- ✅ RBAC System
- ✅ Email Service
- ✅ File Upload Service
- ✅ Chat File Upload Service
- ✅ Notification Service
- ✅ Chat Repository
- ✅ Chat Service
- ✅ Chat API Endpoints

#### 2. Backend - Configuration & Imports (4 tests)
- ✅ Config Loading
- ✅ EmailService Initialization
- ✅ S3UploadService Import
- ✅ RBAC Import

#### 3. Backend - Unit Tests (3 tests)
- ✅ RBAC Unit Tests (15 tests)
- ⚠️ Chat Repository Tests (requires database)
- ⚠️ Chat Service Tests (partial)

#### 4. Frontend - TypeScript Compilation (5 tests)
- ✅ TypeScript Type Check
- ✅ Dashboard Types
- ✅ Stats Types
- ✅ Messages Types
- ✅ Matching Types

#### 5. Frontend - ESLint (1 test)
- ⚠️ ESLint Check (optional)

#### 6. Frontend - Build Test (1 test)
- ✅ Production Build

#### 7. Documentation Validation (6 tests)
- ✅ System Documentation
- ✅ Architecture Docs
- ✅ API Specs
- ✅ RBAC Docs
- ✅ Deployment Guide
- ✅ Test Documentation

#### 8. Environment & Configuration (3 tests)
- ✅ .env.example
- ✅ Frontend .env.example
- ✅ Database Migrations

#### 9. File Structure Validation (5 tests)
- ✅ Backend App Directory
- ✅ Frontend Src Directory
- ✅ Tests Directory
- ✅ Docs Directory
- ✅ Scripts Directory

### 출력 예시

```
╔════════════════════════════════════════════════════════════╗
║         FocusMate - Comprehensive Test Suite              ║
╚════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. Backend - Python Syntax & Compilation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▶ Running: RBAC System
✓ PASSED: RBAC System
▶ Running: Email Service
✓ PASSED: Email Service
...

╔════════════════════════════════════════════════════════════╗
║                     TEST SUMMARY                           ║
╚════════════════════════════════════════════════════════════╝

Total Tests:   36
Passed:        34
Failed:        2

Success Rate:  94%

✓ EXCELLENT! System is production-ready! 🎉
```

### 성공 기준

- **90%+ 성공률**: EXCELLENT - Production-ready ✅
- **70-89% 성공률**: GOOD - Minor issues ⚠️
- **70% 미만**: CRITICAL - Major issues ❌

### 로그 파일

테스트 실행 중 생성되는 로그:
- `/tmp/rbac_test.log` - RBAC 테스트 로그
- `/tmp/chat_repo_test.log` - Chat Repository 테스트 로그
- `/tmp/build.log` - Frontend 빌드 로그

### 문제 해결

#### Database 관련 테스트 실패
```bash
# PostgreSQL 실행 확인
brew services list | grep postgresql

# PostgreSQL 시작
brew services start postgresql@15
```

#### Frontend 빌드 실패
```bash
# 의존성 재설치
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### Python Import 에러
```bash
# 가상환경 활성화
cd backend
source venv/bin/activate

# 의존성 재설치
pip install -r requirements.txt
```

### CI/CD 통합

#### GitHub Actions

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Run all tests
        run: ./scripts/test-all.sh
```

### 개발 워크플로우

```bash
# 1. 코드 수정 후
git add .

# 2. 테스트 실행
./scripts/test-all.sh

# 3. 테스트 통과 시 커밋
git commit -m "feat: add new feature"

# 4. Push
git push
```

---

**작성일**: 2025-12-12
**버전**: 1.0.0
**총 테스트**: 36개
