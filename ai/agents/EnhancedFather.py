"""
Enhanced Father Agent with Intelligent Memory and Analytics

Strategic planner and delegator with advanced memory intelligence for better
decision-making and context awareness. Includes memory analytics for optimization.
"""
from agency_swarm import Agent
from ai.tools.memory_tools import WriteMemory, ReadMemoryContext
from ai.tools.enhanced_memory_tools import (
    SmartWriteMemory, 
    SemanticSearchMemory, 
    GetMemoryByType,
    GetRelatedMemories,
    AnalyzeMemoryUsage,
    OptimizeMemoryStore
)
from ai.tools.release_notes import GenerateReleaseNotes
from ai.tools.next_steps import GenerateNextSteps
from ai.tools.intent import IntentNormalizer

EnhancedFather = Agent(
    name="Enhanced_Father",
    description=(
        "Strategic planner and delegator with intelligent memory capabilities. "
        "Uses semantic search for context-aware planning and memory analytics for optimization."
    ),
    instructions=(
        "Strategic planning with memory intelligence: 1) Analyze existing goals and progress "
        "before creating new plans. 2) Search for related goals and patterns. 3) Plan concisely "
        "(3-5 bullets max) with smart memory tagging. 4) Use memory analytics to optimize "
        "team performance. 5) Delegate to appropriate agents based on historical patterns. "
        "Ask one crisp question only if essential; otherwise proceed with best practices."
    ),
    tools=[
        # Enhanced memory tools with intelligence and analytics
        SmartWriteMemory, 
        SemanticSearchMemory,
        GetMemoryByType,
        GetRelatedMemories,
        AnalyzeMemoryUsage,
        OptimizeMemoryStore,
        # Keep existing functionality  
        WriteMemory, 
        ReadMemoryContext, 
        GenerateReleaseNotes, 
        GenerateNextSteps, 
        IntentNormalizer
    ],
    temperature=0.2,
)
