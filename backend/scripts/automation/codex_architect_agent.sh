#!/bin/bash

# =============================================================================
# FocusMate Autonomous Architect Agent (V10.2 - Absolute Eternal Mode)
# =============================================================================
# V10.2: Implemented a persistent reasoning loop to ensure Zero-Intervention
# Continuity. The agent now auto-restarts after each comprehensive sweep.
# =============================================================================

# Determine the directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PROJECT_ROOT="$(cd "$BACKEND_DIR/.." && pwd)"
LOG_DIR="$BACKEND_DIR/logs"
LOG_FILE="$LOG_DIR/codex_agent_history.log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"
NAS_LOG_CACHE="$LOG_DIR/nas_production.log"

# Define the Master Directive
MASTER_DIRECTIVE="
You are the SRE-Focused Architect. Your mission is to maintain and harden the existing FocusMate V1 deployment while drafting the V2 evolution in a separate namespace.

### [PROHIBITION] DO NOT OVERWRITE V1
- NEVER delete, overwrite, or destructively refactor the existing V1 code (app/api/v1, app/domain/v1, etc.).
- The operational V1 codebase is the sacred production baseline.

### [PRIORITY #1] NAS ERROR TRIAGE
- Inspect pre-fetched production logs in \`backend/logs/nas_production.log\`.
- Fix \`[ERROR]\` or \`[CRITICAL]\` entries in the V1 codebase immediately.
- Focus on stability, pgBouncer compatibility, and async safety.

### [PRIORITY #2] V1 AUDIT & HARDENING (ISO/IEC 2510)
- Audit V1 for Reliability, Security, and Performance.
- Implement non-breaking optimizations (e.g., better SQL execution plans, security headers).
- Ensure consistent error handling across all V1 endpoints.

### [PRIORITY #3] V2 EVOLUTION (Isolated Development)
- All Pydantic v2 refactoring and modern architectural changes MUST take place in a NEW directory/namespace: \`backend/app/api/v2\`, \`backend/app/domain/v2\`, etc.
- This allows for long-term development without risking the stability of the deployed V1.

### OPERATIONAL MANDATE
1. STABILITY OVER SPEED: prioritize fixes that improve uptime.
2. BREADTH OVER MINUTIAE: Skip minor formatting. Focus on structural and logic-breaking issues.
3. SACRED BASELINE: Human-authored code is the baseline. Do not revert manual fixes.

MISSION: Harden the production V1 and safely evolve the V2 bridge.
"

# Cleanup existing stale agent processes
STALE_PIDS=$(pgrep -f "codex.*codex_architect_agent.sh" | grep -v $$)
if [ -n "$STALE_PIDS" ]; then
    echo "🧹 Cleaning up stale Codex agent processes..."
    kill $STALE_PIDS 2>/dev/null || true
fi

echo "🚀 Launching Absolute Eternal Codex Architect Mode (V10.2)..."
echo "👑 Mandate: Atomic Domain Conversion + Eternal Persistence"
echo "🛡️ Safety: Prevents Pydantic V1/V2 version conflicts"
echo "Focus: High-Impact Engineering & Continuous Codebase Evolution"
echo "⚠️  Press Ctrl+C to stop at any time."
echo ""

AGENT_PID_FILE="$BACKEND_DIR/codex_architect_agent.pid"
echo $$ > "$AGENT_PID_FILE"
cd "$PROJECT_ROOT"

# Infinite reasoning loop
while true; do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🔄 Starting new Reasoning Cycle..." | tee -a "$LOG_FILE"

    # Step 0: Fetch NAS logs into local cache
    echo "📡 Fetching latest NAS logs for the agent..." | tee -a "$LOG_FILE"
    # Use python3 or python based on available alias in venv
    python3 "$BACKEND_DIR/scripts/monitoring/auto_debug_watcher.py" --fetch --lines 200 > "$NAS_LOG_CACHE" 2>&1

    # Capture output in a temporary file to check for specific error patterns
    TEMP_OUT=$(mktemp)
    codex exec --full-auto --color always "$MASTER_DIRECTIVE" 2>&1 | tee "$TEMP_OUT"
    EXIT_CODE=${PIPESTATUS[0]}

    # Append temp output to official log
    cat "$TEMP_OUT" >> "$LOG_FILE"

    # Check for usage limit errors
    if grep -Ei "usage limit|limit has been reached|Too Many Requests" "$TEMP_OUT" > /dev/null; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🛑 Usage limit reached. Stopping Agent loop for today." | tee -a "$LOG_FILE"
        rm -f "$TEMP_OUT"
        rm -f "$AGENT_PID_FILE"
        exit 0
    fi
    rm -f "$TEMP_OUT"

    if [ $EXIT_CODE -eq 0 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Cycle completed. Resting for 30 seconds (High-Frequency Mode)..." | tee -a "$LOG_FILE"
        sleep 30
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  Cycle exited with code $EXIT_CODE. Restarting in 10s..." | tee -a "$LOG_FILE"
        sleep 10
    fi
done
