# Contributing Guide

- Use TDD: start with failing tests, make them pass, then refactor
- Link ADRs in PR descriptions; one ADR per architecture-affecting change
- Keep documentation cross-references updated; run docs checks locally
- Prefer small, focused commits with clear messages

Commands:
- Setup: `poetry install --no-root`
- Tests: `poetry run pytest -q`
- Docs check: `python scripts/check_docs_alignment.py --strict`

Cross-references:
- Agent Development: ./AGENT_DEVELOPMENT.md
- ADR Guidelines: ../.cursor/rules/ADR.md

