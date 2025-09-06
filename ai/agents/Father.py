"""
Father Agent - Strategic Planning and Delegation

The Father agent is the strategic planner and delegator with intelligent persistent memory.
It uses memory to track long-term goals, learn from past decisions, and maintain strategic 
context across sessions and deployments.

Key capabilities:
- Strategic planning with memory-informed decisions
- Pattern analysis across development cycles
- Context-aware delegation to specialized agents
- Continuous learning from outcomes

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
        PersistentMemorySearch,
        CrossSessionAnalytics,
        MemoryLearningPatterns
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
    CrossSessionAnalytics = DummyTool
    MemoryLearningPatterns = DummyTool
    MEMORY_TOOLS_AVAILABLE = False

# Standard tools (with graceful fallback)
try:
    from ai.tools.release_notes import GenerateReleaseNotes
    from ai.tools.next_steps import GenerateNextSteps
    from ai.tools.intent import IntentNormalizer
except ImportError:
    class DummyTool:
        def __init__(self, *args, **kwargs):
            pass
    
    GenerateReleaseNotes = DummyTool
    GenerateNextSteps = DummyTool
    IntentNormalizer = DummyTool


class Father(Agent):
    """
    Father agent with intelligent persistent memory for strategic planning and delegation.
    
    The Father agent is the strategic planner that uses memory to:
    - Track long-term goals across sessions
    - Learn from past decisions and outcomes
    - Analyze development patterns and focus areas
    - Maintain strategic context across deployments
    """
    
    def __init__(self):
        super().__init__(
            name="Father",
            description=(
                "Strategic planner and delegator with persistent memory for learning "
                "and continuous improvement. Analyzes past patterns to make better decisions."
            ),
            instructions=(
                "You are the Father agent with intelligent memory capabilities:\\n"
                "\\n"
                "MEMORY STRATEGY:\\n"
                "- Use SmartWriteMemory for goals, decisions, and strategic insights\\n"
                "- Use PersistentMemorySearch to learn from past experiences\\n"
                "- Use CrossSessionAnalytics to understand development patterns\\n"
                "- Use GetMemoryByType to review goals, decisions, and progress\\n"
                "\\n"
                "PLANNING APPROACH:\\n"
                "- Always check past similar goals and their outcomes\\n"
                "- Learn from previous errors and decisions\\n"
                "- Plan concisely (3-5 bullets max) based on learned patterns\\n"
                "- Tag memory entries appropriately (goal/decision/progress/error)\\n"
                "\\n"
                "DELEGATION:\\n"
                "- Route to Architect for TDD/ADR gates based on past requirements\\n"
                "- Consider past agent performance and specializations\\n"
                "- Share relevant context from memory with delegated agents\\n"
                "\\n"
                "LEARNING:\\n"
                "- Reflect on outcomes and store insights for future reference\\n"
                "- Identify patterns in successful vs failed approaches\\n"
                "- Continuously improve planning based on memory analysis\\n"
            ),
            tools=[
                SmartWriteMemory,
                PersistentMemorySearch,
                GetMemoryByType,
                CrossSessionAnalytics,
                MemoryLearningPatterns,
                GenerateReleaseNotes, 
                GenerateNextSteps,
                IntentNormalizer
            ],
            # Using default temperature=1.0 for OpenAI API compatibility
        )
