from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from ai.memory.store import set_memory_store, InMemoryMemoryStore
from ai.tools.memory_tools import WriteMemory
from ai.tools.next_steps import GenerateNextSteps
from ai.tools.release_notes import GenerateReleaseNotes
from ai.tools.dod_checker import DoDCheck


@dataclass
class MVPSummary:
    goal: str
    tags: List[str]
    next_steps: List[str]
    release_notes: str
    dod_summary: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def run_mvp(goal: str = "Improve agent MCP access safely", tags: List[str] | None = None, dry_run: bool = True, include_dod: bool = True) -> Dict[str, Any]:
    """Run an offline, safe MVP planning pass using local tools.

    - Initializes in-memory store
    - Writes the goal to memory
    - Proposes next steps (heuristic)
    - Generates release notes from memory
    - Runs DoD checks (local)
    Returns a dict summary for easy printing/automation.
    """
    tags = tags or ["feature"]

    # Ensure isolated in-memory store
    set_memory_store(InMemoryMemoryStore())

    # Write goal to memory
    WriteMemory(content=f"goal: {goal}", tags=tags).run()  # type: ignore

    # Propose next steps based on recent context
    steps_md = GenerateNextSteps(limit=5, tags=tags).run()  # type: ignore
    steps = [l[2:] for l in steps_md.splitlines() if l.startswith("- ")]

    # Generate release notes from memory
    notes_md = GenerateReleaseNotes(limit=20, tags=None).run()  # type: ignore

    # Run local DoD check (always safe, mirrors CI) unless skipped for speed
    if include_dod:
        dod_md = DoDCheck(lookback_commits=10).run()  # type: ignore
    else:
        dod_md = "# Definition of Done\n- [SKIPPED] Fast mode: DoD check not executed.\n"

    summary = MVPSummary(
        goal=goal,
        tags=tags,
        next_steps=steps,
        release_notes=notes_md,
        dod_summary=dod_md,
    )

    # In future: if not dry_run, we could branch, create ADR, or open a PR.
    return summary.to_dict()
