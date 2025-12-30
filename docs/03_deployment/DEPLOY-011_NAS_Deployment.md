# 시놀로지 NAS 백엔드 배포 가이드

DS223j (Docker 미지원) 모델에서 Python 백엔드 실행하기

## 개요

시놀로지 NAS에서 백엔드를 실행하고 Cloudflare Tunnel로 연결하는 방법입니다.

### 아키텍처

```
사용자 → https://eieconcierge.com (Vercel 프론트엔드)
         ↓ API 요청
         https://api.eieconcierge.com 또는 랜덤 URL (Cloudflare Tunnel)
         ↓ 터널링
         시놀로지 NAS:8000 (Python 백엔드)
```

## DNS 필요 여부

**DNS는 선택사항입니다:**

1. **DNS 사용 (커스텀 도메인)**

   - `api.eieconcierge.com` 같은 깔끔한 주소 사용
   - Cloudflare DNS에서 CNAME 레코드 설정 필요

2. **DNS 없이 사용 (랜덤 URL)**
   - Cloudflare Tunnel이 자동으로 `https://random-name.trycloudflare.com` 제공
   - DNS 설정 불필요, 바로 사용 가능

## 시놀로지 NAS 설정

### 1. Python 설치 (DS223j)

DS223j는 Docker를 지원하지 않으므로 Python을 직접 설치합니다.

#### 방법 1: 시놀로지 Python3 패키지 (권장)

1. **Package Center 열기**

   - DSM → Package Center

2. **Python 3 설치**
   - 검색: "Python 3"
   - SynoCommunity 또는 공식 Python 3 패키지 설치
   - 설치 경로: `/volume1/@appstore/python3` 또는 `/usr/local/python3`

#### 방법 2: SSH로 직접 설치

```bash
# SSH 접속 (관리자 권한)
ssh admin@your-nas-ip

# Python 3 확인
python3 --version

# 없으면 설치 (시놀로지 버전에 따라 다름)
# DSM 7.x: 이미 Python 3.8+ 포함되어 있을 수 있음
```

### 2. 프로젝트 파일 복사

#### 방법 1: File Station 사용

1. File Station에서 `web` 또는 원하는 공유 폴더 선택
2. `focusmate-backend` 폴더 생성
3. 로컬 컴퓨터에서 백엔드 파일들을 복사

#### 방법 2: rsync 사용 (SSH)

```bash
# 로컬 컴퓨터에서 실행
rsync -avz --exclude 'venv' --exclude '__pycache__' \
  /Users/juns/code/personal/notion/juns_workspace/FocusMate/backend/ \
  admin@your-nas-ip:/volume1/web/focusmate-backend/
```

### 3. 가상환경 생성 및 의존성 설치

```bash
# SSH 접속
ssh admin@your-nas-ip

# 프로젝트 디렉토리로 이동
cd /volume1/web/focusmate-backend

# Python 3 경로 확인
which python3
# 또는
/usr/local/python3/bin/python3 --version

# 가상환경 생성 (Python 3 경로 사용)
/usr/local/python3/bin/python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# pip 업그레이드
pip install --upgrade pip

# 의존성 설치
pip install -r requirements.txt
```

### 4. 환경 변수 설정

```bash
# .env 파일 생성
cd /volume1/web/focusmate-backend
nano .env
```

`.env` 파일 내용:

```bash
# Database (Supabase 또는 외부 PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# CORS (Vercel 도메인 포함)
CORS_ORIGINS=https://eieconcierge.com,https://focusmate-*.vercel.app,http://localhost:3000

# 기타 설정
APP_ENV=production
SECRET_KEY=your-secret-key-here
# ... 나머지 설정
```

### 5. 백엔드 실행 스크립트 확인

**NAS 프로덕션 스크립트** `backend/start-nas.sh` 스크립트가 rsync를 통해 NAS에 자동으로 동기화됩니다.

스크립트 위치: `/volume1/web/focusmate-backend/start-nas.sh`

**수동으로 실행 권한 부여 (필요한 경우):**

```bash
chmod +x /volume1/web/focusmate-backend/start-nas.sh
```

**스크립트 기능:**

- 가상환경 자동 활성화
- uvicorn으로 백엔드 실행 (프로덕션 모드)
- 로그 파일 자동 생성 (`logs/app.log`)
- PID 파일 생성 (`app.pid`)
- 백그라운드 실행

### 6. 자동 시작 설정 (Task Scheduler)

1. **DSM → Control Panel → Task Scheduler**
2. **Create → Scheduled Task → User-defined script**
3. 설정:
   - **Task**: `FocusMate Backend`
   - **User**: `root` (또는 관리자 계정)
   - **Schedule**: `Boot-up` (부팅 시 자동 시작)
   - **Run command**:
     ```bash
     /volume1/web/focusmate-backend/start-nas.sh
     ```
4. **Save** 클릭

**수동 실행:**

```bash
# SSH 접속
ssh juns@192.168.45.58

# 백엔드 + Cloudflare Tunnel 자동 실행
cd /volume1/web/focusmate-backend
./start-nas.sh

# 로그 확인
tail -f logs/app.log                    # 백엔드 로그
tail -f /volume1/web/cloudflare-tunnel/tunnel.log  # Tunnel 로그

# 중지 (백엔드 + Tunnel 모두 중지)
./stop-nas.sh
```

**개별 실행 (백엔드만):**

```bash
cd /volume1/web/focusmate-backend
# start-nas.sh는 백엔드와 Tunnel을 함께 시작하므로,
# 백엔드만 실행하려면 직접 uvicorn 실행
```

**개별 실행 (Cloudflare Tunnel만):**

```bash
cd /volume1/web/cloudflare-tunnel
nohup cloudflared tunnel run focusmate-backend > tunnel.log 2>&1 &
echo $! > tunnel.pid
```

## Cloudflare Tunnel 설정 (NAS에서 실행)

### 1. cloudflared 설치 (NAS)

DS223j는 ARM 프로세서이므로 ARM용 바이너리가 필요합니다.

```bash
# SSH 접속
ssh admin@your-nas-ip

# cloudflared 다운로드 (ARM64)
cd /tmp
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64
mv cloudflared-linux-arm64 /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared

# 확인
cloudflared --version
```

### 2. Tunnel 생성 및 실행

#### Zero Trust 대시보드에서 Tunnel 생성

**⚠️ 중요: 기존 macOS용 Tunnel(`focusmate-backend`)과 별도로 NAS용 Tunnel을 생성하거나 하나만 실행.**

1. https://one.dash.cloudflare.com/ 접속
2. Networks → Tunnels → Create a tunnel
3. Tunnel 이름: `focusmate-nas-backend` (기존 `focusmate-backend`와 구분)
4. Connector: `cloudflared` 선택
5. 설치 명령어 복사

**왜 별도 Tunnel이 필요한가요?**

- 같은 Tunnel을 여러 곳에서 실행하면 충돌 발생
- macOS용: 로컬 개발용 (`focusmate-backend`)
- NAS용: 프로덕션 서버용 (`focusmate-nas-backend`)

#### NAS에서 Tunnel 실행

**방법 1: 토큰으로 실행 (간단)**

```bash
# Zero Trust 대시보드에서 복사한 명령어 실행
cloudflared tunnel run focusmate-nas-backend
```

**방법 2: 설정 파일 사용 (권장, 자동 시작용)**

```bash
# 설정 파일 위치
mkdir -p /volume1/web/cloudflare-tunnel
cd /volume1/web/cloudflare-tunnel

# Tunnel 생성 (처음 한 번만)
cloudflared tunnel create focusmate-nas-backend

# 설정 파일 생성
cloudflared tunnel route dns focusmate-nas-backend api.eieconcierge.com
```

### 3. Public Hostname 설정

**⚠️ 중요: NAS용 Tunnel에 별도의 Public Hostname을 설정해야 합니다.**

Zero Trust 대시보드에서:

1. **NAS용 Tunnel 선택** (`focusmate-nas-backend`) → **Public Hostname** 탭
2. **Add a public hostname**
3. 설정:
   - **Subdomain**: `api-nas` 또는 `api` (기존 macOS Tunnel과 구분)
   - **Domain**: `eieconcierge.com` (Cloudflare에서 관리하는 도메인)
   - **Service**: `http://localhost:8000`
4. **Save hostname**

**옵션 1: 별도 서브도메인 사용 (권장)**

- `api-nas.eieconcierge.com` → NAS 백엔드
- `api.eieconcierge.com` → macOS 개발용 (또는 제거)

**옵션 2: 같은 서브도메인 사용**

- macOS Tunnel을 중지하고 NAS Tunnel만 사용
- `api.eieconcierge.com` → NAS 백엔드

### 4. DNS 레코드 (커스텀 도메인 사용 시)

**Cloudflare Tunnel이 자동으로 생성합니다:**

- Cloudflare 대시보드 → DNS → Records
- `api.eieconcierge.com` → CNAME → `[tunnel-id].cfargotunnel.com` 자동 생성됨

**수동 설정이 필요한 경우:**

1. Cloudflare 대시보드 → DNS
2. **Add record**
3. 설정:
   - **Type**: CNAME
   - **Name**: `api`
   - **Target**: Tunnel ID (Zero Trust 대시보드에서 확인)
   - **Proxy status**: Proxied (주황색 구름)

### 5. Tunnel 자동 시작 설정

```bash
# 시작 스크립트 생성
nano /usr/local/bin/cloudflare-tunnel-start.sh
```

```bash
#!/bin/bash
cd /volume1/web/cloudflare-tunnel
nohup cloudflared tunnel run focusmate-nas-backend > /volume1/web/cloudflare-tunnel/tunnel.log 2>&1 &
echo $! > /volume1/web/cloudflare-tunnel/tunnel.pid
```

Task Scheduler에 등록:

- **Boot-up** 스케줄로 설정

### 6. Tunnel 수동 실행/중지

**Tunnel 실행:**

```bash
# 방법 1: Tunnel 이름으로 실행 (권장)
cd /volume1/web/cloudflare-tunnel
nohup cloudflared tunnel run focusmate-backend > tunnel.log 2>&1 &
echo $! > tunnel.pid

# 방법 2: 토큰으로 실행 (Zero Trust 대시보드에서 토큰 복사)
cloudflared tunnel run --token [토큰] > tunnel.log 2>&1 &
```

**Tunnel 중지:**

```bash
# PID 파일이 있는 경우
PID=$(cat /volume1/web/cloudflare-tunnel/tunnel.pid)
kill $PID

# PID 파일이 없는 경우 (프로세스 직접 찾기)
PID=$(ps aux | grep '[c]loudflared tunnel' | awk '{print $2}' | head -1)
kill $PID

# 강제 종료 (필요시)
kill -9 $PID
```

**Tunnel 상태 확인:**

```bash
# 실행 중인 Tunnel 확인
ps aux | grep cloudflared

# 로그 확인
tail -f /volume1/web/cloudflare-tunnel/tunnel.log
```

## 설정 체크리스트

### NAS 설정

- [ ] Python 3 설치 완료
- [ ] 프로젝트 파일 복사 완료
- [ ] 가상환경 생성 및 의존성 설치 완료
- [ ] `.env` 파일 설정 완료
- [ ] 백엔드 실행 스크립트 생성 완료
- [ ] Task Scheduler에 자동 시작 등록

### Cloudflare Tunnel

- [ ] cloudflared 설치 완료 (NAS)
- [ ] Tunnel 생성 완료
- [ ] Public Hostname 설정 완료
- [ ] DNS 레코드 확인 (커스텀 도메인 사용 시)
- [ ] Tunnel 자동 시작 설정 완료

### 백엔드 설정

- [ ] `.env`의 `CORS_ORIGINS`에 Vercel 도메인 포함
- [ ] 데이터베이스 연결 확인 (Supabase 또는 외부 PostgreSQL)

## 테스트

### 1. 백엔드 실행 확인

```bash
# SSH 접속
ssh admin@your-nas-ip

# 백엔드 수동 실행
cd /volume1/web/focusmate-backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 다른 터미널에서 테스트
curl http://localhost:8000/health
```

### 2. Cloudflare Tunnel 확인

```bash
# Tunnel 실행 확인
ps aux | grep cloudflared

# 로그 확인
tail -f /volume1/web/cloudflare-tunnel/tunnel.log
```

### 3. 외부 접속 테스트

```bash
# Cloudflare Tunnel URL로 테스트
curl https://api.eieconcierge.com/health
# 또는
curl https://random-name.trycloudflare.com/health
```

## 보안 고려사항

### 1. 방화벽 설정

- NAS 방화벽에서 포트 8000은 로컬 접근만 허용
- Cloudflare Tunnel은 외부 포트 노출 불필요

### 2. 사용자 권한

- 백엔드 실행은 최소 권한 사용자로 실행
- root 권한은 Task Scheduler에서만 사용

### 3. 로그 관리

```bash
# 로그 로테이션 설정
nano /etc/logrotate.d/focusmate
```

```
/volume1/web/focusmate-backend/logs/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

## 문제 해결

### 문제: Python을 찾을 수 없음

```bash
# Python 경로 확인
which python3
/usr/local/python3/bin/python3 --version

# 가상환경 생성 시 전체 경로 사용
/usr/local/python3/bin/python3 -m venv venv
```

### 문제: 포트 8000이 이미 사용 중

```bash
# 포트 사용 확인
netstat -tuln | grep 8000

# 프로세스 종료
kill $(cat /volume1/web/focusmate-backend/app.pid)
```

### 문제: Cloudflare Tunnel 연결 실패

```bash
# Tunnel 로그 확인
tail -f /volume1/web/cloudflare-tunnel/tunnel.log

# Tunnel 재시작
kill $(cat /volume1/web/cloudflare-tunnel/tunnel.pid)
/usr/local/bin/cloudflare-tunnel-start.sh
```

## 최적화 팁

1. **리소스 모니터링**

   - DSM → Resource Monitor에서 CPU/메모리 사용량 확인
   - DS223j는 저사양이므로 모니터링 중요

2. **로그 관리**

   - 로그 파일 크기 제한
   - 정기적인 로그 정리

3. **백업**
   - `.env` 파일과 설정 파일 정기 백업
   - Hyper Backup 사용 권장

## 참고 자료

- [시놀로지 Python 패키지](https://synocommunity.com/)
- [Cloudflare Tunnel ARM 설치](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/)
- [시놀로지 Task Scheduler 가이드](https://kb.synology.com/en-global/DSM/help/DSM/AdminCenter/task_scheduler_desc)
