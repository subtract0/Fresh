from __future__ import annotations
import os
import subprocess
from pathlib import Path

from ai.memory.store import set_memory_store, InMemoryMemoryStore
from ai.tools.release_notes import GenerateReleaseNotes


def _run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode()


def _git_range_notes() -> str:
    # Determine base..head range
    pr_base = os.getenv("GITHUB_BASE_REF")
    head = os.getenv("GITHUB_SHA") or "HEAD"
    base = None
    if pr_base:
        base = _run(["git", "merge-base", f"origin/{pr_base}", head]).strip()
    else:
        # Fallback to origin/main
        base = _run(["git", "merge-base", "origin/main", head]).strip()
    log = _run(["git", "--no-pager", "log", f"{base}..{head}", "--pretty=format:%s"]) if base else ""
    lines = [l for l in log.splitlines() if l.strip()]
    if not lines:
        return "# Release Notes\n- No recent changes found.\n"
    out = ["# Release Notes", *[f"- {l}" for l in lines]]
    return "\n".join(out) + "\n"


def main() -> None:
    # Ensure an in-memory store (no-op if already set elsewhere)
    set_memory_store(InMemoryMemoryStore())
    md = GenerateReleaseNotes(limit=50).run()
    # If only header (<=2 lines), fallback to git-based notes
    if len([l for l in md.splitlines() if l.strip()]) <= 2:
        md = _git_range_notes()
    print(md)


if __name__ == "__main__":
    main()
