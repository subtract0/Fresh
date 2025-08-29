# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

Repository basics
- Stack: Python 3.12 with Poetry. Dev tests use pytest.
- Key dirs: ai/ (agents, tools, loop), tests/, scripts/, .cursor/rules/, .github/workflows/.
- No README.md is present; core working rules live under .cursor/rules/.

Common commands (copy-pasteable)
- Environment setup (Poetry):
  ```
  poetry install --no-interaction --no-root
  ```
- Run tests (canonical; same as CI):
  ```
  bash scripts/run-tests.sh
  ```
- Run tests directly with Poetry:
  ```
  poetry run pytest -q
  ```
- Run a single test:
  ```
  poetry run pytest -q tests/test_devcycle_loop.py::test_devcycle_slugify
  ```
  Or by keyword:
  ```
  poetry run pytest -q -k devcycle
  ```
- Enforce “tests changed when src changed” gate (local check used in CI):
  ```
  bash scripts/check-tests-changed.sh
  ```
- Build package artifacts (wheel + sdist):
  ```
  poetry build
  ```
- Create an ADR file (writes to .cursor/rules by default; set ADR_DIR to override):
  ```
  # Create into .cursor/rules/
  poetry run python -c "from ai.tools.adr_logger import CreateADR; print(CreateADR(title='Decision title', status='Proposed').run())"

  # Or create into a temp/staging dir
  ADR_DIR=/tmp/adr_out poetry run python -c "from ai.tools.adr_logger import CreateADR; print(CreateADR(title='Decision title').run())"
  ```
- TDD sandbox demo (iterative RED→GREEN example; prints result dict):
  ```
  poetry run python - <<'PY'
  import tempfile, pathlib
  from ai.loop.devcycle import run_devcycle_slugify_sandbox
  base = pathlib.Path(tempfile.mkdtemp())
  print(run_devcycle_slugify_sandbox(base))
  PY
  ```

High-level architecture
- Orchestration (Agency Swarm)
  - ai/agency.py: build_agency() wires a directional loop
    - Architect → Developer → QA → Reviewer → Architect
    - shared_instructions="ai/agency_manifesto.md"
  - Agents (ai/agents/*.py):
    - Architect: enforces TDD-first and ADR discipline before implementation.
    - Developer: minimal code to make tests pass, then refactor.
    - QA: expands tests and hardens edges.
    - Reviewer: checks simplicity, security implications, ADR linkage.
- Tools
  - ai/tools/adr_logger.py (CreateADR): numbered ADR generator. Defaults to .cursor/rules; honors ADR_DIR.
  - ai/tools/test_runner.py (run_pytest): thin wrapper to run pytest in a given path and capture output.
- Dev cycle exemplar
  - ai/loop/devcycle.py: run_devcycle_slugify_sandbox() creates a sandbox, writes failing tests, runs pytest (RED), writes minimal slugify implementation, reruns pytest (GREEN); returns a summary dict.
- Tests (behavioral guardrails)
  - tests/test_agency_bootstrap.py: Agency constructs and has ≥4 distinct agents when agency_swarm is available.
  - tests/test_adr_tool.py: CreateADR writes incrementing ADR-XXX files and includes status/title.
  - tests/test_devcycle_loop.py: Validates the two-iteration RED→GREEN dev loop behavior.
- Scripts and CI gates
  - scripts/check-tests-changed.sh: If ai/src/app/lib changed without corresponding tests, exits with error. Used by CI.
  - scripts/run-tests.sh: Prefers Poetry/pytest; falls back to Node if a JS project is detected (not used here).
  - .github/workflows/ci.yml: Runs the “tests changed” gate and then tests on pushes/PRs.
  - .github/workflows/adr-check.yml: Requires an ADR reference (ADR-###) in PR body.

Local rules to obey (from .cursor/rules)
- TDD-first and ADR discipline
  - Start with failing tests, implement minimally to green, then refactor.
  - Every behavior/architecture change references an ADR (ADR-###).
- Collaboration protocol
  - Summarize → Plan → Clarify (essentials only) → wait for “Go” before editing files or making changes.
  - Search-first: read relevant files and official docs before proposing changes.
  - Deliverables must be copy-pasteable (commands and code).
- Environment & data safety
  - Never connect agents to production databases during development/testing; use staging database endpoints and credentials.

What’s not configured (as of now)
- No linter/type checker config detected (e.g., Ruff/Black/Mypy). No lint command provided.

References (source files)
- pyproject.toml (Poetry, Python 3.12, pytest config)
- ai/agency.py; ai/agents/*.py; ai/agency_manifesto.md
- ai/tools/adr_logger.py; ai/tools/test_runner.py
- ai/loop/devcycle.py
- tests/*.py
- scripts/check-tests-changed.sh; scripts/run-tests.sh
- .github/workflows/ci.yml; .github/workflows/adr-check.yml
- .cursor/rules/ADR.md; ADR-001.md; workflow.md; folder-structure.md; PRD.md

