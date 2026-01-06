# Grading Content Cleanup Plan

## Audit Results

### Files with Grading-Related Content

#### 1. **Critical - Needs Update**
- `docs/05_operations/OPS-001_Seed_Data_Review.md` (Line 184)
  - Contains: "AI 채점관 및 개발자가 즉시 프로젝트의 가치를 확인할 수 있는 풍부한 데이터 환경 제공"
  - **Action**: Replace "AI 채점관" with "개발자 및 테스터"

- `docs/02_architecture/ARC-ADR/ARC-ADR-003_SQLite_Database.md` (Lines 19, 56, 90)
  - Contains: "AI 채점 환경" references
  - **Action**: Replace with "개발/테스트 환경" or "로컬 개발 환경"

- `docs/00_overview/ISO-25010-Report.md` (Line 495)
  - Contains: "The Perfect Score Check"
  - **Action**: Replace with "Quality Assurance Check" or "Automated Validation"

#### 2. **Keep - Legitimate Use**
The following files contain "score" but refer to legitimate business logic:
- `ARC-007_Matching_System_Architecture.md` - Matching algorithm scores ✅
- `ARC-006_Ranking_API.md` - Ranking system scores ✅
- `ARC-013_데이터베이스_아키텍처.md` - Database score fields ✅
- `QUL-003_Quality_Metrics.md` - Code quality metrics ✅
- `DEV-005_API_Documentation.md` - API response examples ✅

#### 3. **Already Updated**
- `docs/MASTER_EVALUATION_GUIDE.md` - Already converted to "AI Testing Automation Index" ✅
- `README.md` - Already updated ✅

## Cleanup Actions

### Phase 1: Documentation Updates (3 files)
1. Update `OPS-001_Seed_Data_Review.md`
2. Update `ARC-ADR-003_SQLite_Database.md`
3. Update `ISO-25010-Report.md`

### Phase 2: Code Audit
Search backend/frontend code for:
- Comments mentioning "grading" or "채점"
- Test fixtures with academic references
- Configuration files with evaluation-specific settings

### Phase 3: Verification
- Run full-text search for remaining references
- Verify all documentation reads naturally for enterprise context

## Summary
- **Total files to update**: 3
- **Legitimate "score" references**: ~40+ (keep as-is)
- **Risk**: Low - changes are cosmetic terminology updates
