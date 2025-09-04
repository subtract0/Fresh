#!/usr/bin/env bash
set -euo pipefail

BASE=${BASE_REF:-origin/main}

git fetch -q origin main || true

CHANGED_SRC=$(git diff --name-only "$BASE"...HEAD | grep -E '^(ai/|src/|app/|lib/)' || true)
CHANGED_TESTS=$(git diff --name-only "$BASE"...HEAD | grep -E '^(tests?/|__tests__/)' || true)

if [[ -n "$CHANGED_SRC" && -z "$CHANGED_TESTS" ]]; then
  echo "Source changed but no tests changed. Add/modify tests."
  echo "Changed source files:" && echo "$CHANGED_SRC"
  exit 2
fi

