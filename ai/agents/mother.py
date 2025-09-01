"""Mother Agent that spawns and manages child agents.

The Mother Agent is responsible for creating and managing child agents
based on task requirements. It implements the core spawning interface
expected by the mission: run(name, instructions, model, output_type).

Cross-references:
    - ADR-008: Autonomous Development Loop Architecture
    - Father Agent: ai/agents/father.py for strategic planning
    - Memory Store: ai/memory/store.py for persistent context
"""
from __future__ import annotations
import time
import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import defaultdict

from ai.memory.store import get_store, InMemoryMemoryStore
from ai.tools.memory_tools import WriteMemory


@dataclass
class SpawnRequest:
    """Request to spawn a new agent."""
    name: str
    instructions: str
    model: str = "gpt-4"
    output_type: str = "code"
    timestamp: datetime = field(default_factory=datetime.now)
    
    def is_valid(self) -> bool:
        """Validate the spawn request."""
        return bool(self.name and self.instructions)


@dataclass
class AgentResult:
    """Result from an agent execution."""
    agent_name: str
    agent_type: str
    instructions: str
    model: str
    output_type: str
    success: bool
    output: Optional[str] = None
    artifacts: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "agent_name": self.agent_name,
            "agent_type": self.agent_type,
            "instructions": self.instructions,
            "model": self.model,
            "output_type": self.output_type,
            "success": self.success,
            "output": self.output,
            "artifacts": self.artifacts or {},
            "error": self.error,
            "duration": self.duration,
            "timestamp": self.timestamp.isoformat()
        }


class MotherAgent:
    """Mother Agent that spawns and manages child agents.
    
    This agent implements the core spawning interface for creating
    specialized agents based on task requirements. It maintains
    history of spawned agents and persists context to memory.
    """
    
    def __init__(self, memory_store=None, max_history: int = 100):
        """Initialize Mother Agent.
        
        Args:
            memory_store: Memory store for persistence (uses global if None)
            max_history: Maximum number of spawn requests to keep in history
        """
        self.memory_store = memory_store or get_store() or InMemoryMemoryStore()
        self.spawn_history: List[SpawnRequest] = []
        self.max_history = max_history
        self._lock = threading.Lock()
        self._agent_registry = self._initialize_agent_registry()
    
    def _initialize_agent_registry(self) -> Dict[str, str]:
        """Initialize mapping of task types to agent types."""
        return {
            "fix": "Developer",
            "bug": "Developer",
            "implement": "Developer",
            "code": "Developer",
            "test": "QA",
            "tests": "QA",
            "quality": "QA",
            "design": "Architect",
            "architecture": "Architect",
            "api": "Architect",
            "review": "Reviewer",
            "validate": "Reviewer",
            "plan": "Father",
            "strategy": "Father",
            "coordinate": "Father"
        }
    
    def run(self, name: str, instructions: str, 
            model: str = "gpt-4", output_type: str = "code") -> AgentResult:
        """Spawn and run a child agent for the given task.
        
        This is the core interface method that implements the mission requirement:
        spawning agents with name, instructions, model, and output_type.
        
        Args:
            name: Name/identifier for the agent
            instructions: Task instructions for the agent
            model: AI model to use (default: gpt-4)
            output_type: Expected output type (code/tests/docs/design/review)
            
        Returns:
            AgentResult with execution details and output
        """
        start_time = time.time()
        
        # Create and validate spawn request
        request = SpawnRequest(name, instructions, model, output_type)
        if not request.is_valid():
            return AgentResult(
                agent_name=name,
                agent_type="None",
                instructions=instructions,
                model=model,
                output_type=output_type,
                success=False,
                error="Invalid agent name or instructions"
            )
        
        # Track spawn request
        self._track_spawn(request)
        
        # Determine appropriate agent type
        agent_type = self._determine_agent_type(instructions, output_type)
        
        # Persist to memory
        self._persist_spawn_to_memory(request, agent_type)
        
        # Execute agent (simplified for now - will integrate with actual agents later)
        try:
            result = self._execute_agent(
                agent_type=agent_type,
                request=request
            )
            
            duration = time.time() - start_time
            
            return AgentResult(
                agent_name=name,
                agent_type=agent_type,
                instructions=instructions,
                model=model,
                output_type=output_type,
                success=True,
                output=result.get("output", "Agent execution completed"),
                artifacts=result.get("artifacts", {}),
                duration=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return AgentResult(
                agent_name=name,
                agent_type=agent_type,
                instructions=instructions,
                model=model,
                output_type=output_type,
                success=False,
                error=str(e),
                duration=duration
            )
    
    def _track_spawn(self, request: SpawnRequest) -> None:
        """Track spawn request in history."""
        with self._lock:
            self.spawn_history.append(request)
            
            # Maintain history limit
            if len(self.spawn_history) > self.max_history:
                self.spawn_history = self.spawn_history[-self.max_history:]
    
    def _determine_agent_type(self, instructions: str, output_type: str) -> str:
        """Determine which agent type to spawn based on instructions."""
        instructions_lower = instructions.lower()
        
        # Check output type first
        if output_type == "tests":
            return "QA"
        elif output_type == "design":
            return "Architect"
        elif output_type == "review":
            return "Reviewer"
        elif output_type == "plan":
            return "Father"
        
        # Check instructions for keywords
        for keyword, agent_type in self._agent_registry.items():
            if keyword in instructions_lower:
                return agent_type
        
        # Default to Father for general coordination
        return "Father"
    
    def _persist_spawn_to_memory(self, request: SpawnRequest, agent_type: str) -> None:
        """Persist spawn request to memory store."""
        memory_content = (
            f"Mother Agent spawned {agent_type} agent '{request.name}' "
            f"with instructions: {request.instructions} "
            f"[model: {request.model}, output: {request.output_type}]"
        )
        
        # Use the instance's memory store directly
        self.memory_store.write(
            content=memory_content,
            tags=["mother", "spawn", agent_type.lower(), request.output_type]
        )
    
    def _execute_agent(self, agent_type: str, request: SpawnRequest) -> Dict[str, Any]:
        """Execute the appropriate agent (placeholder for now).
        
        This will be integrated with the actual agency agents later.
        For now, returns simulated results for testing.
        """
        # Simulate agent execution
        if agent_type == "Developer":
            return {
                "output": f"Code implementation for: {request.instructions}",
                "artifacts": {"files": ["implementation.py"]}
            }
        elif agent_type == "QA":
            return {
                "output": f"Tests written for: {request.instructions}",
                "artifacts": {"test_files": ["test_module.py"]}
            }
        elif agent_type == "Architect":
            return {
                "output": f"Design document for: {request.instructions}",
                "artifacts": {"design_docs": ["architecture.md"]}
            }
        elif agent_type == "Reviewer":
            return {
                "output": f"Review completed for: {request.instructions}",
                "artifacts": {"review_notes": ["review.md"]}
            }
        else:  # Father
            return {
                "output": f"Strategic plan created for: {request.instructions}",
                "artifacts": {"plan": ["strategy.md"]}
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about spawned agents."""
        with self._lock:
            if not self.spawn_history:
                return {
                    "total_spawned": 0,
                    "by_type": {},
                    "by_model": {},
                    "success_rate": 0.0
                }
            
            # Count by output type
            by_type = defaultdict(int)
            by_model = defaultdict(int)
            
            for spawn in self.spawn_history:
                by_type[spawn.output_type] += 1
                by_model[spawn.model] += 1
            
            return {
                "total_spawned": len(self.spawn_history),
                "by_type": dict(by_type),
                "by_model": dict(by_model),
                "success_rate": 1.0  # Placeholder - will track actual success later
            }
