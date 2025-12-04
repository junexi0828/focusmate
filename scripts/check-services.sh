#!/bin/bash
# Focus Mate - Check Service Status

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🔍 Focus Mate - Service Status Check"
echo "======================================"
echo ""

# Check Backend
echo "🔧 Backend Status:"
BACKEND_PID=$(ps aux | grep "[u]vicorn app.main:app" | awk '{print $2}' | head -1)
if [ -n "$BACKEND_PID" ]; then
    echo "   ✅ Running (PID: $BACKEND_PID)"
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "   ✅ Health check: OK"
        echo "   📍 API: http://localhost:8000"
    else
        echo "   ⚠️  Health check: FAILED"
    fi
else
    echo "   ❌ Not running"
fi
echo ""

# Check Frontend
echo "🎨 Frontend Status:"
FRONTEND_PID=$(ps aux | grep "[n]pm run dev\|[v]ite" | awk '{print $2}' | head -1)
if [ -n "$FRONTEND_PID" ]; then
    echo "   ✅ Running (PID: $FRONTEND_PID)"
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "   ✅ Health check: OK"
        echo "   📍 Frontend: http://localhost:3000"
    else
        echo "   ⚠️  Health check: FAILED"
    fi
else
    echo "   ❌ Not running"
fi
echo ""

# Show recent logs
if [ -f /tmp/focusmate-backend.log ]; then
    echo "📋 Backend Logs (last 5 lines):"
    tail -5 /tmp/focusmate-backend.log
    echo ""
fi

if [ -f /tmp/focusmate-frontend.log ]; then
    echo "📋 Frontend Logs (last 5 lines):"
    tail -5 /tmp/focusmate-frontend.log
    echo ""
fi

echo "======================================"

