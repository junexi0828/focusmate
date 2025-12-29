# 하이브리드 아키텍처 설정 가이드

Vercel (프론트엔드) + Cloudflare Tunnel (백엔드) 하이브리드 배포 구성 방법입니다.

## 아키텍처 개요

```
사용자 → https://eieconcierge.com (Vercel)
         ↓ API 요청
         https://api.eieconcierge.com 또는 랜덤 URL (Cloudflare Tunnel)
         ↓ 터널링
         localhost:8000 (로컬 백엔드 또는 NAS)
```

**참고:** 시놀로지 NAS에서 백엔드를 실행하는 경우 [NAS 배포 가이드](./DEPLOY-011_NAS_Deployment.md)를 참고하세요.

### 장점

- ✅ Vercel의 빠른 CDN으로 프론트엔드 자산 전송
- ✅ 백엔드 서버 비용 0원 (집 컴퓨터 사용)
- ✅ 데이터베이스를 클라우드에 올리지 않아도 됨
- ✅ 데이터 관리 주도권 유지

### 단점

- ⚠️ 집 컴퓨터가 꺼지면 API 응답 불가
- ⚠️ 홈 네트워크 상태에 따라 응답 속도 영향 가능

## 필수 설정 3가지

### 1. 백엔드 CORS 설정 (필수)

백엔드 `.env` 파일에 Vercel 도메인 추가:

```bash
# backend/.env
CORS_ORIGINS=https://your-app.vercel.app,https://your-app-*.vercel.app,http://localhost:3000
```

**설명:**

- `your-app.vercel.app`: 프로덕션 도메인
- `your-app-*.vercel.app`: Vercel 프리뷰 도메인 (자동 배포용)
- `localhost:3000`: 로컬 개발용

**환경 변수 형식:**

```bash
# 쉼표로 구분된 문자열
CORS_ORIGINS=https://focusmate.vercel.app,https://focusmate-*.vercel.app,http://localhost:3000
```

### 2. 프론트엔드 API URL 설정

Vercel 프로젝트 설정에서 환경 변수 추가:

**Vercel 대시보드 설정:**

1. 프로젝트 선택 → Settings → Environment Variables
2. 다음 변수 추가:

| Key                 | Value                             | Environment                      |
| ------------------- | --------------------------------- | -------------------------------- |
| `VITE_API_BASE_URL` | `https://api.mydomain.com/api/v1` | Production, Preview, Development |
| `VITE_WS_BASE_URL`  | `wss://api.mydomain.com`          | Production, Preview, Development |

**로컬 개발용 `.env` 파일:**

```bash
# frontend/.env.local (로컬 개발용)
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_BASE_URL=ws://localhost:8000
```

### 3. Cloudflare Tunnel 설정

#### 3.1 Cloudflare 계정 및 Tunnel 생성

1. **Cloudflare 계정 생성**

   - https://dash.cloudflare.com/ 접속
   - 무료 계정으로 시작 가능

2. **도메인 추가 (eieconcierge.com)**

   - Cloudflare 대시보드에서 "Add a Site" 클릭
   - `eieconcierge.com` 입력
   - DNS 레코드 스캔 또는 수동 입력
   - Nameserver 변경 (도메인 등록업체에서 Cloudflare Nameserver로 변경)

3. **Zero Trust 대시보드 접속**

   - 왼쪽 메뉴에서 "Zero Trust" 클릭
   - 또는 https://one.dash.cloudflare.com/ 접속

4. **Tunnel 생성**

   - Networks → Tunnels → Create a tunnel
   - Tunnel 이름: `focusmate-backend`
   - Connector: `cloudflared` 선택

5. **커스텀 도메인 설정 (필수)**

   - Public Hostname 탭에서 "Add a public hostname"
   - **Subdomain**: `api`
   - **Domain**: `eieconcierge.com` (Cloudflare에서 관리하는 도메인)
   - **Service**: `http://localhost:8000`
   - **Path**: (비워두기 - 모든 경로 허용)
   - Save hostname 클릭

6. **DNS 레코드 자동 생성 확인 (커스텀 도메인 사용 시)**
   - Cloudflare Tunnel이 자동으로 DNS 레코드를 생성합니다
   - Cloudflare 대시보드 → DNS → Records에서 확인
   - `api.eieconcierge.com` → CNAME → `[tunnel-id].cfargotunnel.com` 형식으로 생성됨
   - **참고:** DNS 없이도 랜덤 URL(`https://random-name.trycloudflare.com`)로 사용 가능

#### 3.2 cloudflared 설치 및 실행

**macOS:**

```bash
# Homebrew로 설치
brew install cloudflare/cloudflare/cloudflared

# 또는 직접 다운로드
# https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
```

**Tunnel 실행:**

```bash
# Tunnel 토큰으로 실행 (Zero Trust 대시보드에서 복사)
cloudflared tunnel --url http://localhost:8000

# 또는 설정 파일 사용 (권장)
cloudflared tunnel run focusmate-backend
```

**백그라운드 실행 (macOS):**

```bash
# LaunchAgent로 등록하여 자동 시작
mkdir -p ~/Library/LaunchAgents
# cloudflared 설정 파일 생성 후
launchctl load ~/Library/LaunchAgents/com.cloudflare.tunnel.plist
```

#### 3.3 커스텀 도메인 없이 사용 (무료)

Cloudflare Tunnel은 무료로 랜덤 URL을 제공합니다:

```
https://random-name.trycloudflare.com
```

이 URL을 Vercel 환경 변수에 설정하면 됩니다.

## 설정 체크리스트

### 백엔드 설정

- [ ] `.env` 파일에 `CORS_ORIGINS` 설정 (Vercel 도메인 포함)
- [ ] 백엔드 서버가 `localhost:8000`에서 실행 중
- [ ] Cloudflare Tunnel이 백엔드로 연결됨

### 프론트엔드 설정

- [ ] Vercel 환경 변수에 `VITE_API_BASE_URL` 설정
- [ ] Vercel 환경 변수에 `VITE_WS_BASE_URL` 설정
- [ ] 로컬 개발용 `.env.local` 파일 설정

### Cloudflare Tunnel

- [ ] cloudflared 설치 완료
- [ ] Tunnel 생성 및 연결 확인
- [ ] Public Hostname 설정 (커스텀 도메인 사용 시)

## 테스트 방법

### 1. 로컬 테스트

```bash
# 백엔드 실행
cd backend
./run.sh

# 프론트엔드 실행
cd frontend
npm run dev

# 브라우저에서 http://localhost:3000 접속
# 개발자 도구 → Network 탭에서 API 요청 확인
```

### 2. Vercel 배포 후 테스트

```bash
# Vercel에 배포
cd frontend
vercel --prod

# 브라우저에서 배포된 URL 접속
# 개발자 도구 → Console에서 CORS 에러 확인
# Network 탭에서 API 요청 상태 확인
```

### 3. CORS 에러 확인

브라우저 콘솔에서 다음 에러가 나오면 CORS 설정 문제:

```
Access to fetch at 'https://api.mydomain.com/api/v1/...' from origin 'https://your-app.vercel.app' has been blocked by CORS policy
```

**해결 방법:**

1. 백엔드 `.env`의 `CORS_ORIGINS`에 Vercel 도메인 추가 확인
2. 백엔드 서버 재시작
3. 브라우저 캐시 클리어

## 보안 고려사항

### 1. 환경 변수 보안

- Vercel 환경 변수는 암호화되어 저장됨
- `.env` 파일은 절대 Git에 커밋하지 않기
- `.gitignore`에 `.env` 추가 확인

### 2. CORS 설정

- 프로덕션에서는 정확한 도메인만 허용
- 와일드카드(`*`) 사용 지양 (보안 위험)

### 3. HTTPS

- Vercel과 Cloudflare Tunnel 모두 자동 HTTPS 제공
- Mixed Content 에러 걱정 없음

## 배포 워크플로우

### 개발 환경

1. 로컬에서 백엔드 실행 (`./backend/run.sh`)
2. 로컬에서 프론트엔드 실행 (`npm run dev`)
3. `localhost:3000`에서 테스트

### 프로덕션 환경

1. Cloudflare Tunnel 실행 (백엔드 연결)
2. Vercel에 프론트엔드 배포
3. Vercel 환경 변수 확인
4. 배포된 URL에서 테스트

## 문제 해결

### 문제: CORS 에러

**증상:** 브라우저 콘솔에 CORS 에러 메시지

**해결:**

1. 백엔드 `.env`의 `CORS_ORIGINS` 확인
2. Vercel 도메인이 정확히 포함되어 있는지 확인
3. 백엔드 서버 재시작

### 문제: API 연결 실패

**증상:** Network 탭에서 502/503 에러

**해결:**

1. Cloudflare Tunnel이 실행 중인지 확인
2. 백엔드 서버가 `localhost:8000`에서 실행 중인지 확인
3. Tunnel 로그 확인: `cloudflared tunnel info`

### 문제: WebSocket 연결 실패

**증상:** 실시간 기능이 작동하지 않음

**해결:**

1. `VITE_WS_BASE_URL` 환경 변수 확인
2. `ws://` → `wss://` (HTTPS 환경)
3. Cloudflare Tunnel이 WebSocket을 지원하는지 확인

## 참고 자료

- [Cloudflare Tunnel 공식 문서](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [Vercel 환경 변수 설정](https://vercel.com/docs/concepts/projects/environment-variables)
- [FastAPI CORS 설정](https://fastapi.tiangolo.com/tutorial/cors/)
- [CORS 문제 해결 가이드](./DEPLOY-009_CORS_Troubleshooting.md)

