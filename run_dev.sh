#!/bin/bash

# Exit on error
set -e

# Define root directory
ROOT_DIR="$(pwd)"

echo "🚀 Starting Government-Grade RAG Assistant Local Dev Environment..."

# --- Backend Setup ---
echo "--- 🔧 Setting up Backend ---"

# Check if .venv exists
if [ -d ".venv" ]; then
    echo "Using existing virtual environment..."
    source .venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
fi

# Install backend dependencies
echo "📦 Installing backend dependencies..."
pip install -r requirements.txt

# Start Backend in background
echo "🟢 Starting Backend Server..."
# Use uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "Backend running on http://localhost:8000 (PID: $BACKEND_PID)"

# --- Frontend Setup ---
echo "--- 🎨 Setting up Frontend ---"
cd "$ROOT_DIR/frontend"

# Check if node_modules exists, if not install
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Start Frontend
echo "🟢 Starting Frontend Server..."
npm run dev &
FRONTEND_PID=$!

echo "Frontend running on http://localhost:3000 (PID: $FRONTEND_PID)"

# Cleanup function to kill processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    if ps -p $BACKEND_PID > /dev/null; then
        kill $BACKEND_PID
        echo "Backend stopped."
    fi
    if ps -p $FRONTEND_PID > /dev/null; then
        kill $FRONTEND_PID
        echo "Frontend stopped."
    fi
    exit
}

# Trap SIGINT (Ctrl+C)
trap cleanup SIGINT

# Keep script running
echo "✨ All systems go! Press Ctrl+C to stop."
wait
