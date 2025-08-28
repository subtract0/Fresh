from agency_swarm import Agency
from ai.agents.Architect import Architect
from ai.agents.Developer import Developer
from ai.agents.QA import QA
from ai.agents.Reviewer import Reviewer


def build_agency() -> Agency:
    """Construct the basic agency with directional flows.

    Flows (left -> right can initiate):
    - Architect -> Developer
    - Developer -> QA
    - QA -> Reviewer
    - Reviewer -> Architect (close loop)
    """
    agency = Agency(
        [
            Architect,
            [Architect, Developer],
            [Developer, QA],
            [QA, Reviewer],
            [Reviewer, Architect],
        ],
        shared_instructions="ai/agency_manifesto.md",
        temperature=0.2,
    )
    return agency

