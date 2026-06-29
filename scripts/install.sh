#!/usr/bin/env bash
# Idempotent dependency installation for ResearchCloud (backend + frontend).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# --- Backend (Python / FastAPI) ---
if [ -f "$ROOT/backend/pyproject.toml" ]; then
  cd "$ROOT/backend"
  if ! python3 -m venv .venv 2>/dev/null; then
    echo "python venv unavailable; attempting to install python3-venv"
    sudo apt-get update -qq && sudo apt-get install -y -qq python3-venv
    python3 -m venv .venv
  fi
  ./.venv/bin/pip install --upgrade pip -q
  ./.venv/bin/pip install -e ".[dev]" -q
fi

# --- Frontend (Node / Vite) ---
if [ -f "$ROOT/frontend/package.json" ]; then
  cd "$ROOT/frontend"
  npm install
fi

echo "ResearchCloud dependencies installed."
