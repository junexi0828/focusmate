# Docker 개념 완벽 가이드: NAS 배포 및 운영

Docker의 기본 개념부터 NAS 배포 워크플로우, 운영 및 문제 해결 방법까지 상세히 다룹니다.

## 개요

이 문서는 Docker를 "완전히 포장된 이사 박스"에 비유하여 개념을 설명하고, Synology NAS 환경에서의 효율적인 배포 전략(로컬 빌드 vs NAS 빌드)과 실전 운영 방법을 안내합니다.

## 1. Docker란? (비유로 설명)

### Docker = 완전히 포장된 이사 박스 📦

기존 배포 방식과 Docker 배포 방식의 가장 큰 차이는 "환경의 포함 여부"입니다.

**일반 배포 (NAS에서 직접 실행):**
- 📂 **프로젝트 폴더**만 존재
- ├── 🐍 Python 3.13 설치 필요 (수동)
- ├── 📚 라이브러리 설치 필요 (수동)
- ├── ⚙️ 환경 설정 필요 (수동)
- └── ❌ Synology OS와 충돌 가능성 있음

**Docker 배포:**
- 📦 **Docker 이미지** (모든 게 포장됨)
- ├── ✅ Linux OS (표준 환경 포함)
- ├── ✅ Python 3.12 (내장됨)
- ├── ✅ 모든 라이브러리 (설치 완료됨)
- ├── ✅ 코드 (포함됨)
- └── ✅ 실행 명령 (정의됨)

## 2. 배포 방식 비교

### 방법 A: 로컬에서 빌드 → NAS로 전송 (추천! ⭐)

Mac의 강력한 성능을 활용하여 빌드 시간을 단축하고 NAS 리소스를 절약하는 방식입니다.

**Mac에서:**
1. **Docker 이미지 빌드 (약 10분)**
   ```bash
   docker build -t focusmate-backend:latest .
   ```

2. **이미지를 파일로 저장 (약 5분)**
   ```bash
   docker save focusmate-backend:latest -o focusmate-backend.tar
   ```

3. **NAS로 전송 (약 2분)**
   ```bash
   scp focusmate-backend.tar juns@192.168.45.58:/volume1/docker/
   ```

**NAS에서:**
4. **이미지 불러오기 (약 5분)**
   ```bash
   docker load -i /volume1/docker/focusmate-backend.tar
   ```

5. **실행 (즉시)**
   ```bash
   docker-compose -f docker-compose.nas.yml up -d
   ```

**장점:**
- ✅ Mac의 빠른 CPU로 빌드 (10분 vs NAS 30분)
- ✅ 네트워크 대역폭 절약
- ✅ NAS 리소스 부하 최소화

### 방법 B: NAS에서 직접 빌드

NAS에서 소스코드를 받아 직접 빌드하는 방식입니다.

**NAS에서:**
1. **Git으로 코드 받기**
   ```bash
   git pull
   ```

2. **빌드 (약 30분 소요)**
   ```bash
   docker build -t focusmate-backend:latest .
   ```

3. **실행**
   ```bash
   docker-compose -f docker-compose.nas.yml up -d
   ```

**단점:**
- ❌ DS223j CPU 성능 한계로 빌드 속도가 매우 느림
- ❌ 빌드 중 NAS의 다른 작업 성능 저하 발생

## 3. Docker 실행 후 조작 방법

🎯 **핵심**: Docker는 "실행 중인 작은 컴퓨터"입니다.

### 구조도

```text
┌─────────────────────────────────────────┐
│  NAS (Synology OS)                      │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │ Docker Container (Linux)          │  │
│  │                                   │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │ FocusMate Backend           │  │  │
│  │  │ - Python 3.12               │  │  │
│  │  │ - FastAPI                   │  │  │
│  │  │ - psycopg3                  │  │  │
│  │  │ - Redis                     │  │  │
│  │  └─────────────────────────────┘  │  │
│  │                                   │  │
│  │  실행 중: uvicorn app.main:app    │  │
│  └───────────────────────────────────┘  │
│                                         │
│  포트 8000 → 외부 접속                  │
└─────────────────────────────────────────┘
```

### 🛠️ Docker 조작 명령어 모음

#### 기본 조작

1. **컨테이너 시작/중지/재시작**
   ```bash
   docker-compose -f docker-compose.nas.yml up -d     # 백그라운드 시작
   docker-compose -f docker-compose.nas.yml down      # 전체 중지 및 삭제
   docker-compose -f docker-compose.nas.yml restart   # 재시작
   ```

2. **로그 확인 (실시간)**
   ```bash
   docker-compose -f docker-compose.nas.yml logs -f backend
   docker-compose -f docker-compose.nas.yml logs -f redis
   ```

3. **상태 확인**
   ```bash
   docker-compose -f docker-compose.nas.yml ps        # 실행 중인 컨테이너 목록
   docker stats                                       # CPU/메모리 사용량
   ```

#### 컨테이너 안으로 "들어가기"

백엔드 컨테이너에 Bash로 접속하여 마치 SSH로 서버에 들어간 것처럼 작업할 수 있습니다.

```bash
docker exec -it focusmate-backend bash
```

**내부에서 할 수 있는 작업:**
```bash
root@container:/app# ls -la                    # 파일 목록 확인
root@container:/app# cat app/main.py           # 코드 내용 확인
root@container:/app# python -c "import psycopg" # Python 패키지/코드 테스트
root@container:/app# ps aux                    # 실행 중인 프로세스 확인
root@container:/app# exit                      # 컨테이너에서 나가기
```

#### 파일 복사 (컨테이너 ↔ 호스트)

```bash
# NAS → 컨테이너 (설정 파일 반영 등)
docker cp /volume1/config/new.env focusmate-backend:/app/.env

# 컨테이너 → NAS (로그 파일 추출 등)
docker cp focusmate-backend:/app/logs/app.log /volume1/logs/
```

#### 명령 실행 (들어가지 않고)

```bash
docker exec focusmate-backend python -m alembic upgrade head  # DB 마이그레이션 실행
docker exec focusmate-backend pip list                        # 설치된 패키지 목록 확인
docker exec focusmate-backend cat /app/.env                   # 환경 변수 확인
```

## 4. 실전 워크플로우 (Hybrid Mode: Code Sync + Docker Env)

우리는 **"Hybrid 방식"**을 사용합니다.
- **환경(Python, OS)**: Docker 이미지가 담당 (변경 불필요)
- **코드(Source)**: NAS의 폴더를 직접 마운트하여 사용 (rsync로 즉시 변경)

이 방식은 **매번 이미지를 빌드/전송할 필요가 없어** 개발 속도가 매우 빠릅니다.

### Step 1: 초기 1회 셋업 (이미지만 전송)

```bash
# Mac에서:
cd backend
docker build -t focusmate-backend:latest .
docker save focusmate-backend:latest -o focusmate-backend.tar
scp focusmate-backend.tar juns@192.168.45.58:/volume1/docker/

# NAS에서:
docker load -i /volume1/docker/focusmate-backend.tar
```

### Step 2: 컨테이너 실행 (docker-compose.nas.yml)

새로운 `docker-compose.nas.yml` 파일은 다음과 같은 핵심 설정을 포함합니다:
1. `volumes: /volume1/web/focusmate-backend:/app` (NAS 코드 사용)
2. `tunnel`, `log-alerter` 등 보조 컨테이너 포함

```bash
# NAS에서 실행 (최초 1회 및 설정 변경 시)
cd /volume1/web/focusmate-backend
docker-compose -f docker-compose.nas.yml up -d
```

### Step 3: 일상적인 코드 업데이트 (rsync)

코드를 수정했을 때는 **이미지를 다시 만들 필요가 없습니다.**

1. **Mac에서 코드 수정**
2. **rsync로 코드 전송** (기존 배포 스크립트 사용)
   - 코드가 NAS의 `/volume1/web/focusmate-backend`로 전송됨
   - 컨테이너는 이 폴더를 보고 있으므로 **즉시 반영됨**
3. **(필요시) 재시작**
   - Python 코드는 재시작해야 반영되므로:
   ```bash
   docker-compose -f docker-compose.nas.yml restart backend
   ```
   *(단, HTML/CSS나 정적 파일은 재시작 없이도 바로 반영됩니다!)*

---

## 5. 자주 쓰는 명령어 치트시트

### === 주요 조작 ===
```bash
# 전체 시작 (백엔드 + 터널 + 알림)
docker-compose -f docker-compose.nas.yml up -d

# 백엔드만 재시작 (코드 배포 후)
docker-compose -f docker-compose.nas.yml restart backend

# 전체 중지
docker-compose -f docker-compose.nas.yml down
```

### === 상태 확인 ===
```bash
# 컨테이너 상태 (4개 서비스가 모두 보여야 함)
docker-compose -f docker-compose.nas.yml ps

# 로그 확인 (백엔드)
docker-compose -f docker-compose.nas.yml logs -f backend

# 로그 확인 (터널)
docker-compose -f docker-compose.nas.yml logs -f tunnel
```

---

## 6. Q&A: 이미지가 바뀌어야 할 때는?

코드가 아니라 **"환경"**이 바뀔 때만 이미지를 다시 빌드합니다.

**Q: 언제 이미지를 다시 만드나요?**
- `requirements.txt`에 새 패키지를 추가했을 때
- Python 버전을 3.12에서 3.13으로 올릴 때
- Linux 시스템 패키지를 추가로 설치해야 할 때

이때만 **Step 1(빌드 & 전송) → Step 2(재생성)** 과정을 거치면 됩니다.
그 외 99%의 프로그래밍 작업은 **Step 3(rsync & restart)**만 반복하면 됩니다.

