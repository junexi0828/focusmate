# Supabase 연결 가이드 - IPv4 네트워크

## 현재 상황

- **네트워크**: IPv4 사용 중 (192.168.0.68)
- **문제**: Supabase Direct Connection은 IPv6 전용이므로 IPv4에서 연결 불가
- **해결**: Session Pooler 사용 필요

## Supabase 대시보드에서 Session Pooler 연결 문자열 가져오기

### 단계별 가이드

1. **Supabase 대시보드 접속**

   - https://supabase.com/dashboard/project/xevhqwaxxlcsqzhmawjr

2. **Settings > Database 이동**

3. **Connection Pooling 섹션 찾기**

4. **Session Pooler 연결 문자열 복사**

   - "Connection string" 탭 선택
   - "Type": URI
   - "Source": Session Pooler (또는 Transaction Pooler)
   - "Method": Session Pooler
   - 표시된 연결 문자열 복사

5. **연결 문자열 형식**

   ```
   postgresql://postgres.xevhqwaxxlcsqzhmawjr:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
   ```

6. **asyncpg 형식으로 변환**
   ```
   postgresql+asyncpg://postgres.xevhqwaxxlcsqzhmawjr:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
   ```

## .env 파일 업데이트

```bash
# 기존 (Direct Connection - IPv4에서 작동 안 함)
# DATABASE_URL=postgresql+asyncpg://postgres:focusmate202230262@db.xevhqwaxxlcsqzhmawjr.supabase.co:5432/postgres

# Session Pooler (IPv4 호환)
DATABASE_URL=postgresql+asyncpg://postgres.xevhqwaxxlcsqzhmawjr:focusmate202230262@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

**중요**: `[REGION]`을 Supabase 대시보드에서 확인한 실제 리전으로 교체하세요.

## 리전 확인 방법

Supabase 대시보드에서:

1. Settings > General
2. "Region" 섹션에서 리전 확인
3. 예: `ap-northeast-2` (서울), `us-east-1` (버지니아) 등

## 연결 테스트

```bash
cd backend
source venv/bin/activate
python3 test_db_connection.py
```

## 문제 해결

### "Tenant or user not found" 오류

- 리전 정보가 잘못되었을 수 있음
- Supabase 대시보드에서 정확한 리전 확인

### DNS 해석 실패

- IPv4 네트워크에서는 Direct Connection 사용 불가
- 반드시 Session Pooler 사용

### 연결 타임아웃

- 방화벽 설정 확인
- Supabase 대시보드에서 IP 화이트리스트 확인

## 참고

- **IPTV 설정**: 데이터베이스 연결과 무관 (설정 불필요)
- **IPv6**: Direct Connection은 IPv6 전용이지만, 현재 IPv4 네트워크 사용 중
- **Session Pooler**: IPv4 네트워크에서 Supabase 연결을 위한 필수 방법
