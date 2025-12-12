---
id: REQ-003
title: Requirements Management & Change Control Plan
version: 1.0
status: Approved
date: 2025-12-11
author: Focus Mate Team
iso_standard: ISO/IEC/IEEE 29148 Requirements Engineering
---

# 요구사항 관리 및 변경 통제 계획
(Requirements Management & Change Control Plan)

본 문서는 Focus Mate 프로젝트의 요구사항 생명주기를 관리하기 위한 정책을 기술합니다. ISO/IEC/IEEE 29148 (Requirements Engineering) 표준을 준용하여 프로세스를 수립했습니다.

---

## 1. 버전 관리 (Version Control)

### 1.1 문서 식별 규칙
모든 요구사항 문서는 다음과 같은 파일명 및 메타데이터 규칙을 따릅니다:
*   **파일명**: `SRS_{Type}_{Version}.md` (예: `SRS_CORE_v1.0.md`)
*   **버전 체계**: [SemVer](https://semver.org)를 변형하여 사용합니다.
    *   `MAJOR` (1.x): 아키텍처나 핵심 기능의 대대적 변경
    *   `MINOR` (x.1): 기존 기능의 수정 또는 하위 호환되는 새 기능 추가
    *   `PATCH` (x.x.1): 오타 수정, 문구 명확화 등 사소한 변경

### 1.2 베이스라인 (Baseline)
특정 개발 단계의 시작점(Sprint Start 등)에서 요구사항 문서의 버전을 동결(Freeze)하여 베이스라인으로 설정합니다. 베이스라인 이후의 변경은 **변경 통제 프로세스**를 통과해야 합니다.

---

## 2. 추적성 관리 (Traceability Management)

### 2.1 추적성 매트릭스 (RTM - Requirements Traceability Matrix)
모든 요구사항은 고유 ID를 가지며, 이는 설계, 코드, 테스트와 연결되어야 합니다.

**ID 규칙**: `REQ-{Module}-{Number}` (예: `REQ-TIMER-001`, `REQ-AUTH-005`)

| 요구사항 ID | 기능 설명 | 설계 컴포넌트 (Design) | 코드 모듈 (Code) | 테스트 케이스 ID (Test) |
| :--- | :--- | :--- | :--- | :--- |
| `REQ-TIMER-001` | 사용자는 타이머를 시작할 수 있어야 한다. | `TimerService` | `timer_service.py` | `TC-TIMER-01` |
| `REQ-AUTH-001` | 사용자는 이메일로 가입할 수 있어야 한다. | `AuthRouter` | `routers/auth.py` | `TC-AUTH-01` |

### 2.2 추적성 유지 전략
1.  **순방향 추적 (Forward Traceability)**: 요구사항 -> 설계 -> 구현 -> 테스트 (빠짐없는 구현 보장)
2.  **역방향 추적 (Backward Traceability)**: 코드 -> 요구사항 (골드 플레이팅 방지 - 요구사항 없는 기능 구현 금지)

---

## 3. 변경 통제 프로세스 (Change Control Process)

요구사항 변경은 프로젝트의 일정과 비용에 큰 영향을 미치므로 공식적인 절차를 따릅니다.

### 3.1 변경 요청 (Change Request) 프로세스
1.  **발의 (Initiation)**: 이해관계자가 변경 요청서(CR)를 작성합니다. (이유, 예상 효과 포함)
2.  **영향도 분석 (Impact Analysis)**:
    *   기술적 영향: 아키텍처 수정 필요 여부, 코드 수정 범위, 테스트 재작성 범위
    *   관리적 영향: 일정 지연 가능성, 비용 증가
3.  **승인/반려 (Decision)**: CCB(Change Control Board - PM, Tech Lead)가 승인 여부를 결정합니다.
4.  **반영 (Implementation)**:
    *   문서 업데이트 (SRS 판올림)
    *   베이스라인 업데이트
    *   이해관계자 통보

### 3.2 변경 관리 대장 예시

| CR ID | 날짜 | 요청자 | 변경 내용 요약 | 영향도/위험 | 상태 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `CR-001` | 2025-12-11 | 기획팀 | 타이머 최대 시간을 60분에서 120분으로 변경 | 낮음 (상수 변경) | **승인** |
| `CR-002` | 2025-12-12 | 마케팅 | 회원가입 시 전화번호 인증 필수화 | 높음 (DB 스키마 변경, SMS 비용) | **보류** |

---

## 4. 도구 및 인프라 (Tools)
*   **요구사항 저장소**: GitHub Repository (`docs/01_requirements/`)
*   **이슈 트래커**: GitHub Issues (Change Request 관리)
*   **협업 도구**: Slack (변경 사항 전파)
