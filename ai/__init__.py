"""
🤖 Fresh AI Core Package - Autonomous Agent System

This is the core AI package for the Fresh autonomous agent system.
Designed following the lean SpaceX approach - optimized for autonomous agents.

Key Modules:
- agents: Core agent implementations (Mother, Father, Enhanced variants)
- memory: Persistent memory and learning systems  
- cli: Command-line interface for agent operations
- tools: Utility tools for agent tasks
- utils: Helper functions and wrappers
- agency: Agency Swarm integration

Agent Quick Start:
    from ai.agents import MotherAgent
    from ai.memory import IntelligentMemoryStore
    
    # Create agent with memory
    memory = IntelligentMemoryStore()
    agent = MotherAgent(memory_store=memory)
    agent.spawn_workers(tasks)

Integration Points:
- Use ai.memory for persistent learning across sessions
- Import agents from ai.agents for specific capabilities
- Leverage ai.utils for resilient API calls
- Access tools via ai.tools for ADR logging, code analysis

Design Philosophy:
- Lean and efficient - no bloat
- Autonomous-first - agents can navigate without human help
- Continuous learning - every execution improves the system
- Parallel execution - maximize throughput with concurrent agents

Package Structure:
    ai/
    ├── __init__.py          # This file - package initialization
    ├── agents/              # Agent implementations
    │   ├── Mother.py        # Spawns and manages child agents
    │   ├── Father.py        # Strategic planning agent
    │   ├── EnhancedFather.py # Advanced planning with memory
    │   └── enhanced_agents.py # Enhanced agent collection
    ├── memory/              # Memory and learning systems
    │   ├── intelligent_store.py # Smart memory with search
    │   ├── firestore_store.py   # Firebase persistent storage
    │   └── enhanced_father_learning.py # Learning system
    ├── cli/                 # Command-line interface
    │   └── fresh.py         # Main CLI entry point
    ├── tools/               # Agent utility tools
    │   └── adr_logger.py    # Architecture decision records
    └── utils/               # Helper utilities
        └── openai_wrapper.py # Resilient API wrapper

Environment Variables:
- OPENAI_API_KEY: Required for LLM operations
- FIREBASE_*: Optional for persistent memory
- PYTHONPATH: Should include project root

Performance Tips:
- Use parallel orchestrators for independent tasks
- Enable Firebase for cross-session learning
- Monitor costs with budget limits
- Leverage caching in memory stores
"""

# Package metadata
__version__ = "1.0.0"
__author__ = "Fresh AI System"
__description__ = "Autonomous agent system with lean SpaceX approach"

# Make key classes available at package level
__all__ = [
    "agents",
    "memory", 
    "cli",
    "tools",
    "utils",
    "agency",
    "enhanced_agency"
]
