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
from openai import OpenAI
import os
from pathlib import Path
import subprocess
from datetime import datetime
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file
except ImportError:
    pass  # dotenv not available, use system env vars


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
        """Execute the appropriate agent with real OpenAI calls.
        
        This creates a specialized agent prompt and executes it using OpenAI,
        then applies the changes to the actual repository files.
        """
        try:
            # Initialize OpenAI client
            client = OpenAI()
            
            # Get current working directory context
            repo_path = Path.cwd()
            
            # Create agent-specific system prompt
            system_prompt = self._create_agent_system_prompt(agent_type, repo_path)
            
            # Create user prompt with task instructions
            user_prompt = self._create_user_prompt(request, repo_path)
            
            # Call OpenAI API with timeout
            print(f"🤖 Calling OpenAI with model: {self._get_model_name(request.model)}")
            response = client.chat.completions.create(
                model=self._get_model_name(request.model),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Low temperature for precise code changes
                timeout=30.0  # 30 second timeout
            )
            print(f"✅ OpenAI call completed")
            
            # Parse response and apply changes
            result = self._parse_and_apply_agent_response(
                response.choices[0].message.content,
                agent_type,
                request
            )
            
            return result
            
        except Exception as e:
            # Return error result
            return {
                "output": f"Agent execution failed: {str(e)}",
                "artifacts": {},
                "success": False
            }
    
    def _create_agent_system_prompt(self, agent_type: str, repo_path: Path) -> str:
        """Create system prompt for specific agent type."""
        base_prompt = f"""You are a {agent_type} agent working on a software development project.
Your role is to make specific, targeted changes to code files.

IMPORTANT RULES:
1. Always provide complete file content in your response
2. Make minimal, focused changes to fix the specific issue
3. Preserve existing code style and formatting
4. Include clear explanations of what you changed

Repository path: {repo_path}
"""
        
        if agent_type == "Developer":
            return base_prompt + """Your specialization: Fix bugs, implement features, resolve FIXMEs and TODOs.
Focus on: Writing clean, maintainable code that solves the specific problem.
"""
        elif agent_type == "QA":
            return base_prompt + """Your specialization: Write and fix tests, ensure code quality.
Focus on: Creating comprehensive test cases and fixing failing tests.
"""
        elif agent_type == "Architect":
            return base_prompt + """Your specialization: System design, API structure, architectural decisions.
Focus on: Creating well-structured, scalable solutions.
"""
        elif agent_type == "Reviewer":
            return base_prompt + """Your specialization: Code review, validation, quality assurance.
Focus on: Identifying issues and suggesting improvements.
"""
        else:  # Father
            return base_prompt + """Your specialization: Strategic planning, coordination, high-level decisions.
Focus on: Breaking down complex tasks and providing clear guidance.
"""
    
    def _create_user_prompt(self, request: SpawnRequest, repo_path: Path) -> str:
        """Create user prompt with task instructions and context."""
        # Try to extract file path from instructions
        file_path = self._extract_file_path_from_instructions(request.instructions)
        
        context = f"""Task: {request.instructions}

Output Type: {request.output_type}
"""
        
        # Add file content if specific file is mentioned
        if file_path and (repo_path / file_path).exists():
            try:
                with open(repo_path / file_path, 'r') as f:
                    file_content = f.read()
                context += f"\n\nCurrent file content ({file_path}):\n```\n{file_content}\n```"
            except Exception:
                context += f"\n\nNote: Could not read file {file_path}"
        
        context += "\n\nPlease provide your solution with the complete updated file content."
        
        return context
    
    def _extract_file_path_from_instructions(self, instructions: str) -> Optional[str]:
        """Extract file path from task instructions."""
        # Simple pattern matching for common file references
        import re
        
        # Look for file paths like "file.py:line" or "file.py line"
        patterns = [
            r'([a-zA-Z0-9_/\-\.]+\.py)[:line]?\s*(\d+)?',
            r'in\s+([a-zA-Z0-9_/\-\.]+\.[a-zA-Z0-9]+)',
            r'file\s+([a-zA-Z0-9_/\-\.]+\.[a-zA-Z0-9]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, instructions)
            if match:
                return match.group(1)
        
        return None
    
    def _parse_and_apply_agent_response(
        self, 
        response_content: str, 
        agent_type: str, 
        request: SpawnRequest
    ) -> Dict[str, Any]:
        """Parse agent response and apply changes to files."""
        try:
            # Extract code blocks from response
            import re
            code_blocks = re.findall(r'```(?:python|py|\w*)\n(.*?)\n```', response_content, re.DOTALL)
            
            if not code_blocks:
                # No code blocks found, treat entire response as explanation
                return {
                    "output": response_content,
                    "artifacts": {"explanation": "No code changes detected"},
                    "files_modified": []
                }
            
            # Try to identify target file
            file_path = self._extract_file_path_from_instructions(request.instructions)
            
            if file_path and code_blocks:
                # Apply the first code block to the identified file
                full_path = Path.cwd() / file_path
                
                # Create backup
                backup_content = None
                if full_path.exists():
                    with open(full_path, 'r') as f:
                        backup_content = f.read()
                
                # Write new content
                with open(full_path, 'w') as f:
                    f.write(code_blocks[0])
                
                # Commit changes to git
                commit_hash = self._commit_changes(
                    files=[str(file_path)], 
                    agent_type=agent_type,
                    request=request
                )
                
                return {
                    "output": f"Successfully updated {file_path}",
                    "artifacts": {
                        "files_modified": [str(file_path)],
                        "backup_content": backup_content,
                        "explanation": response_content,
                        "commit_hash": commit_hash
                    },
                    "files_modified": [str(file_path)]
                }
            
            # If no specific file identified, return explanation
            return {
                "output": response_content,
                "artifacts": {
                    "code_blocks": code_blocks,
                    "explanation": "Code provided but no target file identified"
                },
                "files_modified": []
            }
            
        except Exception as e:
            return {
                "output": f"Failed to parse agent response: {str(e)}",
                "artifacts": {"error": str(e), "raw_response": response_content},
                "files_modified": []
            }
    
    def _get_model_name(self, model: str) -> str:
        """Map friendly model names to OpenAI model names."""
        model_mapping = {
            "gpt-4": "gpt-4o",
            "gpt-4o": "gpt-4o",
            "gpt-4-mini": "gpt-4o-mini",
            "gpt-4o-mini": "gpt-4o-mini",
            "gpt-3.5": "gpt-3.5-turbo",
            "gpt-3.5-turbo": "gpt-3.5-turbo"
        }
        return model_mapping.get(model, "gpt-4o")  # Default to gpt-4o
    
    def _commit_changes(
        self, 
        files: List[str], 
        agent_type: str, 
        request: SpawnRequest
    ) -> Optional[str]:
        """Commit changes to git repository.
        
        Args:
            files: List of file paths to commit
            agent_type: Type of agent that made the changes
            request: Original spawn request
            
        Returns:
            Commit hash if successful, None otherwise
        """
        try:
            # Check if this is a git repository
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                print("⚠️ Not a git repository - skipping commit")
                return None
            
            # Stage the files
            for file_path in files:
                subprocess.run(
                    ["git", "add", file_path],
                    check=True,
                    timeout=10
                )
            
            # Create commit message
            commit_message = f"{agent_type} Agent: {request.instructions[:50]}"
            if len(request.instructions) > 50:
                commit_message += "..."
            
            commit_message += f"\n\nAuto-commit by Fresh autonomous system"
            commit_message += f"\nAgent: {agent_type}"
            commit_message += f"\nModel: {request.model}"
            commit_message += f"\nFiles: {', '.join(files)}"
            
            # Commit the changes
            result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Get the commit hash
                hash_result = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if hash_result.returncode == 0:
                    commit_hash = hash_result.stdout.strip()[:8]  # Short hash
                    print(f"📝 Committed changes: {commit_hash}")
                    return commit_hash
            
            print(f"⚠️ Git commit failed: {result.stderr}")
            return None
            
        except subprocess.TimeoutExpired:
            print("⚠️ Git commit timed out")
            return None
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Git commit error: {e}")
            return None
        except Exception as e:
            print(f"⚠️ Unexpected error during commit: {e}")
            return None
    
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
