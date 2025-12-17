# 파일 암호화 설정 가이드

## 개요

Focus Mate는 Fernet 대칭 암호화를 사용하여 업로드된 파일을 자동으로 암호화합니다.

## 암호화 시스템 구조

```
파일 업로드 → 암호화 서비스 → 암호화된 파일 저장
파일 다운로드 → 복호화 서비스 → 원본 파일 반환
```

## 1. 기본 설정

### 환경 변수 설정 (.env)

```bash
# 암호화 키 (선택사항 - 없으면 SECRET_KEY에서 자동 생성)
FILE_ENCRYPTION_KEY=your-base64-encoded-fernet-key

# SECRET_KEY (필수)
SECRET_KEY=your-secret-key-here
```

### 암호화 키 생성

```python
from cryptography.fernet import Fernet

# 새로운 Fernet 키 생성
key = Fernet.generate_key()
print(key.decode())  # 이 값을 FILE_ENCRYPTION_KEY로 사용
```

## 2. 미들웨어 통합 (선택사항)

`app/main.py`에 미들웨어 추가:

```python
from app.api.middleware.file_encryption import FileEncryptionMiddleware

# 미들웨어 추가
app.add_middleware(
    FileEncryptionMiddleware,
    encrypt_paths=[
        "/api/v1/chat/upload",
        "/api/v1/verification/upload",
    ],
    decrypt_paths=[
        "/api/v1/chat/download",
        "/api/v1/verification/download",
    ]
)
```

## 3. 서비스 레이어에서 직접 사용

### 파일 업로드 시 암호화

```python
from fastapi import UploadFile
from app.infrastructure.storage.encrypted_file_upload import EncryptedFileUploadService

async def upload_file(file: UploadFile):
    # 암호화된 파일 업로드 서비스 사용
    upload_service = EncryptedFileUploadService()

    # 파일 업로드 (자동으로 암호화됨)
    file_url = await upload_service.upload_file(
        file=file,
        folder="chat",
        allowed_extensions=[".jpg", ".png", ".pdf"]
    )

    return {"file_url": file_url}
```

### 파일 다운로드 시 복호화

```python
from fastapi import Response
from app.infrastructure.storage.encrypted_file_upload import EncryptedFileUploadService

async def download_file(file_path: str):
    upload_service = EncryptedFileUploadService()

    # 파일 읽기 및 복호화
    decrypted_content = await upload_service.download_encrypted_file(file_path)

    return Response(
        content=decrypted_content,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={file_path}"
        }
    )
```

## 4. 현재 구현 상태

### 이미 암호화가 적용된 영역

1. **채팅 파일 업로드**
   - 위치: `app/api/v1/endpoints/chat.py`
   - 서비스: `EncryptedFileUploadService` 사용
   - 폴더: `uploads/chat/`

2. **학생증 인증 파일**
   - 위치: `app/api/v1/endpoints/verification.py`
   - 서비스: `EncryptedFileUploadService` 사용
   - 폴더: `uploads/verification/`

3. **프로필 이미지**
   - 위치: `app/api/v1/endpoints/auth.py`
   - 엔드포인트: `/profile/{user_id}/upload-image`

## 5. 암호화 서비스 상세

### EncryptionService

**위치**: `app/shared/utils/encryption.py`

**주요 메서드**:
```python
class EncryptionService:
    def encrypt(self, data: bytes) -> bytes:
        """바이너리 데이터 암호화"""

    def decrypt(self, encrypted_data: bytes) -> bytes:
        """바이너리 데이터 복호화"""

    def encrypt_string(self, text: str) -> str:
        """문자열 암호화 (base64 반환)"""

    def decrypt_string(self, encrypted_text: str) -> str:
        """문자열 복호화"""
```

**싱글톤 인스턴스**:
```python
from app.shared.utils.encryption import get_encryption_service

encryption_service = get_encryption_service()
encrypted_data = encryption_service.encrypt(b"sensitive data")
```

### EncryptedFileUploadService

**위치**: `app/infrastructure/storage/encrypted_file_upload.py`

**주요 메서드**:
```python
class EncryptedFileUploadService:
    async def upload_file(
        self,
        file: UploadFile,
        folder: str,
        allowed_extensions: list[str] = None
    ) -> str:
        """파일을 암호화하여 업로드"""

    async def download_encrypted_file(self, file_path: str) -> bytes:
        """암호화된 파일을 복호화하여 다운로드"""

    async def delete_file(self, file_path: str) -> bool:
        """암호화된 파일 삭제"""
```

## 6. 보안 고려사항

### 암호화 강도
- **알고리즘**: Fernet (AES-128 CBC + HMAC)
- **키 유도**: PBKDF2-HMAC-SHA256, 100,000 iterations
- **인증**: HMAC으로 무결성 검증

### 키 관리
- ✅ 환경 변수로 키 관리 (.env)
- ✅ SECRET_KEY에서 결정론적 키 생성 가능
- ⚠️  프로덕션에서는 별도의 KEY_ROTATION 전략 필요

### 파일 접근 제어
- ✅ 암호화된 파일은 직접 읽어도 내용 확인 불가
- ✅ 복호화는 인증된 사용자만 가능
- ⚠️  파일 권한 설정 확인 필요 (chmod 600)

## 7. 성능 최적화

### 대용량 파일 처리
```python
# 스트리밍 방식으로 암호화 (메모리 효율적)
async def encrypt_large_file(file_path: str, chunk_size: int = 8192):
    encryption_service = get_encryption_service()

    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            encrypted_chunk = encryption_service.encrypt(chunk)
            yield encrypted_chunk
```

### 캐싱
- 자주 다운로드되는 파일은 복호화 결과 캐싱 고려
- Redis 또는 메모리 캐시 활용

## 8. 테스트

### 암호화/복호화 테스트
```python
import pytest
from app.shared.utils.encryption import get_encryption_service

def test_encryption():
    service = get_encryption_service()

    # 원본 데이터
    original = b"sensitive data"

    # 암호화
    encrypted = service.encrypt(original)
    assert encrypted != original

    # 복호화
    decrypted = service.decrypt(encrypted)
    assert decrypted == original
```

### 파일 업로드 테스트
```python
from fastapi.testclient import TestClient
from io import BytesIO

def test_file_upload(client: TestClient):
    file_content = b"test file content"
    files = {"file": ("test.txt", BytesIO(file_content))}

    response = client.post("/api/v1/chat/upload", files=files)
    assert response.status_code == 200

    # 파일이 암호화되어 저장되었는지 확인
    file_path = response.json()["file_path"]
    with open(file_path, "rb") as f:
        stored_content = f.read()
        # 저장된 내용은 원본과 달라야 함 (암호화됨)
        assert stored_content != file_content
```

## 9. 트러블슈팅

### 복호화 실패
```python
ValueError: Failed to decrypt data: invalid token
```
**원인**:
- 잘못된 암호화 키 사용
- 파일이 암호화되지 않았거나 손상됨

**해결**:
- SECRET_KEY 또는 FILE_ENCRYPTION_KEY 확인
- 파일 무결성 검증

### 성능 저하
**증상**: 대용량 파일 업로드/다운로드 시 느림

**해결**:
- 청크 단위 스트리밍 처리
- 비동기 처리 (Celery 작업)
- CDN 활용 (복호화 후 임시 캐싱)

## 10. 마이그레이션 가이드

### 기존 암호화되지 않은 파일 마이그레이션

```python
import os
from app.shared.utils.encryption import get_encryption_service

def migrate_existing_files(directory: str):
    """기존 파일을 암호화된 버전으로 마이그레이션"""
    encryption_service = get_encryption_service()

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        # 원본 읽기
        with open(file_path, 'rb') as f:
            content = f.read()

        # 암호화
        encrypted = encryption_service.encrypt(content)

        # 백업 생성
        backup_path = f"{file_path}.backup"
        os.rename(file_path, backup_path)

        # 암호화된 버전 저장
        with open(file_path, 'wb') as f:
            f.write(encrypted)

        print(f"Migrated: {filename}")
```

---

## 요약

Focus Mate의 파일 암호화 시스템은:
- ✅ **자동 암호화**: 업로드 시 자동으로 암호화
- ✅ **투명한 복호화**: 다운로드 시 자동으로 복호화
- ✅ **강력한 보안**: Fernet (AES-128) 사용
- ✅ **쉬운 통합**: 기존 코드 변경 최소화
- ✅ **성능 최적화**: 스트리밍 및 캐싱 지원

추가 질문이나 문제가 있으면 개발팀에 문의하세요.
