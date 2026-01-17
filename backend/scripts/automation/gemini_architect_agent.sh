#!/bin/bash

# =============================================================================
# FocusMate Autonomous Gemini Architect Agent (V1.0 - absolute Eternal Mode)
# =============================================================================
# V1.0: Persistent reasoning loop powered by Gemini CLI.
# =============================================================================

# Determine the directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PROJECT_ROOT="$(cd "$BACKEND_DIR/.." && pwd)"
LOG_DIR="$BACKEND_DIR/logs"
LOG_FILE="$LOG_DIR/gemini_agent_history.log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"
NAS_LOG_CACHE="$LOG_DIR/nas_production.log"

# Define the Master Directive
MASTER_DIRECTIVE="
You are a Production Stability Engineer. Your ONLY mission is to fix critical bugs and maintain system reliability.

### [ABSOLUTE PROHIBITION]
- NEVER delete existing code
- NEVER refactor working code
- NEVER rename files or directories
- NEVER change API contracts
- ONLY fix bugs that cause errors or crashes

### [PRIORITY #1] ERROR FIXING ONLY
- Inspect pre-fetched production logs in \\\`backend/logs/nas_production.log\\\`
- Fix ONLY \\\`[ERROR]\\\` or \\\`[CRITICAL]\\\\\\` entries that cause crashes
- Examples: syntax errors, import errors, runtime exceptions
- DO NOT touch code that works correctly

### [PRIORITY #2] MINIMAL CHANGES
- Make the smallest possible change to fix each error
- Add missing imports, fix typos, correct syntax only
- Test that the fix resolves the specific error
- DO NOT optimize, refactor, or improve working code

### [PRIORITY #3] SAFETY RULES
- If unsure whether code is broken, DO NOT modify it
- If a file has no errors in logs, DO NOT touch it
- Human-written code is sacred - preserve it exactly
- When in doubt, do nothing

MISSION: Fix critical production errors ONLY. Preserve all working code.
"

# Cleanup existing stale agent processes
STALE_PIDS=$(pgrep -f "gemini.*gemini_architect_agent.sh" | grep -v $$)
if [ -n "$STALE_PIDS" ]; then
    echo "🧹 Cleaning up stale Gemini agent processes..."
    kill $STALE_PIDS 2>/dev/null || true
fi

echo "🚀 Launching Absolute Eternal Gemini Architect Mode (V1.0)..."
echo "💎 Mandate: Atomic Domain Conversion + Eternal Persistence"
echo "🛡️ Safety: Prevents Pydantic V1/V2 version conflicts"
echo "Focus: High-Impact Engineering & Continuous Codebase Evolution"
echo "⚠️  Press Ctrl+C to stop at any time."
echo ""

AGENT_PID_FILE="$BACKEND_DIR/gemini_architect_agent.pid"
echo $$ > "$AGENT_PID_FILE"
cd "$PROJECT_ROOT"

# Infinite reasoning loop
while true; do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🔄 Starting new Gemini Reasoning Cycle..." | tee -a "$LOG_FILE"

    # Step 0: Fetch NAS logs into local cache
    echo "📡 Fetching latest NAS logs for the agent..." | tee -a "$LOG_FILE"
    python3 "$BACKEND_DIR/scripts/monitoring/auto_debug_watcher.py" --fetch --lines 200 > "$NAS_LOG_CACHE" 2>&1

    # Capture output in a temporary file to check for specific error patterns
    TEMP_OUT=$(mktemp)
    gemini -y -p "$MASTER_DIRECTIVE" 2>&1 | tee "$TEMP_OUT"
    EXIT_CODE=${PIPESTATUS[0]}

    # Append temp output to official log
    cat "$TEMP_OUT" >> "$LOG_FILE"

    # Check for usage limit errors
    if grep -Ei "usage limit|limit has been reached|Too Many Requests" "$TEMP_OUT" > /dev/null; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🛑 Usage limit reached. Stopping Gemini Agent loop for today." | tee -a "$LOG_FILE"
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
