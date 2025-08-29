# Fresh

Minimal agent-ready Python repo with Poetry, pytest, ADRs, and CI gates.

Quick start (new machine)
- Prereqs: Python 3.12, Poetry (https://python-poetry.org/docs/#installation)
- Clone and enter:
  ```
  git clone https://github.com/subtract0/Fresh.git
  cd Fresh
  ```
- Install deps and run tests:
  ```
  bash scripts/run-tests.sh
  ```
- Create local env file (no secrets committed):
  ```
  cp -n .env.example .env || true
  ```

Common tasks
- Run tests:
  ```
  bash scripts/run-tests.sh
  ```
- Run a single test:
  ```
  poetry run pytest -q tests/test_devcycle_loop.py::test_devcycle_slugify
  ```
- Build package:
  ```
  poetry build
  ```
- Create a new ADR (written to .cursor/rules by default):
  ```
  poetry run python -c "from ai.tools.adr_logger import CreateADR; print(CreateADR(title='Decision title', status='Proposed').run())"
  ```

Rules & architecture
- See WARP.md for commands + high-level architecture.
- Hard rules:
  - No Broken Windows: fix issues before adding features; never ship unfinished code.
  - Staging-only data access: never connect agents to production databases in dev/test.
- ADRs live in .cursor/rules/ (see ADR-001, ADR-002, ADR-003).

