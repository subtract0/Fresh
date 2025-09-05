"""
@file Father.py
@description Legacy Father agent - strategic planner and task delegator with basic memory tools.

@connections
- imports: agency_swarm.Agent for base agent functionality, ai.tools.* for memory and workflow tools
- exports: Father agent instance configured for strategic planning and delegation
- implements: Strategic planning agent with basic memory capabilities

@usage
# Use the Father agent for planning and delegation
from ai.agents.Father import Father
result = Father.run("Plan and implement user authentication system")

@notes
- Legacy agent with basic memory tools (WriteMemory, ReadMemoryContext)
- Consider using EnhancedFather from enhanced_agents.py for intelligent memory features
- Temperature=0.2 for consistent, focused planning behavior
- Configured for concise planning (3-5 bullets max) and appropriate delegation

@see
- enhanced_agents.py - Enhanced version with intelligent memory and learning
- docs/ENHANCED_AGENTS.md#enhanced-father - Enhanced agent capabilities
- ai.tools.memory_tools - Basic memory operations

@since v0.1.0
"""
from agency_swarm import Agent
from ai.tools.memory_tools import WriteMemory, ReadMemoryContext
from ai.tools.release_notes import GenerateReleaseNotes
from ai.tools.next_steps import GenerateNextSteps
from ai.tools.intent import IntentNormalizer

Father = Agent(
    name="Father",
    description=(
        "Strategic planner and delegator for the codebase; turns goals into minimal "
        "viable plans, tags memory, and routes work to the right agent."
    ),
    instructions=(
        "Plan concisely (3-5 bullets max), tag memory entries (feature/bug/adr), "
        "delegate to Architect for TDD/ADR gate, then to Developer/QA/Reviewer. "
        "Ask one crisp question only if essential; otherwise proceed with best practices."
    ),
    tools=[WriteMemory, ReadMemoryContext, GenerateReleaseNotes, GenerateNextSteps, IntentNormalizer],
    temperature=0.2,
)
