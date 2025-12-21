# Supabase 연결 설정 가이드

## 프로젝트 정보

- **Project Reference**: `YOUR_PROJECT_REF` (Supabase 대시보드에서 확인)
- **MCP URL**: `https://mcp.supabase.com/mcp?project_ref=YOUR_PROJECT_REF`

## Supabase 연결 설정 방법

### 1. Supabase 대시보드에서 연결 정보 가져오기

1. [Supabase 대시보드](https://supabase.com/dashboard/project/YOUR_PROJECT_REF) 접속
   - `YOUR_PROJECT_REF`를 실제 프로젝트 참조 ID로 교체하세요
2. **Settings** > **Database** 이동
3. **Connection string** 섹션에서 연결 문자열 복사
   - **URI** 또는 **Connection pooling** 사용 권장
   - 형식: `postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres`

### 2. 자동 설정 스크립트 사용

```bash
cd backend
source venv/bin/activate
python scripts/setup_supabase.py
```

스크립트가 연결 문자열을 입력받아 `.env` 파일을 자동으로 업데이트합니다.

### 3. 수동 설정

`.env` 파일에서 `DATABASE_URL`을 Supabase 연결 문자열로 변경:

```bash
# 기존 (로컬 PostgreSQL)
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/focus_mate

# Supabase (Connection Pooling 권장)
DATABASE_URL=postgresql+asyncpg://postgres.YOUR_PROJECT_REF:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres

# 또는 Direct Connection
DATABASE_URL=postgresql+asyncpg://postgres:[PASSWORD]@db.YOUR_PROJECT_REF.supabase.co:5432/postgres
```

**중요**:

- `[PASSWORD]`를 실제 데이터베이스 비밀번호로 교체
- `[REGION]`을 실제 리전으로 교체 (예: `ap-northeast-2`)

### 4. 연결 테스트

```bash
cd backend
source venv/bin/activate
python test_db_connection.py
```

### 5. 마이그레이션 실행

Supabase 데이터베이스에 테이블을 생성하려면:

```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

## Supabase MCP (Model Context Protocol) 설정

### Cursor에서 MCP 서버 설정

`.cursor/mcp.json` 파일에 다음을 추가:

```json
{
  "mcpServers": {
    "supabase": {
      "url": "https://mcp.supabase.com/mcp?project_ref=YOUR_PROJECT_REF"
    }
  }
}
```

### 읽기 전용 모드 (권장)

개발 환경에서는 읽기 전용 모드를 사용하는 것이 안전합니다:

```json
{
  "mcpServers": {
    "supabase": {
      "url": "https://mcp.supabase.com/mcp?project_ref=YOUR_PROJECT_REF&read_only=true"
    }
  }
}
```

## 보안 주의사항

⚠️ **중요**:

- 프로덕션 데이터에 MCP 서버를 연결하지 마세요
- 개발 및 테스트 목적으로만 사용하세요
- 연결 문자열에 비밀번호가 포함되어 있으므로 `.env` 파일을 Git에 커밋하지 마세요
- Supabase 대시보드에서 IP 화이트리스트를 설정하세요

## 문제 해결

### 연결 실패 시

1. **IP 화이트리스트 확인**

   - Supabase 대시보드 > Settings > Database > Connection Pooling
   - 현재 IP 주소가 허용되어 있는지 확인

2. **비밀번호 확인**

   - Supabase 대시보드 > Settings > Database
   - 데이터베이스 비밀번호 확인

3. **연결 문자열 형식 확인**

   - `postgresql+asyncpg://` 접두사 사용 (asyncpg 드라이버)
   - 포트 번호 확인 (Connection Pooling: 6543, Direct: 5432)

4. **방화벽 확인**
   - 회사 네트워크나 VPN이 Supabase 연결을 차단하는지 확인

## 참고 자료

- [Supabase MCP 문서](https://supabase.com/mcp)
- [Supabase 연결 가이드](https://supabase.com/docs/guides/database/connecting-to-postgres)
- [보안 모범 사례](https://supabase.com/mcp#security-best-practices)
