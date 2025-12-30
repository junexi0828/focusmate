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

#### 3-1. 실행 스크립트(`start.sh`) 생성

```bash
nano /volume1/web/focusmate-backend/start.sh
```

```bash
#!/bin/bash
cd /volume1/web/focusmate-backend
# Miniconda 환경 활성화 후 서버 실행
source /volume1/web/miniconda3/bin/activate focusmate_env
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &
echo $! > app.pid
```

```bash
chmod +x /volume1/web/focusmate-backend/start-nas.sh
```

#### 3-2. 부팅 시 자동 실행 등록

- **DSM 제어판 > 작업 스케줄러 > 생성 > 트리거된 작업 > 사용자 정의 스크립트**
- 이벤트: `부트업`, 사용자: `admin`
- 스크립트: `/volume1/web/focusmate-backend/start-nas.sh`

---

### 4단계: Cloudflare Tunnel 설정 (선택 가능)

외부에서 `api.eieconcierge.com`으로 접속 시 NAS의 8000번 포트로 연결해주는 설정입니다. 두 가지 방법 중 하나를 선택하세요.

로컬 개발과 NAS 프로덕션을 **동시에 실행하지 않는다면**, 기존 터널 설정 그대로 사용하면 됩니다.

**⚠️ 주의사항:**

- 같은 Tunnel을 macOS와 NAS에서 **동시에 실행하면 충돌** 발생
- 한 번에 **하나의 장치에서만** Tunnel 실행
- NAS에서 사용할 때는 macOS의 Tunnel을 중지해야 함

#### 공통 준비: `cloudflared` 설치 (NAS)

```bash
cd /tmp
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64
sudo mv cloudflared-linux-arm64 /usr/local/bin/cloudflared
sudo chmod +x /usr/local/bin/cloudflared
cloudflared --version
```

#### [방법 A] 기존 터널에 분기 추가 (추천: 관리 용이)

기존에 맥북 등에서 쓰던 터널을 재활용하여 설정만 추가하는 방식입니다.

1.  **Cloudflare Zero Trust 대시보드** > **Networks** > **Tunnels** > 기존 터널 **Configure**.
2.  **Public Hostname** 탭 > **Add hostname**:
    - Subdomain: `api`
    - Service: `http://localhost:8000`
3.  **NAS에서 터널 실행** (기존 터널 토큰 사용):
    ```bash
    # start-tunnel.sh 작성
    nano /volume1/web/cloudflare-tunnel/start-tunnel.sh
    ```
    ```bash
    #!/bin/bash
    # 기존 터널 토큰 입력
    TUNNEL_TOKEN="eyJhIjoi..."
    nohup cloudflared tunnel run --token $TUNNEL_TOKEN > tunnel.log 2>&1 &
    ```

#### [방법 B] NAS 전용 새 터널 생성 (추천: 운영/개발 분리)

배포용(NAS)과 개발용(Mac)을 완전히 분리하고 싶을 때 사용합니다.

1.  **새 터널 생성**:
    ```bash
    cloudflared tunnel login
    cloudflared tunnel create focusmate-nas-backend
    ```
2.  **DNS 라우팅 연결**:
    ```bash
    cloudflared tunnel route dns focusmate-nas-backend api.eieconcierge.com
    ```
3.  **실행 스크립트 작성**:
    ```bash
    #!/bin/bash
    nohup cloudflared tunnel run focusmate-nas-backend > tunnel.log 2>&1 &
    ```

'''스크립트내용
#!/bin/bash
cd /volume1/web/cloudflare-tunnel
nohup cloudflared tunnel run focusmate-nas-backend > tunnel.log 2>&1 &
echo $! > tunnel.pid
'''

---

## 로컬 개발 → NAS 배포 워크플로우

코드 수정 후 NAS에 반영하는 명령어입니다. 파일 동기화 (rsync)

```bash
# 1. 파일 동기화 (로컬 터미널)
rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '.git' \
  /Users/juns/code/personal/notion/juns_workspace/FocusMate/backend/ \
  juns@192.168.45.58:/volume1/web/focusmate-backend/

# 2. 서버 재시작 (NAS 접속 후)
ssh juns@192.168.45.58
kill $(cat /volume1/web/focusmate-backend/app.pid)
/volume1/web/focusmate-backend/start.sh
```

서버 로그 확인
bash

# 백엔드 로그

tail -f /volume1/web/focusmate-backend/app.log

# Cloudflare Tunnel 로그

## tail -f /volume1/web/cloudflare-tunnel/tunnel.log

### 📊 아키텍처 다이어그램

```
사용자
  ↓ (https://eieconcierge.com)
Vercel (프론트엔드)
  ↓ (API 요청)
Cloudflare Tunnel (api.eieconcierge.com)
  ↓ (터널링, 포트 포워딩 불필요)
Synology NAS (192.168.45.58)
  └─ Miniconda Python 3.13 (FastAPI 백엔드 :8000)
```

## 참고

- [Python 공식 문서](https://docs.python.org/3.14/)
- [Synology 개발자 가이드](https://developer.synology.com/)
