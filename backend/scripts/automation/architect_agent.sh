#!/bin/bash

# =============================================================================
# FocusMate Autonomous Architect Agent
# =============================================================================
# This script launches Codex in a "Full Auto" mode with a Master Directive
# to perform continuous audit, optimization, and debugging.
#
# WARNING: This script allows the agent to make changes autonomously.
# Ensure you have a clean git state and a backup before running!
# =============================================================================

# Define the Master Directive
MASTER_DIRECTIVE="
You are a Senior System Architect and Lead SRE. Your mission is to perform a recursive, deep-dive optimization of the FocusMate project.

Focus areas:
1. ISO/IEC 25010 Standards: Audit for Reliability, Security, Maintainability, and Performance Efficiency.
2. Backend Optimization (Python/FastAPI):
   - Refactor to Pydantic v2 and modern async patterns.
   - Optimize SQLAlchemy queries (N+1 problems, index usage).
   - Ensure robust error handling and logging.
3. Infrastructure & Deployment:
   - Harden the Synology NAS deployment configuration.
   - Verify connection pool safety and watchdog stability.
4. Security Pulse: Scan for vulnerabilities and enforce strict security headers/CORS policies.

Instructions:
- Work autonomously using the tools available.
- If you find an issue, fix it immediately.
- If you find an optimization, implement it.
- If you are blocked, explain why in a log and move to another task.
- NEVER stop until you have traversed the entire codebase and maximized its quality.
"

# Configuration
LOG_FILE="logs/architect_agent.log"
mkdir -p logs

echo "🚀 Launching Autonomous Architect Agent..."
echo "📝 Logs will be written to: $LOG_FILE"
echo "⚠️  Press Ctrl+C to stop at any time."

# Use 'expect' to handle occasional interactive prompts if they occur
# even in --full-auto mode, or simply pipe empty inputs.
# However, Codex CLI --full-auto is usually enough.
# We will use 'expect' to ensure that if it stops for a prompt, we press Enter.

if ! command -v expect &> /dev/null; then
    echo "ℹ️  'expect' not found. Installing via brew for automation..."
    brew install expect
fi

cat <<EOF > .architect_expect.exp
set timeout -1
spawn codex --full-auto "$MASTER_DIRECTIVE"
expect {
    "Are you sure?" { send "\r"; exp_continue }
    "Press Enter to continue" { send "\r"; exp_continue }
    "Continue?" { send "\r"; exp_continue }
    eof
}
EOF

# Run using nohup for background persistence
nohup expect .architect_expect.exp > "$LOG_FILE" 2>&1 &

AGENT_PID=$!
echo "✅ Agent started with PID: $AGENT_PID"
echo "To follow the progress, run: tail -f $LOG_FILE"

# Cleanup temporary expect script on exit
trap "rm -f .architect_expect.exp" EXIT
