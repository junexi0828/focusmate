# OPS-009: Logging and Audit Policy

## 1. 개요 (Overview)
본 문서는 FocusMate 시스템의 로그 수집, 보관 및 감사 정책을 정의합니다. 본 정책은 **ISO/IEC 25010 (유지보수성 및 책임 추적성)** 및 **ISO/IEC 27001 (로그 및 모니터링 관리)** 표준을 준수하며, 시스템 이상 징후의 신속한 파악과 사후 분석을 목적으로 합니다.

## 2. 로그 설계 철학 (Logging Philosophy)
FocusMate의 로그 시스템은 다음 세 가지 원칙을 따릅니다:
1.  **가시성 (Visibility)**: 시스템의 모든 주요 상태 변화(Lifecycle)는 기록되어야 한다.
2.  **불변성 (Immutability)**: 생성된 로그는 인위적으로 수정되지 않으며, 기록된 원형을 유지한다.
3.  **자원 효율성 (Resource Efficiency)**: NAS 등 한정된 인프라 자원을 고려하여 최적화된 보관 주기를 유지한다.

## 3. 로그 수집 및 관리 기준

### 3.1 로그 레벨 규격
| 레벨 | 정의 | 조치 사항 |
| :--- | :--- | :--- |
| **CRITICAL** | 시스템 운영 불능 (DB 다운, 보안 침해) | 즉시 슬랙 알림 및 관리자 긴급 개입 |
| **ERROR** | 특정 기능 실패 (이메일 발송 실패, 마이그레이션 오류) | 실시간 로그 감시기(Log Alerter)를 통한 알림 |
| **WARNING** | 잠재적 위협 (CPU 부하, 디스크 부족) | 모니터링 대시보드 확인 및 예방 조치 |
| **INFO** | 정상적인 상태 변화 (서버 시작/종료, Agent 루틴 완료) | 히스토리 추적용 기록 |

### 3.2 핵심 로그 구성
| 로그 유형 | 저장 경로 | 주요 내용 | 생성 주체 | 호스트 |
| :--- | :--- | :--- | :--- | :--- |
| **App Log** | `logs/app.log` | API 요청, 런타임 에러 | `start-nas.sh` (Uvicorn) | NAS |
| **Monitor Log** | `logs/monitor.log` | 상태 점검 및 재시작 기록 | `nas_monitor.sh` | NAS |
| **Audit Log** | `logs/architect_agent_history.log` | AI Agent 작업 내역 | `architect_agent.sh` | Mac |

### 3.3 알림 채널 (Slack Alerts Mapping)
| 알림 주체 | 실행 방식 | 알림 조건 | 특이 사항 |
| :--- | :--- | :--- | :--- |
| **Log Alerter** | **24/7 상주** | `app.log` 내 ERROR 패턴 감지 | 즉각적인 장애 대응용 |
| **NAS Monitor** | **4시간 주기** | CPU/RAM/Disk 임계치 초과, 서비스 다운 | 시스템 건전성 관리용 |
| **Daily Report** | **24시간 주기** | 매일 정해진 시간 (통계 요약) | 비즈니스 지표 및 일일 요약 |

## 4. 유지보수 및 보관 정책 (Retention Policy)

### 4.1 로그 로테이션 (Log Rotation)
NAS의 디스크 용량 오버플로우를 방지하기 위해 다음과 같은 자동 삭제 정책을 시행합니다:
-   **보관 기간**: 생성일로부터 **3일 (72시간)**
-   **실행 주기**: 시놀로지 작업 스케줄러에 설정된 4시간 주기로 `nas_monitor.sh` 실행 시 자동 수행
-   **삭제 기준**: `find "$LOG_DIR" -name "*.log" -mtime +3 -delete`

### 4.2 감사 (Audit) 절차
1.  **로컬 감사**: Architect Agent가 로컬(Mac)에서 수행한 작업 내역을 `history.log`를 통해 검토한다. Agent 로그는 NAS로 동기화되지 않으며 로컬에만 보관한다.
2.  **원격 감사**: NAS 장애 시 SSH 접근을 통해 `app.log`와 `monitor.log`를 확인하며, 필요 시 로컬로 복사하여 분석한다.
3.  **동기화 검증**: 로컬(Master) 소스와 NAS(Slave) 간의 설정 일관성을 배포 시마다 검증한다.

## 5. 지속적 개선 (Continuous Improvement)
시스템이 고도화됨에 따라 단순 파일 로그를 넘어 ElasticSearch 또는 Grafana Loki와 같은 **중앙 집중형 로그 시스템**으로의 확장을 고려하며, 이상 징후 탐지 AI 모델을 도입하여 로그 분석을 자동화한다.

---
**최종 업데이트**: 2026-01-16
**준수 표준**: ISO/IEC 25010, ISO/IEC 27001 기준 준수
