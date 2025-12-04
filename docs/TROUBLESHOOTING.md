# Troubleshooting Guide

# Team Pomodoro Timer (Focus Mate)

**문서 버전**: 1.0
**작성일**: 2025-12-04

---

## 목차

1. [일반적인 문제](#1-일반적인-문제)
2. [백엔드 문제](#2-백엔드-문제)
3. [프론트엔드 문제](#3-프론트엔드-문제)
4. [데이터베이스 문제](#4-데이터베이스-문제)
5. [네트워크 문제](#5-네트워크-문제)
6. [성능 문제](#6-성능-문제)
7. [로그 분석](#7-로그-분석)

---

## 1. 일반적인 문제

### 1.1 Docker Compose 실행 실패

**증상**:

```bash
$ docker-compose up
ERROR: Could not find a version that satisfies the requirement...
```

**원인**: 의존성 문제 또는 Docker 버전 불일치

**해결 방법**:

```bash
# Docker 버전 확인
docker --version
docker-compose --version

# 이미지 재빌드
docker-compose build --no-cache

# 볼륨 삭제 후 재시작
docker-compose down -v
docker-compose up --build
```

---

### 1.2 포트 충돌

**증상**:

```bash
ERROR: bind: address already in use
```

**원인**: 다른 프로세스가 동일한 포트 사용 중

**해결 방법**:

```bash
# 포트 사용 확인
# macOS/Linux
lsof -i :8000
lsof -i :3000

# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# 포트 사용 중인 프로세스 종료
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# 또는 docker-compose.yml에서 포트 변경
ports:
  - "8001:8000"  # 8000 대신 8001 사용
```

---

### 1.3 컨테이너가 시작되지 않음

**증상**: 컨테이너가 계속 재시작됨

**해결 방법**:

```bash
# 로그 확인
docker-compose logs backend
docker-compose logs frontend

# 컨테이너 상태 확인
docker-compose ps

# 컨테이너 내부 접속
docker-compose exec backend sh
docker-compose exec frontend sh
```

---

## 2. 백엔드 문제

### 2.1 FastAPI 서버 시작 실패

**증상**:

```bash
ERROR: Could not import module 'app.main'
```

**원인**: Python 경로 문제 또는 모듈 누락

**해결 방법**:

```bash
# 의존성 재설치
cd src/backend
pip install -r requirements.txt

# Python 경로 확인
python -c "import sys; print(sys.path)"

# 모듈 직접 테스트
python -m app.main
```

---

### 2.2 데이터베이스 연결 실패

**증상**:

```bash
sqlalchemy.exc.OperationalError: unable to open database file
```

**원인**: SQLite 파일 권한 문제 또는 경로 오류

**해결 방법**:

```bash
# 데이터 디렉토리 확인
ls -la data/

# 권한 수정
chmod 666 data/focusmate.db
chmod 755 data/

# 데이터베이스 파일 재생성
rm data/focusmate.db
docker-compose up --build
```

---

### 2.3 Pydantic 검증 오류

**증상**:

```json
{
  "detail": [
    {
      "loc": ["body", "room_name"],
      "msg": "String should match pattern '^[a-zA-Z0-9_-]+$'"
    }
  ]
}
```

**원인**: 입력 데이터가 스키마와 일치하지 않음

**해결 방법**:

- API 명세서 확인: [API_SPECIFICATION.md](./API_SPECIFICATION.md)
- 요청 데이터 형식 확인
- Pydantic 모델 검증 규칙 확인

---

### 2.4 WebSocket 연결 실패

**증상**: 클라이언트가 WebSocket 연결에 실패

**원인**:

- CORS 설정 문제
- 프록시 설정 문제
- 방화벽 차단

**해결 방법**:

```python
# backend/app/core/config.py
CORS_ORIGINS = [
    "http://localhost:3000",
    "https://focusmate.example.com"
]
```

```bash
# 프록시 설정 확인 (Nginx)
location /ws {
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

---

## 3. 프론트엔드 문제

### 3.1 빌드 실패

**증상**:

```bash
npm ERR! code ELIFECYCLE
npm ERR! errno 1
```

**원인**: 의존성 문제 또는 Node.js 버전 불일치

**해결 방법**:

```bash
# Node.js 버전 확인
node --version  # 20+ 필요

# node_modules 삭제 후 재설치
cd src/frontend
rm -rf node_modules package-lock.json
npm install

# 캐시 클리어
npm cache clean --force
```

---

### 3.2 TypeScript 컴파일 오류

**증상**:

```bash
error TS2345: Argument of type 'string' is not assignable to parameter of type 'number'
```

**원인**: 타입 불일치

**해결 방법**:

```bash
# 타입 체크 실행
npm run type-check

# 자동 수정 시도
npm run lint -- --fix

# 타입 명시적 변환
const num: number = Number(stringValue);
```

---

### 3.3 API 연결 실패

**증상**: 프론트엔드가 백엔드 API에 연결하지 못함

**원인**: 환경 변수 설정 오류

**해결 방법**:

```bash
# 환경 변수 확인
cat src/frontend/.env

# .env 파일 생성/수정
echo "VITE_API_URL=http://localhost:8000" > src/frontend/.env
echo "VITE_WS_URL=ws://localhost:8000" >> src/frontend/.env

# 개발 서버 재시작
npm run dev
```

---

## 4. 데이터베이스 문제

### 4.1 SQLite 락 오류

**증상**:

```bash
sqlite3.OperationalError: database is locked
```

**원인**: 동시 쓰기 작업 충돌

**해결 방법**:

```python
# SQLAlchemy 설정에서 타임아웃 증가
engine = create_engine(
    DATABASE_URL,
    connect_args={"timeout": 20}  # 기본값 5초 → 20초
)
```

---

### 4.2 데이터베이스 마이그레이션 실패

**증상**: 스키마 변경 후 오류 발생

**해결 방법**:

```bash
# 데이터베이스 백업
cp data/focusmate.db data/focusmate.db.backup

# 데이터베이스 재생성
rm data/focusmate.db
docker-compose up --build

# 또는 Alembic 마이그레이션 사용 (v1.1)
alembic upgrade head
```

---

## 5. 네트워크 문제

### 5.1 CORS 오류

**증상**:

```
Access to fetch at 'http://localhost:8000/api/v1/rooms' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**해결 방법**:

```python
# backend/app/core/config.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### 5.2 WebSocket 연결 끊김

**증상**: WebSocket 연결이 자주 끊김

**해결 방법**:

```typescript
// 프론트엔드: 자동 재연결 로직
const reconnect = (attempt: number) => {
  const delay = Math.min(1000 * 2 ** attempt, 30000);
  setTimeout(() => connectWebSocket(), delay);
};
```

```python
# 백엔드: 하트비트 설정
@app.websocket("/ws/room/{room_id}")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # 주기적 핑/퐁
    while True:
        await websocket.send_json({"type": "ping"})
        await asyncio.sleep(30)
```

---

## 6. 성능 문제

### 6.1 API 응답 시간 느림

**증상**: API 응답 시간 > 200ms

**해결 방법**:

```python
# 데이터베이스 쿼리 최적화
# N+1 문제 방지
rooms = await db.query(Room).options(
    joinedload(Room.participants)
).all()

# 인덱스 추가
class Room(Base):
    __table_args__ = (
        Index('idx_room_name', 'name'),
    )
```

---

### 6.2 메모리 사용량 증가

**증상**: 컨테이너 메모리 사용량 지속 증가

**해결 방법**:

```bash
# 메모리 사용량 모니터링
docker stats

# 메모리 제한 설정
# docker-compose.yml
services:
  backend:
    mem_limit: 512m
    mem_reservation: 256m
```

---

## 7. 로그 분석

### 7.1 로그 확인 방법

```bash
# 전체 로그
docker-compose logs

# 특정 서비스 로그
docker-compose logs backend
docker-compose logs frontend

# 실시간 로그
docker-compose logs -f

# 최근 100줄
docker-compose logs --tail=100

# 타임스탬프 포함
docker-compose logs -t
```

### 7.2 로그 레벨 설정

```python
# backend/app/core/config.py
import logging

logging.basicConfig(
    level=logging.INFO,  # DEBUG, INFO, WARNING, ERROR
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

### 7.3 일반적인 로그 패턴

**성공적인 시작**:

```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**오류 발생**:

```
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  ...
```

---

## 8. 추가 도움말

### 8.1 문서 참조

- [API_SPECIFICATION.md](./API_SPECIFICATION.md): API 사용법
- [DEPLOYMENT.md](./DEPLOYMENT.md): 배포 가이드
- [CONTRIBUTING.md](./CONTRIBUTING.md): 개발 환경 설정

### 8.2 커뮤니티 지원

- **GitHub Issues**: [이슈 생성](https://github.com/your-org/focus-mate/issues)
- **GitHub Discussions**: [토론 참여](https://github.com/your-org/focus-mate/discussions)

### 8.3 디버깅 팁

1. **문제 재현**: 최소 재현 가능한 예제 작성
2. **로그 수집**: 관련 로그 모두 수집
3. **환경 정보**: OS, Docker 버전, Python/Node 버전 포함
4. **에러 메시지**: 전체 스택 트레이스 포함

---

## 9. 체크리스트

문제 해결 전 확인사항:

- [ ] Docker 및 Docker Compose 버전 확인
- [ ] 포트 충돌 확인
- [ ] 환경 변수 설정 확인
- [ ] 로그 확인
- [ ] 데이터베이스 권한 확인
- [ ] 네트워크 연결 확인
- [ ] 최신 코드로 업데이트
- [ ] 의존성 재설치

---

**문서 끝**
