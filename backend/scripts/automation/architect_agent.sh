#!/bin/bash

# =============================================================================
# FocusMate Autonomous Architect Agent (V10.2 - Absolute Eternal Mode)
# =============================================================================
# V10.2: Implemented a persistent reasoning loop to ensure Zero-Intervention
# Continuity. The agent now auto-restarts after each comprehensive sweep.
# =============================================================================

# Define the Master Directive
MASTER_DIRECTIVE="
You are the Infinite Architect. Your mission is a Zero-Intervention, High-Impact audit and overhaul of the FocusMate project.

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
STALE_PIDS=$(pgrep -f "codex.*architect_agent.sh" | grep -v $$)
if [ -n "$STALE_PIDS" ]; then
    echo "🧹 Cleaning up stale agent processes..."
    kill $STALE_PIDS 2>/dev/null || true
fi

echo "🚀 Launching Absolute Eternal Architect Mode (V10.2)..."
echo "👑 Mandate: Atomic Domain Conversion + Eternal Persistence"
echo "🛡️ Safety: Prevents Pydantic V1/V2 version conflicts"
echo "Focus: High-Impact Engineering & Continuous Codebase Evolution"
echo "⚠️  Press Ctrl+C to stop at any time."
echo ""

# Infinite reasoning loop
while true; do
    echo "🔄 Starting new Reasoning Cycle..."
    # Use codex exec in non-interactive mode
    codex exec --full-auto --color always "$MASTER_DIRECTIVE"

    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 0 ]; then
        echo "✅ Cycle completed. Resting for 30s before the next sweep..."
        sleep 30
    else
        echo "⚠️  Cycle exited with code $EXIT_CODE. Restarting in 10s..."
        sleep 10
    fi
done
