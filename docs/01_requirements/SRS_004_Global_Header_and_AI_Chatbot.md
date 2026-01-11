# Software Requirements Specification (SRS) for FocusMate - Global Header & AI Chatbot

**Version**: 1.0
**Date**: 2026-01-12
**Status**: DRAFT

---

## 1. Introduction

### 1.1 Purpose
The purpose of this document is to define the functional and non-functional requirements for the **Global Header Enhancements** (Real-time Ticker) and the **AI Chatbot Assistant** module within the FocusMate application. This document serves as the primary reference for development, testing, and verification.

### 1.2 Scope
The scope includes:
*   Implementation of a real-time, scrolling global ticker in the application header.
*   Development of an AI-powered Chatbot interface and backend integration.
*   Integration with existing WebSocket infrastructure for real-time updates.
*   Context-aware prompt engineering for the AI assistant.

### 1.3 Definitions, Acronyms, and Abbreviations
*   **SRS**: Software Requirements Specification
*   **WSS**: WebSocket Secure
*   **LLM**: Large Language Model
*   **FCP**: First Contentful Paint (Performance Metric)

---

## 2. Overall Description

### 2.1 Product Perspective
These features are extensions of the existing FocusMate web application. They interface with:
*   **Frontend**: React + TypeScript (UI Layer)
*   **Backend**: FastAPI + Redis (Event Bus)
*   **External Services**: OpenAI API (or compatible LLM provider)

### 2.2 User Characteristics
*   **Focus Seeker**: Primary user, needs visual motivation and quick assistance without breaking flow.
*   **Administrator**: Needs to broadcast system-wide messages (maintenance, emergencies).

---

## 3. Functional Requirements

### 3.1 Global Ticker (REQ-TICKER) - "The Megaphone"

#### REQ-TICKER-001: Global Broadcasting System
*   **Description**: The header MUST function as a "Global Megaphone," broadcasting real-time system-wide events to foster a sense of community and aliveness.
*   **Acceptance Criteria**:
    *   Messages scroll smoothly from right to left.
    *   **Dynamic Content Source**: Aggregates diverse data streams including:
        *   **Live User Stats**: "Currently 1,204 users focusing online."
        *   **Rankings/Achievements**: "User [Juns] just reached Top 1% in algorithm study!"
        *   **Time-Based Greetings**: "Good Morning! Start your day with a 25m session."
        *   **System Notices**: Maintenance alerts or feature highlights.
    *   Animation pauses on mouse hover.

#### REQ-TICKER-002: Message Types & Priority
*   **Description**: The system SHALL support different message categories with distinct visual indicators and broadcasting rules.
*   **Priorities**:
    1.  **URGENT/SYSTEM**: Red/Yellow accent. (e.g., Maintenance)
    2.  **ACHIEVEMENT**: Gold/Bright accent. (e.g., "UserX reached Lvl 10")
    3.  **SOCIAL**: Blue/Theme accent. (e.g., "150 users focusing")
    4.  **TIPS/QUOTES**: Neutral/Gray. (e.g., "Drink water")

#### REQ-TICKER-003: Deep Linking
*   **Description**: Ticker messages MAY contain hyperlinks or deep links.
*   **Acceptance Criteria**: Clicking a message redirects the user to the relevant page (e.g., Clicking a "New Room" alert opens the room).

### 3.2 AI Chatbot (REQ-BOT)

#### REQ-BOT-000: Architecture Strategy (Hybrid RAG)
*   **Description**: The Chatbot MUST utilize a hybrid architecture to balance performance and quality.
*   **Technical Constraint**:
    *   **Generation**: SHALL use a scalable commercial API (e.g., Gemini Flash, GPT-4o-mini) to minimize local server load (CPU/RAM).
    *   **Retrieval (RAG)**: MAY implement lightweight local vector search (e.g., FAISS/pgvector) for context retrieval if necessary, but generation must be offloaded.
    *   **Justification**: Running a full Local LLM alongside the application server is deemed too resource-intensive for the current infrastructure.

#### REQ-BOT-001: Context-Aware Assistance
*   **Description**: The Chatbot MUST be able to read the user's current session context.
*   **Context Variables**:
    *   Current Page (URL)
    *   Room Status (Active/Idle)
    *   User Stats (Total focus time today)

#### REQ-BOT-002: Floating UI Overlay
*   **Description**: The Chatbot UI SHALL be a non-intrusive floating drawer or popover.
*   **Acceptance Criteria**:
    *   Opened via "Sparkles" icon in header.
    *   Does not block the main timer view.
    *   Persists conversation history during the session.

#### REQ-BOT-003: Pre-defined Personas - "Proactive Study Coach"
*   **Description**: The AI SHALL adopt the persona of a "Proactive Study Coach" (Study Mate) rather than a passive assistant.
*   **Interaction Style**:
    *   **Proactive Nudging**: The AI actively suggests actions based on time and status.
    *   **Tone**: Strict but supportive, like a personal trainer for studying. (존댓말, 친근하지만 단호하게)
*   **Example Scenarios**:
    *   **Greeting**: "Juns님, 좋은 오후입니다! 오늘 목표 달성까지 2시간 남았네요."
    *   **Idle Detection**: "오후 2시인데 아직 세션 기록이 없습니다. 지금 바로 25분 세션을 시작해보세요!"
    *   **Post-Session**: "수고하셨습니다! 5분 휴식 후 바로 다음 세션으로 넘어갈까요?"

---

## 4. System Interface Requirements

### 4.1 WebSocket API (Ticker)
*   **Event Name**: `ticker_update`
*   **Payload Format**:
    ```json
    {
      "type": "system" | "achievement" | "social",
      "content": "Message text here",
      "priority": 1-5,
      "link": "/optional/path",
      "expires_at": "ISO-8601-Timestamp"
    }
    ```

### 4.2 Rest API (AI Chat)
*   **Endpoint**: `POST /api/v1/chat/message`
*   **Request**:
    ```json
    {
      "message": "User query",
      "context": { "route": "/room/123", "focus_time": 45 }
    }
    ```
*   **Response**: Streaming text (Server-Sent Events or Chunked response).

---

## 5. Non-Functional Requirements

### 5.1 Performance
*   **Ticker**: New message rendering delay < 200ms after WebSocket receipt.
*   **AI Response**: Time to First Token (TTFT) < 1.5 seconds.

### 5.2 Reliability
*   Ticker failure MUST NOT crash the main application header.
*   If WebSocket disconnects, the ticker SHOULD rely on cached default messages.

---
**Approved By**: __________Juns__________
**Date**: _______2026.01.12________
