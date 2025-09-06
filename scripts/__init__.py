"""
🚀 Fresh AI Scripts Package - Autonomous Orchestration Hub

This package contains orchestration scripts for autonomous agent execution.
Designed for the lean SpaceX approach - optimized for agents, not humans.

Key Orchestrators:
- enhanced_father_documentation_orchestrator: Strategic planning with learning
- parallel_autonomous_orchestrator: Parallel agent execution framework  
- mother_agent_runner: Spawns and manages child agents
- autonomous_worker: Individual worker agent implementation

Agent Hook Points:
1. Import orchestrators directly:
   from scripts.enhanced_father_documentation_orchestrator import main
   
2. Run parallel tasks:
   from scripts.parallel_autonomous_orchestrator import ParallelAutonomousOrchestrator
   orchestrator = ParallelAutonomousOrchestrator(max_workers=20)
   
3. Spawn autonomous workers:
   from scripts.autonomous_worker import AutonomousWorker
   worker = AutonomousWorker(task_config)

Environment Requirements:
- OPENAI_API_KEY: Required for LLM agent operations
- PYTHONPATH: Should include project root
- Python 3.12+: Required for async operations

Performance Optimization Tips:
- Use parallel orchestrator for independent tasks
- Leverage Enhanced Father for strategic planning
- Store outcomes for continuous learning
- Monitor costs with budget limits

Integration Points:
- ai.memory: For persistent learning
- ai.agents: Core agent implementations
- ai.utils: Utility functions and wrappers
"""

# Version and metadata for autonomous agents
__version__ = "1.0.0"
__author__ = "Fresh AI System"
__description__ = "Autonomous orchestration scripts for lean agent execution"

# Export key orchestrator classes for easy import
__all__ = [
    "ParallelAutonomousOrchestrator",
    "AutonomousWorker",
    "EnhancedFatherOrchestrator",
    "MotherAgentRunner"
]

# Agent-friendly constants
DEFAULT_MAX_WORKERS = 20
DEFAULT_BUDGET_LIMIT = 2.0
DEFAULT_TIMEOUT = 300  # 5 minutes
DEFAULT_RETRY_COUNT = 3

# Orchestrator status codes for agents
STATUS_SUCCESS = "success"
STATUS_FAILED = "failed"
STATUS_TIMEOUT = "timeout"
STATUS_BUDGET_EXCEEDED = "budget_exceeded"
