from agency_swarm import Agent
from ai.tools.memory_tools import WriteMemory, ReadMemoryContext
from ai.tools.mcp_client import DiscoverMCPServers, CallMCPTool

QA = Agent(
    name="QA",
    description="Expands and hardens tests; focuses on edge cases and regression safety.",
    instructions=(
        "Add tests for edge cases. Verify failure first, then confirm green after fix."
    ),
    tools=[WriteMemory, ReadMemoryContext, DiscoverMCPServers, CallMCPTool],
    # Using default temperature=1.0 for OpenAI API compatibility
)

