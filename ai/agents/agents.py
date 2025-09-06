"""
Unified Agent Configurations

Agent configurations with intelligent memory system for persistent learning
and cross-session knowledge retention.

All agents now integrate:
- Intelligent memory classification and storage
- Persistent memory across sessions
- Learning pattern analysis  
- Cross-session context retrieval
- Firestore-based state management

Cross-references:
    - ADR-003: Unified Enhanced Architecture Migration
    - ADR-004: Persistent Agent Memory
    - ai/state/: Firestore state management
    - ai/memory/: Intelligent memory system
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
    SemanticSearchMemory = DummyTool
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
    from ai.tools.mcp_client import DiscoverMCPServers, CallMCPTool
except ImportError:
    GenerateReleaseNotes = DummyTool
    GenerateNextSteps = DummyTool
    IntentNormalizer = DummyTool
    DiscoverMCPServers = DummyTool
    CallMCPTool = DummyTool


class Father(Agent):
    """
    DEPRECATED: Enhanced Father agent with intelligent persistent memory.
    
    WARNING: This class is deprecated as part of the unified architecture migration.
    Use ai.agents.Father.Father instead.
    
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
                "You are the Father agent with enhanced memory capabilities:\n"
                "\n"
                "MEMORY STRATEGY:\n"
                "- Use SmartWriteMemory for goals, decisions, and strategic insights\n"
                "- Use PersistentMemorySearch to learn from past experiences\n"
                "- Use CrossSessionAnalytics to understand development patterns\n"
                "- Use GetMemoryByType to review goals, decisions, and progress\n"
                "\n"
                "PLANNING APPROACH:\n"
                "- Always check past similar goals and their outcomes\n"
                "- Learn from previous errors and decisions\n"
                "- Plan concisely (3-5 bullets max) based on learned patterns\n"
                "- Tag memory entries appropriately (goal/decision/progress/error)\n"
                "\n"
                "DELEGATION:\n"
                "- Route to Architect for TDD/ADR gates based on past requirements\n"
                "- Consider past agent performance and specializations\n"
                "- Share relevant context from memory with delegated agents\n"
                "\n"
                "LEARNING:\n"
                "- Reflect on outcomes and store insights for future reference\n"
                "- Identify patterns in successful vs failed approaches\n"
                "- Continuously improve planning based on memory analysis\n"
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


class Developer(Agent):
    """
    DEPRECATED: Enhanced Developer agent with intelligent persistent memory.
    
    WARNING: This class is deprecated as part of the unified architecture migration.
    Use ai.agents.Developer.Developer instead.
    
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
                "You are the Developer agent with enhanced memory capabilities:\n"
                "\n"
                "MEMORY STRATEGY:\n"
                "- Use SmartWriteMemory for implementation solutions and patterns\n"
                "- Use PersistentMemorySearch to find similar past problems\n"
                "- Use GetRelatedMemories to explore connected solutions\n"
                "- Store both successes AND failures for learning\n"
                "\n"
                "IMPLEMENTATION APPROACH:\n"
                "- Follow RED→GREEN→REFACTOR cycle\n"
                "- Search memory for similar implementations before starting\n"
                "- Learn from past refactoring patterns and techniques\n"
                "- Remember what testing approaches work for different scenarios\n"
                "\n"
                "KNOWLEDGE BUILDING:\n"
                "- Store successful code patterns and techniques\n"
                "- Document lessons learned from bugs and fixes\n"
                "- Remember library/framework usage patterns that work\n"
                "- Track which approaches lead to maintainable code\n"
                "\n"
                "QUALITY:\n"
                "- Keep diffs small but leverage past successful patterns\n"
                "- Prefer clarity over cleverness, based on maintenance experiences\n"
                "- Use MCP tools when remembered patterns suggest they help\n"
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


class Architect(Agent):
    """
    DEPRECATED: Enhanced Architect agent with intelligent persistent memory.
    
    WARNING: This class is deprecated as part of the unified architecture migration.
    Use ai.agents.Architect.Architect instead.
    
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
                "You are the Architect agent with enhanced memory capabilities:\n"
                "\n"
                "MEMORY STRATEGY:\n"
                "- Use SmartWriteMemory for architectural decisions and patterns\n"
                "- Use GetMemoryByType to review past decisions and outcomes\n"
                "- Use PersistentMemorySearch to find similar architectural challenges\n"
                "- Store ADR rationales and their long-term outcomes\n"
                "\n"
                "ARCHITECTURE PROTOCOL:\n"
                "1) Check memory for similar past decisions and their outcomes\n"
                "2) Require failing test first (learn from past TDD experiences)\n"
                "3) Require ADR draft/reference (based on past complexity patterns)\n"
                "4) After both exist, allow minimal implementation\n"
                "\n"
                "LEARNING FROM DECISIONS:\n"
                "- Track which architectural patterns succeeded long-term\n"
                "- Remember testing strategies that caught important bugs\n"
                "- Learn from past design mistakes and their corrections\n"
                "- Build patterns of effective ADR structures and content\n"
                "\n"
                "DESIGN WISDOM:\n"
                "- Apply learned patterns while adapting to new contexts\n"
                "- Leverage past successful abstractions and interfaces\n"
                "- Remember which complexity vs simplicity trade-offs worked\n"
                "- Use memory to guide when to be prescriptive vs flexible\n"
            ),
            tools=[
                SmartWriteMemory,
                GetMemoryByType,
                PersistentMemorySearch,
                GetRelatedMemories
            ],
            # Using default temperature=1.0 for OpenAI API compatibility
        )


class QA(Agent):
    """
    DEPRECATED: Enhanced QA agent with intelligent persistent memory.
    
    WARNING: This class is deprecated as part of the unified architecture migration.
    Use ai.agents.QA.QA instead.
    
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
                "You are the QA agent with enhanced memory capabilities:\n"
                "\n"
                "MEMORY STRATEGY:\n"
                "- Use SmartWriteMemory for test patterns, bugs, and quality insights\n"
                "- Use SemanticSearchMemory to find similar testing challenges\n"
                "- Use GetMemoryByType to review past errors and their patterns\n"
                "- Store both test successes and testing gaps for learning\n"
                "\n"
                "TESTING APPROACH:\n"
                "- Search memory for similar components and their testing needs\n"
                "- Learn from past bugs to identify new edge cases\n"
                "- Remember which test patterns actually caught real issues\n"
                "- Use past failure modes to guide current test design\n"
                "\n"
                "QUALITY LEARNING:\n"
                "- Track which edge cases appear repeatedly across projects\n"
                "- Remember integration points that commonly fail\n"
                "- Learn from past regression incidents\n"
                "- Build patterns of effective test organization and structure\n"
                "\n"
                "CONTINUOUS IMPROVEMENT:\n"
                "- Add tests for edge cases based on learned patterns\n"
                "- Verify failure first, then confirm green after fix\n"
                "- Use MCP tools when memory suggests they help testing\n"
                "- Apply lessons from past testing experiences\n"
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


# Convenience function to create all agents (now unified)
def create_enhanced_agents():
    """
    Create all agents with intelligent memory capabilities.
    
    Returns:
        dict: Dictionary mapping agent names to agent instances
        
    Note: This function is deprecated. Use get_agent() or import agents directly.
    All agents now have enhanced memory by default.
    """
    # Use the unified agents from this module
    return {
        'Father': Father(),
        'Architect': Architect(), 
        'Developer': Developer(),
        'QA': QA()
    }


# Convenience function for unified agent creation
def get_agent(name: str):
    """
    Get an agent instance with unified enhanced memory capabilities.
    
    Args:
        name: Agent name ('Father', 'Architect', 'Developer', 'QA')
        
    Returns:
        Agent instance with enhanced memory capabilities
    
    Note: All agents now use enhanced memory by default.
    The 'enhanced' parameter has been removed as part of the unified architecture.
    """
    # Use unified agents from this module
    agent_map = {
        'Father': Father(),
        'Architect': Architect(),
        'Developer': Developer(), 
        'QA': QA()
    }
    return agent_map.get(name)
