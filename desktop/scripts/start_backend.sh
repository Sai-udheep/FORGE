#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}/../../backend"

echo "=== Starting FORGE 2.0 Backend Daemon ==="
cd "${BACKEND_DIR}"

if [ ! -d ".venv" ]; then
    echo "Virtual environment not found! Please run setup first."
    exit 1
fi

export PYTHONPATH="${BACKEND_DIR}"
exec "${BACKEND_DIR}/.venv/bin/uvicorn" app.main:app --host 127.0.0.1 --port 8000 --reload
