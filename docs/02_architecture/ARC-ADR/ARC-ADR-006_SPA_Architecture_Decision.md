# ADR 001: Adoption of Vite + TanStack SPA Architecture

## Status
Accepted

## Date
2025-12-11

## Context
Focus Mate is a **Productivity Tool** designed for high-focus sessions. The nature of the application requires:
1.  **Long-lived sessions**: Users stay on the timer/dashboard page for hours.
2.  **High interactivity**: Timers, task checks, and UI interactions must be instantaneous.
3.  **App-like feel**: The experience should resemble a native desktop/mobile app rather than a document-based website.
4.  **SEO Independence**: The core application logic is behind authentication and does not require search engine indexing.

We evaluated two primary refinement options:
*   **Option A: Next.js (SSR)** - The industry standard for websites and e-commerce.
*   **Option B: Vite + TanStack Router (SPA)** - The modern standard for complex web applications (e.g., Linear, Figma).

## Decision
We chose **Option B: Vite + TanStack Router (SPA)**.

## Rationale
1.  **Software Nature Alignment**: Focus Mate is an "Application," not a "Site." ISO/IEC 25010 Quality in Use (Efficiency) is maximized when the UI responds immediately without server round-trips for HTML generation.
2.  **Type Safety**: TanStack Router provides 100% type-safe routing, drastically reducing runtime errors related to broken links or missing parameters (Reliability).
3.  **Developer Experience & Maintainability**: decoupling the frontend entirely from the backend (FastAPI) allows for a cleaner separation of concerns compared to Next.js's blurred API lines.
4.  **Performance (Interactivity)**: While Next.js has faster *First Contentful Paint (FCP)*, an SPA architecture offers superior *Interaction to Next Paint (INP)* for sustained usage, which is our primary metric.

## Consequences
*   **Positive**: User experience will be smoother with no page blinks. API and Frontend are strictly decoupled using OpenAPI.
*   **Negative**: Initial load time (bundle download) might be slightly higher than SSR (mitigated by code splitting). SEO on app pages is limited (acceptable for this project).
