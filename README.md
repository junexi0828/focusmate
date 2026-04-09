# FocusMate

[![CI/CD Pipeline](https://github.com/junexi0828/focusmate/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/junexi0828/focusmate/actions/workflows/ci-cd.yml)
[![License](https://img.shields.io/badge/license-MIT-blue)](./LICENSE)
[![Issues](https://img.shields.io/github/issues/junexi0828/focusmate)](https://github.com/junexi0828/focusmate/issues)
[![Pull Requests](https://img.shields.io/github/issues-pr/junexi0828/focusmate)](https://github.com/junexi0828/focusmate/pulls)

FocusMate는 혼자 하기 어려운 집중을 실시간 룸, 타이머, 상태 공유, 채팅, 통계로 바꾸는 생산성 웹앱입니다.
공부하는 사람, 사이드 프로젝트를 하는 메이커, 분산된 팀이 "같이 집중하는 환경"을 가볍게 열고 바로 들어갈 수 있도록 설계했습니다.

## What Is FocusMate

화상 회의는 무겁고, 메신저는 산만하고, 혼자 하는 집중은 쉽게 끊깁니다.
FocusMate는 그 사이에 있는 제품입니다.

- 빠르게 방을 만들고 바로 집중 세션을 시작할 수 있습니다.
- 같은 방에 있는 사람들의 상태와 진행 흐름을 실시간으로 볼 수 있습니다.
- 타이머, 휴식, 참여자 흐름이 하나의 화면 안에서 자연스럽게 연결됩니다.
- 개인 기록과 팀 단위 성과를 누적해 반복 사용의 동기를 만듭니다.

## Why It Matters

FocusMate가 해결하려는 문제는 단순한 타이머 부족이 아닙니다.
문제는 "집중을 계속하게 만드는 구조"가 없다는 점입니다.

- 혼자 공부하거나 일하면 쉽게 흐름이 끊깁니다.
- 온라인 협업 툴은 집중보다 회의와 커뮤니케이션에 최적화돼 있습니다.
- 생산성 앱은 많지만, 함께 달리는 감각까지 주는 제품은 많지 않습니다.

FocusMate는 이런 상황에서 "같이 들어와서, 같이 달리고, 각자 성과를 쌓는" 경험을 제공합니다.

## Core Experience

1. 사용자는 집중 룸을 직접 만들거나 기존 룸에 참여합니다.
2. 집중 시간과 휴식 시간을 설정하고 세션을 시작합니다.
3. 참여자 상태, 타이머, 채팅, 알림을 보면서 흐름을 유지합니다.
4. 세션이 끝나면 기록과 통계가 누적되고, 다음 집중으로 다시 이어집니다.

## Key Features

- 실시간 집중 룸: 공부, 작업, 스프린트에 맞는 룸을 만들고 참여할 수 있습니다.
- 집중 타이머: 작업 시간과 휴식 시간을 조절하며 반복 가능한 세션 흐름을 만들 수 있습니다.
- 참여자 상태 공유: 누가 들어와 있고 어떤 흐름으로 움직이는지 한눈에 파악할 수 있습니다.
- 실시간 채팅: 같은 세션 안에서 짧고 가벼운 상호작용을 유지할 수 있습니다.
- 매칭 기능: 혼자 시작하기 어려운 사용자를 위해 파트너 또는 그룹 연결 흐름을 제공합니다.
- 대시보드와 통계: 집중 시간, 세션 수, 목표 달성률 등 누적된 성과를 확인할 수 있습니다.
- 팀과 랭킹: 팀 단위 경쟁과 동기 부여를 위한 구조를 지원합니다.
- 커뮤니티 확장성: 단순 타이머 앱을 넘어, 반복 사용 가능한 협업형 생산성 경험으로 확장할 수 있습니다.

## Who It Is For

- 혼자 공부하지만 혼자만의 루틴으로는 오래 유지하기 어려운 학생
- 사이드 프로젝트나 포트폴리오 작업을 꾸준히 밀어야 하는 메이커
- 가벼운 집중 세션을 운영하고 싶은 스터디 리더와 커뮤니티 운영자
- 화상 회의보다 덜 무겁고, 메신저보다 덜 산만한 협업 공간이 필요한 팀

## Product Positioning

FocusMate는 단순한 Pomodoro 타이머가 아닙니다.
또한 무거운 회의 중심 협업 툴도 아닙니다.

이 제품은 "집중을 시작하게 만들고, 유지하게 만들고, 다시 돌아오게 만드는" 데 초점을 둔 웹앱입니다.
즉, 개인 생산성과 가벼운 협업 사이를 연결하는 실시간 집중 플랫폼입니다.

## Quick Start

### Prerequisites

- [Git](https://git-scm.com/)
- [Python](https://www.python.org/) 3.10+
- [Node.js](https://nodejs.org/en/) 18+
- [Docker](https://www.docker.com/products/docker-desktop/) and Docker Compose

### Installation

```bash
git clone https://github.com/junexi0828/focusmate.git
cd focusmate
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
./scripts/start.sh
```

### Local Development

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`

## Architecture

FocusMate는 프론트엔드와 백엔드가 분리된 모노레포 구조로 구성되어 있습니다.

- `frontend/`: React, TypeScript, Vite 기반의 SPA
- `backend/`: FastAPI 기반의 API, 실시간 통신, 데이터 처리 계층
- `docs/`: 요구사항, 아키텍처, 개발 및 운영 문서

자세한 시스템 설명은 [시스템 아키텍처 문서](./docs/02_architecture/ARC-001_System_Architecture.md)에서 확인할 수 있습니다.

## Repository Guide

- 제품 및 개요 문서: [docs/00_overview](./docs/00_overview/)
- 요구사항 문서: [docs/01_requirements](./docs/01_requirements/)
- 아키텍처 문서: [docs/02_architecture](./docs/02_architecture/)
- 개발 문서: [docs/04_development](./docs/04_development/)
- 운영 문서: [docs/05_operations](./docs/05_operations/)

## Open Source

FocusMate는 공개 저장소로 운영됩니다.
이슈 제안, 버그 리포트, 개선 아이디어, 기능 제안은 언제든 환영합니다.

- Issues: [GitHub Issues](https://github.com/junexi0828/focusmate/issues)
- Discussions: [GitHub Discussions](https://github.com/junexi0828/focusmate/discussions)

## License

This project is licensed under the [MIT License](./LICENSE).
