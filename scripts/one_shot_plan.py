#!/usr/bin/env python3
"""
One-shot autonomous planning pass that generates tangible artifacts in the repo.

- Runs the MVP planning (next steps + release notes + DoD summary)
- Writes outputs under docs/AUTONOMY/{next_steps,release_notes,runs}
- Prints created file paths for easy scripting

Usage:
  poetry run python scripts/one_shot_plan.py
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import sys

# Ensure project root is on path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai.runner.mvp import run_mvp


def main() -> int:
    # Run planning pass (safe, offline heuristics)
    summary = run_mvp(include_dod=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = Path(__file__).resolve().parent.parent / "docs" / "AUTONOMY"
    next_dir = base / "next_steps"
    notes_dir = base / "release_notes"
    runs_dir = base / "runs"

    # Ensure directories exist
    for d in (next_dir, notes_dir, runs_dir):
        d.mkdir(parents=True, exist_ok=True)

    # Files
    next_path = next_dir / f"next_steps_{ts}.md"
    notes_path = notes_dir / f"release_notes_{ts}.md"
    run_path = runs_dir / f"plan_{ts}.json"

    # Write next steps
    next_md_lines = [
        f"# Autonomous Next Steps ({ts})",
        "",
        "Origin: one_shot_plan (MVP planning pass)",
        "",
    ]
    steps = summary.get("next_steps", []) or []
    if steps:
        next_md_lines.append("## Proposed Steps")
        next_md_lines.extend([f"- {s}" for s in steps])
    else:
        next_md_lines.append("(No steps proposed)")

    if summary.get("dod_summary"):
        next_md_lines += ["", "## Definition of Done Summary", "", summary["dod_summary"].strip()]

    next_path.write_text("\n".join(next_md_lines), encoding="utf-8")

    # Write release notes
    notes_md = summary.get("release_notes", "").strip() or "# Release Notes\n(No content)\n"
    notes_path.write_text(notes_md, encoding="utf-8")

    # Write full JSON summary
    run_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # Print created files (for automation)
    for p in (next_path, notes_path, run_path):
        print(f"CREATED: {p}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

