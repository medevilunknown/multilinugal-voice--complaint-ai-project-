#!/bin/bash
# Guardia Lingua - Local Development Startup Script (macOS)
# --------------------------------------------------------

echo "🛡️ Starting Guardia Lingua Local Environment..."

# 1. Start Backend in a new terminal window
osascript -e 'tell application "Terminal" to do script "cd \"'$(pwd)'/backend\" && source .venv/bin/activate && python -m uvicorn main:app --reload --port 8000"'

echo "✅ Backend starting on http://localhost:8000"

# 2. Start Frontend in the current terminal window
echo "🚀 Starting Frontend on http://localhost:8080..."
cd frontend
npm run dev
