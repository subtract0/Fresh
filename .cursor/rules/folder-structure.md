# Fresh Repository Structure (Canonical)

Purpose: Reflect the actual layout of this repository to help agents and humans navigate consistently.

## Top-level structure

```
project-root/
├── ai/                      # Core code for agents, tools, memory, orchestration
│   ├── agents/              # Architect, Developer, QA, Reviewer, Mother, etc.
│   ├── cli/                 # fresh CLI entrypoint (python module)
│   ├── integration/         # Integrations: MCP discovery, GitHub, etc.
│   ├── loop/                # Dev loop + repo scanner
│   ├── memory/              # Intelligent store + Firestore backends & integration
│   ├── monitor/             # Web/console monitors, cost trackers
│   └── system/              # Memory/system integration utilities
├── tests/                   # Pytest suites (CI uses pytest-timeout)
├── scripts/                 # Bootstrap, diagnostics, demos, monitors
├── docs/                    # Documentation (INDEX.md hub, guides)
│   └── _generated/          # Generated inventories/reports
├── .cursor/rules/           # Collaboration rules + ADRs (ADR-###.md)
├── .github/workflows/       # CI workflows
├── fresh                    # Bash wrapper for poetry launching ai.cli.fresh
├── WARP.md                  # Warp terminal quick guide
├── pyproject.toml           # Poetry config (pytest-timeout enabled)
├── poetry.lock
├── README.md
└── .warp                    # Warp helper functions (source ./.warp)
```

## Naming conventions
- Python modules: snake_case.py
- Documentation: Title Case for top-level docs, kebab-case for files where helpful
- Environment variables: UPPER_SNAKE_CASE
- Directories: snake_case (Python), kebab-case acceptable in docs

## Security & best practices
- Never commit real secrets (.env stays local). Keep .env.example with placeholders.
- Keep a comprehensive .gitignore.
- Reference ADRs (ADR-###) in PR descriptions for behavior/architecture changes.

## Notes for agents (and humans)
- Long-running commands live in:
  - fresh run --watch (ai/cli/fresh.py)
  - scripts/watch-agents-adaptive.py (adaptive monitor)
  - fresh::monitor::web (uvicorn, ai/monitor/web.py)
- Memory defaults to an intelligent local store; Firestore backends are optional and guarded by env.
- Tests are under tests/, and CI enforces a global timeout via pytest-timeout.
