# New Feature Ideas & Roadmap

> 💡 **Strategic Goal:** Create a rich, interactive study environment with minimal operating costs. Implement "Internal Bots" that run on our backend rather than separate services.

## 1. The "90/10" Hybrid Bot Architecture
**Core Philosophy:** 90% of requests are handled by free, instant logic. Only the top 10% of complex queries go to the LLM (Gemini).

### Logic Flow (The Waterall)
When a user sends a message, the backend (`handle_message`) processes it in this order:

1.  **Command interceptor (90% - Instant)**
    *   Check for prefixes: `@`, `/`
    *   Example: `@쓴소리` -> Returns random pre-written quote.
    *   Example: `@노래` -> Updates room music state.
    *   **Cost: $0 / Latency: ~10ms**

2.  **FAQ Matcher (Rules - Very Fast)**
    *   If no command, check keywords: "사용법", "타이머안됨", "랭킹"
    *   Return pre-written help text.
    *   **Cost: $0 / Latency: ~10ms**

3.  **LLM Agent (10% - Fallback)**
    *   Trigger: Explicit call like `@AI` or detected "Complex Question" that fails FAQ match.
    *   Action: Call Gemini API (Free Tier).
    *   **Cost: $0 (within limits) / Latency: ~1-3s**

---

## 2. Feature Specification

### A. 🤬 Nagging Bot (Motivation Manager)
*   **Trigger**: `@쓴소리`, `@매니저`, `@혼내줘`
*   **Response**: Random selection from a curated list of strict motivational quotes.
*   **UI Effect**: Messages appear with a special "Mega Phone" icon or red border to distinguish from users.
*   **Dataset Needed**: List of 50-100 "tough love" quotes.

### B. 🎵 DJ / Music Integration
*   **Trigger**: `@노래 lofi`, `@노래 quiet`, `@노래 off`
*   **Implementation**:
    *   **Frontend**: Embed `react-youtube` (hidden or minimized mode).
    *   **Backend**: Add `music_video_id` and `music_status` to the Room model.
    *   **Sync**: When host changes music, websocket event broadcasts to all participants to sync video ID.
*   **Content**: Curated list of safe-for-work study streams (Lofi Girl, Cafe Jazz).

### C. 🖼️ Visual Themes
*   **Trigger**: `@배경 [keyword]` (e.g., `@배경 비오는날`, `@배경 도서관`)
*   **Theory**: Uses Unsplash Source API to fetch an image URL based on the keyword and updates `room_cackground_url`.
*   **Effect**: Instantly changes the mood of the room for all participants.

### D. 🤖 AI Study Assistant (The LLM Part)
*   **Trigger**: `@AI [question]`
*   **Model**: Google Gemini (Flash model - cost effective/free).
*   **Capabilities**:
    *   "Study Plan Generation": `@AI 오늘 3시간 남았는데 수학 계획 짜줘`
    *   "Concept Explanation": `@AI 피타고라스 정의가 뭐야?`

---

## 3. Development Roadmap (Prioritized)

### Phase 1: Foundation & Nagging Bot
- [ ] Refactor `chatService.py` to support "System Messages" (messages sent by the server).
- [ ] Implement the **Command Interceptor** logic.
- [ ] Add the "Nagging" dataset and `@쓴소리` handler.
- [ ] **Goal**: Verify the "Bot" concept works technically.

### Phase 2: Room State & Music
- [ ] Update `Room` DB schema to hold `music_id` and `theme_url`.
- [ ] Update Frontend `Room.tsx` to mount the YouTube Widget.
- [ ] Implement `@노래` commands.

### Phase 3: The AI Brain
- [ ] Integrate Google Gemini API Key.
- [ ] Implement `@AI` handler.
- [ ] Add rate limiting (prevent abuse of free tier).
