#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=========================================================="
echo " Starting Enterprise Doc Intelligence Local Services"
echo "=========================================================="

mkdir -p "$ROOT_DIR/data/embedded_pg" "$ROOT_DIR/data/chromadb" "$ROOT_DIR/data/uploads"

echo "-> Starting Backend on http://localhost:8000 ..."
cd "$ROOT_DIR/backend"
"$ROOT_DIR/backend/.venv/bin/python" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "-> Starting Frontend on http://localhost:3000 ..."
cd "$ROOT_DIR/frontend"
npm run dev -- --host 0.0.0.0 --port 3000 &
FRONTEND_PID=$!

cleanup() {
    echo "Stopping services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "Platform running! Press Ctrl+C to terminate."
wait
