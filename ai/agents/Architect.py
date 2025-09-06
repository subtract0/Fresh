from agency_swarm import Agent
from ai.tools.memory_tools import WriteMemory, ReadMemoryContext

Architect = Agent(
    name="Architect",
    description="Enforces TDD-first and ADR discipline before any implementation.",
    instructions=(
        "Protocol: 1) Require failing test first. 2) Require ADR draft/reference. "
        "3) After both exist, allow minimal implementation."
    ),
    tools=[WriteMemory, ReadMemoryContext],
    # Using default temperature=1.0 for OpenAI API compatibility
)

