"""
QA Agent - Quality Assurance and Testing

The QA agent is the quality assurance specialist with intelligent persistent memory.
It uses memory to learn from past bugs, remember effective testing strategies, and build
knowledge of failure modes across testing scenarios.

Key capabilities:
- Pattern-based test design from past experiences
- Bug pattern recognition and prevention
- Testing strategy effectiveness tracking
- Edge case knowledge accumulation

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
        GetMemoryByType,
        GetRelatedMemories
    )
    MEMORY_TOOLS_AVAILABLE = True
except ImportError:
    # Create placeholder tools for environments without full dependencies
    class DummyTool:
        def __init__(self, *args, **kwargs):
            pass
    
    SmartWriteMemory = DummyTool
    SemanticSearchMemory = DummyTool
    GetMemoryByType = DummyTool
    GetRelatedMemories = DummyTool
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


class QA(Agent):
    """
    QA agent with intelligent persistent memory for quality assurance and testing.
    
    The QA agent uses memory to:
    - Learn from past bugs and edge cases
    - Remember effective testing strategies
    - Track which test patterns catch real issues
    - Build knowledge of failure modes
    """
    
    def __init__(self):
        super().__init__(
            name="QA",
            description=(
                "Quality assurance specialist with persistent memory for learning "
                "testing patterns, bug patterns, and effective quality strategies."
            ),
            instructions=(
                "You are the QA agent with enhanced memory capabilities:\\n"
                "\\n"
                "MEMORY STRATEGY:\\n"
                "- Use SmartWriteMemory for test patterns, bugs, and quality insights\\n"
                "- Use SemanticSearchMemory to find similar testing challenges\\n"
                "- Use GetMemoryByType to review past errors and their patterns\\n"
                "- Store both test successes and testing gaps for learning\\n"
                "\\n"
                "TESTING APPROACH:\\n"
                "- Search memory for similar components and their testing needs\\n"
                "- Learn from past bugs to identify new edge cases\\n"
                "- Remember which test patterns actually caught real issues\\n"
                "- Use past failure modes to guide current test design\\n"
                "\\n"
                "QUALITY LEARNING:\\n"
                "- Track which edge cases appear repeatedly across projects\\n"
                "- Remember integration points that commonly fail\\n"
                "- Learn from past regression incidents\\n"
                "- Build patterns of effective test organization and structure\\n"
                "\\n"
                "CONTINUOUS IMPROVEMENT:\\n"
                "- Add tests for edge cases based on learned patterns\\n"
                "- Verify failure first, then confirm green after fix\\n"
                "- Use MCP tools when memory suggests they help testing\\n"
                "- Apply lessons from past testing experiences\\n"
            ),
            tools=[
                SmartWriteMemory,
                SemanticSearchMemory,
                GetMemoryByType, 
                GetRelatedMemories,
                DiscoverMCPServers,
                CallMCPTool
            ],
            # Using default temperature=1.0 for OpenAI API compatibility
        )

