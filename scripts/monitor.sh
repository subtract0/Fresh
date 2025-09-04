#!/usr/bin/env bash
set -euo pipefail

if ! command -v poetry >/dev/null 2>&1; then
  echo "Poetry is required. Install from https://python-poetry.org/docs/#installation" >&2
  exit 2
fi

poetry install --no-interaction --no-root >/dev/null
poetry run python -m ai.monitor.status
