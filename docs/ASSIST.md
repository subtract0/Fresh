# Assist workflow

Fresh provides safe, planning-first assist commands that never modify code by default.

Commands:
- Scan: Find TODO/FIXME and issues deterministically
  - python -m ai.cli.fresh assist scan . --json --limit 10
- Report: Generate a markdown plan (docs-only artifact)
  - python -m ai.cli.fresh assist report . --out assist_report.md
- Plan PR: Create a docs-only branch with the report and optional draft PR
  - python -m ai.cli.fresh assist plan-pr . --out assist_report.md --push --create-pr

Guardrails:
- Enforces docs-only staged content (docs/**, .fresh/**, *.md, *.rst, *.txt)
- Refuses to proceed on dirty working tree unless only the report is dirty
- Deterministic ordering and policy-driven allow/deny filters via .fresh/assist.yaml

Examples:
- JSON scan with allow filter:
  - python -m ai.cli.fresh assist scan . --json --allow src ai
- Generate and commit a report (new branch auto-named):
  - python -m ai.cli.fresh assist plan-pr .

Notes:
- Passing --push and --create-pr requires the GitHub CLI (gh) and an authenticated remote.
- No code changes are performed by these commands.

