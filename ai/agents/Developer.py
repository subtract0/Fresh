from agency_swarm import Agent
from ai.tools.memory_tools import WriteMemory, ReadMemoryContext
from ai.tools.mcp_client import DiscoverMCPServers, CallMCPTool

Developer = Agent(
    name="Developer",
    description="Implements smallest change to make tests green, then refactors.",
    instructions=(
        "Follow RED→GREEN→REFACTOR. Keep diffs small. Prefer clarity over cleverness."
    ),
    tools=[WriteMemory, ReadMemoryContext, DiscoverMCPServers, CallMCPTool],
    temperature=0.2,
)

