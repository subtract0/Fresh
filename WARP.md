# ⚡ WARP Terminal Guide

> **For WARP (warp.dev)**: Complete command reference and workflow guide for Fresh agent development ecosystem.

**📚 Cross-References**: [Documentation Index](docs/INDEX.md) | [Agent Development Guide](docs/AGENT_DEVELOPMENT.md) | [Deployment Guide](docs/DEPLOYMENT.md)

---

## 🔧 Initialization

In Warp, initialize helper commands for this repo:

```bash
source ./.warp
```

## 🎯 Quick Command Reference

### Agent Operations
```bash
# Deploy agent swarms
./scripts/deploy.sh create research-team     # Create agent config
./scripts/deploy.sh deploy default          # Deploy default swarm  
./scripts/deploy.sh list                    # List configurations

# Request autonomous features
./scripts/ask.sh "add MCP browser integration"  # Feature request

# Monitor agent status
./scripts/monitor.sh                        # One-shot status check
```

### Development Workflow  
```bash
# Bootstrap environment
bash scripts/bootstrap.sh                   # Full setup

# Testing (matches CI)
bash scripts/run-tests.sh                   # All tests
poetry run pytest -q tests/test_name.py     # Single test

# Planning and release
bash scripts/mvp.sh                         # MVP planning pass
```

**Complete Interface Guide**: [Interface Documentation](docs/INTERFACES.md)

### Documentation Guardrails
```bash
# Run documentation alignment checks
fresh::docs::check

# Show full system status (includes docs alignment metrics)
fresh::deploy::status
```

Configuration (optional)
- DOCS_CHECK_ENABLED=true|false (default: true)
- DOCS_CHECK_INTERVAL_SEC=600 (seconds)

See also: [Capabilities vs Claims](docs/CAPABILITIES.md) and [Docs Index](docs/INDEX.md).

This guide provides comprehensive guidance for working with the Fresh agent development ecosystem.

Repository basics
- Stack: Python 3.12 with Poetry; tests use pytest
- Key dirs: ai/ (agents, tools, loop), tests/, scripts/, .cursor/rules/, .github/workflows/
- README.md is present (Quick start + common tasks)
- CI: runs “tests changed” gate, then tests; PRs must reference an ADR

Mission
- To create a persistent-memory and learning mother-agent that spawns agents; she expects arguments: name, instructions, model, output_type.

Common commands (copy-pasteable)
- Environment setup (Poetry):
  ```bash
  poetry install --no-interaction --no-root
  ```
- Bootstrap local dev (installs deps, prepares .env, smoke-runs tests):
  ```bash
  bash scripts/bootstrap.sh
  ```
- Run tests (canonical; same as CI step):
  ```bash
  bash scripts/run-tests.sh
  ```
- Run tests directly with Poetry:
  ```bash
  poetry run pytest -q
  ```
- Run a single test:
  ```bash
  poetry run pytest -q tests/test_devcycle_loop.py::test_devcycle_slugify
  ```
- Or by keyword:
  ```bash
  poetry run pytest -q -k devcycle
  ```
- Enforce “tests changed when src changed” gate (local check used in CI):
  ```bash
  bash scripts/check-tests-changed.sh
  ```
- Build package artifacts (wheel + sdist):
  ```bash
  poetry build
  ```
- Create an ADR file (writes to .cursor/rules by default; set ADR_DIR to override):
  ```bash
  # Create into .cursor/rules/
  poetry run python -c "from ai.tools.adr_logger import CreateADR; print(CreateADR(title='Decision title', status='Proposed').run())"

  # Or create into a temp/staging dir
  ADR_DIR=/tmp/adr_out poetry run python -c "from ai.tools.adr_logger import CreateADR; print(CreateADR(title='Decision title').run())"
  ```
- TDD sandbox demo (iterative RED→GREEN example; prints result dict):
  ```bash
  poetry run python - <<'PY'
  import tempfile, pathlib
  from ai.loop.devcycle import run_devcycle_slugify_sandbox
  base = pathlib.Path(tempfile.mkdtemp())
  print(run_devcycle_slugify_sandbox(base))
  PY
  ```

High-level architecture
- Agents (ai/agents/*.py)
  - Father: strategic planner and delegator; writes/reads memory and routes work
  - Architect: enforces TDD-first and ADR discipline before implementation
  - Developer: minimal code to make tests green, then refactor
  - QA: expands tests and hardens edges
  - Reviewer: checks simplicity, security, and ADR linkage
- Orchestration (Agency Swarm integration expected)
  - Implement a user-defined ai/agency.py exposing build_agency() that wires your agents and flow (e.g., Architect → Developer → QA → Reviewer → Architect)
  - Optionally reference shared_instructions via a local agency_manifesto.md as per Agency Swarm docs
  - Note: tests/test_agency_bootstrap.py expects ai.agency.build_agency; this test is skipped unless agency_swarm is installed and OPENAI_API_KEY is set to a real value
- Persistent memory (ADR-003 → ADR-004)
  - MemoryStore abstraction with in-memory default and optional Firestore backend (staging-only)
  - Tools: WriteMemory, ReadMemoryContext; default store initialized in ai/agency.py
  - Env (see .env.example): FIREBASE_PROJECT_ID, FIREBASE_CLIENT_EMAIL, FIREBASE_PRIVATE_KEY
- Tools
  - ai/tools/adr_logger.py (CreateADR): numbered ADR generator; defaults to .cursor/rules; honors ADR_DIR
  - ai/tools/test_runner.py (run_pytest): thin wrapper to invoke pytest in a given path and capture output
- Dev cycle exemplar
  - ai/loop/devcycle.py: run_devcycle_slugify_sandbox() writes failing tests in a sandbox, runs pytest (RED), writes minimal slugify implementation, reruns pytest (GREEN); returns a summary dict
- Tests (behavioral guardrails)
  - tests/test_agency_bootstrap.py: constructs an Agency via ai.agency.build_agency; skipped without real OPENAI_API_KEY or agency_swarm
  - tests/test_adr_tool.py: CreateADR writes incrementing ADR-XXX files and includes status/title
  - tests/test_devcycle_loop.py: validates the two-iteration RED→GREEN dev loop behavior
- Scripts and CI gates
  - scripts/check-tests-changed.sh: if ai/src/app/lib changed without corresponding tests, exits non-zero; used by CI
  - scripts/run-tests.sh: prefers Poetry/pytest; falls back to Node if a JS project detected (not used here)
  - scripts/bootstrap.sh: installs Poetry deps and prepares .env from .env.example if present
  - .github/workflows/ci.yml: runs the “tests changed” gate and then tests on pushes/PRs
  - .github/workflows/adr-check.yml: requires an ADR reference (ADR-###) in PR body

Local rules to obey (from .cursor/rules)
- TDD-first and ADR discipline
  - Start with failing tests, implement minimally to green, then refactor
  - Every behavior/architecture change references an ADR (ADR-###)
- Collaboration protocol
  - Summarize → Plan → Clarify (essentials only) → wait for “Go” before editing files or making changes
  - Search-first: read relevant files and official docs before proposing changes
  - Deliverables must be copy-pasteable (commands and code)
- Environment & data safety
  - Never connect agents to production databases during development/testing; use staging database endpoints and credentials (ADR-002)
- No Broken Windows (hard rule)
  - Fix issues before adding features; never ship unfinished code; keep code/tests/docs clean, simple, tidy, and documented for handoff

What’s not configured (as of now)
- No linter/type checker config detected (e.g., Ruff/Black/Mypy). No lint command provided.

Known gaps/pitfalls
- In CI, OPENAI_API_KEY=dummy (see .github/workflows/ci.yml), which intentionally skips the agency bootstrap test
- If FIREBASE_* envs are not set, memory falls back to in-memory (intended for dev); Firestore path requires google-cloud-firestore and staging credentials

---

## 🧯 Long-running commands and how to exit (ADR-009)
Some commands are intended to run continuously until you stop them:
- fresh run --watch (continuous dev loop)
- fresh::monitor::live (Rich live UI)
- fresh::monitor::web (uvicorn web monitor)

Tips
- Stop with Ctrl-C.
- For automation, prefer bounded runs (where available) such as a forthcoming `--stop-after` option for watch modes.

## 📴 Offline (safe) mode (ADR-009)
Use Offline Mode to avoid network calls during local development or demos.

Environment variable
```bash
export FRESH_OFFLINE=1
```

CLI flag (to be added)
```bash
fresh run --once --offline   # Example: run a single cycle offline
```

Behavior
- Skips networked operations (OpenAI, GitHub, remote discovery) with a clear message.
- Local paths (e.g., intelligent memory, local scans) still run.

## ⏱️ Default timeouts (ADR-009)
- External calls should use a 30s default timeout (HTTP, OpenAI, git/gh subprocesses, Firestore where applicable).
- If a command seems slow, check connectivity or re-run with Offline Mode.

---

References (source files)
- README.md (Quick start, common tasks)
- pyproject.toml (Poetry, Python 3.12, pytest config)
- ai/agents/*.py; ai/tools/adr_logger.py; ai/tools/test_runner.py; ai/loop/devcycle.py
- tests/*.py
- scripts/*.sh
- .github/workflows/*.yml
- .cursor/rules/ADR-009.md; folder-structure.md; ADR-001.md; ADR-002.md; ADR-003.md; workflow.md; PRD.md

