"""Dynamic Agent Spawning and Execution System.

This module implements the intelligent agent spawning system that Father uses
to dynamically create, configure, and execute specialized agents based on task analysis.
It supports real-time agent creation, execution monitoring, and coordination.

Cross-references:
    - Father Agent: ai/agents/Father.py for delegation decisions
    - Execution Monitor: ai/execution/monitor.py for real-time execution
    - Status Coordinator: ai/coordination/status.py for real-time updates
    - GitHub Integration: ai/integration/github.py for PR creation
    - Memory System: ai/memory/README.md for context sharing

Related:
    - ai.agency: Core agency swarm framework integration
    - ai.tools: Available tools for agent configuration
    - ai.interface.telegram_bot: User interface and notifications
"""
from __future__ import annotations
import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Union, Set
from dataclasses import dataclass, field
from pathlib import Path

from ai.memory.store import get_store
from ai.tools.memory_tools import WriteMemory, ReadMemoryContext
from ai.interface.deploy_agents import AgentDeploymentInterface, AgentConfig, SwarmConfig

# Import execution and coordination systems
try:
    from ai.execution.monitor import get_execution_monitor, ExecutionStatus
    from ai.coordination.status import get_status_coordinator, UpdateType, StatusLevel
    from ai.integration.github import get_github_integration
    HAS_EXECUTION_SYSTEM = True
except ImportError:
    HAS_EXECUTION_SYSTEM = False
    logger = logging.getLogger(__name__)
    logger.warning("Execution system modules not available, running in compatibility mode")

logger = logging.getLogger(__name__)


@dataclass
class SpawnedAgent:
    """Represents a dynamically spawned agent with its configuration and state."""
    agent_id: str
    agent_type: str
    role: str
    instructions: str
    tools: List[str]
    status: str = "created"
    spawn_time: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    parent_task: Optional[str] = None


@dataclass  
class SpawnRequest:
    """Request for spawning new agents based on task analysis."""
    request_id: str
    user_request: str
    task_analysis: Dict[str, Any]
    proposed_agents: List[Dict[str, Any]]
    context: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1
    estimated_time: str = "unknown"


class AgentSpawner:
    """Manages dynamic agent spawning, execution, and lifecycle."""
    
    def __init__(self):
        self.deployment_interface = AgentDeploymentInterface()
        self.spawned_agents: Dict[str, SpawnedAgent] = {}
        self.active_spawn_requests: Dict[str, SpawnRequest] = {}
        self.spawn_history: List[Dict[str, Any]] = []
        self.execution_history: Dict[str, Dict[str, Any]] = {}
        
        # Initialize execution and coordination systems if available
        self.execution_monitor = None
        self.status_coordinator = None
        
        if HAS_EXECUTION_SYSTEM:
            self.execution_monitor = get_execution_monitor()
            self.status_coordinator = get_status_coordinator()
            
            # Start execution monitoring in a background task
            asyncio.create_task(self._start_execution_systems())
    
    async def _start_execution_systems(self):
        """Start the execution and coordination systems."""
        if self.execution_monitor:
            await self.execution_monitor.start_monitoring()
        if self.status_coordinator:
            await self.status_coordinator.start_coordination()
        
    async def process_spawn_request(self, spawn_request: SpawnRequest, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a spawn request and create the appropriate agents.
        
        Cross-references:
            - Agent Configuration: docs/AGENT_DEVELOPMENT.md#creating-new-agents
            - Memory Integration: ai/memory/README.md#agent-coordination
            - Tool Assignment: docs/TOOLS.md for available capabilities
            - Execution Monitor: ai/execution/monitor.py for real-time execution
        """
        logger.info(f"Processing spawn request: {spawn_request.request_id}")
        
        # Store spawn request in memory for context
        WriteMemory(
            content=f"Spawn request: {spawn_request.user_request} - Proposed {len(spawn_request.proposed_agents)} agents",
            tags=["spawn", "request", spawn_request.request_id, "father-decision"]
        ).run()
        
        results = {
            "request_id": spawn_request.request_id,
            "spawned_agents": [],
            "deployment_status": "in_progress",
            "errors": [],
            "execution_id": None
        }
        
        try:
            # Create agent configurations
            agent_configs = await self._create_agent_configurations(spawn_request)
            
            # Spawn individual agents
            spawned_agents = []
            for config in agent_configs:
                try:
                    spawned_agent = await self._spawn_single_agent(config, spawn_request)
                    self.spawned_agents[spawned_agent.agent_id] = spawned_agent
                    spawned_agents.append(spawned_agent)
                    results["spawned_agents"].append({
                        "agent_id": spawned_agent.agent_id,
                        "type": spawned_agent.agent_type,
                        "role": spawned_agent.role,
                        "status": spawned_agent.status
                    })
                    
                except Exception as e:
                    error_msg = f"Failed to spawn {config.name}: {str(e)}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)
            
            # Record successful spawn in history
            spawn_record = {
                "request_id": spawn_request.request_id,
                "timestamp": datetime.now(),
                "user_request": spawn_request.user_request,
                "agents_spawned": len(results["spawned_agents"]),
                "success": len(results["errors"]) == 0
            }
            self.spawn_history.append(spawn_record)
            
            # If execution system is available, execute agents in real-time
            if HAS_EXECUTION_SYSTEM and self.execution_monitor and spawned_agents:
                # Execute agents with real-time monitoring
                results["execution_status"] = "starting"
                
                # Start agent execution batch
                batch_id = await self.execution_monitor.execute_agent_batch(
                    spawn_request_id=spawn_request.request_id,
                    user_request=spawn_request.user_request,
                    agents=spawned_agents,
                    user_id=user_id,
                    auto_create_pr=spawn_request.task_analysis.get("task_type") == "development"
                )
                
                results["execution_id"] = batch_id
                results["execution_status"] = "started"
                
                # Register coordination context
                if self.status_coordinator:
                    context_id = f"ctx_{spawn_request.request_id}"
                    agent_ids = [agent.agent_id for agent in spawned_agents]
                    
                    # Create dependency graph based on agent types
                    dependency_graph = await self._create_dependency_graph(spawned_agents)
                    
                    # Register coordination context
                    self.status_coordinator.register_context(
                        context_id=context_id,
                        spawn_request_id=spawn_request.request_id,
                        agent_ids=agent_ids,
                        user_id=user_id,
                        dependency_graph=dependency_graph
                    )
                    
                    # Add initial status update
                    await self.status_coordinator.update_status(
                        context_id=context_id,
                        source_id="spawner",
                        update_type=UpdateType.MILESTONE,
                        message=f"Started execution of {len(spawned_agents)} agents for: {spawn_request.user_request[:100]}",
                        user_visible=True
                    )
                    
                    results["coordination_id"] = context_id
            else:
                # Legacy mode: Create swarm configuration for the spawned agents
                if results["spawned_agents"]:
                    swarm_config = await self._create_dynamic_swarm(spawn_request, agent_configs)
                    deployment_result = self.deployment_interface.deploy_swarm(
                        swarm_config.name,
                        f"Dynamic spawn for: {spawn_request.user_request}"
                    )
                    results["swarm_deployed"] = deployment_result
            
            results["deployment_status"] = "completed"
            
            # Store completion in memory
            WriteMemory(
                content=f"Spawn completed: {len(results['spawned_agents'])} agents ready for '{spawn_request.user_request}'",
                tags=["spawn", "completed", spawn_request.request_id, "deployment"]
            ).run()
            
        except Exception as e:
            results["deployment_status"] = "failed"
            results["errors"].append(f"Spawn process failed: {str(e)}")
            logger.error(f"Spawn request failed: {e}")
            
        return results
    
    async def _create_agent_configurations(self, spawn_request: SpawnRequest) -> List[AgentConfig]:
        """Create agent configurations from spawn request."""
        agent_configs = []
        
        for i, agent_spec in enumerate(spawn_request.proposed_agents):
            agent_id = f"{spawn_request.request_id}_agent_{i+1}"
            
            # Map tools from names to actual tool classes
            tools = await self._resolve_agent_tools(agent_spec.get("tools", []))
            
            # Create enhanced instructions with context
            instructions = await self._enhance_agent_instructions(
                agent_spec.get("instructions", ""),
                spawn_request,
                agent_spec
            )
            
            config = AgentConfig(
                name=f"{agent_spec['type']}_{agent_id}",
                role=agent_spec.get("role", agent_spec["type"]),
                instructions=instructions,
                tools=tools,
                model="claude-3-5-sonnet-20241022",
                active=True
            )
            
            agent_configs.append(config)
            
        return agent_configs
    
    async def _spawn_single_agent(self, config: AgentConfig, spawn_request: SpawnRequest) -> SpawnedAgent:
        """Spawn a single agent with the given configuration."""
        agent_id = f"spawn_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{config.name.lower()}"
        
        # Create spawned agent instance
        spawned_agent = SpawnedAgent(
            agent_id=agent_id,
            agent_type=config.name,
            role=config.role,
            instructions=config.instructions,
            tools=config.tools,
            status="spawned",
            parent_task=spawn_request.request_id,
            context={
                "user_request": spawn_request.user_request,
                "spawn_time": datetime.now().isoformat(),
                "task_analysis": spawn_request.task_analysis
            }
        )
        
        # Store agent context in memory
        WriteMemory(
            content=f"Agent spawned: {agent_id} ({spawned_agent.agent_type}) for task: {spawn_request.user_request}",
            tags=["agent", "spawned", spawned_agent.agent_type.lower()]
        ).run()
        
        logger.info(f"Spawned agent: {agent_id} ({spawned_agent.agent_type})")
        return spawned_agent
    
    async def _resolve_agent_tools(self, tool_names: List[str]) -> List[str]:
        """Resolve tool names to available tool classes."""
        # Available tools mapping
        available_tools = {
            "WriteMemory": "WriteMemory",
            "ReadMemoryContext": "ReadMemoryContext", 
            "GenerateNextSteps": "GenerateNextSteps",
            "GenerateReleaseNotes": "GenerateReleaseNotes",
            "CreateADR": "CreateADR",
            "DoDCheck": "DoDCheck",
            "DiscoverMCPServers": "DiscoverMCPServers",
            "CallMCPTool": "CallMCPTool",
            "IntentNormalizer": "IntentNormalizer"
        }
        
        resolved_tools = []
        for tool_name in tool_names:
            if tool_name in available_tools:
                resolved_tools.append(available_tools[tool_name])
            else:
                logger.warning(f"Unknown tool: {tool_name}, skipping")
                
        # Ensure all agents have basic memory tools
        if "WriteMemory" not in resolved_tools:
            resolved_tools.append("WriteMemory")
        if "ReadMemoryContext" not in resolved_tools:
            resolved_tools.append("ReadMemoryContext")
            
        return resolved_tools
    
    async def _enhance_agent_instructions(
        self, 
        base_instructions: str, 
        spawn_request: SpawnRequest,
        agent_spec: Dict[str, Any]
    ) -> str:
        """Enhance agent instructions with context and cross-references."""
        
        # Get relevant context from memory and documentation
        context = ReadMemoryContext(limit=10, tags=["spawn", "context"]).run()
        
        enhanced_instructions = f"""
# Agent Instructions: {agent_spec.get('type', 'Agent')}

## Primary Task
{base_instructions}

## Context
**User Request:** {spawn_request.user_request}
**Task Type:** {spawn_request.task_analysis.get('task_type', 'general')}
**Request ID:** {spawn_request.request_id}

## Available Tools
{', '.join(agent_spec.get('tools', []))}

## Collaboration Guidelines
- Use WriteMemory to share progress and findings with other agents
- Use ReadMemoryContext to understand previous work and decisions
- Follow Fresh documentation standards and cross-reference related docs
- Reference ADRs when making architectural decisions

## Documentation References
- Agent Development Guide: docs/AGENT_DEVELOPMENT.md
- Tool Reference: docs/TOOLS.md
- Memory System: ai/memory/README.md
- Architecture Decisions: .cursor/rules/ADR-*.md

## Quality Standards
- Follow TDD principles where applicable
- Create clear, actionable deliverables
- Document decisions and reasoning
- Coordinate with other agents through memory system

## Recent Context
{context[:200] if context else 'No recent context available'}

Remember: You are part of a dynamically spawned team working on: {spawn_request.user_request}
        """
        
        return enhanced_instructions.strip()
    
    async def _create_dynamic_swarm(
        self, 
        spawn_request: SpawnRequest, 
        agent_configs: List[AgentConfig]
    ) -> SwarmConfig:
        """Create a dynamic swarm configuration for spawned agents."""
        
        # Create flows based on agent types and task analysis
        flows = await self._determine_agent_flows(spawn_request, agent_configs)
        
        swarm_name = f"dynamic_{spawn_request.request_id}_{datetime.now().strftime('%H%M%S')}"
        
        swarm_config = SwarmConfig(
            name=swarm_name,
            description=f"Dynamically spawned swarm for: {spawn_request.user_request}",
            agents=agent_configs,
            flows=flows,
            shared_instructions=f"Collaborative work on: {spawn_request.user_request}. Use memory system for coordination."
        )
        
        # Save the dynamic configuration
        config_path = self.deployment_interface.save_config(swarm_config, f"{swarm_name}.yaml")
        logger.info(f"Created dynamic swarm config: {config_path}")
        
        return swarm_config
    
    async def _determine_agent_flows(
        self, 
        spawn_request: SpawnRequest, 
        agent_configs: List[AgentConfig]
    ) -> List[List[str]]:
        """Determine optimal flows between spawned agents."""
        
        if len(agent_configs) <= 1:
            return []
            
        flows = []
        task_type = spawn_request.task_analysis.get("task_type", "general")
        
        # Create flows based on task type and agent roles
        if task_type == "development":
            # Typical development flow: Architect -> Developer -> QA
            architect_agents = [a for a in agent_configs if "architect" in a.name.lower()]
            developer_agents = [a for a in agent_configs if "developer" in a.name.lower()]
            qa_agents = [a for a in agent_configs if "qa" in a.name.lower()]
            
            # Connect architect to developer
            for arch in architect_agents:
                for dev in developer_agents:
                    flows.append([arch.name, dev.name])
                    
            # Connect developer to QA
            for dev in developer_agents:
                for qa in qa_agents:
                    flows.append([dev.name, qa.name])
                    
        elif task_type == "documentation":
            # Documentation flow: Researcher -> Documenter
            researcher_agents = [a for a in agent_configs if "researcher" in a.name.lower()]
            documenter_agents = [a for a in agent_configs if "documenter" in a.name.lower()]
            
            for researcher in researcher_agents:
                for documenter in documenter_agents:
                    flows.append([researcher.name, documenter.name])
                    
        else:
            # Default: sequential flow
            for i in range(len(agent_configs) - 1):
                flows.append([agent_configs[i].name, agent_configs[i + 1].name])
                
        return flows
    
    async def _create_dependency_graph(self, agents: List[SpawnedAgent]) -> Dict[str, List[str]]:
        """Create a dependency graph based on agent types and execution order."""
        dependency_graph = {}
        
        # Extract agent types
        architect_agents = [a for a in agents if "architect" in a.agent_type.lower()]
        developer_agents = [a for a in agents if "developer" in a.agent_type.lower()]
        qa_agents = [a for a in agents if "qa" in a.agent_type.lower() or "test" in a.agent_type.lower()]
        doc_agents = [a for a in agents if "doc" in a.agent_type.lower()]
        
        # Set up dependencies
        for agent in agents:
            dependencies = []
            
            # Developers depend on architects
            if "developer" in agent.agent_type.lower() and architect_agents:
                dependencies.extend([a.agent_id for a in architect_agents])
                
            # QA depends on developers
            if ("qa" in agent.agent_type.lower() or "test" in agent.agent_type.lower()) and developer_agents:
                dependencies.extend([a.agent_id for a in developer_agents])
                
            # Documentation depends on developers and QA
            if "doc" in agent.agent_type.lower():
                if developer_agents:
                    dependencies.extend([a.agent_id for a in developer_agents])
                if qa_agents:
                    dependencies.extend([a.agent_id for a in qa_agents])
                    
            if dependencies:
                dependency_graph[agent.agent_id] = dependencies
                
        return dependency_graph
    
    def get_spawn_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a spawn request.

        Synchronous and side-effect free for ease of use in simple integrations/tests.
        Returns None if there are no spawned agents for the given request yet.
        """
        # Get spawned agents for this request
        spawned_agents_for_request = [
            agent for agent in self.spawned_agents.values()
            if agent.parent_task == request_id
        ]
        if not spawned_agents_for_request:
            return None
        
        status: Dict[str, Any] = {
            "request_id": request_id,
            "spawned_agents": len(spawned_agents_for_request),
            "agents": [
                {
                    "agent_id": agent.agent_id,
                    "type": agent.agent_type,
                    "role": agent.role,
                    "status": agent.status
                }
                for agent in spawned_agents_for_request
            ]
        }
        
        # Legacy/simple status field
        status["status"] = "active"
        return status
    
    def list_active_agents(self) -> List[Dict[str, Any]]:
        """List all currently active spawned agents (synchronous)."""
        result = [
            {
                "agent_id": agent.agent_id,
                "type": agent.agent_type,
                "role": agent.role,
                "status": agent.status,
                "spawn_time": agent.spawn_time.isoformat(),
                "parent_task": agent.parent_task,
            }
            for agent in self.spawned_agents.values()
            if agent.status in ["spawned", "active", "working"]
        ]
        return result
    
    def get_spawn_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent spawn history."""
        return self.spawn_history[-limit:] if self.spawn_history else []
        
    async def execute_spawned_agents(self, request_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute previously spawned agents with real-time monitoring."""
        if not HAS_EXECUTION_SYSTEM or not self.execution_monitor:
            return {"error": "Execution system not available"}
            
        # Get spawned agents for this request
        spawned_agents = [
            agent for agent in self.spawned_agents.values()
            if agent.parent_task == request_id
        ]
        
        if not spawned_agents:
            return {"error": f"No spawned agents found for request {request_id}"}
            
        # Get the original request details
        user_request = "Unknown request"
        task_type = "general"
        
        if request_id in self.active_spawn_requests:
            spawn_request = self.active_spawn_requests[request_id]
            user_request = spawn_request.user_request
            task_type = spawn_request.task_analysis.get("task_type", "general")
        else:
            # Try to reconstruct from spawn history
            for record in self.spawn_history:
                if record["request_id"] == request_id:
                    user_request = record["user_request"]
                    break
        
        # Execute the spawned agents
        batch_id = await self.execution_monitor.execute_agent_batch(
            spawn_request_id=request_id,
            user_request=user_request,
            agents=spawned_agents,
            user_id=user_id,
            auto_create_pr=task_type == "development"
        )
        
        # Register coordination context if not already registered
        if self.status_coordinator:
            context_id = f"ctx_{request_id}"
            agent_ids = [agent.agent_id for agent in spawned_agents]
            
            # Check if context already exists
            if context_id not in self.status_coordinator.contexts:
                # Create dependency graph
                dependency_graph = await self._create_dependency_graph(spawned_agents)
                
                # Register new coordination context
                self.status_coordinator.register_context(
                    context_id=context_id,
                    spawn_request_id=request_id,
                    agent_ids=agent_ids,
                    user_id=user_id,
                    dependency_graph=dependency_graph
                )
                
            # Add execution start status update
            await self.status_coordinator.update_status(
                context_id=context_id,
                source_id="spawner",
                update_type=UpdateType.MILESTONE,
                message=f"Started execution of {len(spawned_agents)} agents for: {user_request[:100]}",
                user_visible=True
            )
        
        return {
            "execution_id": batch_id,
            "request_id": request_id,
            "agents": len(spawned_agents),
            "status": "started"
        }
        
    async def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Get detailed status of an execution batch."""
        if not HAS_EXECUTION_SYSTEM or not self.execution_monitor:
            return {"error": "Execution system not available"}
            
        # Get the batch status
        batch = self.execution_monitor.get_batch_status(execution_id)
        if not batch:
            return {"error": f"Execution batch {execution_id} not found"}
            
        # Format results
        status = {
            "execution_id": batch.batch_id,
            "request_id": batch.spawn_request_id,
            "status": batch.status.value,
            "start_time": batch.start_time.isoformat(),
            "end_time": batch.end_time.isoformat() if batch.end_time else None,
            "agents": len(batch.agent_executions),
            "coordination_log": batch.coordination_log[-10:],  # Last 10 entries
            "agent_executions": []
        }
        
        # Add detailed agent execution information
        for execution in batch.agent_executions:
            agent_info = {
                "agent_id": execution.agent.agent_id,
                "type": execution.agent.agent_type,
                "status": execution.status.value,
                "progress": execution.progress_percentage,
                "current_step": execution.current_step,
                "steps": len(execution.steps),
                "completed_steps": len([s for s in execution.steps if s.status.value == "completed"]),
                "result": execution.result[:100] + "..." if execution.result and len(execution.result) > 100 else execution.result
            }
            status["agent_executions"].append(agent_info)
            
        # Get coordination status if available
        if self.status_coordinator:
            context_id = f"ctx_{batch.spawn_request_id}"
            summary = await self.status_coordinator.get_status_summary(context_id)
            
            if summary:
                status["coordination"] = {
                    "overall_progress": summary.overall_progress,
                    "phase_status": summary.phase_status,
                    "active_agents": summary.active_agents,
                    "completed_agents": summary.completed_agents,
                    "failed_agents": summary.failed_agents,
                    "next_milestones": summary.next_milestones,
                    "estimated_completion": summary.estimated_completion.isoformat() if summary.estimated_completion else None,
                    "blocking_dependencies": summary.blocking_dependencies
                }
                
                # Add recent updates
                status["recent_updates"] = [
                    {
                        "message": update.message,
                        "timestamp": update.timestamp.isoformat(),
                        "source": update.source_id,
                        "type": update.update_type.value,
                        "level": update.level.value
                    }
                    for update in summary.recent_updates[-5:]  # Last 5 updates
                ]
                
        return status


# Global spawner instance
_spawner_instance: Optional[AgentSpawner] = None

def get_agent_spawner() -> AgentSpawner:
    """Get the global agent spawner instance."""
    global _spawner_instance
    if _spawner_instance is None:
        _spawner_instance = AgentSpawner()
    return _spawner_instance
