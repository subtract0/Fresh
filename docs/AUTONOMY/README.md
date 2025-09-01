# Autonomy Artifacts

The one-shot planner produces timestamped artifacts here:

- next_steps/: Proposed short next actions
- release_notes/: Summaries of recent context
- runs/: JSON payloads with planner outputs

Daily planning workflow
- The GitHub Action `.github/workflows/autonomy-planning.yml` runs the planner daily and opens/updates a PR on branch `auto/daily-planning` containing new files under this directory.

Local run
```bash path=null start=null
poetry run python scripts/one_shot_plan.py
```

