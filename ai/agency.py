from __future__ import annotations
from pathlib import Path

from agency_swarm import Agency
from ai.agents.Architect import Architect
from ai.agents.Developer import Developer
from ai.agents.QA import QA
from ai.agents.Reviewer import Reviewer
from ai.agents.Father import Father

# Initialize memory store: prefer Firestore if staging creds are present, else in-memory
import os  # noqa: E402
from ai.memory.store import set_memory_store, InMemoryMemoryStore  # noqa: E402
try:
    from ai.memory.firestore import FirestoreMemoryStore  # type: ignore
except Exception:  # pragma: no cover
    FirestoreMemoryStore = None  # type: ignore

use_firestore = (
    os.getenv("FIREBASE_PROJECT_ID")
    and os.getenv("FIREBASE_CLIENT_EMAIL")
    and os.getenv("FIREBASE_PRIVATE_KEY")
)

if use_firestore and FirestoreMemoryStore is not None:
    try:
        set_memory_store(FirestoreMemoryStore())  # type: ignore
    except Exception:
        # Fallback to in-memory if Firestore init fails
        set_memory_store(InMemoryMemoryStore())
else:
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

