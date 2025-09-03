#!/usr/bin/env bash
set -euo pipefail

# GitHub MCP server launcher
# Requires a GitHub token available via $GITHUB_TOKEN or gh auth token fallback.

if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  if command -v gh >/dev/null 2>&1; then
    # Use gh to retrieve a token without printing it
    export GITHUB_TOKEN="$(gh auth token 2>/dev/null || true)"
  fi
fi

if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  echo "Error: GITHUB_TOKEN is not set and gh auth token not available."
  echo "Set a token first: export GITHUB_TOKEN={{GITHUB_TOKEN}}"
  exit 1
fi

# Optionally pass through verbose logging
ARGS=( )
if [[ "${MCP_DEBUG:-}" == "1" ]]; then
  ARGS+=("--log-level" "debug")
fi

exec npx -y @modelcontextprotocol/server-github "${ARGS[@]}"

