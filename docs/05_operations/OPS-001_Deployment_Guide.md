---
id: OPS-001
title: Deployment Guide
version: 1.0
status: Approved
date: 2025-12-04
author: Focus Mate Team
iso_standard: ISO/IEC 20000 Service Management
---

# Deployment Guide

## [Home](../README.md) > [Operations](./README.md) > OPS-001

---

# Deployment Guide

# Team Pomodoro Timer (Focus Mate)

**문서 버전**: 1.0
**작성일**: 2025-12-04

---

## 목차

1. [개요](#1-개요)
2. [사전 요구사항](#2-사전-요구사항)
3. [로컬 배포](#3-로컬-배포)
4. [프로덕션 배포](#4-프로덕션-배포)
5. [환경 변수](#5-환경-변수)
6. [헬스체크](#6-헬스체크)
7. [모니터링](#7-모니터링)
8. [롤백 전략](#8-롤백-전략)

---

## 1. 개요

Focus Mate는 Docker Compose를 사용하여 단일 명령으로 배포할 수 있도록 설계되었습니다.

**배포 환경**:

- 개발 환경: Docker Compose (로컬)
- 프로덕션 환경: Docker Compose 또는 Kubernetes (선택)

---

## 2. 사전 요구사항

### 필수 요구사항

- **Docker**: 20.10 이상
- **Docker Compose**: 2.0 이상
- **디스크 공간**: 최소 2GB (이미지 포함)

### 선택 요구사항

- **도메인**: 프로덕션 배포 시 (예: focusmate.example.com)
- **SSL 인증서**: HTTPS 사용 시 (Let's Encrypt 권장)
- **모니터링**: Prometheus, Grafana (선택)

---

## 3. 로컬 배포

### 3.1 빠른 시작

```bash
# 저장소 클론
git clone https://github.com/your-org/focus-mate.git
cd focus-mate

# 환경 변수 설정 (선택)
cp .env.example .env
# .env 파일 편집

# 전체 스택 실행
docker-compose up --build

# 백그라운드 실행
docker-compose up -d --build
```

### 3.2 서비스 확인

```bash
# 서비스 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f backend
docker-compose logs -f frontend

# 서비스 중지
docker-compose down

# 볼륨 포함 삭제
docker-compose down -v
```

### 3.3 접속 URL

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 4. 프로덕션 배포

### 4.1 Docker Compose 배포

#### 4.1.1 환경 변수 설정

```bash
# .env.production 파일 생성
cat > .env.production << EOF
# Backend
BACKEND_PORT=8000
DATABASE_URL=sqlite:///./data/focusmate.db
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=https://focusmate.example.com

# Frontend
VITE_API_URL=https://api.focusmate.example.com
VITE_WS_URL=wss://api.focusmate.example.com

# Environment
ENVIRONMENT=production
DEBUG=false
EOF
```

#### 4.1.2 배포 실행

```bash
# 프로덕션 환경 변수 사용
docker-compose --env-file .env.production up -d --build

# 또는 docker-compose.prod.yml 사용
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

#### 4.1.3 Nginx 리버스 프록시 설정 (선택)

```nginx
# /etc/nginx/sites-available/focusmate
server {
    listen 80;
    server_name focusmate.example.com;

    # HTTPS로 리다이렉트
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name focusmate.example.com;

    ssl_certificate /etc/letsencrypt/live/focusmate.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/focusmate.example.com/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4.2 Kubernetes 배포 (선택)

```yaml
# k8s/deployment.yaml 예시
apiVersion: apps/v1
kind: Deployment
metadata:
  name: focusmate-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: focusmate-backend
  template:
    metadata:
      labels:
        app: focusmate-backend
    spec:
      containers:
        - name: backend
          image: focusmate/backend:latest
          ports:
            - containerPort: 8000
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: focusmate-secrets
                  key: database-url
---
apiVersion: v1
kind: Service
metadata:
  name: focusmate-backend
spec:
  selector:
    app: focusmate-backend
  ports:
    - port: 80
      targetPort: 8000
  type: LoadBalancer
```

---

## 5. 환경 변수

### 5.1 Backend 환경 변수

| 변수명         | 설명                  | 기본값                          | 필수 |
| :------------- | :-------------------- | :------------------------------ | :--- |
| `DATABASE_URL` | 데이터베이스 연결 URL | `sqlite:///./data/focusmate.db` | ❌   |
| `SECRET_KEY`   | JWT 시크릿 키 (v1.1)  | -                               | ❌   |
| `CORS_ORIGINS` | 허용된 CORS 오리진    | `*`                             | ❌   |
| `DEBUG`        | 디버그 모드           | `false`                         | ❌   |
| `LOG_LEVEL`    | 로그 레벨             | `INFO`                          | ❌   |

### 5.2 Frontend 환경 변수

| 변수명         | 설명           | 기본값                  | 필수 |
| :------------- | :------------- | :---------------------- | :--- |
| `VITE_API_URL` | 백엔드 API URL | `http://localhost:8000` | ❌   |
| `VITE_WS_URL`  | WebSocket URL  | `ws://localhost:8000`   | ❌   |

### 5.3 환경 변수 설정 예시

```bash
# .env 파일
DATABASE_URL=sqlite:///./data/focusmate.db
SECRET_KEY=your-secret-key-change-in-production
CORS_ORIGINS=http://localhost:3000,https://focusmate.example.com
DEBUG=false
LOG_LEVEL=INFO

VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

---

## 6. 헬스체크

### 6.1 Backend 헬스체크

```bash
# 헬스체크 엔드포인트
curl http://localhost:8000/health

# 응답 예시
{
  "status": "healthy",
  "timestamp": "2025-12-04T10:00:00Z",
  "version": "1.0.0"
}
```

### 6.2 Docker 헬스체크

```yaml
# docker-compose.yml
services:
  backend:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 30s
```

### 6.3 헬스체크 스크립트

```bash
# scripts/health_check.sh 사용
./scripts/health_check.sh

# 또는 수동 실행
curl -f http://localhost:8000/health || exit 1
```

---

## 7. 모니터링

### 7.1 로그 모니터링

```bash
# 실시간 로그 확인
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f backend

# 로그 파일 저장
docker-compose logs > logs/$(date +%Y%m%d).log
```

### 7.2 메트릭 수집 (선택)

**Prometheus 설정**:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: "focusmate-backend"
    static_configs:
      - targets: ["backend:8000"]
```

**Grafana 대시보드**:

- API 응답 시간
- WebSocket 연결 수
- 활성 방 수
- 에러율

---

## 8. 롤백 전략

### 8.1 Docker 이미지 태깅

```bash
# 특정 버전 태깅
docker tag focusmate/backend:latest focusmate/backend:v1.0.0

# 이전 버전으로 롤백
docker-compose down
docker-compose up -d --image focusmate/backend:v0.9.0
```

### 8.2 데이터베이스 백업

```bash
# SQLite 백업
cp data/focusmate.db data/focusmate.db.backup

# 복원
cp data/focusmate.db.backup data/focusmate.db
```

### 8.3 롤백 절차

1. **서비스 중지**

   ```bash
   docker-compose down
   ```

2. **이전 버전으로 전환**

   ```bash
   git checkout v0.9.0
   docker-compose up -d --build
   ```

3. **데이터베이스 복원** (필요 시)

   ```bash
   cp data/focusmate.db.backup data/focusmate.db
   ```

4. **헬스체크 확인**
   ```bash
   ./scripts/health_check.sh
   ```

---

## 9. 트러블슈팅

자세한 내용은 [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)를 참조하세요.

### 일반적인 문제

1. **포트 충돌**

   ```bash
   # 포트 사용 확인
   lsof -i :8000
   lsof -i :3000

   # docker-compose.yml에서 포트 변경
   ```

2. **데이터베이스 권한**

   ```bash
   # SQLite 파일 권한 확인
   ls -la data/focusmate.db
   chmod 666 data/focusmate.db
   ```

3. **메모리 부족**
   ```bash
   # Docker 메모리 제한 확인
   docker stats
   ```

---

## 10. 보안 체크리스트

배포 전 확인사항:

- [ ] 환경 변수에 민감한 정보 포함 여부 확인
- [ ] `DEBUG=false` 설정
- [ ] `SECRET_KEY` 강력한 값으로 변경
- [ ] CORS 오리진 제한 설정
- [ ] HTTPS 사용 (프로덕션)
- [ ] 데이터베이스 백업 설정
- [ ] 로그 레벨 적절히 설정
- [ ] 방화벽 규칙 확인

---

## 참조

- [CONTRIBUTING.md](./CONTRIBUTING.md): 개발 환경 설정
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md): 문제 해결 가이드
- [ARCHITECTURE.md](./ARCHITECTURE.md): 시스템 아키텍처

---

**문서 끝**
