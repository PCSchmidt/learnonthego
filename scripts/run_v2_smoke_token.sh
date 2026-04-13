#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

PYTHON_EXE="${LOTG_PYTHON_EXE:-$REPO_ROOT/../.venv/Scripts/python.exe}"
BASE_URL="${LOTG_BASE_URL:-http://localhost:8000}"
TIMEOUT_SECONDS="${LOTG_TIMEOUT_SECONDS:-3}"
STRICT_BYOK="${LOTG_STRICT_BYOK:-false}"

if [[ -z "${LOTG_TOKEN:-}" ]]; then
  echo "ERROR: LOTG_TOKEN is required for token-based smoke test."
  echo "Set LOTG_TOKEN in your shell and retry."
  exit 1
fi

if [[ ! -x "$PYTHON_EXE" ]]; then
  echo "ERROR: Python executable not found at $PYTHON_EXE"
  echo "Set LOTG_PYTHON_EXE to your python path and retry."
  exit 1
fi

echo "Running V2 smoke test"
echo "Base URL: $BASE_URL"
echo "Timeout: ${TIMEOUT_SECONDS}s"
echo "Strict BYOK: $STRICT_BYOK"

cd "$REPO_ROOT"
LOTG_BASE_URL="$BASE_URL" \
LOTG_TIMEOUT_SECONDS="$TIMEOUT_SECONDS" \
LOTG_STRICT_BYOK="$STRICT_BYOK" \
"$PYTHON_EXE" -u scripts/v2_endpoint_smoke.py
