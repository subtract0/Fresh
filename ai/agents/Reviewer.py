from agency_swarm import Agent
from ai.tools.memory_tools import WriteMemory, ReadMemoryContext

Reviewer = Agent(
    name="Reviewer",
    description="Reviews diffs for simplicity, security, and ADR linkage.",
    instructions=(
        "Ensure PR links ADR-XXX; check security implications; request tests for any behavior changes."
    ),
    tools=[WriteMemory, ReadMemoryContext],
    temperature=0.2,
)

