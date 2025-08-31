#!/usr/bin/env bash
set -euo pipefail

# Minimal MVP runner: prints JSON-like summary and release notes
if ! command -v poetry >/dev/null 2>&1; then
  echo "Poetry is required. Install from https://python-poetry.org/docs/#installation" >&2
  exit 2
fi

poetry install --no-interaction --no-root >/dev/null

poetry run python - <<'PY'
from ai.runner.mvp import run_mvp
import json
out = run_mvp(include_dod=False)
print(json.dumps(out, indent=2))
PY
