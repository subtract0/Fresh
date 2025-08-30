from __future__ import annotations
from pathlib import Path

from agency_swarm import Agency
from ai.agents.Architect import Architect
from ai.agents.Developer import Developer
from ai.agents.QA import QA
from ai.agents.Reviewer import Reviewer
from ai.agents.Father import Father

# Initialize default memory store (in-memory by default) so tools can operate
from ai.memory.store import set_memory_store, InMemoryMemoryStore  # noqa: E402
set_memory_store(InMemoryMemoryStore())


def build_agency() -> Agency:
    """Construct the basic agency with directional flows.

    Flows (left -> right can initiate):
    - Architect -> Developer
    - Developer -> QA
    - QA -> Reviewer
    - Reviewer -> Architect (close loop)

    If a local agency_manifesto.md exists, it will be used as shared instructions.
    """
    repo_root = Path(__file__).resolve().parents[1]
    manifesto = repo_root / "agency_manifesto.md"

    agency_chart = [
        Father,
        [Father, Architect],
        [Architect, Developer],
        [Developer, QA],
        [QA, Reviewer],
        [Reviewer, Father],
    ]

    kwargs = {"temperature": 0.2}
    if manifesto.exists():
        kwargs["shared_instructions"] = str(manifesto)

    return Agency(agency_chart, **kwargs)

