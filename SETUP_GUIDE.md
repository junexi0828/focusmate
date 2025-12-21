# 프로젝트 초기 설정 가이드

이 가이드는 프로젝트를 처음 클론했을 때 필요한 모든 설정을 안내합니다.

## 📋 필수 파일 확인

프로젝트를 클론한 후 다음 파일들이 존재하는지 확인하세요:

### 백엔드

- ✅ `backend/requirements.txt` - Python 의존성 목록
- ✅ `backend/.env.example` - 환경 변수 템플릿
- ✅ `backend/.gitignore` - Git 무시 파일 목록

### 프론트엔드

- ✅ `frontend/package.json` - Node.js 의존성 목록
- ✅ `frontend/.env.example` - 환경 변수 템플릿
- ✅ `frontend/.gitignore` - Git 무시 파일 목록 (새로 생성됨)

## 🚀 빠른 시작

### 방법 1: 통합 스크립트 사용 (권장)

```bash
# 프로젝트 루트에서 실행
./scripts/start.sh
```

이 스크립트는 자동으로:

1. 백엔드 `.env.example` → `.env` 복사
2. 프론트엔드 `.env.example` → `.env` 복사
3. Python 가상환경 생성 및 의존성 설치
4. Node.js 의존성 설치
5. 서버 시작

### 방법 2: 개별 스크립트 사용

#### 백엔드

```bash
cd backend
./run.sh
```

#### 프론트엔드

```bash
cd frontend
./run.sh
```

### 방법 3: 수동 설정

#### 백엔드

```bash
cd backend

# 1. 환경 변수 설정
cp .env.example .env

# 2. 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 서버 시작
uvicorn app.main:app --reload
```

#### 프론트엔드

```bash
cd frontend

# 1. 환경 변수 설정
cp .env.example .env

# 2. 의존성 설치
npm install

# 3. 개발 서버 시작
npm run dev
```

## ⚙️ 환경 변수 설정

### 백엔드 `.env` 파일

`.env.example`을 복사한 후 다음 항목들을 확인/수정하세요:

1. **SECRET_KEY** (필수)

   ```bash
   # 최소 32자 이상의 랜덤 문자열 생성
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **DATABASE_URL** (필수)

   - 로컬 PostgreSQL: `postgresql+asyncpg://postgres:postgres@localhost:5432/focus_mate`
   - Supabase: 프로젝트 설정에서 연결 문자열 복사

3. **NAVER_CLIENT_ID / NAVER_CLIENT_SECRET** (선택)
   - 네이버 로그인을 사용하는 경우에만 설정

### 프론트엔드 `.env` 파일

`.env.example`을 복사한 후 다음 항목들을 확인/수정하세요:

1. **VITE_API_BASE_URL** (필수)

   - 개발: `http://localhost:8000/api/v1`
   - 프로덕션: 실제 API 서버 URL

2. **VITE_WS_BASE_URL** (필수)

   - 개발: `ws://localhost:8000`
   - 프로덕션: 실제 WebSocket 서버 URL

3. **VITE_SUPABASE_URL / VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY** (선택)
   - Supabase를 사용하는 경우에만 설정

## ✅ 검증 체크리스트

설정이 완료되었는지 확인하세요:

- [ ] `backend/.env` 파일이 존재하고 `.env.example`에서 복사됨
- [ ] `frontend/.env` 파일이 존재하고 `.env.example`에서 복사됨
- [ ] `backend/requirements.txt`가 Git에 포함되어 있음
- [ ] `frontend/package.json`이 Git에 포함되어 있음
- [ ] `backend/.env.example`이 Git에 포함되어 있음
- [ ] `frontend/.env.example`이 Git에 포함되어 있음
- [ ] `.gitignore`에 `.env`가 포함되어 있음
- [ ] `backend/.gitignore`에 `.env`가 포함되어 있음
- [ ] `frontend/.gitignore`에 `.env`가 포함되어 있음

## 🔒 보안 주의사항

1. **절대 `.env` 파일을 Git에 커밋하지 마세요**

   - `.gitignore`에 이미 포함되어 있지만 확인하세요

2. **프로덕션 환경에서는 반드시 SECRET_KEY를 변경하세요**

   - `.env.example`의 기본값은 개발용입니다

3. **민감한 정보는 환경 변수로 관리하세요**
   - API 키, 비밀번호, 토큰 등

## 📝 추가 참고사항

- 모든 예제 파일(`.env.example`, `requirements.txt`, `package.json`)은 Git에 포함되어 있습니다
- 실제 설정 파일(`.env`)은 Git에 포함되지 않습니다 (`.gitignore`에 의해 제외)
- 프로젝트를 클론한 후 바로 `./scripts/start.sh`를 실행하면 자동으로 모든 설정이 완료됩니다
