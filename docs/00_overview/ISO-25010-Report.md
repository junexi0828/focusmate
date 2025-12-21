# **ISO/IEC 25010 표준 준수 Team Pomodoro Timer 아키텍처 및 AI 기반 개발 전략 보고서**

## **1\. 서론: AI 시대의 소프트웨어 품질과 표준화의 필요성**

현대 소프트웨어 공학은 인간 개발자와 인공지능(AI) 에이전트가 협업하는 하이브리드 워크플로우로 급격히 전환되고 있습니다. 이러한 변화 속에서 코드의 품질을 평가하는 주체 또한 인간의 정성적 리뷰에서 AI 기반의 정량적, 구조적 평가로 이동하고 있습니다. 본 보고서는 ISO/IEC 25010 품질 모델을 기반으로, AI 평가 환경에서 만점을 획득할 수 있는 'Team Pomodoro Timer' 프로젝트의 아키텍처 설계, 요구사항 정의, 그리고 개발 시나리오를 포괄적으로 다룹니다.

Team Pomodoro Timer는 단순한 개인용 타이머가 아닌, 원격 근무 환경에서의 팀 생산성을 극대화하기 위한 실시간 협업 도구입니다. 이 시스템은 여러 사용자가 동시에 접속하여 타이머 상태를 공유하고, 업무와 휴식 사이클을 동기화해야 합니다. 따라서 \*\*신뢰성(Reliability)\*\*과 \*\*성능 효율성(Performance Efficiency)\*\*이 극도로 중요하며, 장기적인 프로젝트의 생명주기를 고려할 때 \*\*유지보수성(Maintainability)\*\*은 타협할 수 없는 핵심 가치입니다.1

본 보고서는 ISO/IEC 25010의 8가지 품질 특성을 완벽하게 만족시키기 위한 기술적 전략을 제시합니다. 특히, ISO/IEC/IEEE 29148 요구사항 공학 표준과 ISO/IEC/IEEE 42010 아키텍처 기술 표준을 준수하여 문서화의 체계를 잡고, 최신 llms.txt 표준을 도입하여 AI 에이전트(Cursor, Copilot 등)가 프로젝트의 컨텍스트를 완벽하게 이해하고 개발에 착수할 수 있는 환경을 구축합니다.3 이는 단순히 기능이 작동하는 소프트웨어를 넘어, 코드의 구조적 건전성과 문서의 무결성까지 보장하는 '결함 없는(Zero-Defect)' 소프트웨어 개발을 목표로 합니다.

## ---

**2\. ISO/IEC 25010 제품 품질 모델 기반 분석 및 전략**

ISO/IEC 25010 표준은 소프트웨어 제품의 품질을 평가하기 위한 국제 표준으로, 8개의 주 특성과 31개의 부 특성으로 구성됩니다. Team Pomodoro Timer 프로젝트가 AI 평가 환경에서 만점을 받기 위해서는 각 특성에 대한 명확한 달성 목표와 이를 검증할 수 있는 정량적 지표가 수립되어야 합니다.1

### **2.1 기능 적합성 (Functional Suitability)**

기능 적합성은 명시된 요구사항과 내재된 요구사항을 소프트웨어가 얼마나 만족시키는지를 평가합니다.

* **기능 완전성 (Functional Completeness):** 팀 포모도로 타이머의 핵심 기능인 타이머 시작/정지/리셋, 팀원 간 상태 동기화, 휴식 시간 관리, 사용자 통계 저장 등의 기능이 누락 없이 구현되어야 합니다. AI 평가 환경에서는 명세서(SRS)에 정의된 모든 기능 요구사항이 코드 레벨에서 구현되었는지를 추적합니다.6  
* **기능 정확성 (Functional Correctness):** 타이머는 네트워크 지연(Latency)이 발생하더라도 모든 클라이언트에서 동일한 남은 시간을 표시해야 합니다. 이를 위해 NTP(Network Time Protocol) 기반의 시간 동기화 로직이나 서버 타임스탬프 기준의 계산 로직이 필수적입니다. 정확성은 단위 테스트와 통합 테스트의 커버리지로 증명됩니다.  
* **기능 적절성 (Functional Appropriateness):** 사용자의 업무 흐름을 방해하지 않으면서 포모도로 기법의 철학(집중-휴식 반복)을 유도하는 UX가 설계되어야 합니다.

### **2.2 성능 효율성 (Performance Efficiency)**

실시간 협업 도구에서 성능은 사용자 경험과 직결됩니다.

* **시간 반응성 (Time Behavior):** 웹소켓(WebSocket) 메시지 전송 및 처리는 100ms 이내에 완료되어야 하며, API 응답 속도는 95분위(p95) 기준 200ms 미만을 목표로 합니다. 이는 비동기 처리(AsyncIO)와 경량화된 메시지 포맷을 통해 달성할 수 있습니다.5  
* **자원 효율성 (Resource Utilization):** 클라이언트 애플리케이션(React)은 브라우저 메모리 누수를 방지해야 하며, 백엔드 컨테이너는 최소한의 CPU와 RAM으로 다수의 동시 접속을 처리할 수 있어야 합니다.

### **2.3 호환성 (Compatibility)**

다양한 환경에서의 작동을 보장해야 합니다.

* **공존성 (Co-existence):** Docker 컨테이너 환경에서 데이터베이스, 캐시 서버 등 다른 서비스와 충돌 없이 실행되어야 합니다.1  
* **상호운용성 (Interoperability):** 표준 RESTful API와 JSON 포맷을 사용하여 Slack, Calendar 등 외부 도구와의 연동 가능성을 열어두어야 합니다.

### **2.4 사용성 (Usability)**

사용성은 시스템의 학습 용이성과 운영 편의성을 다룹니다.

* **학습 용이성 (Learnability):** 별도의 매뉴얼 없이도 직관적으로 팀 방을 생성하고 타이머를 시작할 수 있어야 합니다.  
* **사용자 오류 방지 (User Error Protection):** 실수로 타이머를 리셋하거나 방을 삭제하는 행위를 방지하기 위한 확인 절차와 실행 취소(Undo) 메커니즘이 필요합니다.6

### **2.5 신뢰성 (Reliability)**

AI 평가에서 가장 엄격하게 다뤄지는 항목 중 하나입니다. 시스템은 오류 상황에서도 견고해야 합니다.

* **성숙성 (Maturity):** 코드의 결함을 최소화하기 위해 엄격한 정적 분석과 90% 이상의 테스트 커버리지를 유지해야 합니다.2  
* **가용성 (Availability):** 무중단 배포 전략과 오토힐링(Auto-healing) 아키텍처를 통해 서비스 다운타임을 최소화해야 합니다.  
* **결함 허용성 (Fault Tolerance):** 네트워크 단절 시 클라이언트는 로컬 타이머로 전환되어야 하며, 재연결 시 자동으로 서버 상태와 동기화되는 복구 로직(Recoverability)을 갖춰야 합니다.6

### **2.6 보안성 (Security)**

데이터 보호와 접근 제어는 필수적입니다.

* **기밀성 (Confidentiality):** 팀의 세션 정보와 대화 내용은 인가된 사용자만 접근 가능해야 합니다. JWT(JSON Web Token) 기반의 인증과 SSL/TLS 암호화가 적용됩니다.  
* **무결성 (Integrity):** 사용자의 수행 기록 데이터는 위변조로부터 보호되어야 합니다.

### **2.7 유지보수성 (Maintainability)**

'완벽한 코드'의 핵심 지표입니다. AI가 코드를 분석할 때 가장 중점적으로 보는 부분입니다.

* **모듈성 (Modularity):** 코드는 높은 응집도(Cohesion)와 낮은 결합도(Coupling)를 유지해야 합니다. 백엔드의 서비스 레이어와 프론트엔드의 컴포넌트 구조가 이를 반영해야 합니다.  
* **분석성 (Analysability):** 코드의 복잡도(Cyclomatic Complexity)를 낮게 유지하여, 사람과 AI 모두 로직을 쉽게 파악할 수 있어야 합니다.6  
* **변경 용이성 (Modifiability):** 기능 추가 시 기존 코드에 미치는 영향(Ripple Effect)이 최소화되도록 설계되어야 합니다.  
* **시험성 (Testability):** 모든 비즈니스 로직은 단위 테스트가 가능하도록 의존성 주입(DI) 패턴 등을 활용해야 합니다.

### **2.8 이식성 (Portability)**

* **적응성 (Adaptability):** 다양한 OS(Windows, macOS, Linux) 및 브라우저 환경에서 동일하게 동작해야 합니다.  
* **설치 용이성 (Installability):** Docker Compose를 통해 단일 명령어로 전체 스택을 배포할 수 있어야 합니다.8

**\[표 1\] Team Pomodoro Timer의 ISO 25010 품질 목표 매트릭스**

| 품질 특성 (Quality Characteristic) | 부 특성 (Sub-Characteristic) | 정량적 목표 지표 (Target Metric) | 측정 도구 (Tool) |
| :---- | :---- | :---- | :---- |
| **기능 적합성** | 기능 완전성 | 요구사항 추적성 100% | Traceability Matrix |
| **성능 효율성** | 시간 반응성 | API Latency \< 100ms (p95) | Load Testing (Locust) |
| **신뢰성** | 성숙성, 결함 허용성 | Test Coverage \> 90%, Type Coverage 100% | Pytest-cov, Jest, Mypy |
| **유지보수성** | 분석성, 모듈성 | Cyclomatic Complexity \< 10, MI \> 20 (Grade A) | Radon, Xenon, ESLint |
| **보안성** | 기밀성, 무결성 | 취약점 제로 (Zero Vulnerabilities) | Bandit, npm audit |
| **이식성** | 설치 용이성 | 배포 성공률 100% | Docker Healthcheck |

## ---

**3\. 요구사항 공학 및 명세화 (ISO/IEC/IEEE 29148\)**

AI가 코드를 생성하기 위해서는 명확하고 모호함이 없는 요구사항 정의가 선행되어야 합니다. ISO/IEC/IEEE 29148 표준은 요구사항 명세(SRS)의 구조와 품질을 정의하며, 이를 준수함으로써 AI 에이전트가 "할루시네이션(Hallucination)" 없이 정확한 기능을 구현하도록 유도할 수 있습니다.9

### **3.1 요구사항 명세 구조 (SyRS Structure)**

ISO 29148에 따라 요구사항은 기능 요구사항(Functional Requirements)과 비기능 요구사항(Non-Functional Requirements)으로 엄격히 구분하며, 각 요구사항은 고유 식별자(ID)를 가집니다.

#### **3.1.1 기능 요구사항 (Functional Requirements)**

기능 요구사항은 시스템이 *무엇을 해야 하는지*를 정의합니다. Team Pomodoro Timer의 핵심 기능은 다음과 같이 정의됩니다.

* **REQ-F-001 (Room Management):** 사용자는 고유한 이름으로 팀 방(Room)을 생성하고, 공유 가능한 URL을 통해 다른 사용자를 초대할 수 있어야 한다.  
* **REQ-F-002 (Timer Synchronization):** 방에 참여한 모든 사용자는 서버에서 관리되는 단일 타이머 상태(남은 시간, 진행 상태)를 실시간으로 공유받아야 한다. 타이머 오차는 1초 이내여야 한다.  
* **REQ-F-003 (Timer Control):** 방의 구성원은 타이머를 시작, 일시 정지, 재설정할 수 있는 권한을 가진다. (권한 레벨에 따라 제한 가능)  
* **REQ-F-004 (Configuration):** 사용자는 포모도로 집중 시간(기본 25분)과 휴식 시간(기본 5분)을 설정할 수 있어야 한다.  
* **REQ-F-005 (Notifications):** 타이머 종료 시 브라우저 알림 또는 소리 알림을 통해 사용자에게 상태 변화를 알려야 한다.

#### **3.1.2 비기능 요구사항 (Non-Functional Requirements)**

비기능 요구사항은 시스템이 *어떻게 동작해야 하는지*를 정의하며, ISO 25010 품질 모델과 직접적으로 연결됩니다.

* **REQ-NF-001 (Maintainability \- Complexity):** 모든 백엔드 함수 및 프론트엔드 컴포넌트의 순환 복잡도(Cyclomatic Complexity)는 10 이하로 유지되어야 한다.11  
* **REQ-NF-002 (Reliability \- Typing):** Python 코드는 strict 모드의 타입 힌트를 준수해야 하며 Any 타입의 사용을 원칙적으로 금지한다. TypeScript 또한 strict: true 설정을 준수해야 한다.12  
* **REQ-NF-003 (Performance \- Latency):** 타이머 상태 변경 이벤트는 발생 후 200ms 이내에 모든 접속 클라이언트에 전파되어야 한다.  
* **REQ-NF-004 (Portability \- Deployment):** 전체 애플리케이션은 docker compose up 명령 하나로 의존성 설치부터 실행까지 완료되어야 한다.

### **3.2 요구사항 추적성 (Traceability)**

ISO 29148은 요구사항의 추적성을 강조합니다. 모든 코드는 특정 요구사항에 매핑되어야 하며, 테스트 케이스 또한 요구사항을 검증해야 합니다. AI 에이전트에게 작업을 지시할 때, "REQ-F-002를 구현하라"는 식의 지시는 모호함을 제거하는 강력한 수단이 됩니다.10

**\[표 2\] 요구사항 추적 매트릭스 (RTM) 예시**

| 요구사항 ID | 기능 설명 | 구현 모듈 | 테스트 케이스 ID | 검증 방법 |
| :---- | :---- | :---- | :---- | :---- |
| **REQ-F-002** | 타이머 동기화 | backend/services/timer.py, frontend/hooks/useSocket.ts | TC-SYNC-01 | 통합 테스트 (WebSocket) |
| **REQ-NF-001** | 코드 복잡도 제한 | github/workflows/quality.yml (Radon Check) | N/A | 정적 분석 자동화 |
| **REQ-NF-002** | 엄격한 타입 준수 | pyproject.toml (Mypy Config) | N/A | 정적 분석 자동화 |

## ---

**4\. 아키텍처 기술 및 설계 전략 (ISO/IEC/IEEE 42010\)**

ISO/IEC/IEEE 42010 표준은 시스템 아키텍처를 이해관계자의 관점(Viewpoint)에 따라 기술하도록 권고합니다.15 Team Pomodoro Timer는 유지보수성과 확장성을 최우선으로 하는 **클라이언트-서버(Client-Server)** 구조를 기반으로 하며, 실시간성을 위한 **이벤트 기반(Event-Driven)** 패턴을 혼용합니다.

### **4.1 논리적 뷰 (Logical View)**

시스템의 기능적 요소들이 어떻게 구성되는지를 설명합니다.

1. **클라이언트 레이어 (Frontend):** React (TypeScript) 기반의 SPA(Single Page Application)입니다. 상태 관리 라이브러리(Zustand 또는 Redux Toolkit)를 사용하여 타이머 상태와 UI 상태를 분리하며, '아토믹 디자인(Atomic Design)' 패턴을 적용하여 컴포넌트의 재사용성을 높입니다.17  
2. **API 게이트웨이 (Backend Entry):** FastAPI (Python)가 REST API 요청과 WebSocket 연결의 진입점 역할을 합니다. Pydantic 모델을 통해 들어오는 모든 데이터의 유효성을 런타임 이전에 엄격하게 검증합니다.18  
3. **서비스 레이어 (Business Logic):** 타이머 계산, 방 관리 로직 등 핵심 비즈니스 로직이 위치합니다. 이 계층은 프레임워크(FastAPI)와 독립적으로 작성되어 단위 테스트가 용이하도록 설계됩니다 (Dependency Injection 활용).  
4. **데이터 액세스 레이어 (Repository):** 데이터베이스와의 통신을 담당합니다. SQLAlchemy (Async)를 사용하여 비동기 I/O 성능을 극대화합니다.  
5. **데이터 스토리지:** 개발 환경에서는 SQLite를 사용하되, 프로덕션 환경에서는 PostgreSQL로의 전환이 용이하도록 ORM을 사용합니다. 실시간 상태 저장을 위해 Redis와 같은 인메모리 저장소 도입도 고려할 수 있으나, 초기 버전에서는 애플리케이션 메모리 또는 DB로 처리합니다.

### **4.2 프로세스 뷰 (Process View)**

시스템의 동시성 및 동기화 처리 방식을 설명합니다.

* **타이머 동기화 메커니즘:** 서버가 '진실의 원천(Single Source of Truth)' 역할을 합니다. 클라이언트는 타이머를 직접 계산하지 않고, 서버로부터 받은 target\_timestamp (종료 예정 시각)와 status (진행 중/일시정지) 정보를 바탕으로 남은 시간을 렌더링합니다. 이는 클라이언트 간 시간 오차(Drift)를 방지하는 핵심 설계입니다.  
* **하트비트(Heartbeat):** WebSocket 연결 유지를 위해 주기적인 핑/퐁(Ping/Pong) 메시지를 교환하며, 연결 끊김 시 클라이언트는 지수 백오프(Exponential Backoff) 전략으로 재접속을 시도합니다.

### **4.3 물리적/배포 뷰 (Physical/Deployment View)**

* **컨테이너화:** 모든 서비스(Frontend, Backend, DB)는 Docker Container로 패키징됩니다.  
* **오케스트레이션:** Docker Compose를 사용하여 서비스 간 의존성(Dependency)과 네트워크를 정의합니다.  
* **Healthcheck:** 각 컨테이너는 헬스체크 스크립트를 내장하여, 의존성 서비스(예: DB)가 준비되지 않았을 때 애플리케이션이 시작되지 않도록 제어합니다.8

### **4.4 아키텍처 결정 기록 (Architecture Decision Records \- ADRs)**

ISO 42010 준수를 위해 주요 설계 결정의 이유를 문서화합니다.20

* **ADR-001: FastAPI 선정 이유.** Django 대비 가볍고 비동기 처리에 최적화되어 있으며, Pydantic과의 강력한 결합을 통해 ISO 25010의 '신뢰성(데이터 검증)'을 확보하기 유리함.  
* **ADR-002: TypeScript Strict Mode.** JavaScript의 느슨한 타입으로 인한 런타임 오류를 방지하여 '성숙성(Maturity)'을 확보하기 위함.  
* **ADR-003: Server-Side Timer Logic.** 클라이언트 사이드 타이머는 브라우저 스로틀링 등으로 인해 정확성을 보장할 수 없으므로, 서버 중심의 시간 계산 방식을 채택함.

## ---

**5\. 구현 전략: ISO 품질 달성을 위한 코딩 표준**

'완벽한 점수'는 코딩 스타일과 정적 분석의 엄격함에서 나옵니다. 백엔드와 프론트엔드 모두 **Self-Healing(자가 치유)** 및 **Defensive Programming(방어적 프로그래밍)** 원칙을 따릅니다.

### **5.1 백엔드 엔지니어링 표준 (Python & FastAPI)**

Python은 동적 타입 언어이지만, ISO 25010의 신뢰성을 위해 정적 타입 언어 수준의 엄격함을 적용합니다.

#### **5.1.1 Pydantic Strict Mode와 데이터 무결성**

Pydantic V2의 Strict 모드를 사용하여 데이터 타입의 자동 변환(Coercion)을 차단합니다. 예를 들어, 문자열 "123"이 정수형 필드에 입력되면 에러를 발생시켜야 합니다. 이는 데이터의 모호함을 제거하여 **기능 정확성**을 높입니다.12

Python

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr

class TimerSettings(BaseModel):  
    """  
    타이머 설정을 위한 데이터 모델.  
    ISO 25010 신뢰성 확보를 위해 Strict 모드 사용.  
    """  
    model\_config \= ConfigDict(strict=True)  \# 자동 형변환 금지  
      
    work\_duration\_minutes: StrictInt \= Field(  
       ...,   
        gt=0,   
        le=60,   
        description="집중 시간(분). 0보다 크고 60 이하여야 함."  
    )  
    break\_duration\_minutes: StrictInt \= Field(  
       ...,   
        gt=0,   
        le=30,   
        description="휴식 시간(분). 0보다 크고 30 이하여야 함."  
    )  
    room\_name: StrictStr \= Field(  
       ...,   
        min\_length=3,   
        max\_length=50,   
        pattern=r"^\[a-zA-Z0-9\_-\]+$"  
    )

#### **5.1.2 순환 복잡도(Cyclomatic Complexity) 제어**

함수의 복잡도는 유지보수성과 직결됩니다. radon 도구를 사용하여 복잡도(CC)가 10을 초과하는 함수는 배포 파이프라인에서 차단합니다. 복잡한 함수는 더 작은 단위 함수로 리팩토링해야 합니다.11

* **지표 기준:** Cyclomatic Complexity \<= 10 (함수당)  
* **Maintainability Index:** \>= 20 (Radon 기준 Rank A)

#### **5.1.3 Mypy 엄격 모드 (Strict Typing)**

mypy 설정을 통해 Any 타입의 사용을 금지하고, 모든 함수에 타입 힌트를 강제합니다. 이는 잠재적인 런타임 오류를 컴파일 타임(정적 분석 시점)에 발견하게 해줍니다.13

Ini, TOML

\# pyproject.toml  
\[tool.mypy\]  
strict \= true  
disallow\_any\_generics \= true  
disallow\_untyped\_defs \= true  
warn\_return\_any \= true  
plugins \= \["pydantic.mypy"\]

### **5.2 프론트엔드 엔지니어링 표준 (React & TypeScript)**

프론트엔드는 사용자와 직접 상호작용하므로 **사용성**과 **성능 효율성**이 중요합니다.

#### **5.2.1 컴포넌트 복잡도 관리**

React 컴포넌트가 비대해지는 것을 방지하기 위해 eslint-plugin-complexity를 적용합니다. 렌더링 로직의 분기문(if, switch)이 많아지면 별도의 하위 컴포넌트나 커스텀 훅(Custom Hook)으로 분리해야 합니다.23

**ESLint 설정 예시:**

JSON

"rules": {  
  "complexity": \["error", { "max": 10 }\],  
  "max-lines-per-function": \["error", 50\],  
  "react/jsx-no-bind": "error"  
}

#### **5.2.2 웹 접근성 (Accessibility) 준수**

ISO 25010의 **접근성(Accessibility)** 부 특성을 만족시키기 위해 eslint-plugin-jsx-a11y를 사용하여 ARIA 속성, 이미지 대체 텍스트, 키보드 네비게이션 지원 등을 강제합니다.

### **5.3 테스트 전략 및 커버리지**

테스트는 ISO 25010의 **성숙성**을 보장하는 유일한 수단입니다. 단순히 테스트를 작성하는 것을 넘어, 정량적인 커버리지 목표를 설정하고 이를 CI 파이프라인에서 강제합니다.25

* **단위 테스트 (Unit Test):** 비즈니스 로직 검증. (Mocking 활용)  
* **통합 테스트 (Integration Test):** API 엔드포인트 및 DB 연동 검증.  
* **커버리지 목표:** 라인 커버리지(Line Coverage) 90% 이상, 분기 커버리지(Branch Coverage) 85% 이상.

**Pytest 설정:**

Ini, TOML

\[tool.pytest.ini\_options\]  
addopts \= "--cov=app \--cov-report=term-missing \--cov-fail-under=90"

**Jest 설정:**

JSON

"jest": {  
  "coverageThreshold": {  
    "global": {  
      "branches": 90,  
      "functions": 90,  
      "lines": 90  
    }  
  }  
}

## ---

**6\. AI 친화적 문서화 전략 (llms.txt 표준 도입)**

이 프로젝트의 핵심 차별점은 AI 에이전트(Cursor 등)가 프로젝트를 완벽하게 이해하도록 돕는 문서화 전략입니다. 전통적인 README.md 만으로는 부족하며, AI가 탐색하기 최적화된 llms.txt 표준을 도입합니다.3

### **6.1 llms.txt의 역할과 구조**

llms.txt는 웹사이트의 robots.txt와 유사하지만, 검색 엔진 크롤러가 아닌 LLM(Large Language Model)을 위한 파일입니다. 이 파일은 프로젝트의 핵심 문서, 아키텍처 정의, API 명세 등으로 가는 '지도' 역할을 합니다. AI는 이 파일을 통해 프로젝트의 전체 맥락(Context)을 빠르고 정확하게 파악하여 할루시네이션 없는 코드를 생성할 수 있습니다.

**Team Pomodoro Timer의 llms.txt 예시:**

# **Team Pomodoro Timer Project Context**

This project is a real-time collaborative timer built with FastAPI and React, strictly adhering to ISO/IEC 25010 quality standards.

## **Core Documentation**

\-(docs/architecture.md): System design, viewpoints, and technology decisions (ISO 42010).  
\-(docs/requirements.md): Functional and non-functional requirements (ISO 29148).  
\-(docs/standards.md): Strict coding guidelines for Python and TypeScript.  
\-(docs/api.md): REST API and WebSocket protocol specifications.

## **Key Constraints**

* All backend code must pass mypy \--strict.  
* All Python functions must have Cyclomatic Complexity \< 10\.  
* Test coverage must remain above 90%.

### **6.2 마크다운 문서 최적화 (LLM-Friendly Docs)**

AI가 문서를 잘 이해하려면 불필요한 서식을 줄이고, 의미론적 구조(Semantic Structure)를 강화해야 합니다.28

* **명확한 계층 구조:** H1, H2, H3 헤더를 논리적으로 사용하여 AI가 문서의 구조를 파싱하기 쉽게 합니다.  
* **코드 스니펫 중심:** 설명보다는 실행 가능한 코드 예제를 풍부하게 제공합니다.  
* **컨텍스트 명시:** 모호한 대명사 사용을 피하고, 각 섹션이 독립적으로도 이해될 수 있도록 작성합니다.

## ---

**7\. 자동화된 거버넌스 및 CI/CD 파이프라인**

품질 표준은 문서에만 존재해서는 안 되며, 자동화된 파이프라인에 의해 강제되어야 합니다. GitHub Actions를 활용한 'Quality Gate'를 구축하여, 기준을 충족하지 못하는 코드는 병합(Merge)될 수 없도록 차단합니다.30

### **7.1 파이프라인 단계 (Workflow Steps)**

1. **환경 설정:** 의존성 설치 및 캐싱.  
2. **Linting & Formatting:** ruff, eslint 실행. 스타일 위반 시 즉시 실패.  
3. **정적 분석 (Static Analysis):**  
   * Backend: mypy \--strict 실행 (타입 오류 검출).  
   * Frontend: tsc \--noEmit 실행 (타입 오류 검출).  
4. **복잡도 분석 (Complexity Scan):**  
   * Backend: radon cc \--min A 및 xenon 실행. 복잡도 10 초과 시 실패.31  
5. **보안 스캔 (Security Scan):**  
   * bandit (Python 코드 취약점 분석).  
   * npm audit (라이브러리 취약점 분석).  
6. **테스트 및 커버리지 (Test & Coverage):**  
   * pytest 및 jest 실행. 커버리지 90% 미달 시 실패.  
7. **빌드 검증:** Docker 이미지 빌드 테스트.

### **7.2 견고한 대기 스크립트 (Robust Wait Scripts)**

통합 테스트 시 데이터베이스나 백엔드 서버가 준비될 때까지 기다리는 로직은 매우 중요합니다. netcat과 같은 외부 도구 의존성을 줄이고, Bash 내장 기능이나 docker healthcheck를 활용하여 이식성을 높입니다.32

Bash

\#\!/bin/bash  
\# wait-for-it.sh (Robust Version)  
set \-e  
host="$1"  
port="$2"  
timeout="${3:-30}"

\# 순수 Bash TCP 연결 시도 (이식성 극대화)  
for ((i=0; i\<timeout; i++)); do  
    if (echo \> /dev/tcp/$host/$port) \>/dev/null 2\>&1; then  
        echo "Service $host:$port is ready\!"  
        exit 0  
    fi  
    sleep 1  
done  
echo "Timeout waiting for $host:$port"  
exit 1

## ---

**8\. Master README.md (Artifact)**

다음은 위에서 분석한 모든 전략이 집약된 프로젝트의 Master README.md 파일입니다. 이 파일은 AI 에이전트와 인간 개발자 모두를 위한 진입점입니다.

# **Team Pomodoro Timer (ISO/IEC 25010 Certified Architecture)**

(https://github.com/yourorg/team-pomodoro/actions/workflows/ci.yml/badge.svg)\](https://github.com/yourorg/team-pomodoro/actions)  
(https://sonarcloud.io/api/project\_badges/measure?project=team-pomodoro\&metric=sqale\_rating)\](https://sonarcloud.io/dashboard?id=team-pomodoro)

(https://img.shields.io/badge/python-strict-blue)\](pyproject.toml)  
(https://img.shields.io/badge/typescript-strict-blue)\](tsconfig.json)

## **1\. 프로젝트 개요 및 품질 목표**

Team Pomodoro Timer는 ISO/IEC 25010 소프트웨어 품질 표준을 준수하여 설계된 실시간 협업 시간 관리 도구입니다.

**핵심 품질 목표:**

* **신뢰성 (Reliability):** 100% Type Safety (Mypy Strict), \>90% Test Coverage.  
* **유지보수성 (Maintainability):** 함수당 Cyclomatic Complexity \< 10, Maintainability Index \> 20\.  
* **이식성 (Portability):** Docker 컨테이너 기반의 환경 불가지론적(Agnostic) 배포.

## **2\. AI 에이전트 컨텍스트 (llms.txt)**

🤖 AI 에이전트(Cursor, Copilot)를 위한 안내:  
본 프로젝트의 구조와 제약 조건을 파악하기 위해 /llms.txt 파일을 가장 먼저 참조하십시오. 해당 파일은 ISO 42010 아키텍처 문서와 ISO 29148 요구사항 명세서로 연결되는 인덱스를 제공합니다.

## **3\. 아키텍처 명세 (ISO 42010\)**

본 프로젝트는 에 기술된 클라이언트-서버 및 이벤트 기반 아키텍처를 따릅니다.

## **4\. 개발 표준 (Strict Enforcement)**

### **4.1 Backend (Python)**

* **Linting:** ruff 사용 (스타일 및 에러 검출).  
* **Typing:** mypy strict 모드 적용. Any 타입 사용 금지.  
* **Complexity:** radon 사용. 모든 함수 복잡도(CC) 10 이하 유지.  
* **Testing:** pytest 사용. 커버리지 90% 미만 시 CI 실패.

### **4.2 Frontend (TypeScript)**

* **Linting:** eslint 적용. complexity 규칙(max 10\) 및 jsx-a11y 준수.  
* **Typing:** tsconfig.json의 strict: true 설정 준수.  
* **Testing:** jest / vitest 사용. 커버리지 90% 임계값 설정.

## **5\. 설치 및 실행 가이드**

### **필수 요구사항**

* Docker & Docker Compose  
* Node.js 20+ (로컬 개발 시)  
* Python 3.12+ (로컬 개발 시)

### **실행 명령어bash**

# **저장소 복제**

git clone  
cd team-pomodoro

# **전체 스택 실행 (DB, Backend, Frontend)**

docker compose up \--build

.  
├── backend/ \# FastAPI Application  
│ ├── app/  
│ │ ├── main.py \# Entry point  
│ │ ├── api/ \# Route handlers (Modularity)  
│ │ ├── core/ \# Config & Security  
│ │ ├── models/ \# Pydantic Strict Models (Reliability)  
│ │ └── services/ \# Business Logic (Functional Suitability)  
│ ├── tests/ \# Pytest Suite  
│ └── pyproject.toml \# Tool Configuration  
├── frontend/ \# React Application  
│ ├── src/  
│ │ ├── components/ \# Atomic Design Components  
│ │ ├── hooks/ \# Custom Hooks (Reusability)  
│ │ └── stores/ \# State Management  
│ └── package.json  
├── docs/ \# ISO Standard Documentation  
│ ├── architecture.md \# ISO 42010 Description  
│ ├── requirements.md \# ISO 29148 Specs  
│ └── standards.md \# Coding Guidelines  
├── llms.txt \# AI Context Index  
└── docker-compose.yml \# Orchestration

## ---

**9\. Cursor 개발 시나리오 및 프롬프트 엔지니어링**

이 시나리오는 Cursor(또는 유사 AI 도구)가 위에서 정의한 Master README와 문서를 바탕으로 즉시 개발에 착수하도록 설계되었습니다. 단순한 코드 생성이 아닌, \*\*규정 준수(Compliance)\*\*를 강제하는 프롬프트 전략을 사용합니다.

### **9.1 컨텍스트 주입 (Context Ingestion)**

개발 시작 전, AI에게 프로젝트의 '법칙'을 학습시킵니다.

**프롬프트 1: 컨텍스트 로딩**

"현재 디렉토리의 llms.txt 파일을 읽고, 여기에 링크된 docs/architecture.md, docs/requirements.md, docs/standards.md 파일을 재귀적으로 분석해. 특히 ISO 25010 품질 목표인 'Strict Typing'과 'Cyclomatic Complexity \< 10' 제약 조건을 완벽하게 숙지했는지 확인하고, 준비가 되면 요약해줘."

### **9.2 제로-샷 구현 프롬프트 (Zero-Shot Implementation)**

AI에게 ISO 29148의 요구사항 ID를 직접 참조하여 작업을 지시합니다. 이는 할루시네이션을 방지하고 명세서와 코드 간의 추적성을 확보합니다.

**프롬프트 2: 백엔드 기초 구현 (Reliability Focus)**

"시니어 백엔드 엔지니어로서 docs/architecture.md의 설계를 바탕으로 FastAPI 백엔드 구조를 스캐폴딩해줘.

작업 목표: TimerSettings Pydantic 모델과 create\_room API 엔드포인트 구현.  
필수 제약사항:

1. **REQ-NF-002 준수:** Pydantic 모델에 ConfigDict(strict=True)를 반드시 사용하여 데이터 신뢰성을 확보할 것.  
2. **REQ-NF-001 준수:** 엔드포인트 함수의 Cyclomatic Complexity가 10을 넘지 않도록 로직을 분리할 것.  
3. **REQ-F-001 준수:** 방 생성 및 URL 반환 로직을 구현할 것.  
4. 각 함수에는 ISO 25010 신뢰성 기준을 어떻게 만족시켰는지 설명하는 Docstring을 포함할 것."

**프롬프트 3: 프론트엔드 구현 (Usability & Maintainability Focus)**

"시니어 프론트엔드 엔지니어로서 TimerDisplay 컴포넌트를 구현해줘.

작업 목표: SVG 또는 CSS를 활용한 시각적 타이머 구현.  
필수 제약사항:

1. **REQ-NF-001 준수:** 렌더링 복잡도가 10을 넘으면 하위 컴포넌트로 분리할 것.  
2. **REQ-NF-002 준수:** 모든 Props에 대해 Strict TypeScript 인터페이스를 정의할 것 (any 사용 금지).  
3. **ISO 25010 사용성 준수:** 접근성(A11y)을 위해 적절한 ARIA role과 aria-label을 포함할 것.  
4. 비즈니스 로직은 useTimer 커스텀 훅으로 분리하여 재사용성(Reusability)을 높일 것."

**프롬프트 4: 자동화된 거버넌스 구축 (The Perfect Score Check)**

"우리의 품질 기준을 강제할 GitHub Actions 워크플로우 파일 .github/workflows/quality.yml을 작성해줘.

**포함되어야 할 Job:**

1. Backend: mypy \--strict, radon cc \--min A, pytest \--cov \--cov-fail-under=90 실행.  
2. Frontend: tsc \--noEmit, eslint \--max-warnings=0, npm test 실행.  
3. **조건:** 위 단계 중 하나라도 실패하면 파이프라인 전체를 실패 처리하여 배포를 차단할 것."

### **9.3 시나리오의 기대 효과**

이 시나리오는 AI가 개발자의 의도를 추측하게 하는 대신, \*\*명시적인 표준 문서(ISO Specs)\*\*를 따르게 만듭니다. 결과적으로 생성된 코드는 초기 단계부터 높은 신뢰성과 유지보수성을 가지게 되며, 이는 정적 분석 도구와 테스트 커버리지를 통해 정량적으로 증명됩니다. 이를 통해 Team Pomodoro Timer 프로젝트는 AI 평가 환경에서 만점을 획득할 수 있는 견고한 기반을 갖추게 됩니다.

## ---

**10\. 결론**

본 보고서는 ISO/IEC 25010 표준을 기반으로 'Team Pomodoro Timer' 프로젝트의 품질을 극대화하기 위한 포괄적인 전략을 제시했습니다. Pydantic의 Strict 모드와 Mypy를 활용한 **신뢰성** 강화, Radon 및 ESLint를 통한 **유지보수성** 지표의 강제, 그리고 llms.txt를 통한 **AI 협업 최적화**는 현대적인 고품질 소프트웨어 개발의 표준을 보여줍니다. 제시된 Master README와 개발 시나리오를 통해, 개발 팀은 인간과 AI가 협업하여 결함 없는 소프트웨어를 구축하는 이상적인 프로세스를 즉시 시작할 수 있습니다.

#### **참고 자료**

1. ISO/IEC 25010, 12월 4, 2025에 액세스, [https://iso25000.com/en/iso-25000-standards/iso-25010](https://iso25000.com/en/iso-25000-standards/iso-25010)  
2. Understanding ISO/IEC 25010: A Comprehensive Framework for Software Quality Evaluation | by Obed C | Medium, 12월 4, 2025에 액세스, [https://medium.com/@oczz/understanding-iso-iec-25010-a-comprehensive-framework-for-software-quality-evaluation-ae3cc5250057](https://medium.com/@oczz/understanding-iso-iec-25010-a-comprehensive-framework-for-software-quality-evaluation-ae3cc5250057)  
3. What is the llms.txt file, and how do you create one for your website? \- Hostinger, 12월 4, 2025에 액세스, [https://www.hostinger.com/tutorials/what-is-llms-txt](https://www.hostinger.com/tutorials/what-is-llms-txt)  
4. What is llms.txt? Why it's important and how to create it for your docs – GitBook Blog, 12월 4, 2025에 액세스, [https://www.gitbook.com/blog/what-is-llms-txt](https://www.gitbook.com/blog/what-is-llms-txt)  
5. CISQ Supplements ISO/IEC 25000 Series with Automated Quality Characteristic MEasures, 12월 4, 2025에 액세스, [https://www.it-cisq.org/cisq-supplements-isoiec-25000-series-with-automated-quality-characteristic-measures/](https://www.it-cisq.org/cisq-supplements-isoiec-25000-series-with-automated-quality-characteristic-measures/)  
6. What Is ISO 25010? | Perforce Software, 12월 4, 2025에 액세스, [https://www.perforce.com/blog/qac/what-is-iso-25010](https://www.perforce.com/blog/qac/what-is-iso-25010)  
7. Exploring Maintainability Index Variants for Software Maintainability Measurement in Object-Oriented Systems \- MDPI, 12월 4, 2025에 액세스, [https://www.mdpi.com/2076-3417/13/5/2972](https://www.mdpi.com/2076-3417/13/5/2972)  
8. Control startup and shutdown order with Compose \- Docker Docs, 12월 4, 2025에 액세스, [https://docs.docker.com/compose/how-tos/startup-order/](https://docs.docker.com/compose/how-tos/startup-order/)  
9. ISO/IEC/IEEE 29148 Requirements Specification Templates | ReqView Documentation, 12월 4, 2025에 액세스, [https://www.reqview.com/doc/iso-iec-ieee-29148-templates/](https://www.reqview.com/doc/iso-iec-ieee-29148-templates/)  
10. ISO/IEC/IEEE 29148 Systems and Software Requirements Specification (SRS) Example Template, 12월 4, 2025에 액세스, [https://www.well-architected-guide.com/documents/iso-iec-ieee-29148-template/](https://www.well-architected-guide.com/documents/iso-iec-ieee-29148-template/)  
11. flake8-adjustable-complexity \- PyPI, 12월 4, 2025에 액세스, [https://pypi.org/project/flake8-adjustable-complexity/](https://pypi.org/project/flake8-adjustable-complexity/)  
12. Strict Mode \- Pydantic, 12월 4, 2025에 액세스, [https://docs.pydantic.dev/2.6/concepts/strict\_mode/](https://docs.pydantic.dev/2.6/concepts/strict_mode/)  
13. Mypy \- Pydantic, 12월 4, 2025에 액세스, [https://docs.pydantic.dev/2.8/integrations/mypy/](https://docs.pydantic.dev/2.8/integrations/mypy/)  
14. Improving Clarity in Software Requirements Engineering Through ISO and Template Alignment | by Oleh Dubetcky, 12월 4, 2025에 액세스, [https://oleg-dubetcky.medium.com/improving-clarity-in-software-requirements-engineering-through-iso-and-template-alignment-5e96daebdcd7](https://oleg-dubetcky.medium.com/improving-clarity-in-software-requirements-engineering-through-iso-and-template-alignment-5e96daebdcd7)  
15. Architecture Viewpoint Template for ISO/IEC/IEEE 42010, 12월 4, 2025에 액세스, [http://www.iso-architecture.org/42010/templates/42010-vp-template.pdf](http://www.iso-architecture.org/42010/templates/42010-vp-template.pdf)  
16. Architecture description template for use with ISO/IEC/IEEE 42010:2011, 12월 4, 2025에 액세스, [http://www.iso-architecture.org/42010/templates/42010-ad-template.pdf](http://www.iso-architecture.org/42010/templates/42010-ad-template.pdf)  
17. The TIOBE Quality Indicator, 12월 4, 2025에 액세스, [https://tiobe.com/files/TIOBEQualityIndicator\_v4\_10.pdf](https://tiobe.com/files/TIOBEQualityIndicator_v4_10.pdf)  
18. FastAPI and Pydantic: A Powerful Duo \- Theodo Data & AI, 12월 4, 2025에 액세스, [https://data-ai.theodo.com/en/technical-blog/fastapi-pydantic-powerful-duo](https://data-ai.theodo.com/en/technical-blog/fastapi-pydantic-powerful-duo)  
19. Docker Compose Health Checks: An Easy-to-follow Guide \- Last9, 12월 4, 2025에 액세스, [https://last9.io/blog/docker-compose-health-checks/](https://last9.io/blog/docker-compose-health-checks/)  
20. Markdown Architectural Decision Records: Format and Tool Support \- ResearchGate, 12월 4, 2025에 액세스, [https://www.researchgate.net/publication/324745676\_Markdown\_Architectural\_Decision\_Records\_Format\_and\_Tool\_Support](https://www.researchgate.net/publication/324745676_Markdown_Architectural_Decision_Records_Format_and_Tool_Support)  
21. Strict Mode \- Pydantic Validation, 12월 4, 2025에 액세스, [https://docs.pydantic.dev/latest/concepts/strict\_mode/](https://docs.pydantic.dev/latest/concepts/strict_mode/)  
22. radon/docs/intro.rst at master \- GitHub, 12월 4, 2025에 액세스, [https://github.com/rubik/radon/blob/master/docs/intro.rst](https://github.com/rubik/radon/blob/master/docs/intro.rst)  
23. complexity \- ESLint \- Pluggable JavaScript Linter, 12월 4, 2025에 액세스, [https://eslint.org/docs/latest/rules/complexity](https://eslint.org/docs/latest/rules/complexity)  
24. How to use ESLint to improve your workflow \- Blog Eleven Labs, 12월 4, 2025에 액세스, [https://blog.eleven-labs.com/en/use-eslint-improve-workflow/](https://blog.eleven-labs.com/en/use-eslint-improve-workflow/)  
25. Increasing Unit Test Coverage with jest-it-up | by Ilan Klinghofer | Slalom Build | Medium, 12월 4, 2025에 액세스, [https://medium.com/slalom-build/increasing-unit-test-coverage-with-jest-it-up-108fa5c79157](https://medium.com/slalom-build/increasing-unit-test-coverage-with-jest-it-up-108fa5c79157)  
26. Configuring code coverage in Jest, the right way \- Valentino Gagliardi, 12월 4, 2025에 액세스, [https://www.valentinog.com/blog/jest-coverage/](https://www.valentinog.com/blog/jest-coverage/)  
27. What is llms.txt? Breaking down the skepticism \- Mintlify, 12월 4, 2025에 액세스, [https://www.mintlify.com/blog/what-is-llms-txt](https://www.mintlify.com/blog/what-is-llms-txt)  
28. Optimizing technical documentations for LLMs \- DEV Community, 12월 4, 2025에 액세스, [https://dev.to/joshtom/optimizing-technical-documentations-for-llms-4bcd](https://dev.to/joshtom/optimizing-technical-documentations-for-llms-4bcd)  
29. Designing for LLMs and AI Agents: Best Practices for the New Digital Users | by Pur4v, 12월 4, 2025에 액세스, [https://medium.com/@pur4v/designing-for-llms-and-ai-agents-best-practices-for-the-new-digital-users-82050320ce00](https://medium.com/@pur4v/designing-for-llms-and-ai-agents-best-practices-for-the-new-digital-users-82050320ce00)  
30. Building Robust CI/CD Pipelines: Best Practices and Automation \- Wolk, 12월 4, 2025에 액세스, [https://www.wolk.work/blog/posts/building-robust-ci-cd-pipelines-best-practices-and-automation](https://www.wolk.work/blog/posts/building-robust-ci-cd-pipelines-best-practices-and-automation)  
31. davidslusser/actions\_python\_radon: Github action for running code complexity analysis, 12월 4, 2025에 액세스, [https://github.com/davidslusser/actions\_python\_radon](https://github.com/davidslusser/actions_python_radon)  
32. Working without Netcat \- Floating Octothorpe, 12월 4, 2025에 액세스, [https://floatingoctothorpe.uk/2018/working-without-netcat.html](https://floatingoctothorpe.uk/2018/working-without-netcat.html)  
33. wait-for-it \- script to test and wait on the availability of a TCP host and port \- Ubuntu Manpage, 12월 4, 2025에 액세스, [https://manpages.ubuntu.com/manpages/bionic/man8/wait-for-it.8.html](https://manpages.ubuntu.com/manpages/bionic/man8/wait-for-it.8.html)