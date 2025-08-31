#!/usr/bin/env bash
set -euo pipefail

# Agent deployment interface: configure and deploy agent swarms

if ! command -v poetry >/dev/null 2>&1; then
  echo "Poetry is required. Install from https://python-poetry.org/docs/#installation" >&2
  exit 2
fi

# Install dependencies if needed
poetry install --no-interaction --no-root >/dev/null

if [ $# -eq 0 ]; then
  echo "Agent Deployment Interface"
  echo ""
  echo "Commands:"
  echo "  create [name]           - Create agent configuration"
  echo "  deploy [config] [ctx]   - Deploy agents from config"
  echo "  list                    - List available configurations"
  echo "  edit [config]           - Open config file for editing"
  echo ""
  echo "Examples:"
  echo "  ./scripts/deploy.sh create research-team"
  echo "  ./scripts/deploy.sh deploy research-team 'focus on MCP documentation'"
  echo "  ./scripts/deploy.sh list"
  exit 1
fi

command="$1"
shift

case "$command" in
  "create")
    config_name="${1:-default}"
    poetry run python -m ai.interface.deploy_agents create "$config_name"
    echo ""
    echo "Edit the config file to customize agents:"
    echo "  ./scripts/deploy.sh edit $config_name"
    ;;
  "deploy")
    config_name="${1:-default}"
    context="${2:-}"
    if [ -n "$context" ]; then
      poetry run python -m ai.interface.deploy_agents deploy "$config_name" "$context"
    else
      poetry run python -m ai.interface.deploy_agents deploy "$config_name"
    fi
    ;;
  "list")
    poetry run python -m ai.interface.deploy_agents list
    ;;
  "edit")
    config_name="${1:-default}"
    config_file="agent_configs/${config_name}.yaml"
    if [ ! -f "$config_file" ]; then
      echo "Config file not found: $config_file"
      echo "Create it first with: ./scripts/deploy.sh create $config_name"
      exit 1
    fi
    ${EDITOR:-nano} "$config_file"
    ;;
  *)
    echo "Unknown command: $command"
    echo "Run ./scripts/deploy.sh for usage help"
    exit 1
    ;;
esac
