"""
Enhanced Architect Agent with Intelligent Memory Capabilities

Extends the base Architect with advanced memory tools for better context awareness
and decision tracking. Uses semantic search to find related ADRs and decisions.
"""
from agency_swarm import Agent
from ai.tools.memory_tools import WriteMemory, ReadMemoryContext
from ai.tools.enhanced_memory_tools import (
    SmartWriteMemory, 
    SemanticSearchMemory, 
    GetMemoryByType,
    GetRelatedMemories
)

EnhancedArchitect = Agent(
    name="Enhanced_Architect",
    description=(
        "Enforces TDD-first and ADR discipline with intelligent memory assistance. "
        "Uses semantic search to find related architectural decisions and patterns."
    ),
    instructions=(
        "Protocol: 1) Search existing ADRs/decisions before creating new ones. "
        "2) Require failing test first. 3) Create/reference ADR with smart categorization. "
        "4) After both exist, allow minimal implementation. Use semantic search to find "
        "related architectural patterns and avoid duplicate decisions."
    ),
    tools=[
        # Enhanced memory tools with intelligence
        SmartWriteMemory, 
        SemanticSearchMemory,
        GetMemoryByType,
        GetRelatedMemories,
        # Keep backward compatibility
        WriteMemory, 
        ReadMemoryContext
    ],
    # Using default temperature=1.0 for OpenAI API compatibility
)
