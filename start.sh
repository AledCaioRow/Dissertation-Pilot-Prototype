#!/usr/bin/env bash
# One-step local launch for the study app (backend + frontend), for Mac/Linux.
# Runs in STUB mode out of the box (no API key needed). First run installs dependencies.
set -e
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  echo "First run: setting up the Python virtualenv…"
  python3 -m venv .venv
  ./.venv/bin/pip install --quiet --upgrade pip
  ./.venv/bin/pip install --quiet -r requirements.txt
fi

if [ ! -d frontend/node_modules ]; then
  echo "First run: installing frontend dependencies…"
  (cd frontend && npm install)
fi

echo ""
echo "Starting the study app…"
echo "  backend  -> http://localhost:8000"
echo "  frontend -> http://localhost:5173   (opens in your browser)"
echo "Press Ctrl+C to stop both."
echo ""

./.venv/bin/python -m uvicorn backend.main:app --port 8000 &
BACKEND_PID=$!
(cd frontend && npm run dev) &
FRONTEND_PID=$!

trap "echo; echo 'Stopping…'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" INT TERM
wait
