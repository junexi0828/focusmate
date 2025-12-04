# Quick Fix Guide

## Python 3.14 호환성 문제 해결

### 문제

Python 3.14를 사용하면 `pydantic-core` 빌드가 실패합니다.

### 해결 방법

#### 방법 1: 자동 수정 스크립트 (권장)

```bash
cd backend
./scripts/fix-python.sh
```

이 스크립트는:

- Python 3.13 또는 3.12를 자동으로 찾아서 사용
- 기존 venv를 삭제하고 새로 생성
- 모든 의존성을 재설치

#### 방법 2: 수동 수정

```bash
cd backend

# 1. 기존 venv 삭제
rm -rf venv

# 2. Python 3.13으로 새 venv 생성
python3.13 -m venv venv

# 3. 활성화 및 의존성 설치
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### 방법 3: 호환성 플래그 사용 (임시)

Python 3.14를 계속 사용하려면:

```bash
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 확인

```bash
# Python 버전 확인
source venv/bin/activate
python --version  # Python 3.13.x 또는 3.12.x여야 함

# uvicorn 확인
which uvicorn  # venv/bin/uvicorn이어야 함

# 서버 시작
./run.sh
```

---

**Last Updated**: 2025-12-04
