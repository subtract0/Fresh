from agency_swarm import Agent

Architect = Agent(
    name="Architect",
    description="Enforces TDD-first and ADR discipline before any implementation.",
    instructions=(
        "Protocol: 1) Require failing test first. 2) Require ADR draft/reference. "
        "3) After both exist, allow minimal implementation."
    ),
    temperature=0.2,
)

