# ADR-002: TypeScript Strict Mode 사용

**날짜**: 2025-12-04
**상태**: 승인됨
**결정자**: 아키텍처 팀

---

## 컨텍스트 (Context)

프론트엔드 개발 시 JavaScript와 TypeScript 중 선택해야 했습니다.
JavaScript는 빠른 개발이 가능하지만, 런타임 에러 가능성이 높고 유지보수가 어렵습니다.
TypeScript는 타입 안정성을 제공하지만, 설정과 학습 곡선이 있습니다.

ISO/IEC 25010의 **신뢰성(Reliability)** 특성 중 **성숙성(Maturity)**을 확보하기 위해서는
컴파일 타임에 가능한 많은 오류를 검출해야 합니다.

---

## 결정 (Decision)

TypeScript를 사용하고, **strict 모드**를 활성화합니다.

**설정**:

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true
  }
}
```

---

## 근거 (Rationale)

### 1. 신뢰성 확보

- **컴파일 타임 에러 검출**: 런타임 에러의 90% 이상을 사전에 방지
- **타입 안정성**: `any` 타입 사용 금지로 예상치 못한 타입 변환 방지
- **ISO 25010 준수**: REQ-NF-004 (타입 안정성) 요구사항 충족

### 2. 유지보수성 향상

- **IDE 지원**: 자동완성, 리팩토링, 네비게이션 향상
- **자기 문서화**: 타입 시그니처만으로 함수 동작 이해 가능
- **리팩토링 안전성**: 타입 체크로 리팩토링 시 부작용 최소화

### 3. 팀 협업

- **명확한 계약**: 함수 시그니처가 명확한 API 계약 역할
- **코드 리뷰 효율성**: 타입 오류는 자동으로 검출되어 리뷰 시간 절약

---

## 대안 (Alternatives)

### 대안 1: JavaScript 사용

**장점**:

- 설정 불필요
- 빠른 프로토타이핑

**단점**:

- 런타임 에러 가능성 높음
- IDE 지원 제한적
- 유지보수 어려움
- ISO 25010 신뢰성 요구사항 미충족

**결론**: 타입 안정성 요구사항을 충족하지 못하여 채택하지 않음

### 대안 2: TypeScript (Non-strict)

**장점**:

- 점진적 마이그레이션 가능
- 기존 JavaScript 코드와 호환

**단점**:

- 타입 안정성 보장 불가
- `any` 타입 남용 가능
- strict 모드 대비 이점 제한적

**결론**: strict 모드의 이점을 포기할 수 없어 채택하지 않음

---

## 결과 (Consequences)

### 긍정적 결과

✅ **타입 안정성**: 컴파일 타임에 대부분의 타입 오류 검출
✅ **코드 품질**: 자동완성과 리팩토링 지원으로 개발 생산성 향상
✅ **문서화**: 타입 시그니처가 자동 문서 역할
✅ **ISO 25010 준수**: 신뢰성 요구사항 충족

### 부정적 결과

⚠️ **초기 설정 시간**: strict 모드 활성화 시 기존 코드 수정 필요
⚠️ **학습 곡선**: 팀원들의 TypeScript 학습 필요
⚠️ **컴파일 시간**: JavaScript 대비 빌드 시간 증가 (미미함)

### 완화 전략

- **점진적 마이그레이션**: 기존 코드는 `// @ts-nocheck`로 우회 후 점진적 개선
- **교육 자료 제공**: TypeScript 베스트 프랙티스 문서화
- **자동화**: CI/CD에서 타입 체크 자동화

---

## 참조 (References)

- [TypeScript Handbook - Strict Mode](https://www.typescriptlang.org/docs/handbook/tsconfig-json.html#strict)
- [ISO/IEC 25010: Software Quality Model](https://iso25000.com/index.php/en/iso-25000-standards/iso-25010)
- [REQ-NF-004](./../SRS.md#req-nf-004-타입-안정성): 타입 안정성 요구사항
- [CODING_STANDARDS.md](./../CODING_STANDARDS.md#32-typescript-코딩-표준): TypeScript 코딩 표준

---

**문서 끝**
