"""Dynamic Agent Spawning and Deployment System.

This module implements the intelligent agent spawning system that Father uses
to dynamically create and configure specialized agents based on task analysis.
It supports real-time agent creation, configuration, and deployment.

Cross-references:
    - Father Agent: ai/agents/Father.py for delegation decisions
    - Agent Development: docs/AGENT_DEVELOPMENT.md for agent patterns
    - Deployment Interface: ai/interface/deploy_agents.py for configuration
    - Memory System: ai/memory/README.md for context sharing

Related:
    - ai.agency: Core agency swarm framework
    - ai.tools: Available tools for agent configuration
    - ai.interface.telegram_bot: User interface integration
"""
from __future__ import annotations
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path

from ai.memory.store import get_store
from ai.tools.memory_tools import WriteMemory, ReadMemoryContext
from ai.interface.deploy_agents import AgentDeploymentInterface, AgentConfig, SwarmConfig

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
    """Manages dynamic agent spawning and lifecycle."""
    
    def __init__(self):
        self.deployment_interface = AgentDeploymentInterface()
        self.spawned_agents: Dict[str, SpawnedAgent] = {}
        self.active_spawn_requests: Dict[str, SpawnRequest] = {}
        self.spawn_history: List[Dict[str, Any]] = []
        
    async def process_spawn_request(self, spawn_request: SpawnRequest) -> Dict[str, Any]:
        """Process a spawn request and create the appropriate agents.
        
        Cross-references:
            - Agent Configuration: docs/AGENT_DEVELOPMENT.md#creating-new-agents
            - Memory Integration: ai/memory/README.md#agent-coordination
            - Tool Assignment: docs/TOOLS.md for available capabilities
        """
        logger.info(f"Processing spawn request: {spawn_request.request_id}")
        
        # Store spawn request in memory for context
        WriteMemory(
            content=f"Spawn request: {spawn_request.user_request} - Proposed {len(spawn_request.proposed_agents)} agents",
            tags=["spawn", "request", "father-decision"]
        ).run()
        
        results = {
            "request_id": spawn_request.request_id,
            "spawned_agents": [],
            "deployment_status": "in_progress",
            "errors": []
        }
        
        try:
            # Create agent configurations
            agent_configs = await self._create_agent_configurations(spawn_request)
            
            # Spawn individual agents
            for config in agent_configs:
                try:
                    spawned_agent = await self._spawn_single_agent(config, spawn_request)
                    self.spawned_agents[spawned_agent.agent_id] = spawned_agent
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
                    
            # Create swarm configuration for the spawned agents
            if results["spawned_agents"]:
                swarm_config = await self._create_dynamic_swarm(spawn_request, agent_configs)
                deployment_result = self.deployment_interface.deploy_swarm(
                    swarm_config.name,
                    f"Dynamic spawn for: {spawn_request.user_request}"
                )
                results["swarm_deployed"] = deployment_result
                results["deployment_status"] = "completed"
                
            # Record successful spawn in history
            self.spawn_history.append({
                "request_id": spawn_request.request_id,
                "timestamp": datetime.now(),
                "user_request": spawn_request.user_request,
                "agents_spawned": len(results["spawned_agents"]),
                "success": len(results["errors"]) == 0
            })
            
            # Store completion in memory
            WriteMemory(
                content=f"Spawn completed: {len(results['spawned_agents'])} agents deployed for '{spawn_request.user_request}'",
                tags=["spawn", "completed", "deployment"]
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
    
    def get_spawn_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a spawn request."""
        if request_id not in self.active_spawn_requests:
            return None
            
        spawned_agents_for_request = [
            agent for agent in self.spawned_agents.values()
            if agent.parent_task == request_id
        ]
        
        return {
            "request_id": request_id,
            "status": "active" if spawned_agents_for_request else "completed",
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
    
    def list_active_agents(self) -> List[Dict[str, Any]]:
        """List all currently active spawned agents."""
        return [
            {
                "agent_id": agent.agent_id,
                "type": agent.agent_type,
                "role": agent.role,
                "status": agent.status,
                "spawn_time": agent.spawn_time.isoformat(),
                "parent_task": agent.parent_task
            }
            for agent in self.spawned_agents.values()
            if agent.status in ["spawned", "active", "working"]
        ]
    
    def get_spawn_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent spawn history."""
        return self.spawn_history[-limit:] if self.spawn_history else []


# Global spawner instance
_spawner_instance: Optional[AgentSpawner] = None

def get_agent_spawner() -> AgentSpawner:
    """Get the global agent spawner instance."""
    global _spawner_instance
    if _spawner_instance is None:
        _spawner_instance = AgentSpawner()
    return _spawner_instance
