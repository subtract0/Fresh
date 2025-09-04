#!/usr/bin/env bash
set -euo pipefail

if [ -f pyproject.toml ]; then
  if command -v poetry >/dev/null 2>&1; then
    poetry install --no-interaction --no-root >/dev/null
    poetry run pytest -q
    exit 0
  fi
fi

if [ -f package.json ]; then
  if command -v yarn >/dev/null 2>&1 && [ -f yarn.lock ]; then
    yarn --frozen-lockfile --silent
    yarn test --silent
  else
    npm ci --silent
    npm test --silent
  fi
  exit 0
fi

if command -v pytest >/dev/null 2>&1; then
  pytest -q
  exit 0
fi

echo "No test runner found. Add Poetry/pytest or npm/yarn tests." >&2
exit 1

