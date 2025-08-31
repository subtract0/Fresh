# Fresh

> **Agent-ready Python ecosystem** with memory persistence, TDD discipline, and autonomous swarm orchestration.

## 🎯 Mission

Create a persistent-memory and learning mother-agent that spawns specialized agents with configurable roles, instructions, models, and output types.

## 🚀 Quick Navigation

- **📚 [Complete Documentation Hub](docs/INDEX.md)** - Central navigation to all docs
- **🤖 [Agent Development Guide](docs/AGENT_DEVELOPMENT.md)** - Create and configure agents
- **🚀 [Deployment Interface](docs/DEPLOYMENT.md)** - Deploy and manage agent swarms
- **⚡ [WARP Terminal Guide](WARP.md)** - Complete command reference
- **📐 [Architecture Decisions](docs/ADR_INDEX.md)** - All ADRs with cross-references

Quick start
- Prereqs: Python 3.12, Poetry (https://python-poetry.org/docs/#installation)
- Bootstrap dev environment (installs deps, prepares .env, smoke-runs tests):
  ```
  bash scripts/bootstrap.sh
  ```
- Run tests (canonical; same as CI step):
  ```
  bash scripts/run-tests.sh
  ```
- Run a single test (example):
  ```
  poetry run pytest -q tests/test_devcycle_loop.py::test_devcycle_slugify
  ```
- Build package artifacts:
  ```
  poetry build
  ```
- Create a new ADR (writes to .cursor/rules by default; set ADR_DIR to override):
  ```
  poetry run python -c "from ai.tools.adr_logger import CreateADR; print(CreateADR(title='Decision title', status='Proposed').run())"
  ```
- MVP planning pass (offline/safe):
  ```
  bash scripts/mvp.sh
  ```
- Monitor status (one-shot, non-interactive):
  ```
  bash scripts/monitor.sh
  ```
- **🎛️ Adaptive Agent Monitoring (ADR-005)**:
  ```
  PYTHONPATH=/Users/am/Code/Fresh poetry run python scripts/watch-agents-adaptive.py
  ```
  Features: Rich UI, activity-based refresh rates (1s-10s), agent timelines, memory metrics
- **🤖 Agent Activity Demo (ADR-007)**:
  ```
  PYTHONPATH=/Users/am/Code/Fresh poetry run python scripts/demo-agent-activity.py
  ```
  Simulates complete development cycle: Father→Architect→Developer→QA→Reviewer→Father
- **🧪 Monitoring Validation Suite**:
  ```
  PYTHONPATH=/Users/am/Code/Fresh poetry run python scripts/validate-monitoring.py
  ```
  Comprehensive validation of all activity levels and UI components
- TDD sandbox demo (shows RED→GREEN loop and prints a summary dict):
  ```
  poetry run python - <<'PY'
  import tempfile, pathlib
  from ai.loop.devcycle import run_devcycle_slugify_sandbox
  base = pathlib.Path(tempfile.mkdtemp())
  print(run_devcycle_slugify_sandbox(base))
  PY
  ```

Architecture (big picture)
- Agents (ai/agents/*.py)
  - Father: strategic planner and delegator; writes/reads memory and routes work
  - Architect: enforces TDD-first and ADR discipline before implementation
  - Developer: minimal code to make tests green, then refactor
  - QA: expands tests and hardens edges
  - Reviewer: checks simplicity, security, and ADR linkage
- Agency Swarm integration
  - ai/agency.py exposes build_agency(), wiring a directional flow (e.g., Architect → Developer → QA → Reviewer → Architect)
  - If agency_manifesto.md exists, it is used as shared_instructions for all agents
  - tests/test_agency_bootstrap.py validates agency construction; it runs when OPENAI_API_KEY is set to a real value and agency_swarm is installed
- Dev cycle exemplar
  - ai/loop/devcycle.py: runs a two-iteration RED→GREEN loop in a sandbox with a minimal slugify implementation

ADRs and CI gates
- TDD + ADR discipline
  - Start with failing tests, implement minimally to green, then refactor
  - Every behavior/architecture change references an ADR (ADR-###)
- CI
  - scripts/check-tests-changed.sh enforces “tests changed when src changed”
  - .github/workflows/adr-check.yml requires an ADR reference (ADR-###) in PR body
  - .github/workflows/ci.yml runs the gate then tests (OPENAI_API_KEY=dummy in CI skips the agency bootstrap test)

Persistent memory (roadmap)
- ADR-003 adopts Firebase Firestore for staging-only usage; production access is prohibited for dev/test (see ADR-002)
- Next step (planned ADR-004): introduce a MemoryStore with Firestore backend and Agency Swarm tools to read/write context, enabling the mother-agent to learn from interaction history
- Env placeholders (to be added to .env.example): FIREBASE_PROJECT_ID, FIREBASE_CLIENT_EMAIL, FIREBASE_PRIVATE_KEY (keep real secrets local in .env)

References
- WARP.md for commands and high-level architecture
- .cursor/rules/ for ADRs and collaboration rules (ADR-001, ADR-002, ADR-003, workflow.md, ADR.md)

