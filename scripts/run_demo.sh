#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "=========================================="
echo "  Starting ProofChain Demo System"
echo "=========================================="

cleanup() {
    echo "Stopping background processes..."
    kill $(jobs -p) 2>/dev/null || true
}
trap cleanup EXIT

# 1. Start backend
echo "Starting FastAPI Backend on http://localhost:8000..."
cd "$ROOT_DIR/backend"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to be live
echo "Waiting for backend to be ready..."
sleep 3

# 2. Start frontend
echo "Starting Frontend on http://localhost:5173..."
cd "$ROOT_DIR/frontend"
npm run dev -- --host &
FRONTEND_PID=$!

echo "=========================================="
echo "  ProofChain is live!"
echo "  Frontend: http://localhost:5173"
echo "  Backend Docs: http://localhost:8000/docs"
echo "  Press Ctrl+C to terminate both servers."
echo "=========================================="

wait
