#!/bin/zsh
set -e
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

if [[ ! -x "$PROJECT_DIR/.venv/bin/uvicorn" ]]; then
  python3 -m venv "$PROJECT_DIR/.venv"
  "$PROJECT_DIR/.venv/bin/pip" install -r backend/requirements.txt
fi

if [[ ! -d "$PROJECT_DIR/frontend/node_modules" ]]; then
  (cd frontend && npm install)
fi

echo "ARGUS API: http://localhost:8000"
echo "ARGUS UI : http://localhost:5173"
echo "Press Ctrl+C to stop both servers."
trap 'kill 0' INT TERM EXIT
"$PROJECT_DIR/.venv/bin/uvicorn" backend.app.main:app --host 127.0.0.1 --port 8000 &
(cd frontend && npm run dev -- --host 127.0.0.1) &
wait
