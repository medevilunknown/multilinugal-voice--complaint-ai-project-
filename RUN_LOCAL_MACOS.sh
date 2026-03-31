#!/bin/bash
# Guardia Lingua - Local Development Startup Script (macOS)
# --------------------------------------------------------

echo "🛡️ Starting Guardia Lingua Local Environment..."

# 0. Clean up any stale processes on our ports
echo "🧹 Cleaning up existing processes on 8000 and 8080..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:8080 | xargs kill -9 2>/dev/null || true

# 1. Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
  echo "⚠️  Note: Ollama is not detected on http://localhost:11434"
  echo "   To use local AI, please start Ollama and run: ollama pull llama3"
fi

# 2. Start Backend in the background
echo "🛡️  Starting Backend on http://localhost:8000..."
cd "$(pwd)/backend"
source .venv/bin/activate
echo "💾 Running database migrations..."
python migrate.py
python -m uvicorn main:app --port 8000 --reload > backend.log 2>&1 &
BACKEND_PID=$!


# Ensure backend stops if this script is killed
trap "kill $BACKEND_PID; exit" INT TERM EXIT

echo "✅ Backend PID: $BACKEND_PID (Logs: backend/backend.log)"
echo "⏳ Waiting 3 seconds for backend to initialize..."
sleep 3

# 3. Start Frontend in the foreground
echo "🚀 Starting Frontend on http://localhost:8080..."
cd ../frontend
npm run dev
