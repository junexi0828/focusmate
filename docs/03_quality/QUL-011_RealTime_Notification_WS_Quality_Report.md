---
id: QUL-011
title: Real-Time Sync and Notification Quality Report
version: 1.0
status: Draft
date: 2026-01-08
author: Focus Mate Development Team
iso_standard: ISO/IEC 25010 (Software Quality)
related_docs:
  - QUL-001_Quality_Strategy_ISO25010.md
  - QUL-003_Quality_Metrics.md
  - ARC-017_Enterprise_Notification_System.md
---

# Real-Time Sync and Notification Quality Report

**문서 ID**: QUL-011  
**문서 버전**: 1.0  
**작성일**: 2026-01-08  
**표준 준수**: ISO/IEC 25010 (Software Quality Model)  
**최종 업데이트**: 2026-01-08  

---

## 1. 개요

### 1.1 목적
본 보고서는 FocusMate의 실시간 동기화(WebSocket) 및 알림 시스템 개선 작업에 대해 ISO/IEC 25010 품질 특성 기준으로 품질 영향을 평가하고, 안정성/신뢰성 강화를 목적으로 한 변경 사항을 정리합니다.

### 1.2 배경
기존 구조에서 폴링 제거 후 WS 기반으로 전환했으나, 타이머 만료/알림/참여자 동기화가 일부 누락될 수 있는 리스크가 확인되었습니다. 이를 해결하기 위해 서버 권위 브로드캐스트, 만료 처리 백업, 알림 트리거 연결, 재접속 백필을 포함한 개선을 수행했습니다.

---

## 2. 범위

### 2.1 포함 범위
- Room WebSocket 권위 처리 및 이벤트 브로드캐스트
- 타이머 만료 처리의 안정성(Redis TTL + APScheduler 백업)
- 알림 이벤트 트리거 연결(메시지/커뮤니티/친구/랭킹/예약)
- 알림 재접속 백필
- 참가자 수 동기화 개선
- NotificationBell 폴링 제거

### 2.2 제외 범위
- 긴 휴식(4세션) 로직 추가
- Break 세션 기록 정책 변경
- 사용자 설정 화면/UX 개선

---

## 3. 품질 목표 (ISO/IEC 25010 연계)

| 품질 특성 | 목표 | 적용 내용 |
|---|---|---|
| **Reliability** | 실시간 이벤트 누락 방지, 만료 처리 안정화 | Redis TTL 만료 처리 + APScheduler 백업, WS 권위 브로드캐스트 |
| **Performance Efficiency** | 폴링 제거로 네트워크/서버 부하 감소 | NotificationBell 폴링 제거, WS 기반 동기화 |
| **Functional Suitability** | 사용자 기대 동작과 실제 기능 일치 | 타이머 완료/알림/참여자 수 동기화 보강 |
| **Security** | WS 연결 인증 및 권한 강화 | Room WS 토큰 연결 요구 |
| **Compatibility** | 멀티 서버 환경 실시간 동기화 | Redis Pub/Sub 기반 이벤트 브로드캐스트 |
| **Maintainability** | 기능별 분리된 워커/서비스 | 예약 알림 워커 분리, 백필 API 분리 |

---

## 4. 주요 개선 내용 요약

### 4.1 실시간 타이머/방 동기화 안정화
- Room WS를 서버 권위 이벤트로 전환하여 상태 불일치 위험을 감소
- `timer_complete` 이벤트를 명시적으로 발행하여 클라이언트 완료 흐름 일관성 확보
- 참여자 수(`current_count`)를 WS 이벤트에 포함해 UI 표기 정확도 개선

### 4.2 타이머 만료 처리 신뢰성 강화
- Redis TTL 기반 만료 감지 유지
- Redis 이벤트 미사용 시 APScheduler 백업으로 1분 단위 폴링 보완
- 만료 처리에서 세션 기록 누락 방지

### 4.3 알림 시스템 신뢰성 강화
- 메시지/커뮤니티/친구/랭킹/예약 등 핵심 도메인 이벤트에 알림 트리거 연결
- 알림 재접속 백필 API 추가로 WS 미수신 보정
- 예약 리마인드 전용 워커 추가로 자동 발송 안정화

### 4.4 폴링 제거 및 WS 중심화
- NotificationBell 폴링 제거
- WS + 백필 기반으로 알림 상태 동기화

---

## 5. 품질 영향 분석

### 5.1 Reliability (신뢰성)
**개선 효과**
- 타이머 만료 시 누락 리스크 감소
- WS 연결 단절 후 재접속 시 알림 백필로 데이터 일관성 확보

**잔여 리스크**
- Redis Keyspace Notifications 미지원 환경에서는 APScheduler 백업 의존

### 5.2 Performance Efficiency (성능 효율성)
**개선 효과**
- 폴링 제거로 불필요한 API 호출 감소
- 서버/클라이언트 네트워크 비용 절감

### 5.3 Functional Suitability (기능 적합성)
**개선 효과**
- “완료 버튼 미사용/이탈” 상황에서 통계 기록 보강
- 참여자 수 정확도 향상으로 UI 정보 신뢰성 증가

### 5.4 Security (보안성)
**개선 효과**
- Room WS 연결 시 토큰 인증으로 접근 통제 강화

---

## 6. 검증 전략 (테스트 사용자 수행 예정)

### 6.1 핵심 시나리오
1. Room WS 연결 후 타이머 시작/일시정지/완료 이벤트 동기화
2. 모든 사용자 이탈 후 타이머 만료 시 통계 기록 여부 확인
3. 메시지/댓글/좋아요/친구요청/랭킹초대 알림 수신 여부
4. WS 재접속 시 알림 백필 수신 여부
5. 참가자 수 UI 표기 및 불일치 보정 동작 확인

---

## 7. 미해결 항목 및 다음 단계

### 7.1 미해결 항목
- Break 세션 기록 정책 확정 및 반영
- WS connect/disconnect 시 Participant 레코드 상태 업데이트 정확도 향상
- UI에 “현재/최대 인원” 표기 추가

### 7.2 권장 후속 작업
1. Break 세션 기록 여부 정책 확정 후 적용
2. Participant 상태를 WS 연결 상태와 일관되게 유지
3. 참여자 UI에 정원/현재 수 표시

---

## 8. 결론

본 개선 작업은 실시간 동기화와 알림 안정성을 ISO/IEC 25010 기준으로 강화하며, 폴링 제거 후 발생 가능한 기능 다운그레이드를 예방합니다. 특히 타이머 만료 처리 백업, WS 권위 브로드캐스트, 알림 트리거 연결, 백필 추가로 **Reliability 및 Functional Suitability 품질 지표를 직접 개선**했습니다. 남은 항목은 정책 확정 및 UI 보강이며, 테스트 결과에 따라 추가 보정이 권장됩니다.

---

## 9. 변경 이력

| 날짜 | 버전 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| 2026-01-08 | 1.0 | 실시간/알림 품질 보고서 초안 | Focus Mate Development Team |
