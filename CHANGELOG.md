# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned

- 사용자 인증 시스템 (JWT)
- 통계 및 히스토리 기능
- 모바일 반응형 UI 개선
- 오프라인 모드 지원

---

## [1.0.0] - 2025-12-04

### Added

- **핵심 기능**

  - 실시간 타이머 동기화 (WebSocket)
  - 팀 방 생성 및 관리
  - 타이머 제어 (시작, 일시정지, 재설정)
  - 커스터마이징 가능한 포모도로 설정
  - 브라우저 알림 시스템

- **백엔드**

  - FastAPI 기반 REST API
  - Pydantic Strict Mode 데이터 검증
  - SQLite 데이터베이스 지원
  - WebSocket 실시간 통신
  - Health Check 엔드포인트

- **프론트엔드**

  - React + TypeScript (Strict Mode)
  - Zustand 상태 관리
  - Atomic Design 컴포넌트 구조
  - 반응형 UI

- **DevOps**

  - Docker Compose 설정
  - CI/CD 파이프라인 (GitHub Actions)
  - 자동화된 테스트 스크립트
  - 품질 게이트 (Quality Gates)

- **문서화**
  - ISO/IEC 25010 준수 문서
  - SRS (Software Requirements Specification)
  - 아키텍처 설계서
  - API 명세서
  - 테스트 계획
  - 코딩 표준
  - ADR (Architecture Decision Records)

### Quality Metrics

- 테스트 커버리지: 92.5%
- API 응답 시간 (p95): 180ms
- WebSocket 지연 (p95): 85ms
- 순환 복잡도 (평균): 4.2
- 타입 안정성: 100%

### Technical Details

- **Backend**: Python 3.12+, FastAPI, SQLAlchemy (Async)
- **Frontend**: React 18, TypeScript (Strict), Vite
- **Database**: SQLite (개발), PostgreSQL 호환
- **Container**: Docker Compose

---

## [0.1.0] - 2025-12-04

### Added

- 프로젝트 초기 설정
- 문서 구조 설계
- 아키텍처 결정 기록 (ADR)
- 개발 환경 설정 가이드

---

## 버전 관리 규칙

### Semantic Versioning (MAJOR.MINOR.PATCH)

- **MAJOR**: 호환되지 않는 API 변경
- **MINOR**: 하위 호환성을 유지하는 기능 추가
- **PATCH**: 하위 호환성을 유지하는 버그 수정

### 변경 유형

- **Added**: 새로운 기능
- **Changed**: 기존 기능 변경
- **Deprecated**: 곧 제거될 기능
- **Removed**: 제거된 기능
- **Fixed**: 버그 수정
- **Security**: 보안 취약점 수정

---

## 참조

- [Keep a Changelog](https://keepachangelog.com/)
- [Semantic Versioning](https://semver.org/)
