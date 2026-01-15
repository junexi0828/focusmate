# OPS-008: Monitoring and Observability Strategy

## 1. Overview and Standards Compliance
This document defines the monitoring strategy for FocusMate, ensuring compliance with **ISO/IEC 25010** (Reliability, Maintainability) and **ISO/IEC 20000** (Service Management).

## 2. Tri-Track Monitoring Philosophy
We classify monitoring signals into three distinct tracks to ensure high availability and resource efficiency.

### Track A: Real-Time Negative Monitoring (Critical Failures) 🛑
*   **Purpose:** Immediate detection of crashes, unhandled exceptions, and logic-breaking errors.
*   **Target:** DevOps, Backend Engineers.
*   **Execution**: Continuous Daemon (Started by `start-nas.sh`).
*   **Components**:
    -   **Log Alerter (`log_alerter.py`)**: Monitors `app.log` line-by-line. Sends immediate Slack alerts for database timeouts, connection errors, and 500 status codes.
    -   **Sentry**: Automated external crash reporting for deep stack trace analysis.

### Track B: Periodic Infrastructure Monitoring (Watchdog) 🐕
*   **Purpose:** Ensure system resources (CPU, RAM) are healthy and backend services are alive.
*   **Execution**: Scheduled Task (Synology Task Scheduler - Every 5-10m).
*   **Component**:
    -   **NAS Monitor (`nas_monitor.sh`)**: Checks if the backend PID is alive and port 8000 is responsive. Automatically attempts restart if service is down.

### Track C: Business Observability & Reporting (Daily Reports) 📈
*   **Purpose:** Track user growth, focus time trends, and aggregated system logs.
*   **Execution**: Scheduled Task (Synology Task Scheduler - Daily).
*   **Component**:
    -   **Daily Health Report (`daily_health_report.py`)**: Aggregates database stats and system performance into a polymorphic Slack report for stakeholders.

---

## 3. Operational Setup (Synology NAS)

### 3.1. Real-Time Setup
Real-time monitoring is integrated into the application lifecycle. Starting the backend automatically starts the log monitor.
```bash
bash start-nas.sh  # Starts Backend + Log Alerter + Webhook Listener
```

### 3.2. Scheduled Setup (Task Scheduler)
Register the following in **Synology Control Panel -> Task Scheduler**:

| Task Name | Schedule | Command |
| :--- | :--- | :--- |
| **FocusMate Watchdog** | Every 5 min | `bash /volume1/web/focusmate-backend/scripts/monitoring/nas_monitor.sh` |
| **FocusMate Daily** | Daily (00:00) | `/volume1/web/miniconda3/envs/focusmate_env/bin/python /volume1/web/focusmate-backend/scripts/monitoring/daily_health_report.py` |

---

## 4. Maintenance and Scaling
-   **Log Rotation**: Ensure `/volume1/web/focusmate-backend/logs/` is rotated to prevent disk exhaustion.
-   **Slack Webhook**: Periodically verify that `SLACK_WEBHOOK_URL` in `.env` is valid.
-   **Watcher Review**: If the Watchdog restarts the server frequently, investigate `app.log` for memory leaks or DB connection pool exhaustion.

---
**Document Version**: 2.0
**Last Modified**: 2026-01-15
