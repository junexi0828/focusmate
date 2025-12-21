# Documentation Standards & Naming Convention
(ISO/IEC 26514 Compliant)

This document defines the rules for creating, naming, and maintaining documentation within the Focus Mate project.

## 1. Naming Convention (파일 명명 규칙)

All documentation files must follow the format:
`[CATEGORY]-[ID]_[Descriptive_Name].md`

### 1.1 Category Codes (카테고리 코드)
*   **GEN**: General / Overview (일반/개요)
*   **REQ**: Requirements (요구사항)
*   **ARC**: Architecture (아키텍처)
*   **QUL**: Quality Assurance (품질 보증)
*   **DEV**: Development (개발 가이드)
*   **OPS**: Operations / Deployment (운영/배포)
*   **ADR**: Architecture Decision Records (아키텍처 의사결정)

### 1.2 ID Rules (ID 규칙)
*   `001` ~ `999`: Sequential number starting from 001.
*   IDs must be unique within a Category.

### 1.3 Examples
*   `GEN-001_Project_Nature.md`
*   `REQ-001_Software_Requirements_Specification.md`
*   `ARC-001_System_Architecture.md`

---

## 2. Metadata Schema (메타데이터 스키마)

All Markdown documents MUST define the following YAML frontmatter at the top of the file.

```yaml
---
id: [CATEGORY]-[ID]
title: [Official Document Title]
version: [Major].[Minor] (e.g., 1.0)
status: [Draft | Review | Approved | Deprecated]
date: YYYY-MM-DD
author: [Author Name / Team]
iso_standard: [Related ISO Standard, e.g., ISO/IEC 25010]
---
```

## 3. Directory Structure (디렉토리 구조)

```
docs/
├── 00_overview/       # GEN (General)
├── 01_requirements/   # REQ (Requirements)
├── 02_architecture/   # ARC (Architecture) & ADR
├── 03_quality/        # QUL (Quality)
├── 04_development/    # DEV (Development)
├── 05_operations/     # OPS (Operations)
└── DOCUMENTATION_STANDARD.md
```
