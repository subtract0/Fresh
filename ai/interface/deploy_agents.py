"""Agent deployment configuration interface with YAML-based management.

This module provides a comprehensive interface for configuring and deploying
agent swarms. It supports YAML-based configuration files that define agent
roles, tools, flows, and deployment context.

Cross-references:
    - Deployment Guide: docs/DEPLOYMENT.md for usage patterns and examples
    - Agent Development: docs/AGENT_DEVELOPMENT.md#creating-new-agents
    - CLI Interface: scripts/deploy.sh for command-line usage
    - Tool Reference: docs/TOOLS.md#interface-tools
    
Related:
    - ai.agency: Core agency swarm implementation
    - ai.agents: Individual agent implementations
    - ai.memory: Memory system integration for deployment context
"""
from __future__ import annotations
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

from ai.memory.store import set_memory_store, InMemoryMemoryStore
from ai.tools.memory_tools import WriteMemory


@dataclass
class AgentConfig:
    name: str
    role: str
    instructions: str
    model: str = "claude-3-5-sonnet-20241022"
    tools: List[str] = None
    active: bool = True
    
    def __post_init__(self):
        if self.tools is None:
            self.tools = []


@dataclass
class SwarmConfig:
    name: str
    description: str
    agents: List[AgentConfig]
    flows: List[List[str]]  # [["Agent1", "Agent2"]] means Agent1 can initiate to Agent2
    shared_instructions: Optional[str] = None


class AgentDeploymentInterface:
    """Interface for configuring and deploying agent swarms."""
    
    def __init__(self, config_dir: Path = None):
        self.config_dir = config_dir or Path.cwd() / "agent_configs"
        self.config_dir.mkdir(exist_ok=True)
    
    def create_default_config(self) -> SwarmConfig:
        """Create default swarm configuration matching current hardcoded setup."""
        agents = [
            AgentConfig(
                name="Father",
                role="Strategic Planner & Delegator", 
                instructions="Strategic planning, memory management, and work delegation. Coordinates overall project direction.",
                tools=["WriteMemory", "ReadMemoryContext", "GenerateNextSteps", "IntentNormalizer", "DoDCheck"]
            ),
            AgentConfig(
                name="Architect",
                role="TDD & ADR Enforcer",
                instructions="Enforce TDD-first development and ADR discipline. Ensure tests exist before implementation.",
                tools=["CreateADR", "WriteMemory", "ReadMemoryContext"]
            ),
            AgentConfig(
                name="Developer", 
                role="Implementation Specialist",
                instructions="Write minimal code to make tests green, then refactor. Focus on clean, simple implementations.",
                tools=["DiscoverMCPServers", "CallMCPTool", "WriteMemory"]
            ),
            AgentConfig(
                name="QA",
                role="Test & Quality Assurance",
                instructions="Expand test coverage and harden edge cases. Ensure code quality and reliability.",
                tools=["DiscoverMCPServers", "CallMCPTool", "WriteMemory"]
            ),
            AgentConfig(
                name="Reviewer",
                role="Code Review & Security",
                instructions="Review for simplicity, security, and ADR linkage. Final quality gate before completion.",
                tools=["WriteMemory", "ReadMemoryContext"]
            )
        ]
        
        flows = [
            ["Father", "Architect"],
            ["Architect", "Developer"], 
            ["Developer", "QA"],
            ["QA", "Reviewer"],
            ["Reviewer", "Father"]
        ]
        
        return SwarmConfig(
            name="default",
            description="Standard TDD-focused development swarm with memory persistence",
            agents=agents,
            flows=flows,
            shared_instructions="Follow TDD principles, maintain ADR discipline, and use memory tools for coordination."
        )
    
    def save_config(self, config: SwarmConfig, filename: str = None) -> Path:
        """Save swarm configuration to YAML file."""
        filename = filename or f"{config.name}.yaml"
        config_path = self.config_dir / filename
        
        config_dict = asdict(config)
        with open(config_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)
        
        return config_path
    
    def load_config(self, filename: str) -> SwarmConfig:
        """Load swarm configuration from YAML file.""" 
        config_path = self.config_dir / filename
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        
        # Convert agent dicts back to AgentConfig objects
        agents = [AgentConfig(**agent_dict) for agent_dict in config_dict['agents']]
        config_dict['agents'] = agents
        
        return SwarmConfig(**config_dict)
    
    def list_configs(self) -> List[str]:
        """List available configuration files."""
        return [f.name for f in self.config_dir.glob("*.yaml")]
    
    def deploy_swarm(self, config_name: str = "default", memory_context: str = None) -> Dict[str, Any]:
        """Deploy agents according to configuration."""
        try:
            config = self.load_config(f"{config_name}.yaml")
        except FileNotFoundError:
            # Create default if doesn't exist
            config = self.create_default_config()
            self.save_config(config)
        
        # Set up isolated memory for this deployment
        set_memory_store(InMemoryMemoryStore())
        
        # Write deployment info to memory
        active_agents = [a.name for a in config.agents if a.active]
        WriteMemory(
            content=f"deployed swarm: {config.name} with {len(active_agents)} active agents: {', '.join(active_agents)}",
            tags=["deployment", "swarm"]
        ).run()  # type: ignore
        
        if memory_context:
            WriteMemory(content=f"deployment context: {memory_context}", tags=["deployment"]).run()  # type: ignore
        
        return {
            "swarm_name": config.name,
            "description": config.description,
            "active_agents": active_agents,
            "total_agents": len(config.agents),
            "flows": config.flows,
            "status": "deployed",
            "config_file": f"{config_name}.yaml"
        }


def main():
    """CLI interface for agent deployment."""
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m ai.interface.deploy_agents create [config_name]")
        print("  python -m ai.interface.deploy_agents deploy [config_name] [context]")
        print("  python -m ai.interface.deploy_agents list")
        return
    
    interface = AgentDeploymentInterface()
    command = sys.argv[1]
    
    if command == "create":
        config_name = sys.argv[2] if len(sys.argv) > 2 else "default"
        config = interface.create_default_config()
        config.name = config_name
        config_path = interface.save_config(config)
        print(f"Created config: {config_path}")
        
    elif command == "deploy":
        config_name = sys.argv[2] if len(sys.argv) > 2 else "default"
        context = sys.argv[3] if len(sys.argv) > 3 else None
        result = interface.deploy_swarm(config_name, context)
        print(json.dumps(result, indent=2))
        
    elif command == "list":
        configs = interface.list_configs()
        if configs:
            print("Available configurations:")
            for config in configs:
                print(f"  - {config}")
        else:
            print("No configurations found. Use 'create' to make one.")
    
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
