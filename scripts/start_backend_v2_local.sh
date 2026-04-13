#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$REPO_ROOT/backend"

PYTHON_EXE="${LOTG_PYTHON_EXE:-$REPO_ROOT/../.venv/Scripts/python.exe}"
PORT="${PORT:-8000}"

export JWT_SECRET_KEY="${JWT_SECRET_KEY:-local-dev-jwt-secret}"
export ENABLE_V2_PIPELINE="${ENABLE_V2_PIPELINE:-true}"

if [[ ! -x "$PYTHON_EXE" ]]; then
  echo "ERROR: Python executable not found at $PYTHON_EXE"
  echo "Set LOTG_PYTHON_EXE to your python path and retry."
  exit 1
fi

echo "Starting LearnOnTheGo backend"
echo "Backend dir: $BACKEND_DIR"
echo "Python: $PYTHON_EXE"
echo "Port: $PORT"
echo "ENABLE_V2_PIPELINE=$ENABLE_V2_PIPELINE"

cd "$BACKEND_DIR"
exec "$PYTHON_EXE" -m uvicorn main:app --host 0.0.0.0 --port "$PORT"
