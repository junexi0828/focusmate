# FocusMate 배포 가이드

## 환경 변수

### 필수 환경 변수

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/focusmate

# Redis
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000,https://focusmate.app

# SMTP Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@focusmate.com
FROM_NAME=FocusMate

# AWS S3
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=focusmate-uploads

# Frontend
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

### 선택 환경 변수

```bash
# Logging
LOG_LEVEL=INFO

# File Upload
MAX_UPLOAD_SIZE=52428800  # 50MB

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

## 로컬 개발 환경

### 1. 데이터베이스 설정

```bash
# PostgreSQL 설치 (macOS)
brew install postgresql@15
brew services start postgresql@15

# 데이터베이스 생성
createdb focusmate

# 마이그레이션 실행
cd backend
alembic upgrade head
```

### 2. Redis 설정

```bash
# Redis 설치 (macOS)
brew install redis
brew services start redis

# 연결 확인
redis-cli ping  # PONG
```

### 3. Backend 실행

```bash
cd backend

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Frontend 실행

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

## Production 배포

### Docker 배포

#### Backend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/focusmate
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://backend:8000

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=focusmate
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### AWS 배포

#### 1. RDS (PostgreSQL)

```bash
# RDS 인스턴스 생성
aws rds create-db-instance \
  --db-instance-identifier focusmate-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password <password> \
  --allocated-storage 20
```

#### 2. ElastiCache (Redis)

```bash
# Redis 클러스터 생성
aws elasticache create-cache-cluster \
  --cache-cluster-id focusmate-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1
```

#### 3. S3 버킷

```bash
# S3 버킷 생성
aws s3 mb s3://focusmate-uploads

# CORS 설정
aws s3api put-bucket-cors \
  --bucket focusmate-uploads \
  --cors-configuration file://cors.json
```

#### 4. ECS (Backend)

```bash
# ECR 리포지토리 생성
aws ecr create-repository --repository-name focusmate-backend

# 이미지 빌드 및 푸시
docker build -t focusmate-backend ./backend
docker tag focusmate-backend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/focusmate-backend:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/focusmate-backend:latest

# ECS 서비스 생성
aws ecs create-service \
  --cluster focusmate \
  --service-name backend \
  --task-definition focusmate-backend \
  --desired-count 2
```

#### 5. Vercel (Frontend)

```bash
# Vercel CLI 설치
npm i -g vercel

# 배포
cd frontend
vercel --prod
```

### Kubernetes 배포

#### backend-deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: focusmate-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: focusmate-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: url
```

## 모니터링

### Sentry (에러 추적)

```python
# Backend
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
)
```

### Prometheus (메트릭)

```python
# Backend
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

### Grafana (대시보드)

- CPU/메모리 사용량
- API 응답 시간
- 에러율
- WebSocket 연결 수

## 백업

### 데이터베이스

```bash
# 백업
pg_dump -h localhost -U postgres focusmate > backup.sql

# 복원
psql -h localhost -U postgres focusmate < backup.sql
```

### S3 파일

```bash
# S3 버킷 동기화
aws s3 sync s3://focusmate-uploads s3://focusmate-backup
```

## 보안 체크리스트

- [ ] 환경 변수 암호화
- [ ] HTTPS 강제
- [ ] CORS 설정
- [ ] Rate Limiting
- [ ] SQL Injection 방지
- [ ] XSS 방지
- [ ] CSRF 토큰
- [ ] 파일 업로드 검증
- [ ] 비밀번호 해싱
- [ ] JWT 토큰 만료

---

**작성일**: 2025-12-12
**버전**: 1.0.0
