---
description: How to perform autonomous debugging using NAS logs
---

# Auto-Debugging Workflow (Fully Automated)

This workflow describes the seamless, autonomous debugging process where the Architect Agent identifies and fixes production errors without human intervention.

## Core Flow (Autonomous)

1.  **Launch the Architect Agent**:
    Run the master script on your Mac. This is the only command you need:
    ```bash
    ./backend/scripts/automation/architect_agent.sh
    ```

2.  **How it works (Behind the scenes)**:
    - **Step 1 (Fetch)**: At the start of each reasoning cycle, the script calls `auto_debug_watcher.py --fetch` to pull the latest 200 lines from the NAS.
    - **Step 2 (Analyze)**: The logs are saved locally to `backend/logs/nas_production.log`.
    - **Step 3 (Prioritize)**: The agent reads this file first. If an `[ERROR]` or `Traceback` is found, it pauses general refactoring and focuses entirely on fixing that production bug.
    - **Step 4 (Fix & Deploy)**: The agent applies the fix to the local codebase, commits, and pushes to GitHub, which triggers the automatic NAS deployment hook.

3.  **User Monitoring (Optional)**:
    If you want to watch the logs in real-time while the agent works, you can still run:
    ```bash
    python3 backend/scripts/monitoring/auto_debug_watcher.py
    ```

## Benefits
- **Zero-Intervention**: Errors are caught and fixed while you sleep.
- **Resource Efficient**: Log fetching happens only once per cycle, avoiding a constant SSH stream.
- **Single Entry Point**: All automation for FocusMate is centralized in `architect_agent.sh`.
