---
id: GEN-002
title: Industry Benchmarks & Technology Analysis
version: 1.0
status: Approved
date: 2025-12-12
author: Focus Mate Team
iso_standard: ISO/IEC 25010 Comparative Analysis
---

# 업계 표준 및 벤치마킹 분석

## 1. "Vite + TanStack Router"가 표준인가요?

**네, "애플리케이션" 분야에서는 표준입니다.**
이커머스나 뉴스 사이트 같은 "웹사이트" 분야에서는 **Next.js**가 표준이지만, SaaS, 관리자 패널, 생산성 도구 같은 복잡한 **"웹 애플리케이션"** 분야에서는 **Vite** 생태계가 지배적인 표준입니다.

특히 **TanStack Router**는 기존의 `react-router-dom`을 대체하며, 높은 복잡도를 가진 프로젝트에서 타입 안정성과 캐싱 효율을 위해 선택하는 최신 기술 표준(Emerging Standard)입니다.

---

## 2. 유사한 기업들은 무엇을 쓰나요?

Focus Mate와 유사한 고품질 제품들이 어떤 기술을 선택했는지 분석했습니다.

### 그룹 A: "프로 도구(Pro Tool)" 아키텍처 (SPA / Vite 계열)
*Focus Mate가 지향하는 방향입니다.*
이 제품들은 긴 세션 시간, 복잡한 로컬 상태 관리, 즉각적인 반응속도를 최우선으로 합니다.

| 제품 | 카테고리 | 스택 특성 | 선택 이유 |
| :--- | :--- | :--- | :--- |
| **Linear** | 이슈 트래커 | **Advanced SPA** | 페이지 이동 시 0.01초의 지연도 허용하지 않는 즉각성을 위해 SPA를 고수합니다. |
| **Figma** | 디자인 도구 | **WebGL / SPA** | 브라우저 안에서 돌아가는 거대한 프로그램이므로 서버 렌더링이 의미가 없습니다. |
| **Discord** | 메신저 | **SPA** | 실시간 통신과 상태 유지가 핵심이며, 검색 엔진 노출이 필요 없습니다. |
| **Notion** | 워크스페이스 | **Hybrid SPA** | 앱 페이지(`notion.so/app`) 진입 후에는 데스크탑 앱처럼 동작합니다. |

### 그룹 B: "콘텐츠 플랫폼" 아키텍처 (SSR / Next.js 계열)
이 제품들은 많은 사람에게 검색되고(SEO), 첫 화면이 빨리 뜨는 것이 매출과 직결됩니다.

| 제품 | 카테고리 | 스택 특성 | 선택 이유 |
| :--- | :--- | :--- | :--- |
| **Netflix** | OTT | **Next.js** | 수백만 개의 작품 페이지가 구글 검색에 노출되어야 합니다. |
| **TikTok** | 소셜 미디어 | **Next.js** | 공유된 링크의 미리보기가 중요하고 모바일 웹 로딩이 빨라야 합니다. |
| **Nike** | 쇼핑몰 | **Next.js** | 상품 검색 노출이 곧 매출입니다. |

---

## 3. Focus Mate를 위한 결론

Focus Mate는 넷플릭스 같은 **콘텐츠 사이트**가 아니라, 리니어(Linear)나 노션(Notion) 같은 **생산성 도구**입니다.
따라서 **Vite + SPA 아키텍처**를 채택하는 것은 공학적으로 올바른 결정입니다.

이 선택은 다음을 최적화합니다:
1.  **몰입 경험 (Flow State)**: 사용 중 끊김 없음.
2.  **앱 사용성 (App-Feel)**: 타이머 등 UI 요소의 상태 유지.
3.  **단순성 (Simplicity)**: Python AI 백엔드와 React UI의 명확한 분리.
