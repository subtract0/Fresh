# CI/CD Documentation

Current workflows:
- .github/workflows/ci.yml — core CI (tests changed gate + pytest)
- .github/workflows/adr-check.yml — PRs must reference an ADR
- .github/workflows/docs-alignment.yml — documentation alignment checks (new)

Local equivalents:
- scripts/run-tests.sh — run test suite
- scripts/check-tests-changed.sh — ensure tests changed with code

Cross-references:
- Quality Gates: ./QUALITY_GATES.md
- Testing: ./TESTING.md
- ADR Index: ./ADR_INDEX.md

---

## Daily Autonomous Planning (GitHub Actions)

A daily non-interactive workflow generates planning artifacts and opens/updates a PR.

- Workflow file: .github/workflows/autonomy-planning.yml
- Runtime: Python 3.12 (matches pyproject)
- Schedule: 05:16 UTC daily (cron)
- Steps:
  1) Checkout repo, install Poetry
  2) poetry install --no-root
  3) Run one-shot planner: `poetry run python scripts/one_shot_plan.py`
  4) Create or update PR on branch auto/daily-planning (using peter-evans/create-pull-request)
- Artifacts added (version-controlled):
  - docs/AUTONOMY/next_steps/*.md
  - docs/AUTONOMY/release_notes/*.md
  - docs/AUTONOMY/runs/*.json

Notes
- The workflow only touches docs/AUTONOMY/** (see add-paths) and is safe and non-destructive.
- Merge cadence is up to you; the PR will refresh daily with the latest planning snapshot.

