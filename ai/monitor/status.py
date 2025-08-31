from __future__ import annotations
import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from ai.agency import build_agency
from ai.memory.store import set_memory_store, InMemoryMemoryStore, render_context
from ai.tools.next_steps import GenerateNextSteps
from ai.tools.release_notes import GenerateReleaseNotes


@dataclass
class MonitorStatus:
    agents: List[str]
    flows: List[List[str]]
    memory_context: str
    next_steps: List[str]
    release_notes: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def get_status(limit: int = 10) -> Dict[str, Any]:
    # Use in-memory store for safe readout (does not mutate existing persistent store)
    set_memory_store(InMemoryMemoryStore())

    agency = build_agency()
    agents = [a.name for a in agency.agents]
    # Extract flows by inspecting agency.agents and agency._flows if available; fallback to empty
    flows: List[List[str]] = []
    chart = getattr(agency, "_Agency__agency_chart", None) or getattr(agency, "agency_chart", None)
    if isinstance(chart, list):
        for pair in chart[1:]:
            if isinstance(pair, list) and len(pair) == 2 and hasattr(pair[0], "name") and hasattr(pair[1], "name"):
                flows.append([pair[0].name, pair[1].name])

    context = render_context(limit=limit)

    steps_md = GenerateNextSteps(limit=3).run()  # type: ignore
    steps = [l[2:] for l in steps_md.splitlines() if l.startswith("- ")]

    notes_md = GenerateReleaseNotes(limit=limit).run()  # type: ignore

    status = MonitorStatus(
        agents=agents,
        flows=flows,
        memory_context=context,
        next_steps=steps,
        release_notes=notes_md,
    )
    return status.to_dict()


if __name__ == "__main__":
    print(json.dumps(get_status(), indent=2))
