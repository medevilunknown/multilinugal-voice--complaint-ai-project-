#!/bin/bash
# Guardia Lingua - Local Development Startup Script (macOS)
# --------------------------------------------------------

echo "🛡️ Starting Guardia Lingua Local Environment..."

# 0. Clean up any stale processes on our ports
echo "🧹 Cleaning up existing processes on 8000 and 8080..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:8080 | xargs kill -9 2>/dev/null || true

# 1. Check if Ollama is running (optional but helpful)
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
  echo "⚠️  Note: Ollama is not detected on http://localhost:11434"
  echo "   If you want to use local AI, please start Ollama and run: ollama pull llama3"
fi

# 2. Start Backend in a new terminal window
osascript -e 'tell application "Terminal" to do script "cd \"'$(pwd)'/backend\" && source .venv/bin/activate && python -m uvicorn main:app --reload --port 8000"'

echo "✅ Backend starting on http://localhost:8000"

# 3. Start Frontend in the current terminal window
echo "🚀 Starting Frontend on http://localhost:8080..."
cd frontend
npm run dev


