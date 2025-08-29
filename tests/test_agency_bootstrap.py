import importlib
import os
import sys

import pytest


@pytest.mark.skipif(
    os.getenv("OPENAI_API_KEY") in (None, "", "dummy"),
    reason="No OpenAI key available for agency_swarm; skipping networked assistant init",
)
def test_agency_bootstrap_constructs():
    try:
        import agency_swarm  # noqa: F401
    except Exception:
        pytest.skip("agency_swarm not installed")

    # Import builder
    from ai.agency import build_agency  # type: ignore

    agency = build_agency()

    # Basic type/shape assertions without depending on internal structure
    from agency_swarm.agency.agency import Agency  # type: ignore

    assert isinstance(agency, Agency)

    # Expect at least 4 distinct agent names in the flow
    names = [a.name for a in agency.agents]
    assert len(set(names)) >= 4

