# OPS-008: Monitoring and Observability Strategy

## 1. Overview and Standards Compliance
This document defines the monitoring and observability strategy for the FocusMate platform, designed to meet **ISO/IEC 25010 Quality Model** standards, specifically:
-   **Reliability (Fault Tolerance, Recoverability):** Rapid detection of failures via Sentry.
-   **Maintainability (Analyzability):** Clear separation of business events and technical errors.

## 2. Dual-Track Monitoring Philosophy
We classify monitoring signals into two distinct tracks based on their nature and required action. This separation prevents "alert fatigue" and ensures the right stakeholders receive relevant information.

### Track A: Negative Monitoring (Available Reliability) 🛑
*   **Purpose:** Detect software defects, unhandled exceptions, and system outages immediately.
*   **Target Audience:** DevOps, Backend Engineers.
*   **Tool:** **Sentry** (Automated Error Tracking).
*   **Triggers:**
    -   `500 Internal Server Error` (Unhandled Exceptions).
    -   Database connection failures.
    -   Redis timeouts.
    -   Critical service anomalies.
*   **Mechanism:**
    -   Exceptions are automatically captured by the `sentry-sdk` middleware in `app/main.py`.
    -   Grouped by issue signature to avoid redundant notifications.
    -   Delivers rich stack traces for debugging.

### Track B: Positive Monitoring (Business Observability) ✅
*   **Purpose:** Track operational success, business milestones, and system lifecycle events.
*   **Target Audience:** Product Owners, Stakeholders, Entire Team.
*   **Tool:** **Slack Webhook** (Manual Instrumentation).
*   **Triggers:**
    -   **Lifecycle:** Server Startup (`🚀`), Server Shutdown (`🛑`).
    -   **Business Events:** New User Signup, Subscription Payment, Goal Achievement.
    -   **Traffic:** Concurrent user spikes (e.g., >100 users).
*   **Mechanism:**
    -   Manually triggered via `app.core.notify.send_slack_notification`.
    -   Human-readable messages with actionable data.

---

## 3. Implementation Guide

### 3.1. Sentry Integration (Technical Errors)
Sentry is initialized in `app/main.py` and requires no manual invocation for standard crash reporting.

**Configuration:**
-   Enabled via `SENTRY_ENABLED=True` in `.env`.
-   DSN managed via `SENTRY_DSN`.

**Workflow:**
1.  Developer commits code.
2.  Bug causes `500 Error`.
3.  Sentry captures stack trace.
4.  Slack (Sentry Bot) notifies `#dev-alerts`.
5.  Developer fixes bug -> Issue Resolved.

### 3.2. Slack Notification (Business Events)
Use the `app.core.notify` module to send verified business events.

**Usage Example:**
```python
from app.core.notify import send_slack_notification

# Example: New User Signup
await send_slack_notification(
    message="🎉 New User Registration",
    level="info",  # Options: info (green), warning (yellow), error (red)
    details={
        "User": user.email,
        "Source": "Google OAuth",
        "Time": "2024-01-01 12:00:00"
    }
)
```

**Best Practices:**
-   **Do NOT** use this for stack traces (use Sentry).
-   **Do NOT** use for high-frequency low-value logs (use standard logging).
-   **DO** use for high-value signals that team members celebrate or need to know immediately.

## 4. Operational Maintenance
-   **Daily:** Check Sentry for new "Unresolved" issues.
-   **Weekly:** Review Slack alert volume. If too noisy, adjust `level` or throttle notifications.
-   **Monthly:** Verify Webhook validity and Sentry quota usage.
