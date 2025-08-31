#!/usr/bin/env bash
set -euo pipefail

# Ask and implement interface: describe what you want, get a feature branch with implementation plan
if [ $# -eq 0 ]; then
  echo "Usage: bash scripts/ask.sh 'describe what you want implemented'"
  echo "Example: bash scripts/ask.sh 'add a web scraper tool for documentation'"
  exit 1
fi

if ! command -v poetry >/dev/null 2>&1; then
  echo "Poetry is required. Install from https://python-poetry.org/docs/#installation" >&2
  exit 2
fi

poetry install --no-interaction --no-root >/dev/null
poetry run python -m ai.interface.ask_implement "$*"
