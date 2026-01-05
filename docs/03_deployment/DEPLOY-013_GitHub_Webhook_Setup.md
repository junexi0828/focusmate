# GitHub Webhook을 통한 NAS 자동 배포 설정

GitHub에 push하면 자동으로 NAS에서 git pull을 수행하여 최신 코드를 배포합니다.

## 아키텍처

```
GitHub Push
  ↓
GitHub Webhook (POST 요청)
  ↓
NAS Webhook Listener (포트 9000)
  ↓
git pull + 마이그레이션 + 서버 재시작 (선택적)
```

## NAS 설정

### 1. Webhook Listener 설치

```bash
# NAS SSH 접속
ssh juns@192.168.45.58

# 프로젝트 디렉토리로 이동
cd /volume1/web/focusmate-backend

# Webhook listener 스크립트에 실행 권한 부여
chmod +x scripts/github-webhook-listener.py
chmod +x scripts/start-webhook-listener.sh
```

### 2. Webhook Secret 설정

`.env` 파일에 webhook secret 추가:

```bash
# backend/.env
GITHUB_WEBHOOK_SECRET=your-random-secret-string-here
```

Secret 생성 방법:

```bash
# 랜덤 secret 생성
openssl rand -hex 32
```

### 3. Webhook Listener 시작

```bash
# 수동 시작
cd /volume1/web/focusmate-backend
./scripts/start-webhook-listener.sh

# 자동 시작 설정 (Task Scheduler)
# DSM → Control Panel → Task Scheduler
# Create → Scheduled Task → User-defined script
# Run command: /volume1/web/focusmate-backend/scripts/start-webhook-listener.sh
# Schedule: Boot-up
```

### 4. Cloudflare Tunnel에 Webhook 경로 추가

Cloudflare Zero Trust 대시보드에서:

1. Tunnel 선택 → **Public Hostname** 탭
2. **Add a public hostname**
3. 설정:
   - **Subdomain**: `webhook` (또는 원하는 이름)
   - **Domain**: `eieconcierge.com` (또는 사용 중인 도메인)
   - **Service**: `http://localhost:9000`
4. **Save hostname**

또는 기존 Tunnel의 Public Hostname에 경로 추가:

- **Path**: `/webhook`
- **Service**: `http://localhost:9000`

## GitHub 설정

### 1. Webhook 추가

1. GitHub 저장소 → **Settings** → **Webhooks** → **Add webhook**
2. 설정:
   - **Payload URL**: `https://webhook.eieconcierge.com/webhook` (또는 Cloudflare Tunnel URL)
   - **Content type**: `application/json`
   - **Secret**: `.env`에 설정한 `GITHUB_WEBHOOK_SECRET` 값
   - **Events**: `Just the push event` 선택
   - **Active**: 체크
3. **Add webhook** 클릭

### 2. Webhook 테스트

GitHub에서 webhook을 추가하면 자동으로 테스트 요청을 보냅니다.

**성공 응답 확인:**

- GitHub → Settings → Webhooks → 해당 webhook 클릭
- Recent Deliveries에서 `200 OK` 응답 확인

## 동작 확인

### 1. Webhook Listener 상태 확인

```bash
# NAS 접속
ssh juns@192.168.45.58

# 프로세스 확인
ps aux | grep github-webhook-listener

# 로그 확인
tail -f /volume1/web/focusmate-backend/logs/webhook-listener.log
```

### 2. 테스트 Push

```bash
# 로컬에서
git add .
git commit -m "Test webhook"
git push origin main
```

**예상 동작:**

1. GitHub에서 webhook 전송
2. NAS webhook listener가 요청 수신
3. `git pull origin main` 실행
4. 마이그레이션 실행 (변경사항이 있으면)
5. 로그에 기록

### 3. 로그 확인

```bash
# NAS에서
tail -f /volume1/web/focusmate-backend/logs/webhook-listener.log
```

**성공 로그 예시:**

```
[Webhook] 📥 Event: push
[Webhook] 🔄 Processing push to refs/heads/main
[Webhook] 📂 Project directory: /volume1/web/focusmate-backend
[Webhook] ✅ Git pull successful
[Webhook] ✅ Migrations completed
```

## 문제 해결

### Webhook이 작동하지 않음

1. **Listener 실행 확인**

   ```bash
   ps aux | grep github-webhook-listener
   ```

2. **포트 확인**

   ```bash
   netstat -tuln | grep 9000
   ```

3. **로그 확인**

   ```bash
   tail -f /volume1/web/focusmate-backend/logs/webhook-listener.log
   ```

4. **Cloudflare Tunnel 확인**
   - Tunnel이 실행 중인지 확인
   - Public Hostname이 올바르게 설정되었는지 확인

### Signature 검증 실패

- `.env`의 `GITHUB_WEBHOOK_SECRET`이 GitHub webhook 설정의 Secret과 일치하는지 확인

### Git pull 실패

- NAS에서 Git 저장소가 올바르게 설정되어 있는지 확인
- SSH 키 또는 인증 정보가 올바른지 확인

## 보안 고려사항

1. **Webhook Secret 사용**: 반드시 secret을 설정하여 무단 요청 방지
2. **HTTPS 사용**: Cloudflare Tunnel을 통해 HTTPS로 webhook 수신
3. **IP 화이트리스트**: 가능하면 GitHub IP 범위만 허용 (선택적)
4. **로그 모니터링**: 정기적으로 로그를 확인하여 이상 요청 탐지

## 🚨 실운영 배포 전 필수 체크리스트

> [!CAUTION]
> **실운영 환경에 배포하기 전 반드시 확인하세요!**

### 1. 서버 자동 재시작 비활성화

**현재 상태: 개발 환경용 자동 재시작 활성화됨**

실운영 배포 전 `scripts/deployment/github-webhook-listener.py` 파일을 수정하세요:

```python
# ⚠️ 개발 환경용: 서버 자동 재시작 활성화
# 🚨 실운영 배포 전 반드시 주석 처리 필요!
# 실운영에서는 무중단 배포 또는 수동 재시작 권장
self.restart_server()  # ← 이 줄을 주석 처리하세요!
```

**실운영 설정:**

```python
# ⚠️ 개발 환경용: 서버 자동 재시작 활성화
# 🚨 실운영 배포 전 반드시 주석 처리 필요!
# 실운영에서는 무중단 배포 또는 수동 재시작 권장
# self.restart_server()  # ← 주석 처리됨 (실운영)
```

**이유:**
- 실운영 환경에서는 **무중단 배포** 또는 **계획된 유지보수 시간**에 재시작해야 합니다
- 자동 재시작 시 **사용자 연결이 끊기고** 진행 중인 작업이 손실될 수 있습니다
- **롤백 계획** 없이 자동 배포하면 문제 발생 시 대응이 어렵습니다

### 2. 실운영 배포 워크플로우

**권장 방식:**

1. **코드 변경 → GitHub push**
   - Webhook이 자동으로 `git pull` 실행
   - 마이그레이션 자동 실행
   - **서버는 재시작하지 않음** (실운영 설정)

2. **계획된 시간에 수동 재시작**
   ```bash
   # NAS SSH 접속
   ssh juns@192.168.45.58

   # 서버 재시작
   cd /volume1/web/focusmate-backend
   bash stop-nas.sh && bash start-nas.sh
   ```

3. **또는 무중단 배포 구성** (고급)
   - Blue-Green 배포
   - Rolling 업데이트
   - Load Balancer 사용

### 3. 개발 vs 실운영 환경 구분

| 항목 | 개발 환경 | 실운영 환경 |
|------|----------|------------|
| 자동 재시작 | ✅ 활성화 (편의성) | ❌ 비활성화 (안정성) |
| Git pull | ✅ 자동 | ✅ 자동 |
| 마이그레이션 | ✅ 자동 | ✅ 자동 |
| 서버 재시작 | ✅ 자동 | ⚠️ 수동 (계획된 시간) |
| 롤백 계획 | 선택적 | 필수 |

## 현재 상태

✅ **로컬 커밋 시 자동 동기화**: `post-commit` hook으로 rsync 실행
✅ **GitHub push 시 자동 배포**: Webhook listener로 git pull 실행
✅ **코드 변경 감지**: "Already up to date"일 때는 재시작하지 않음
⚠️ **서버 자동 재시작**: 현재 활성화됨 (개발 환경용)

## 참고

- GitHub webhook은 push 이벤트만 처리합니다.
- `main` 또는 `develop` 브랜치만 자동 배포됩니다.
- 실제로 코드가 변경되었을 때만 서버를 재시작합니다 ("Already up to date"는 무시).
- **실운영 배포 전 반드시 자동 재시작을 비활성화하세요!**

