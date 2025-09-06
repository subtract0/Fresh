"""
Enhanced Developer Agent with Intelligent Memory Capabilities

Extends the base Developer with advanced memory tools for learning from past
implementations and finding related solutions.
"""
from agency_swarm import Agent
from ai.tools.memory_tools import WriteMemory, ReadMemoryContext
from ai.tools.enhanced_memory_tools import (
    SmartWriteMemory, 
    SemanticSearchMemory, 
    GetMemoryByType,
    GetRelatedMemories
)
from ai.tools.mcp_client import DiscoverMCPServers, CallMCPTool

EnhancedDeveloper = Agent(
    name="Enhanced_Developer",
    description=(
        "Implements smallest change to make tests green with intelligent memory assistance. "
        "Learns from past implementations and searches for related solutions."
    ),
    instructions=(
        "Follow RED→GREEN→REFACTOR with memory intelligence. 1) Search for similar tasks "
        "and solutions before implementing. 2) Keep diffs small. 3) Document decisions and "
        "patterns learned. 4) Prefer clarity over cleverness. Use semantic search to find "
        "related implementations and avoid repeating past mistakes."
    ),
    tools=[
        # Enhanced memory tools with intelligence
        SmartWriteMemory, 
        SemanticSearchMemory,
        GetMemoryByType,
        GetRelatedMemories,
        # Keep existing functionality
        WriteMemory, 
        ReadMemoryContext, 
        DiscoverMCPServers, 
        CallMCPTool
    ],
    # Using default temperature=1.0 for OpenAI API compatibility
)
