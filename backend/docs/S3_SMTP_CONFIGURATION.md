# S3 및 SMTP 환경변수 설정 가이드

이 문서는 FocusMate 백엔드에서 AWS S3 파일 저장소와 SMTP 이메일 서비스를 설정하는 방법을 설명합니다.

## 목차

1. [SMTP 이메일 설정](#smtp-이메일-설정)
2. [AWS S3 파일 저장소 설정](#aws-s3-파일-저장소-설정)
3. [환경변수 설정 예시](#환경변수-설정-예시)
4. [설정 확인 및 테스트](#설정-확인-및-테스트)
5. [문제 해결](#문제-해결)

---

## SMTP 이메일 설정

### 개요

SMTP 이메일 서비스는 다음 기능에서 사용됩니다:

- 사용자 인증 이메일 (인증 요청, 승인, 반려 알림)
- 팀 초대 이메일
- 기타 시스템 알림

### 지원하는 SMTP 서비스

- **Gmail** (권장 - 개발 환경)
- **AWS SES** (권장 - 프로덕션)
- **SendGrid**
- **Mailgun**
- 기타 SMTP 호환 서비스

### Gmail 설정 (개발 환경)

1. **Google 계정 설정**

   - Google 계정 → 보안 → 2단계 인증 활성화
   - 앱 비밀번호 생성: [Google 계정 관리](https://myaccount.google.com/apppasswords)

2. **환경변수 설정**
   ```bash
   SMTP_ENABLED=true
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-16-char-app-password
   SMTP_FROM_EMAIL=noreply@focusmate.com
   SMTP_FROM_NAME=Focus Mate
   SMTP_USE_TLS=true
   ```

### AWS SES 설정 (프로덕션)

1. **AWS SES 설정**

   - AWS 콘솔 → SES → 이메일 주소/도메인 인증
   - SMTP 자격 증명 생성

2. **환경변수 설정**
   ```bash
   SMTP_ENABLED=true
   SMTP_HOST=email-smtp.us-east-1.amazonaws.com  # 리전에 따라 변경
   SMTP_PORT=587
   SMTP_USER=your-smtp-username
   SMTP_PASSWORD=your-smtp-password
   SMTP_FROM_EMAIL=noreply@yourdomain.com
   SMTP_FROM_NAME=Focus Mate
   SMTP_USE_TLS=true
   ```

### SendGrid 설정

1. **SendGrid 설정**

   - SendGrid 계정 생성
   - API 키 생성 또는 SMTP 자격 증명 확인

2. **환경변수 설정**
   ```bash
   SMTP_ENABLED=true
   SMTP_HOST=smtp.sendgrid.net
   SMTP_PORT=587
   SMTP_USER=apikey
   SMTP_PASSWORD=your-sendgrid-api-key
   SMTP_FROM_EMAIL=noreply@yourdomain.com
   SMTP_FROM_NAME=Focus Mate
   SMTP_USE_TLS=true
   ```

### 환경변수 설명

| 변수명            | 필수   | 기본값                  | 설명                                |
| ----------------- | ------ | ----------------------- | ----------------------------------- |
| `SMTP_ENABLED`    | 아니오 | `false`                 | SMTP 이메일 서비스 활성화 여부      |
| `SMTP_HOST`       | 예     | `smtp.gmail.com`        | SMTP 서버 호스트                    |
| `SMTP_PORT`       | 예     | `587`                   | SMTP 서버 포트 (587: TLS, 465: SSL) |
| `SMTP_USER`       | 예     | `""`                    | SMTP 인증 사용자명                  |
| `SMTP_PASSWORD`   | 예     | `""`                    | SMTP 인증 비밀번호                  |
| `SMTP_FROM_EMAIL` | 예     | `noreply@focusmate.com` | 발신자 이메일 주소                  |
| `SMTP_FROM_NAME`  | 예     | `Focus Mate`            | 발신자 이름                         |
| `SMTP_USE_TLS`    | 아니오 | `true`                  | TLS 암호화 사용 여부                |

---

## AWS S3 파일 저장소 설정

### 개요

AWS S3는 프로덕션 환경에서 파일 저장소로 사용됩니다. 다음 기능에서 사용됩니다:

- 사용자 인증 문서 업로드
- 채팅 파일 첨부
- 팀 프로필 이미지
- 기타 사용자 업로드 파일

### 로컬 저장소 vs S3

- **로컬 저장소** (`STORAGE_TYPE=local`): 개발 환경용, 파일을 서버 디스크에 저장
- **S3 저장소** (`STORAGE_TYPE=s3`): 프로덕션 환경용, AWS S3에 저장

### AWS S3 설정 단계

#### 1. AWS 계정 및 S3 버킷 생성

1. **AWS 콘솔 접속**

   - [AWS 콘솔](https://console.aws.amazon.com/) 로그인

2. **S3 버킷 생성**

   ```bash
   # AWS CLI 사용 시
   aws s3 mb s3://focusmate-uploads --region us-east-1
   ```

   또는 AWS 콘솔에서:

   - S3 → 버킷 만들기
   - 버킷 이름: `focusmate-uploads` (고유한 이름)
   - 리전: `us-east-1` (또는 원하는 리전)

3. **버킷 정책 설정** (선택사항)
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "PublicReadGetObject",
         "Effect": "Allow",
         "Principal": "*",
         "Action": "s3:GetObject",
         "Resource": "arn:aws:s3:::focusmate-uploads/*"
       }
     ]
   }
   ```

#### 2. IAM 사용자 및 액세스 키 생성

1. **IAM 사용자 생성**

   - IAM → 사용자 → 사용자 추가
   - 사용자 이름: `focusmate-s3-user`
   - 액세스 유형: 프로그래밍 방식 액세스

2. **권한 정책 연결**

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "s3:PutObject",
           "s3:GetObject",
           "s3:DeleteObject",
           "s3:ListBucket"
         ],
         "Resource": [
           "arn:aws:s3:::focusmate-uploads",
           "arn:aws:s3:::focusmate-uploads/*"
         ]
       }
     ]
   }
   ```

3. **액세스 키 저장**
   - 액세스 키 ID와 비밀 액세스 키를 안전하게 저장

#### 3. 환경변수 설정

```bash
# 파일 저장소 타입 설정
STORAGE_TYPE=s3

# AWS S3 설정
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_S3_BUCKET=focusmate-uploads
AWS_S3_REGION=us-east-1

# 파일 크기 제한 (10MB)
STORAGE_MAX_FILE_SIZE=10485760
```

### 환경변수 설명

| 변수명                  | 필수         | 기본값      | 설명                               |
| ----------------------- | ------------ | ----------- | ---------------------------------- |
| `STORAGE_TYPE`          | 예           | `local`     | 저장소 타입 (`local` 또는 `s3`)    |
| `AWS_ACCESS_KEY_ID`     | S3 사용 시   | `""`        | AWS 액세스 키 ID                   |
| `AWS_SECRET_ACCESS_KEY` | S3 사용 시   | `""`        | AWS 비밀 액세스 키                 |
| `AWS_S3_BUCKET`         | S3 사용 시   | `""`        | S3 버킷 이름                       |
| `AWS_S3_REGION`         | S3 사용 시   | `us-east-1` | AWS 리전                           |
| `STORAGE_LOCAL_PATH`    | 로컬 사용 시 | `./uploads` | 로컬 저장 경로                     |
| `STORAGE_MAX_FILE_SIZE` | 아니오       | `10485760`  | 최대 파일 크기 (바이트, 기본 10MB) |

---

## 환경변수 설정 예시

### 개발 환경 (.env)

```bash
# SMTP (Gmail 사용)
SMTP_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=dev@example.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@focusmate.com
SMTP_FROM_NAME=Focus Mate
SMTP_USE_TLS=true

# 파일 저장소 (로컬 사용)
STORAGE_TYPE=local
STORAGE_LOCAL_PATH=./uploads
STORAGE_MAX_FILE_SIZE=10485760
```

### 프로덕션 환경 (.env)

```bash
# SMTP (AWS SES 사용)
SMTP_ENABLED=true
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USER=your-ses-smtp-username
SMTP_PASSWORD=your-ses-smtp-password
SMTP_FROM_EMAIL=noreply@yourdomain.com
SMTP_FROM_NAME=Focus Mate
SMTP_USE_TLS=true

# 파일 저장소 (S3 사용)
STORAGE_TYPE=s3
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_S3_BUCKET=focusmate-uploads
AWS_S3_REGION=us-east-1
STORAGE_MAX_FILE_SIZE=10485760
```

---

## 설정 확인 및 테스트

### SMTP 설정 확인

1. **환경변수 확인**

   ```bash
   # Backend 디렉토리에서
   python -c "from app.core.config import settings; print(f'SMTP Enabled: {settings.SMTP_ENABLED}'); print(f'SMTP Host: {settings.SMTP_HOST}')"
   ```

2. **이메일 전송 테스트**

   ```python
   # Python REPL에서
   from app.infrastructure.email.email_service import EmailService
   from app.core.config import settings

   email_service = EmailService(
       smtp_host=settings.SMTP_HOST,
       smtp_port=settings.SMTP_PORT,
       from_email=settings.SMTP_FROM_EMAIL,
       from_name=settings.SMTP_FROM_NAME,
       smtp_user=settings.SMTP_USER,
       smtp_password=settings.SMTP_PASSWORD,
   )

   # 테스트 이메일 전송
   await email_service.send_verification_submitted_email(
       team_name="Test Team",
       leader_email="test@example.com"
   )
   ```

### S3 설정 확인

1. **환경변수 확인**

   ```bash
   # Backend 디렉토리에서
   python -c "from app.core.config import settings; print(f'Storage Type: {settings.STORAGE_TYPE}'); print(f'S3 Bucket: {settings.AWS_S3_BUCKET}')"
   ```

2. **S3 연결 테스트**

   ```python
   # Python REPL에서
   import boto3
   from app.core.config import settings

   s3_client = boto3.client(
       's3',
       aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
       aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
       region_name=settings.AWS_S3_REGION
   )

   # 버킷 목록 확인
   response = s3_client.list_buckets()
   print([bucket['Name'] for bucket in response['Buckets']])

   # 특정 버킷 접근 확인
   s3_client.head_bucket(Bucket=settings.AWS_S3_BUCKET)
   print(f"✅ Successfully connected to bucket: {settings.AWS_S3_BUCKET}")
   ```

---

## 문제 해결

### SMTP 관련 문제

#### 1. "Authentication failed" 오류

**원인**: 잘못된 사용자명/비밀번호 또는 앱 비밀번호 미사용 (Gmail)

**해결**:

- Gmail의 경우 앱 비밀번호 사용 확인
- AWS SES의 경우 SMTP 자격 증명 확인
- 비밀번호에 특수문자가 있는 경우 따옴표로 감싸기

#### 2. "Connection timeout" 오류

**원인**: 방화벽 또는 네트워크 문제

**해결**:

- 포트 587 (TLS) 또는 465 (SSL) 방화벽 허용 확인
- `SMTP_HOST` 값 확인
- 네트워크 연결 확인

#### 3. "TLS/SSL handshake failed" 오류

**원인**: TLS 설정 문제

**해결**:

- `SMTP_USE_TLS=true` 확인
- 포트 587 사용 시 TLS, 포트 465 사용 시 SSL 필요
- 일부 서비스는 `SMTP_USE_TLS=false` 필요

### S3 관련 문제

#### 1. "Access Denied" 오류

**원인**: IAM 권한 부족 또는 잘못된 액세스 키

**해결**:

- IAM 사용자 권한 정책 확인
- 액세스 키 ID와 비밀 액세스 키 확인
- 버킷 이름과 리전 확인

#### 2. "Bucket not found" 오류

**원인**: 버킷 이름 오타 또는 리전 불일치

**해결**:

- `AWS_S3_BUCKET` 값 확인
- `AWS_S3_REGION` 값이 버킷 생성 리전과 일치하는지 확인
- AWS 콘솔에서 버킷 존재 확인

#### 3. "Connection timeout" 오류

**원인**: 네트워크 문제 또는 AWS 서비스 장애

**해결**:

- 네트워크 연결 확인
- AWS 서비스 상태 확인: [AWS Status](https://status.aws.amazon.com/)
- VPC 엔드포인트 설정 확인 (VPC 내부에서 실행 시)

---

## 보안 권장사항

### SMTP

1. **비밀번호 관리**

   - 환경변수에 직접 저장하지 않고 시크릿 관리 서비스 사용 (AWS Secrets Manager, HashiCorp Vault 등)
   - 프로덕션 환경에서는 앱 비밀번호 또는 API 키 사용

2. **이메일 인증**
   - SPF, DKIM, DMARC 레코드 설정 (도메인 이메일 사용 시)
   - 발신자 이메일 주소 검증

### S3

1. **액세스 키 관리**

   - 최소 권한 원칙 적용 (필요한 권한만 부여)
   - 정기적으로 액세스 키 로테이션
   - 프로덕션 환경에서는 IAM 역할 사용 권장 (EC2, ECS 등)

2. **버킷 정책**

   - 공개 읽기 권한 최소화
   - 버전 관리 및 수명 주기 정책 설정
   - 암호화 활성화 (SSE-S3 또는 SSE-KMS)

3. **네트워크 보안**
   - VPC 엔드포인트 사용 (VPC 내부에서 실행 시)
   - CloudFront를 통한 CDN 사용 고려

---

## 추가 리소스

- [AWS S3 문서](https://docs.aws.amazon.com/s3/)
- [AWS SES 문서](https://docs.aws.amazon.com/ses/)
- [Gmail 앱 비밀번호 가이드](https://support.google.com/accounts/answer/185833)
- [SendGrid SMTP 설정](https://docs.sendgrid.com/for-developers/sending-email/getting-started-smtp)

---

**작성일**: 2025-12-13
**버전**: 1.0.0
**상태**: Production Ready ✅
