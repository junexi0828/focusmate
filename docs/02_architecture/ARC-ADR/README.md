# Architecture Decision Records (ADR)

이 디렉토리는 Focus Mate 프로젝트의 주요 아키텍처 결정을 문서화합니다.

## ADR 인덱스

| ADR                                              | 제목                           | 상태   | 날짜       |
| ------------------------------------------------ | ------------------------------ | ------ | ---------- |
| [ADR-001](./ADR-001-fastapi-backend.md)          | FastAPI 백엔드 프레임워크 선정 | 승인됨 | 2025-12-04 |
| [ADR-002](./ADR-002-typescript-strict-mode.md)   | TypeScript Strict Mode 사용    | 승인됨 | 2025-12-04 |
| [ADR-003](./ADR-003-sqlite-database.md)          | SQLite 데이터베이스 선택       | 승인됨 | 2025-12-04 |
| [ADR-004](./ADR-004-zustand-state-management.md) | Zustand 상태 관리 라이브러리   | 승인됨 | 2025-12-04 |
| [ADR-005](./ADR-005-server-side-timer.md)        | 서버 사이드 타이머 로직        | 승인됨 | 2025-12-04 |

## ADR 템플릿

새로운 ADR을 작성할 때는 다음 템플릿을 사용하세요:

```markdown
# ADR-XXX: [제목]

**날짜**: YYYY-MM-DD
**상태**: [제안됨 | 승인됨 | 폐기됨 | 대체됨]
**결정자**: [이름]

## 컨텍스트 (Context)

어떤 문제를 해결하려고 하는가?

## 결정 (Decision)

어떤 결정을 내렸는가?

## 근거 (Rationale)

왜 이 결정을 내렸는가?

## 대안 (Alternatives)

어떤 다른 옵션들을 고려했는가?

## 결과 (Consequences)

이 결정의 장단점은 무엇인가?

## 참조 (References)

관련 문서, 이슈, PR 링크
```

## ADR 프로세스

1. **제안**: 새로운 ADR 작성 및 PR 생성
2. **토론**: 팀 리뷰 및 피드백
3. **승인**: 합의 후 상태를 "승인됨"으로 변경
4. **구현**: 결정 사항 구현
5. **회고**: 필요 시 ADR 업데이트 또는 대체

## 참조

- [Architecture Decision Records (ADR) - GitHub](https://adr.github.io/)
- [Documenting Architecture Decisions - Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
