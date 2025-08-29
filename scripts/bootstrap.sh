#!/usr/bin/env bash
set -euo pipefail

# Bootstrap script for a fresh machine
# - Installs Poetry deps
# - Creates .env from .env.example if missing

if ! command -v poetry >/dev/null 2>&1; then
  echo "Poetry is required. Install from https://python-poetry.org/docs/#installation" >&2
  exit 2
fi

poetry install --no-interaction --no-root

if [ -f .env ]; then
  echo ".env already exists, leaving it unchanged."
else
  if [ -f .env.example ]; then
    cp .env.example .env
    echo "Created .env from .env.example"
  else
    echo "No .env.example found; creating an empty .env"
    touch .env
  fi
fi

echo "Running tests to validate setup..."
poetry run pytest -q || true

echo "Bootstrap complete."

