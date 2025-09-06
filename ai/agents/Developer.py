"""
Developer Agent - Implementation and Development

The Developer agent is the implementation specialist with intelligent persistent memory.
It uses memory to remember successful patterns, learn from bugs, and track refactoring
techniques that worked across sessions.

Key capabilities:
- Pattern-based implementation from memory
- Learning from past bugs and solutions
- Refactoring technique knowledge accumulation
- Codebase pattern understanding

Cross-references:
    - ADR-003: Unified Enhanced Architecture Migration
    - ADR-004: Persistent Agent Memory
    - ai/memory/firestore_store.py: Persistent storage
    - ai/tools/enhanced_memory_tools.py: Memory tools
"""
try:
    from agency_swarm import Agent
except ImportError:
    # Fallback for environments without agency_swarm
    class Agent:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

# Enhanced memory tools (with graceful fallback)
try:
    from ai.tools.enhanced_memory_tools import (
        SmartWriteMemory,
        SemanticSearchMemory,
        GetRelatedMemories
    )
    from ai.tools.persistent_memory_tools import (
        PersistentMemorySearch
    )
    MEMORY_TOOLS_AVAILABLE = True
except ImportError:
    # Create placeholder tools for environments without full dependencies
    class DummyTool:
        def __init__(self, *args, **kwargs):
            pass
    
    SmartWriteMemory = DummyTool
    SemanticSearchMemory = DummyTool
    GetRelatedMemories = DummyTool
    PersistentMemorySearch = DummyTool
    MEMORY_TOOLS_AVAILABLE = False

# Standard tools (with graceful fallback)
try:
    from ai.tools.mcp_client import DiscoverMCPServers, CallMCPTool
except ImportError:
    class DummyTool:
        def __init__(self, *args, **kwargs):
            pass
    
    DiscoverMCPServers = DummyTool
    CallMCPTool = DummyTool


class Developer(Agent):
    """
    Developer agent with intelligent persistent memory for implementation and development.
    
    The Developer agent uses memory to:
    - Remember successful implementation patterns
    - Learn from past bugs and solutions
    - Track refactoring techniques that worked
    - Build knowledge of codebase patterns
    """
    
    def __init__(self):
        super().__init__(
            name="Developer", 
            description=(
                "Implementation specialist with persistent memory for learning "
                "patterns, solutions, and techniques across sessions."
            ),
            instructions=(
                "You are the Developer agent with enhanced memory capabilities:\\n"
                "\\n"
                "MEMORY STRATEGY:\\n"
                "- Use SmartWriteMemory for implementation solutions and patterns\\n"
                "- Use PersistentMemorySearch to find similar past problems\\n"
                "- Use GetRelatedMemories to explore connected solutions\\n"
                "- Store both successes AND failures for learning\\n"
                "\\n"
                "IMPLEMENTATION APPROACH:\\n"
                "- Follow RED→GREEN→REFACTOR cycle\\n"
                "- Search memory for similar implementations before starting\\n"
                "- Learn from past refactoring patterns and techniques\\n"
                "- Remember what testing approaches work for different scenarios\\n"
                "\\n"
                "KNOWLEDGE BUILDING:\\n"
                "- Store successful code patterns and techniques\\n"
                "- Document lessons learned from bugs and fixes\\n"
                "- Remember library/framework usage patterns that work\\n"
                "- Track which approaches lead to maintainable code\\n"
                "\\n"
                "QUALITY:\\n"
                "- Keep diffs small but leverage past successful patterns\\n"
                "- Prefer clarity over cleverness, based on maintenance experiences\\n"
                "- Use MCP tools when remembered patterns suggest they help\\n"
            ),
            tools=[
                SmartWriteMemory,
                PersistentMemorySearch, 
                SemanticSearchMemory,
                GetRelatedMemories,
                DiscoverMCPServers,
                CallMCPTool
            ],
            # Using default temperature=1.0 for OpenAI API compatibility
        )

