---
id: GEN-001
title: Focus Mate Project Nature & Product Identity
version: 1.0
status: Approved
date: 2025-12-12
author: Focus Mate Team
iso_standard: ISO/IEC 25010 Quality in Use
---

# Project Nature & Product Identity

## [Home](../README.md) > [Overview](./README.md) > GEN-001

---

# Focus Mate: 프로젝트 컨셉 및 제품의 본질

## 1. 제품 정체성 ("소프트웨어의 본질")
**Focus Mate**는 단순한 콘텐츠 웹사이트가 아니라, **고품질 생산성 애플리케이션(High-Fidelity Productivity Application)**입니다. 사용자가 장시간 머물며 깊이 있는 작업을 수행하는 디지털 워크스페이스로서, 다음 요소가 필수적입니다:

*   **몰입감 (Immersive Experience)**: 페이지 로딩으로 인한 깜빡임 없이 작업에 집중할 수 있는 환경.
*   **즉각적인 반응 (Instant Feedback)**: 타이머 조작, 할 일 완료 등의 액션이 0.1초 이내에 반응해야 함.
*   **신뢰성 (Reliability)**: 세션 도중 네트워크가 불안정해도 타이머와 핵심 기능은 끊기지 않고 작동해야 함.

### 왜 "웹사이트(Website)"가 아닌 "애플리케이션(Application)"인가?
블로그나 쇼핑몰처럼 정보를 *탐색*하는 것이 주 목적이 아니라, 타이머를 켜고 업무를 수행하는 *행동(Action)*이 주 목적이기 때문입니다. 따라서 문서를 보여주는 방식(SSR)보다는 **상태를 관리하는 방식(SPA)**이 적합합니다.

---

## 2. 기술 철학 (Technical Philosophy)
우리의 기술 선택은 이러한 제품의 본질을 반영합니다.

### 프론트엔드: 클라이언트 중심 (Vite + TanStack Router)
*   **철학**: "브라우저는 강력한 플랫폼이다." 렌더링과 라우팅 처리를 브라우저로 가져와 네이티브 앱과 같은 사용성을 구현합니다.
*   **사용자 가치**: 클릭 시 흰 화면이 뜨지 않으며, 앱이 살아있는 것처럼 부드럽게 반응합니다.

### 백엔드: 성능 중심 (FastAPI)
*   **철학**: "무거운 작업은 서버에서." AI 연산, 통계 집계, 데이터 저장은 고성능 Python 비동기 서버가 담당합니다.
*   **사용자 가치**: 복잡한 데이터 처리가 UI를 멈추게(Freezing) 하지 않습니다.

---

## 3. 핵심 가치 제안 (Core Value Proposition)
1.  **몰입 (Flow)**: 느린 로딩이나 거슬리는 화면 전환을 제거하여 사용자의 몰입을 방해하지 않습니다.
2.  **프라이버시 (Privacy)**: 사용자 데이터를 안전하게 보호하며 불필요한 추적을 최소화합니다.
3.  **효율성 (Efficiency)**: 파워 유저를 위한 단축키와 커맨드 메뉴 등이 즉각적으로 반응합니다.
