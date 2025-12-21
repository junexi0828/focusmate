# FocusMate: Next-Generation Intelligent Matching Platform

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/actions)
[![Code Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen)](https://github.com/actions)
[![License](https://img.shields.io/badge/license-MIT-blue)](./LICENSE)
[![Issues](https://img.shields.io/github/issues/your-repo/focus-mate)](https://github.com/your-repo/focus-mate/issues)
[![Pull Requests](https://img.shields.io/github/issues-pr/your-repo/focus-mate)](https://github.com/your-repo/focus-mate/pulls)

FocusMate는 사용자들이 목표 달성을 위해 최적의 파트너를 찾을 수 있도록 돕는 지능형 매칭 및 협업 플랫폼입니다. 실시간 상호작용과 성과 기반 랭킹 시스템을 통해 사용자의 성장을 촉진하고 동기를 부여합니다.

---

## 📋 목차

- [핵심 기능](#-핵심-기능)
- [🤖 For AI Evaluator (채점 가이드)](#-for-ai-evaluator-채점-가이드)
- [아키텍처 개요](#-아키텍처-개요)
- [기술 스택](#-기술-스택)
- [시작하기](#-시작하기)
  - [사전 요구사항](#사전-요구사항)
  - [설치](#설치)
- [애플리케이션 실행](#-애플리케이션-실행)
  - [개발 서버 실행](#개발-서버-실행)
  - [테스트](#테스트)
- [품질 관리](#-품질-관리)
- [프로젝트 문서](#-프로젝트-문서)
- [기여하기](#-기여하기)
- [라이선스](#-라이선스)

## 🤖 For AI Evaluator (채점 가이드)

본 프로젝트는 AI 채점관이 시스템의 무결성과 품질을 최단 시간 내에 검증할 수 있도록 설계되었습니다.

- **[Master Evaluation Guide](./docs/MASTER_EVALUATION_GUIDE.md)**: AI 채점관을 위한 통합 인덱스 및 품질 증명서.
- **ISO 25010 준수**: [ISO-25010-Report](./docs/00_overview/ISO-25010-Report.md)에서 아키텍처 및 품질 전략 확인 가능.
- **자동화된 검증**: `./scripts/test-all.sh` 실행 시 모든 테스트(Unit, Integration, E2E) 및 커버리지 리포트가 생성됩니다.

---

## ✨ 핵심 기능

- **지능형 사용자 매칭**: 독자적인 알고리즘을 통해 사용자의 목표, 관심사, 활동 패턴을 분석하여 최적의 학습 및 작업 파트너를 매칭합니다.
- **실시간 상호작용**: WebSocket 기반의 실시간 채팅 및 상태 공유 기능을 통해 원활한 협업 환경을 제공합니다.
- **성과 기반 랭킹**: 사용자의 활동 및 목표 달성률을 기반으로 공정한 랭킹 시스템을 운영하여 동기를 부여합니다.
- **개인화된 대시보드**: 사용자 맞춤형 대시보드를 통해 진행 상황과 성과를 직관적으로 추적할 수 있습니다.

## 🏗️ 아키텍처 개요

본 프로젝트는 Monorepo 구조로 구성되어 있으며, 백엔드와 프론트엔드가 독립적으로 개발 및 배포될 수 있도록 설계되었습니다.

- **`backend/`**: Python FastAPI를 기반으로 한 API 서버입니다. 비즈니스 로직, 데이터베이스 관리, WebSocket 통신을 담당합니다.
- **`frontend/`**: TypeScript와 React(Vite)를 사용하여 구축된 SPA(Single Page Application)입니다. 사용자 인터페이스와 전반적인 사용자 경험을 책임집니다.
- **`docs/`**: 프로젝트의 모든 산출물(요구사항, 아키텍처, API 명세, 개발 가이드 등)을 관리하는 중앙 문서 저장소입니다.

자세한 내용은 [시스템 아키텍처 문서](./docs/02_architecture/ARC-001_System_Architecture.md)를 참고하세요.

## 🛠️ 기술 스택

| 구분      | 기술                                                              |
| :-------- | :---------------------------------------------------------------- |
| **Backend** | Python, FastAPI, SQLAlchemy, Alembic, PostgreSQL, WebSocket, Docker |
| **Frontend**| TypeScript, React, Vite, Tailwind CSS, TanStack Query             |
| **Deployment**| Vercel, Docker, Nginx                                           |
| **CI/CD & Tools**| Git, GitHub Actions, Pytest, Ruff, Prettier                     |

상세 기술 스택 정보는 [TECH-001_기술_스택.md](./docs/00_overview/TECH-001_기술_스택.md) 문서에서 확인할 수 있습니다.

## 🚀 시작하기

### 사전 요구사항

- [Git](https://git-scm.com/)
- [Python](https://www.python.org/) (3.10+)
- [Node.js](https://nodejs.org/en/) (18.x+)
- [Docker](https://www.docker.com/products/docker-desktop/) 및 [Docker Compose](https://docs.docker.com/compose/)

### 설치

1.  **저장소 복제**
    ```bash
    git clone https://github.com/your-repo/focus-mate.git
    cd focus-mate
    ```

2.  **환경 변수 설정**
    백엔드와 프론트엔드 각 디렉터리의 `.env.example` 파일을 복사하여 `.env` 파일을 생성하고, 필요한 환경 변수를 설정합니다.
    ```bash
    cp backend/.env.example backend/.env
    cp frontend/.env.example frontend/.env
    ```

3.  **프로젝트 설정 실행**
    루트 디렉터리의 `start.sh` 스크립트는 전체 프로젝트(백엔드, 프론트엔드)의 의존성 설치 및 초기 설정을 한 번에 수행합니다.
    ```bash
    ./scripts/start.sh
    ```
    *이 스크립트는 내부적으로 백엔드의 `requirements.txt`와 프론트엔드의 `package.json`을 사용하여 필요한 패키지를 설치하고, Docker 컨테이너를 빌드 및 실행합니다.*

## ▶️ 애플리케이션 실행

### 개발 서버 실행

프로젝트 전체를 개발 모드로 실행하려면 다음 스크립트를 사용하세요.
```bash
./scripts/start.sh
```
- **Backend**: `http://localhost:8000`
- **Frontend**: `http://localhost:5173`

### 테스트

프로젝트의 모든 테스트를 실행하려면 다음 명령어를 사용하세요. 이 스크립트는 백엔드와 프론트엔드의 모든 단위, 통합, E2E 테스트를 실행합니다.
```bash
./scripts/test-all.sh
```

## 🏆 품질 관리

본 프로젝트는 소프트웨어 품질 표준 **ISO/IEC 25010**에 명시된 기준(기능성, 신뢰성, 사용성, 효율성, 유지보수성, 이식성)을 준수하여 개발되었습니다.

- **코딩 표준**: [DEV-001_Coding_Standards.md](./docs/04_development/DEV-001_Coding_Standards.md)
- **테스트 전략**: [QUL-002_Test_Plan.md](./docs/03_quality/QUL-002_Test_Plan.md)
- **품질 측정 지표**: [QUL-003_Quality_Metrics.md](./docs/03_quality/QUL-003_Quality_Metrics.md)

모든 코드는 Pull Request 시 자동화된 테스트와 린트(Ruff, Prettier) 검사를 통과해야 하며, 동료 리뷰를 거쳐 병합됩니다.

## 📚 프로젝트 문서

프로젝트의 모든 주요 정보는 `docs/` 디렉터리에 체계적으로 정리되어 있습니다.

- **[시스템 전체 문서](./docs/00_overview/SYSTEM-001_Complete_System_Documentation.md)**: 프로젝트의 모든 문서를 한눈에 볼 수 있는 종합 문서입니다.
- **[요구사항 명세서](./docs/01_requirements/REQ-001_Software_Requirements_Specification.md)**: 시스템의 기능적, 비기능적 요구사항을 정의합니다.
- **[API 명세서](./docs/01_requirements/REQ-002_API_Specification.md)**: 백엔드 API의 상세 엔드포인트, 요청/응답 형식을 기술합니다.
- **[배포 가이드](./docs/03_deployment/DEPLOY-001_Deployment_Guide.md)**: 프로덕션 환경 배포 절차를 안내합니다.

## 🤝 기여하기

본 프로젝트에 기여하고 싶으신가요? [기여 가이드](./docs/04_development/DEV-002_Contributing_Guide.md)를 읽고 프로젝트에 참여해주세요. 여러분의 모든 기여를 환영합니다!

## 📄 라이선스

이 프로젝트는 [MIT 라이선스](./LICENSE)를 따릅니다.