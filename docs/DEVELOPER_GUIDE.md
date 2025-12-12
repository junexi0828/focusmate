# FocusMate 개발자 가이드

## 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [아키텍처](#아키텍처)
3. [개발 환경 설정](#개발-환경-설정)
4. [코딩 표준](#코딩-표준)
5. [기여 가이드](#기여-가이드)
6. [테스트](#테스트)
7. [배포](#배포)

---

## 프로젝트 개요

### 기술 스택

**Backend**:
- FastAPI (Python 3.12+)
- SQLAlchemy (Async ORM)
- Pydantic (데이터 검증)
- PostgreSQL/SQLite
- JWT 인증
- SMTP 이메일
- Fernet 암호화

**Frontend**:
- React 18
- TypeScript (Strict Mode)
- TanStack Query (상태 관리)
- Axios (HTTP 클라이언트)
- Tailwind CSS
- Framer Motion

**DevOps**:
- Docker & Docker Compose
- Pytest (Backend 테스트)
- Jest/Vitest (Frontend 테스트)

---

## 아키텍처

### Backend 구조

```
backend/
├── app/
│   ├── api/v1/endpoints/     # API 엔드포인트
│   │   ├── auth.py
│   │   ├── stats.py
│   │   ├── chat.py
│   │   ├── community.py
│   │   └── ranking.py
│   ├── domain/               # 비즈니스 로직
│   │   ├── achievement/
│   │   ├── community/
│   │   ├── ranking/
│   │   └── verification/
│   ├── infrastructure/       # 인프라 계층
│   │   ├── database/
│   │   ├── repositories/
│   │   ├── email/
│   │   └── storage/
│   ├── core/                 # 핵심 설정
│   │   ├── config.py
│   │   ├── security.py
│   │   └── dependencies.py
│   └── services/             # 공통 서비스
├── tests/                    # 테스트
└── scripts/                  # 유틸리티 스크립트
```

### Frontend 구조

```
frontend/
├── src/
│   ├── api/                  # API 클라이언트
│   │   ├── auth.ts
│   │   ├── stats.ts
│   │   ├── chat.ts
│   │   └── miniGames.ts
│   ├── pages/                # 페이지 컴포넌트
│   │   ├── Dashboard.tsx
│   │   ├── Community.tsx
│   │   └── Ranking.tsx
│   ├── components/           # 재사용 컴포넌트
│   │   ├── Sidebar.tsx
│   │   └── charts/
│   ├── types/                # TypeScript 타입
│   └── utils/                # 유틸리티
└── tests/                    # 테스트
```

### 아키텍처 패턴

**Backend**:
- **Layered Architecture**: API → Domain → Infrastructure
- **Repository Pattern**: 데이터 액세스 추상화
- **Dependency Injection**: FastAPI Depends
- **Service Layer**: 비즈니스 로직 분리

**Frontend**:
- **Component-Based**: React 컴포넌트
- **Custom Hooks**: 로직 재사용
- **API Client Layer**: 중앙화된 API 호출

---

## 개발 환경 설정

### Backend 설정

```bash
# 1. Python 가상환경 생성
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경 변수 설정
cp .env.example .env
# .env 파일 편집

# 4. 데이터베이스 마이그레이션
alembic upgrade head

# 5. 개발 서버 실행
uvicorn app.main:app --reload
```

### Frontend 설정

```bash
# 1. 의존성 설치
cd frontend
npm install

# 2. 개발 서버 실행
npm run dev
```

### 환경 변수

**Backend (.env)**:
```bash
# Database
DATABASE_URL=sqlite:///./focusmate.db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Encryption
FILE_ENCRYPTION_KEY=your-base64-encoded-key

# SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password
SMTP_FROM_EMAIL=noreply@focusmate.com
SMTP_ENABLED=true

# AWS S3 (Optional)
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_S3_BUCKET=your-bucket
```

**Frontend (.env)**:
```bash
VITE_API_BASE_URL=http://localhost:8000
```

---

## 코딩 표준

### Python (Backend)

**스타일 가이드**: PEP 8

**Linting**:
```bash
ruff check app/
black app/
```

**타입 체크**:
```bash
mypy app/ --strict
```

**예시**:
```python
from typing import Optional
from pydantic import BaseModel

class UserGoalCreate(BaseModel):
    """사용자 목표 생성 스키마."""

    daily_goal_minutes: int
    weekly_goal_sessions: int

async def create_goal(
    user_id: str,
    goal_data: UserGoalCreate,
) -> UserGoal:
    """사용자 목표 생성.

    Args:
        user_id: 사용자 ID
        goal_data: 목표 데이터

    Returns:
        생성된 목표
    """
    # 구현...
```

### TypeScript (Frontend)

**스타일 가이드**: Airbnb TypeScript

**Linting**:
```bash
npm run lint
npm run type-check
```

**예시**:
```typescript
interface UserGoal {
  goalId: string;
  dailyGoalMinutes: number;
  weeklyGoalSessions: number;
}

export const saveUserGoal = async (
  goal: UserGoalCreate
): Promise<UserGoal> => {
  const response = await api.post('/stats/goals', goal);
  return response.data;
};
```

### 네이밍 규칙

**Backend**:
- 파일: `snake_case.py`
- 클래스: `PascalCase`
- 함수/변수: `snake_case`
- 상수: `UPPER_SNAKE_CASE`

**Frontend**:
- 파일: `PascalCase.tsx` (컴포넌트), `camelCase.ts` (유틸)
- 컴포넌트: `PascalCase`
- 함수/변수: `camelCase`
- 상수: `UPPER_SNAKE_CASE`

---

## 기여 가이드

### 브랜치 전략

```
main          # 프로덕션
├── develop   # 개발
    ├── feature/xxx  # 새 기능
    ├── fix/xxx      # 버그 수정
    └── docs/xxx     # 문서
```

### 커밋 메시지

**Conventional Commits** 형식 사용:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: 새 기능
- `fix`: 버그 수정
- `docs`: 문서
- `style`: 코드 스타일
- `refactor`: 리팩토링
- `test`: 테스트
- `chore`: 기타

**예시**:
```
feat(stats): add user goal saving API

- Add POST /stats/goals endpoint
- Add UserGoal model and schema
- Integrate with Dashboard component

Closes #123
```

### Pull Request 프로세스

1. **Fork & Clone**
   ```bash
   git clone https://github.com/your-username/focusmate.git
   cd focusmate
   ```

2. **브랜치 생성**
   ```bash
   git checkout -b feature/my-feature
   ```

3. **개발 & 커밋**
   ```bash
   git add .
   git commit -m "feat: add my feature"
   ```

4. **테스트 실행**
   ```bash
   ./scripts/test-all.sh
   ```

5. **Push & PR 생성**
   ```bash
   git push origin feature/my-feature
   ```

6. **코드 리뷰 대기**

### 코드 리뷰 체크리스트

- [ ] 테스트 커버리지 90% 이상
- [ ] 타입 체크 통과
- [ ] Lint 에러 없음
- [ ] 문서 업데이트
- [ ] 커밋 메시지 규칙 준수
- [ ] 순환 복잡도 < 10

---

## 테스트

### Backend 테스트

**단위 테스트**:
```bash
pytest tests/unit/
```

**통합 테스트**:
```bash
pytest tests/integration/
```

**커버리지**:
```bash
pytest --cov=app --cov-report=html
```

**예시**:
```python
import pytest
from app.domain.stats.service import StatsService

@pytest.mark.asyncio
async def test_create_user_goal():
    """사용자 목표 생성 테스트."""
    service = StatsService(...)

    goal_data = UserGoalCreate(
        daily_goal_minutes=120,
        weekly_goal_sessions=10,
    )

    result = await service.create_goal("user-123", goal_data)

    assert result.daily_goal_minutes == 120
    assert result.weekly_goal_sessions == 10
```

### Frontend 테스트

**컴포넌트 테스트**:
```bash
npm test
```

**E2E 테스트**:
```bash
npm run test:e2e
```

**예시**:
```typescript
import { render, screen } from '@testing-library/react';
import Dashboard from './Dashboard';

test('renders dashboard', () => {
  render(<Dashboard />);
  const heading = screen.getByText(/Dashboard/i);
  expect(heading).toBeInTheDocument();
});
```

---

## 배포

### Docker Compose

```bash
# 전체 스택 실행
docker-compose up --build

# 백그라운드 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

### 프로덕션 배포

1. **환경 변수 설정**
   - `.env.production` 파일 생성
   - 보안 키 설정
   - 데이터베이스 URL 설정

2. **데이터베이스 마이그레이션**
   ```bash
   alembic upgrade head
   ```

3. **빌드**
   ```bash
   docker-compose -f docker-compose.prod.yml build
   ```

4. **실행**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

5. **헬스 체크**
   ```bash
   curl http://localhost:8000/health
   ```

---

## 디버깅

### Backend 디버깅

**로깅**:
```python
import logging

logger = logging.getLogger(__name__)
logger.info("User goal created", extra={"user_id": user_id})
```

**디버거**:
```python
import pdb; pdb.set_trace()
```

### Frontend 디버깅

**React DevTools**: 브라우저 확장 설치

**Console Logging**:
```typescript
console.log('API Response:', response);
```

**Network 탭**: API 요청/응답 확인

---

## 성능 최적화

### Backend

- **데이터베이스 인덱스**: 자주 조회하는 컬럼
- **비동기 처리**: AsyncSession 사용
- **캐싱**: Redis (향후 추가)
- **쿼리 최적화**: N+1 문제 방지

### Frontend

- **코드 스플리팅**: React.lazy
- **메모이제이션**: useMemo, useCallback
- **이미지 최적화**: WebP 형식
- **번들 크기**: Tree shaking

---

## 보안

### Backend

- **SQL Injection**: SQLAlchemy ORM 사용
- **XSS**: Pydantic 검증
- **CSRF**: SameSite 쿠키
- **파일 암호화**: Fernet
- **비밀번호**: bcrypt 해싱

### Frontend

- **XSS**: React 자동 이스케이프
- **HTTPS**: 프로덕션 필수
- **토큰 저장**: httpOnly 쿠키 권장

---

## 참고 자료

### 공식 문서
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [TanStack Query](https://tanstack.com/query/)

### 프로젝트 문서
- [API Documentation](./API_DOCUMENTATION.md)
- [User Guide](./USER_GUIDE.md)
- [Architecture](../docs/02_architecture/)

---

**Happy Coding!** 🚀

**Last Updated**: 2025-12-12
**Version**: 1.0.0
