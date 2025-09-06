"""
Architect Agent - Design and Architecture

The Architect agent is the design and architecture specialist with intelligent persistent memory.
It uses memory to learn from past architectural decisions, track TDD patterns, and build 
knowledge of design patterns that work.

Key capabilities:
- Memory-informed architectural decisions
- TDD pattern analysis and effectiveness tracking
- Design pattern learning and application
- ADR outcome tracking and lessons learned

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
        GetMemoryByType,
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
    GetMemoryByType = DummyTool
    GetRelatedMemories = DummyTool
    PersistentMemorySearch = DummyTool
    MEMORY_TOOLS_AVAILABLE = False


class Architect(Agent):
    """
    Architect agent with intelligent persistent memory for design and architecture.
    
    The Architect agent uses memory to:
    - Learn from past architectural decisions
    - Track TDD patterns and their effectiveness
    - Build knowledge of design patterns that work
    - Remember ADR outcomes and lessons
    """
    
    def __init__(self):
        super().__init__(
            name="Architect",
            description=(
                "Design and architecture specialist with persistent memory for "
                "learning design patterns, ADR outcomes, and TDD effectiveness."
            ),
            instructions=(
                "You are the Architect agent with enhanced memory capabilities:\\n"
                "\\n"
                "MEMORY STRATEGY:\\n"
                "- Use SmartWriteMemory for architectural decisions and patterns\\n"
                "- Use GetMemoryByType to review past decisions and outcomes\\n"
                "- Use PersistentMemorySearch to find similar architectural challenges\\n"
                "- Store ADR rationales and their long-term outcomes\\n"
                "\\n"
                "ARCHITECTURE PROTOCOL:\\n"
                "1) Check memory for similar past decisions and their outcomes\\n"
                "2) Require failing test first (learn from past TDD experiences)\\n"
                "3) Require ADR draft/reference (based on past complexity patterns)\\n"
                "4) After both exist, allow minimal implementation\\n"
                "\\n"
                "LEARNING FROM DECISIONS:\\n"
                "- Track which architectural patterns succeeded long-term\\n"
                "- Remember testing strategies that caught important bugs\\n"
                "- Learn from past design mistakes and their corrections\\n"
                "- Build patterns of effective ADR structures and content\\n"
                "\\n"
                "DESIGN WISDOM:\\n"
                "- Apply learned patterns while adapting to new contexts\\n"
                "- Leverage past successful abstractions and interfaces\\n"
                "- Remember which complexity vs simplicity trade-offs worked\\n"
                "- Use memory to guide when to be prescriptive vs flexible\\n"
            ),
            tools=[
                SmartWriteMemory,
                GetMemoryByType,
                PersistentMemorySearch,
                GetRelatedMemories
            ],
            # Using default temperature=1.0 for OpenAI API compatibility
        )

