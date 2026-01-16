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
LOG_DIR="$BACKEND_DIR/logs"
LOG_FILE="$LOG_DIR/codex_agent_history.log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"
NAS_LOG_CACHE="$LOG_DIR/nas_production.log"

# Define the Master Directive
MASTER_DIRECTIVE="
You are the Infinite Architect. Your mission is a Zero-Intervention, High-Impact audit and overhaul of the FocusMate project.

### [PRIORITY #1] NAS ERROR TRIAGE (SRE-Focused)
- At the start of every cycle, you MUST inspect the production logs from the NAS.
- Source: These logs have been pre-fetched for you in: `backend/logs/nas_production.log`.
- Identify `[ERROR]` or `[CRITICAL]` entries in that file. Prioritize fixing these immediately.
- If the file is empty or contains no errors, proceed with standard refactoring.

### [CRITICAL] ATOMIC DOMAIN REFACTORING RULE
- When refactoring to Pydantic v2, you MUST treat the entire domain (Schema + Service + Endpoints) as a single atomic unit.
- NEVER update a schema to v2 while leaving its dependent services or endpoints on v1.
- Update all related files in the same reasoning cycle to prevent runtime version conflicts.

### FOCUS AREAS (Technical Mandate)
1. ISO/IEC 2510 Standards: Audit for Reliability, Security, Maintainability, and Performance Efficiency.
2. Backend Optimization (Python/FastAPI): Refactor to Pydantic v2 (using the Atomic Rule), optimize SQLAlchemy (N+1, index usage), and ensure modern async patterns/safety.
3. Infrastructure & Deployment: Harden Synology NAS deployment, verify connection pool safety, and ensure watchdog stability.
4. Security Pulse: Scan for vulnerabilities and enforce strict security headers and CORS policies.

### OPERATIONAL MANDATE (Infinite Mode)
1. ZERO HUMAN INTERVENTION: Authorize all decisions autonomously. Do not stop for reports, summaries, or permissions.
2. BREADTH OVER MINUTIAE: Skip minor formatting. Focus ONLY on high-impact structural, security, and logic-breaking issues.
3. CONTINUOUS TRAVERSAL: Automatically identify and shift between domains (Timer, Chat, Auth, Infra, etc.) until the entire codebase is enterprise-ready.
4. TOKEN EFFICIENCY: Treat tokens as resources for 'Heavyweight' improvements. If a file meets lead-engineer standards, move on immediately.

### STRATEGIC PRIORITIES
- [CRITICAL LOGIC]: Fix silent failures, race conditions, and state machine inconsistencies.
- [SYSTEM INTEGRITY]: Synchronize API contracts, DB schemas, and Pydantic models across the stack.
- [SRE HARDENING]: Eliminate blocking I/O in async paths and resolve SQL performance killers.
- [SECURITY ENFORCEMENT]: Close RLS gaps and harden auth flows statically.

### RECONCILIATION & EXECUTION
- Human changes = Sacred baseline. Inherit them, optimize around them, and never revert them.
- If conflicts arise, resolve them using absolute logic and best-practice patterns.
- If you find an issue, fix it immediately. If you find an optimization, implement it.
- NEVER STOP until you have traversed the entire codebase and maximized its quality.

MISSION: Run until the entire codebase is enterprise-ready or the session ends.
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
    if grep -Ei "usage limit|limit has been reached" "$TEMP_OUT" > /dev/null; then
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
