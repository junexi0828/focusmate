### 1. 타입 힌트 문법 사용 현황

- Python 3.10+ 전용 문법 (`str | None`, `list[str] | None` 등): 약 2,410개 라인
- 기존 `Union`, `Optional` 사용: 88개 파일
- 프로젝트 요구사항: `requires-python = ">=3.12"` (pyproject.toml)

결론: Python 3.9 사용 시 약 2,410개 라인 수정 필요.

### 2. Python 버전별 호환성

| Python 버전 | `str   | None` 문법           | 코드 수정 필요                                 | 비고 |
| ----------- | ------ | -------------------- | ---------------------------------------------- | ---- |
| 3.9 이하    | 불가능 | 약 2,410개 라인 수정 | `Union[str, None]` 또는 `Optional[str]`로 변경 |
| 3.10+       | 가능   | 수정 불필요          | 현재 코드 그대로 사용 가능                     |
| 3.12+       | 가능   | 수정 불필요          | 프로젝트 요구사항 충족                         |

### 3. 시놀로지 NAS 설치 방법 비교

| 방법                     | DS223j 가능 여부 | Python 버전 | 코드 수정                 | 비고                         |
| ------------------------ | ---------------- | ----------- | ------------------------- | ---------------------------- |
| 시놀로지 공식 Python 3.9 | 가능             | 3.9         | 약 2,410개 라인 수정 필요 | 가장 안정적, 빠름            |
| Miniconda                | 가능             | 3.11/3.12   | 수정 불필요               | 바이너리 설치, 컴파일 불필요 |
| pyenv                    | 어려움           | 3.14        | 수정 불필요               | 컴파일 필요, 하드웨어 한계   |
| Docker                   | 불가능           | -           | -                         | DS223j 미지원                |

### 4. 권장 사항

#### 옵션 1: Miniconda로 Python 3.11/3.12 설치 (권장)

- 장점: 코드 수정 없음, 바이너리 설치로 빠름
- 단점: Miniconda 설치 필요
- 작업량: Miniconda 설치만

#### 옵션 2: 시놀로지 공식 Python 3.9 사용

- 장점: 안정적, 빠름, 추가 설치 불필요
- 단점: 약 2,410개 라인 수정 필요
- 작업량: 대규모 코드 수정

### 5. 최종 권장사항

Miniconda로 Python 3.11 설치를 권장합니다.

## 시놀로지 NAS(DS223j) Python 백엔드 24/7 배포 가이드 (최종 수정본)

이 문서는 Docker를 지원하지 않는 **Synology DS223j (ARM64)** 모델에서 최신 Python 백엔드를 구동하고 외부 접속을 설정하는 전체 과정을 다룹니다.

### 환경 정보

- **NAS 모델**: Synology DS223j (ARM64, Docker 미지원)
- **로컬 개발 환경**: macOS (Python 3.14.0 사용 중)
- **NAS IP**: 192.168.45.58 (사용자 계정: `juns`)
- **프로젝트 경로**: `/volume1/web/focusmate-backend`
- **배포 구조**: Vercel (프론트엔드) → Cloudflare Tunnel → NAS (백엔드)

---

## 핵심 문제 및 해결 방법

### 문제 1: Python 버전 호환성

- **상황**: 로컬 코드는 Python 3.10 이상의 최신 문법(`str | None` 등)을 사용하지만, NAS 패키지 센터는 Python 3.9만 제공하여 문법 에러가 발생함.
- **제약**: DS223j는 저사양 ARM CPU라 Python 소스 빌드(pyenv 등)가 불가능에 가까움.
- **해결책**: **Miniconda**를 설치하여 NAS 시스템과 무관하게 독립적인 **Python 3.11/3.12/3.13 환경**을 구축. (바이너리 설치라 컴파일 불필요)[1]

### 문제 2: Miniconda 설치 시 `glibc` 에러

- **상황**: Miniconda 설치 스크립트가 NAS의 `glibc` 버전을 인식하지 못해 설치 실패.
- **해결책**: 가짜 `ldd` 스크립트를 만들어 설치 관리자를 속여서 설치 진행. (아래 2단계 참조)

---

## 단계별 설정 가이드

### 1단계: SSH 키 기반 접속 설정

비밀번호 입력 없이 안전하게 NAS에 접속하기 위한 필수 설정입니다.

#### 1-1. SSH 키 복사 및 권한 설정

```bash
# 1. 로컬(맥북)에서 실행: 키 복사
ssh-copy-id juns@192.168.45.58

# 2. NAS 접속
ssh juns@192.168.45.58

# 3. 권한 설정 (시놀로지 보안 정책상 필수)
sudo chmod 755 /volume1/homes/juns # 홈 폴더 권한
chmod 700 /volume1/homes/juns/.ssh # .ssh 폴더 권한
chmod 600 /volume1/homes/juns/.ssh/authorized_keys # authorized_keys 권한
sudo chown -R juns:users /volume1/homes/juns/.ssh #

SSH 키 로그인이 안 될 때
sshd_config에서 PubkeyAuthentication yes 확인

```

#### 1-2. SSH 데몬 설정 수정

```bash
sudo vi /etc/ssh/sshd_config
# [수정] 주석(#) 제거: PubkeyAuthentication yes

# SSH 서비스 재시작
sudo synosystemctl restart sshd
```

---

### 2단계: Miniconda 설치 (트러블슈팅 포함)

NAS에 `ldd` 명령어가 없어 설치가 막히는 문제를 우회하여 설치합니다.

#### 2-1. 가짜 `ldd` 생성 (설치 스크립트 우회용)

```bash
cd ~
echo -e '#!/bin/sh\necho "ldd (GNU libc) 2.28"' > ldd
chmod +x ldd
export PATH=$HOME:$PATH
```

#### 2-2. Miniconda 설치 및 환경 설정

```bash
# 1. 설치 파일 다운로드
cd /tmp
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh

# 2. 설치 실행 (가짜 ldd 덕분에 통과됨)
bash Miniconda3-latest-Linux-aarch64.sh -b -p /volume1/web/miniconda3

# 3. 쉘 초기화
/volume1/web/miniconda3/bin/conda init bash
source ~/.bashrc

# 4. (중요) 설치 후 임시 파일 삭제
rm ~/ldd /tmp/Miniconda3-latest-Linux-aarch64.sh
```

#### 2-3. Python 3.13 가상환경 구축

```bash
cd /volume1/web/focusmate-backend

# 약관 동의 (에러 방지)
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main

# 가상환경 생성 및 활성화
conda create -n focusmate_env python=3.13 -y
conda activate focusmate_env

# 패키지 설치
pip upgrade
pip install -r requirements.txt
```

---

### 3단계: 백엔드 서버 자동 시작 설정 (Task Scheduler)

#### 3-1. 실행 스크립트 확인

프로젝트에 이미 `start-nas.sh` 스크립트가 포함되어 있습니다. 이 스크립트는:

- Miniconda 환경 자동 활성화
- 백엔드 서버 시작 (uvicorn with workers)
- Cloudflare Tunnel 자동 시작 (토큰 또는 config.yml 방식)
- PID 파일 생성 및 로그 관리

**스크립트 위치**: `/volume1/web/focusmate-backend/start-nas.sh`

**실행 권한 확인**:

```bash
chmod +x /volume1/web/focusmate-backend/start-nas.sh
```

#### 3-2. 중지 스크립트 확인

프로젝트에 `stop-nas.sh` 스크립트가 포함되어 있습니다. 이 스크립트는:

- 백엔드 프로세스 그룹 전체 종료 (모든 워커 포함)
- Cloudflare Tunnel 종료
- PID 파일 정리

**스크립트 위치**: `/volume1/web/focusmate-backend/stop-nas.sh`

**실행 권한 확인**:

```bash
chmod +x /volume1/web/focusmate-backend/stop-nas.sh
```

#### 3-3. 부팅 시 자동 실행 등록

- **DSM 제어판 > 작업 스케줄러 > 생성 > 트리거된 작업 > 사용자 정의 스크립트**
- 이벤트: `부트업`, 사용자: `admin`
- 스크립트: `/volume1/web/focusmate-backend/start-nas.sh`

**수동 실행/중지**:

```bash
# 시작
/volume1/web/focusmate-backend/start-nas.sh

# 중지
/volume1/web/focusmate-backend/stop-nas.sh
```

---

### 4단계: Cloudflare Tunnel 설정

외부에서 `api.eieconcierge.com`으로 접속 시 NAS의 8000번 포트로 연결해주는 설정입니다.

**⚠️ 주의사항:**

- 같은 Tunnel을 macOS와 NAS에서 **동시에 실행하면 충돌** 발생
- 한 번에 **하나의 장치에서만** Tunnel 실행
- NAS에서 사용할 때는 macOS의 Tunnel을 중지해야 함

#### 4-1. `cloudflared` 설치 (NAS)

```bash
cd /tmp
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64
sudo mv cloudflared-linux-arm64 /usr/local/bin/cloudflared
sudo chmod +x /usr/local/bin/cloudflared
cloudflared --version
```

#### 4-2. Tunnel 설정 방법 (두 가지 중 선택)

**방법 A: 토큰 방식 (권장 - 간단하고 안정적)**

1. **터널 토큰 생성** (로컬 macOS에서):

   ```bash
   # Cloudflare Zero Trust 대시보드에서 토큰 복사
   # 또는 기존 터널의 토큰 사용
   ```

2. **NAS의 `.env` 파일에 토큰 추가**:

   ```bash
   # /volume1/web/focusmate-backend/.env 파일에 추가
   CLOUDFLARE_TUNNEL_TOKEN=eyJhIjoiZWQyNzU0OGI3ZjNlNTUxY2Y0ZjliM2M4YmFmMzk0MmUiLCJ0IjoiMDI0MWY0MTMtMDBmNS00NmY2LWE3MDUtZjU1ZGI1MjdjYjc4IiwicyI6IlltTTFaVFEwWm1VdFlXSmpZUzAwTldJeExUaG1ZMlF0TnpCbVptWTRNVFJrTkRRNSJ9
   ```

3. **`start-nas.sh`가 자동으로 토큰을 읽어서 Tunnel 시작**
   - 토큰이 `.env`에 있으면 자동으로 사용됨
   - 별도 스크립트 작성 불필요

**방법 B: config.yml 방식 (백업 방법)**

1. **터널 생성 및 로그인** (NAS에서):

   ```bash
   # Cloudflare 로그인
   cloudflared tunnel login

   # 터널 생성 (이미 존재하면 생략)
   cloudflared tunnel create focusmate-backend
   ```

2. **DNS 라우팅 설정**:

   ```bash
   cloudflared tunnel route dns focusmate-backend api.eieconcierge.com
   ```

3. **config.yml 생성** (자동 생성됨):

   ```bash
   # ~/.cloudflared/config.yml 파일이 자동 생성됨
   cat ~/.cloudflared/config.yml
   ```

4. **JSON credentials 파일 확인**:

   ```bash
   # 터널 생성 시 JSON 파일이 생성됨
   # 예: ~/.cloudflared/{tunnel-id}.json
   ls -la ~/.cloudflared/*.json
   ```

5. **config.yml 수정 (필요시)**:

   ```yaml
   tunnel: focusmate-backend
   credentials-file: /var/services/homes/juns/.cloudflared/{tunnel-id}.json

   ingress:
     - hostname: api.eieconcierge.com
       service: http://localhost:8000
     - service: http_status:404
   ```

   **⚠️ 중요**: `credentials-file` 경로는 **절대 경로**로 지정해야 하며, Synology NAS의 실제 홈 디렉토리는 `/var/services/homes/juns`입니다.

6. **`start-nas.sh`가 자동으로 config.yml을 읽어서 Tunnel 시작**
   - 토큰이 없으면 config.yml 방식으로 자동 전환
   - JSON 파일 경로를 자동으로 수정함

#### 4-3. Tunnel 수동 실행/중지

**수동 시작**:

```bash
# 토큰 방식
cloudflared tunnel run --token "YOUR_TOKEN" > /volume1/web/cloudflare-tunnel/tunnel.log 2>&1 &

# config.yml 방식
cloudflared tunnel run focusmate-backend > /volume1/web/cloudflare-tunnel/tunnel.log 2>&1 &
```

**수동 중지**:

```bash
# PID 파일 확인
cat /volume1/web/cloudflare-tunnel/tunnel.pid

# 프로세스 종료
kill $(cat /volume1/web/cloudflare-tunnel/tunnel.pid)

# 또는 프로세스 직접 찾기
ps aux | grep cloudflared
kill <PID>
```

**상태 확인**:

```bash
# 프로세스 확인
ps aux | grep cloudflared

# 로그 확인
tail -f /volume1/web/cloudflare-tunnel/tunnel.log
```

#### 4-4. 트러블슈팅

**문제 1: `cloudflared: command not found`**

- **원인**: PATH에 `/usr/local/bin`이 포함되지 않음
- **해결**: 스크립트에 `export PATH="/usr/local/bin:$PATH"` 추가
- **확인**: `start-nas.sh`와 `stop-nas.sh`에 이미 포함되어 있음

**문제 2: `tunnel credentials file not found` (config.yml 방식)**

- **원인 1**: `credentials-file` 경로가 잘못됨

  - **해결**: 절대 경로 사용 (`/var/services/homes/juns/.cloudflared/{tunnel-id}.json`)
  - **확인**: `start-nas.sh`가 자동으로 경로 수정

- **원인 2**: JSON 파일 대신 PEM 파일(`cert.pem`)을 참조
  - **해결**: `cloudflared tunnel create`로 생성된 JSON 파일 사용
  - **참고**: `cert.pem`은 `cloudflared tunnel login`으로 생성되며, `credentials-file`에는 사용 불가

**문제 3: 홈 디렉토리 경로 불일치**

- **문제**: `~/.cloudflared/config.yml`에서 `~`가 `/home/juns`로 해석됨
- **실제 경로**: Synology NAS는 `/var/services/homes/juns` 사용
- **해결**: `start-nas.sh`가 `ACTUAL_HOME=$(eval echo ~$USER)`로 실제 경로 확인 후 자동 수정

**문제 4: Cloudflare Dashboard에서 Tunnel이 DOWN으로 표시됨**

- **원인**: DNS 라우팅이 설정되지 않았거나, Tunnel이 실제로 실행되지 않음
- **확인 사항**:
  1. `cloudflared tunnel route dns` 명령어 실행 여부
  2. Tunnel 프로세스 실행 여부: `ps aux | grep cloudflared`
  3. 로그 확인: `tail -f /volume1/web/cloudflare-tunnel/tunnel.log`
  4. 백엔드 서버 실행 여부: `curl http://localhost:8000/health`

**문제 5: 백엔드 프로세스가 완전히 종료되지 않음**

- **원인**: uvicorn이 여러 워커 프로세스(`--workers 2`)를 생성하여 메인 PID만 종료하면 워커가 남음
- **해결**: `stop-nas.sh`가 프로세스 그룹 전체(PGID)와 모든 uvicorn 워커 프로세스를 종료하도록 수정됨
- **확인**: `ps aux | grep uvicorn`으로 남은 프로세스 확인
- **수동 종료**:

  ```bash
  # 모든 uvicorn 프로세스 찾기
  ps aux | grep uvicorn

  # 프로세스 그룹 전체 종료
  kill -TERM -$(ps -p $(cat app.pid) -o pgid= | tr -d ' ')

  # 강제 종료 (필요시)
  pkill -9 -f uvicorn
  ```

**문제 6: rsync 동기화 실패 (Protocol version mismatch)**

- **원인**: macOS의 `openrsync`(protocol 29)와 NAS의 `rsync`(protocol 31) 버전 불일치
- **해결**: Homebrew `rsync` 사용

  ```bash
  # macOS에서 Homebrew rsync 설치
  brew install rsync

  # rsync 명령어에 절대 경로 사용
  /opt/homebrew/bin/rsync -avz ...
  # 또는
  /usr/local/bin/rsync -avz ...
  ```

- **확인**: `which rsync`로 경로 확인

**문제 7: `.env` 파일이 NAS에 동기화되지 않음**

- **원인**: `rsync` 명령어에 `--exclude '.env'` 옵션이 포함됨
- **해결**: `setup-nas-initial.sh`와 `.git/hooks/post-commit`에서 `.env` 제외 옵션 제거
- **확인**: NAS에서 `.env` 파일 존재 여부 확인
  ```bash
  ls -la /volume1/web/focusmate-backend/.env
  ```

**문제 8: CORS 에러 발생**

- **원인**: `.env` 파일의 `CORS_ORIGINS`에 프론트엔드 도메인이 포함되지 않음
- **해결**: `backend/.env` 파일에 다음 추가
  ```bash
  CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://eieconcierge.com,https://www.eieconcierge.com
  ```
- **확인**: 백엔드 재시작 후 브라우저 콘솔에서 CORS 에러 확인

**문제 9: Python SyntaxError (타입 힌트 문법)**

- **원인**: Python 3.9 이하에서 `str | None` 문법 미지원
- **해결**: Miniconda로 Python 3.11 이상 설치 (이 문서의 2단계 참조)
- **확인**: `python --version`으로 버전 확인

---

### 5단계: 환경 변수 설정

#### 5-1. `.env` 파일 설정

NAS의 백엔드 디렉토리에 `.env` 파일이 필요합니다. 이 파일은 Git 커밋 시 자동으로 동기화됩니다.

**필수 환경 변수**:

```bash
# 데이터베이스
DATABASE_URL=postgresql://user:password@host:port/database

# 보안
SECRET_KEY=your-secret-key-here

# CORS 설정 (프론트엔드 도메인 포함 필수)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://eieconcierge.com,https://www.eieconcierge.com

# Cloudflare Tunnel (토큰 방식 사용 시)
CLOUDFLARE_TUNNEL_TOKEN=eyJhIjoi...

# NAS 설정 (로컬 스크립트에서 사용)
NAS_USER=juns
NAS_IP=192.168.45.58
NAS_BACKEND_PATH=/volume1/web/focusmate-backend
NAS_TUNNEL_PATH=/volume1/web/cloudflare-tunnel
```

**`.env` 파일 위치**: `/volume1/web/focusmate-backend/.env`

**확인**:

```bash
# NAS에서 확인
cat /volume1/web/focusmate-backend/.env

# 로컬에서 확인
cat backend/.env
```

#### 5-2. 환경 변수 자동 동기화

Git 커밋 시 `.env` 파일이 자동으로 NAS에 동기화됩니다 (`.git/hooks/post-commit`).

**수동 동기화** (필요시):

```bash
# 로컬에서 실행
rsync -avz backend/.env juns@192.168.45.58:/volume1/web/focusmate-backend/
```

---

## 로컬 개발 → NAS 배포 워크플로우

### 자동 배포 (Git Hook 사용 - 권장)

코드 수정 후 Git 커밋만 하면 자동으로 NAS에 동기화됩니다.

```bash
# 1. 코드 수정 및 커밋
git add .
git commit -m "변경사항 설명"
git push

# 2. 자동 동기화 (post-commit hook이 자동 실행)
# - backend/ 디렉토리 전체가 NAS에 동기화됨
# - .env 파일도 포함됨

# 3. NAS에서 서버 재시작 (필요시)
ssh juns@192.168.45.58
/volume1/web/focusmate-backend/stop-nas.sh
/volume1/web/focusmate-backend/start-nas.sh
```

### 수동 배포

Git Hook을 사용하지 않을 때:

```bash
# 1. 파일 동기화 (로컬 터미널)
rsync -avz \
  --exclude 'venv' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '.pytest_cache' \
  --exclude '.mypy_cache' \
  --exclude '*.log' \
  --exclude '.DS_Store' \
  --exclude 'node_modules' \
  /Users/juns/code/personal/notion/juns_workspace/FocusMate/backend/ \
  juns@192.168.45.58:/volume1/web/focusmate-backend/

# 2. 서버 재시작 (NAS 접속 후)
ssh juns@192.168.45.58
/volume1/web/focusmate-backend/stop-nas.sh
/volume1/web/focusmate-backend/start-nas.sh
```

### 서버 로그 확인

```bash
# NAS 접속
ssh juns@192.168.45.58

# 백엔드 로그
tail -f /volume1/web/focusmate-backend/logs/app.log

# Cloudflare Tunnel 로그
tail -f /volume1/web/cloudflare-tunnel/tunnel.log

# 실시간 프로세스 확인
watch -n 1 'ps aux | grep -E "uvicorn|cloudflared"'
```

### 📊 아키텍처 다이어그램

```
사용자
  ↓ (https://eieconcierge.com)
Vercel (프론트엔드)
  ↓ (API 요청)
Cloudflare Tunnel (api.eieconcierge.com)
  ↓ (터널링, 포트 포워딩 불필요)
Synology NAS (192.168.45.58)
  └─ Miniconda Python 3.11/3.12/3.13 (FastAPI 백엔드 :8000)
```

### 주요 스크립트 위치

| 스크립트               | 경로                                          | 설명                       |
| ---------------------- | --------------------------------------------- | -------------------------- |
| `start-nas.sh`         | `/volume1/web/focusmate-backend/start-nas.sh` | 백엔드 및 Tunnel 자동 시작 |
| `stop-nas.sh`          | `/volume1/web/focusmate-backend/stop-nas.sh`  | 백엔드 및 Tunnel 종료      |
| `setup-nas-initial.sh` | `scripts/setup-nas-initial.sh`                | NAS 초기 설정 마법사       |
| `test-nas-sync.sh`     | `scripts/test-nas-sync.sh`                    | NAS 동기화 테스트          |
| `post-commit`          | `.git/hooks/post-commit`                      | Git 커밋 시 자동 동기화    |

### 주요 디렉토리 구조

```
/volume1/web/
├── focusmate-backend/          # 백엔드 프로젝트
│   ├── .env                    # 환경 변수 (자동 동기화)
│   ├── app.pid                 # 백엔드 PID 파일
│   ├── logs/                   # 로그 디렉토리
│   │   └── app.log             # 백엔드 로그
│   ├── start-nas.sh            # 시작 스크립트
│   └── stop-nas.sh             # 중지 스크립트
├── cloudflare-tunnel/          # Cloudflare Tunnel
│   ├── tunnel.pid              # Tunnel PID 파일
│   └── tunnel.log              # Tunnel 로그
└── miniconda3/                 # Miniconda 설치
    └── envs/
        └── focusmate_env/      # Python 가상환경
```

## 참고 자료

### 공식 문서

- [Python 공식 문서](https://docs.python.org/3.14/)
- [Synology 개발자 가이드](https://developer.synology.com/)
- [Cloudflare Tunnel 문서](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [Miniconda 설치 가이드](https://docs.conda.io/en/latest/miniconda.html)

### 관련 문서

- `DEPLOY-011_NAS_Deployment.md`: 기본 NAS 배포 가이드
- `backend/.env.example`: 환경 변수 템플릿
- `scripts/start.sh`: 로컬 개발 스크립트 (NAS 관리 기능 포함)

### 유용한 명령어

```bash
# NAS 접속
ssh juns@192.168.45.58

# 백엔드 상태 확인
ps aux | grep uvicorn
curl http://localhost:8000/health

# Tunnel 상태 확인
ps aux | grep cloudflared
tail -f /volume1/web/cloudflare-tunnel/tunnel.log

# 프로세스 강제 종료 (비상시)
pkill -9 -f uvicorn
pkill -9 -f cloudflared

# 로그 실시간 확인
tail -f /volume1/web/focusmate-backend/logs/app.log
tail -f /volume1/web/cloudflare-tunnel/tunnel.log
```
