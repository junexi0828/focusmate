#!/bin/bash
# Focus Mate Frontend - Quick Start Script

set -e

# Change to frontend directory (script is in frontend/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Focus Mate Frontend - Starting..."
echo "   Working directory: $(pwd)"
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo "✅ Dependencies installed"
    echo ""
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ .env file created. Please review and update if needed."
    else
        echo "⚠️  .env.example not found. Skipping..."
    fi
    echo ""
fi

echo "✅ Setup complete!"
echo ""
echo "🚀 Starting development server..."
echo "📍 Frontend: http://localhost:3000"
echo ""

# Run dev server
npm run dev

