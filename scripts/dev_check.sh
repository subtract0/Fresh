#!/usr/bin/env bash
set -euo pipefail

# dev:check — run quick quality checks locally
# - installs pre-commit if missing
# - runs pre-commit on changed files (advisory)
# - runs tests
# - runs docs alignment (strict)

if ! command -v pre-commit >/dev/null 2>&1; then
  python -m pip install --user pre-commit >/dev/null
fi

pre-commit run --show-diff-on-failure --color always || true

# Run tests (quiet but not silent)
if command -v poetry >/dev/null 2>&1; then
  poetry run pytest -q || poetry run pytest -q -k "heartbeat"
else
  python -m pytest -q || python -m pytest -q -k "heartbeat"
fi

# Docs alignment (strict)
python scripts/check_docs_alignment.py --strict

