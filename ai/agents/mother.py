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
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import defaultdict

from ai.memory.store import get_store, InMemoryMemoryStore
from ai.memory.intelligent_store import IntelligentMemoryStore, MemoryType
from ai.tools.memory_tools import WriteMemory
from ai.agents.enhanced_agents import EnhancedDeveloper, EnhancedArchitect, EnhancedQA
from ai.agents.senior_reviewer import SeniorReviewer, ReviewDecision
from ai.integration.github_pr import GitHubPRIntegration
from ai.utils.settings import is_offline, TIMEOUT_SECONDS
import os
import uuid
from pathlib import Path
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file
except ImportError:
    pass  # dotenv not available, use system env vars

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # OpenAI not available


@dataclass
class ChildAgent:
    """Child agent spawned by Mother Agent."""
    id: str
    name: str
    instructions: str
    model: str
    output_type: str
    parent_id: str
    working_directory: Optional[str] = None
    status: str = "spawned"
    memory_store: Optional[Any] = None
    _messages: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.memory_store:
            self.memory_store = get_store() or InMemoryMemoryStore()
    
    def execute(self) -> Dict[str, Any]:
        """Execute the agent task."""
        self.status = "executing"
        
        try:
            # Record task start in memory
            self.memory_store.write(
                content=f"Started task: {self.instructions}",
                tags=["agent", self.name, "task_start"]
            )
            
            # Phase 1: Analyze the task and codebase
            analysis = self._analyze_task()
            
            # Phase 2: Look for similar patterns in memory
            patterns = self._find_patterns()
            
            # Phase 3: Generate solution
            solution = self._generate_solution(analysis, patterns)
            
            # Phase 4: Validate solution
            validation = self._validate_solution(solution)
            
            # Phase 5: Create deliverable
            result = self._create_deliverable(solution, validation)
            
            # Record completion in memory
            self.memory_store.write(
                content=f"Completed task: {self.instructions}. Success: {result.get('success', False)}",
                tags=["agent", self.name, "task_complete"]
            )
            
            self.status = "completed"
            return result
            
        except Exception as e:
            # Record failure in memory
            self.memory_store.write(
                content=f"Failed task: {self.instructions}. Error: {str(e)}",
                tags=["agent", self.name, "task_failed", "error"]
            )
            
            self.status = "failed"
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.id
            }
    
    def _analyze_task(self) -> Dict[str, Any]:
        """Analyze the task and codebase."""
        # Placeholder for task analysis
        return {
            "task_type": self.output_type,
            "complexity": "medium",
            "estimated_effort": "30min"
        }
    
    def _find_patterns(self) -> List[Any]:
        """Find similar patterns from memory."""
        # Look for similar successful tasks
        patterns = self.memory_store.query(
            tags=["success", "pattern"],
            limit=3
        )
        
        return patterns[:3]  # Top 3 most relevant patterns
    
    def _generate_solution(self, analysis: Dict[str, Any], patterns: List[Any]) -> Dict[str, Any]:
        """Generate solution based on analysis and patterns."""
        # Placeholder for solution generation
        return {
            "approach": "pattern_based" if patterns else "novel",
            "solution": f"Generated solution for: {self.instructions}",
            "confidence": 0.8 if patterns else 0.6
        }
    
    def _validate_solution(self, solution: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the generated solution."""
        # Placeholder for solution validation
        return {
            "valid": True,
            "tests_pass": True,
            "quality_score": 0.9
        }
    
    def _create_deliverable(self, solution: Dict[str, Any], validation: Dict[str, Any]) -> Dict[str, Any]:
        """Create the final deliverable."""
        success = validation.get("valid", False) and validation.get("tests_pass", False)
        
        return {
            "success": success,
            "solution": solution.get("solution"),
            "approach": solution.get("approach"),
            "confidence": solution.get("confidence"),
            "quality_score": validation.get("quality_score"),
            "files_changed": solution.get("files_changed", []),  # Use files_changed from solution
            "agent_id": self.id
        }
    
    def send_message_to_parent(self, message: Dict[str, Any]) -> None:
        """Send message to parent agent."""
        message["from"] = self.id
        message["to"] = self.parent_id
        self._messages.append(message)
    
    def on_progress(self, update: Dict[str, Any]) -> None:
        """Handle progress updates (can be overridden)."""
        pass


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
        
        # New attributes for v1.0
        self.id = f"mother-{uuid.uuid4().hex[:8]}"
        self.active_agents: Dict[str, ChildAgent] = {}
        self.agent_messages: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    
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
    
    def spawn(self, name: str, instructions: str, model: str = "gpt-4", 
              output_type: str = "code", working_directory: Optional[str] = None) -> ChildAgent:
        """Spawn a new child agent.
        
        This is the new v1.0 interface for spawning agents that return
        actual agent objects for more sophisticated workflows.
        
        Args:
            name: Name/identifier for the agent
            instructions: Task instructions for the agent
            model: AI model to use (default: gpt-4)
            output_type: Expected output type (code/tests/docs/design/review)
            working_directory: Directory for agent to work in
            
        Returns:
            ChildAgent instance ready for execution
        """
        # Generate unique agent ID
        agent_id = f"agent-{uuid.uuid4().hex[:8]}"
        
        # Create child agent
        child_agent = ChildAgent(
            id=agent_id,
            name=name,
            instructions=instructions,
            model=model,
            output_type=output_type,
            parent_id=self.id,
            working_directory=working_directory,
            memory_store=self.memory_store
        )
        
        # Register the agent
        with self._lock:
            self.active_agents[agent_id] = child_agent
        
        # Record spawn in memory
        self.memory_store.write(
            content=f"Spawned agent '{name}' for task: {instructions}",
            tags=["mother", "spawn", name]
        )
        
        return child_agent
    
    def get_active_agents(self) -> List[ChildAgent]:
        """Get list of currently active agents."""
        with self._lock:
            return list(self.active_agents.values())
    
    def get_agent_by_id(self, agent_id: str) -> Optional[ChildAgent]:
        """Get agent by ID."""
        with self._lock:
            return self.active_agents.get(agent_id)
    
    def get_messages_from(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get messages from a specific agent."""
        return self.agent_messages.get(agent_id, [])
    
    def cleanup_completed_agents(self) -> int:
        """Remove completed agents from active registry."""
        removed = 0
        with self._lock:
            completed_agents = [
                agent_id for agent_id, agent in self.active_agents.items()
                if agent.status in ['completed', 'failed']
            ]
            
            for agent_id in completed_agents:
                del self.active_agents[agent_id]
                removed += 1
        
        return removed
    
    def scan_for_issues(self, directory: str) -> List[Dict[str, Any]]:
        """Scan directory for issues that agents can fix."""
        # Placeholder implementation - would integrate with repo scanner
        issues = [
            {
                "type": "potential_error",
                "file": "src/main.py",
                "line": 6,
                "description": "Division by zero possible in divide function",
                "severity": "medium"
            }
        ]
        return issues
    
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
            # Respect offline mode: skip networked OpenAI calls
            if is_offline():
                return {
                    "output": "Offline mode: skipped OpenAI call",
                    "artifacts": {"offline": True},
                    "success": False
                }

            # Initialize OpenAI client
            if OpenAI is None:
                return {
                    "output": "OpenAI not available: python package not installed",
                    "artifacts": {"openai_available": False},
                    "success": False
                }
            client = OpenAI()
            
            # Get current working directory context
            repo_path = Path.cwd()
            
            # Create agent-specific system prompt
            system_prompt = self._create_agent_system_prompt(agent_type, repo_path)
            
            # Create user prompt with task instructions
            user_prompt = self._create_user_prompt(request, repo_path)
            
            # Call OpenAI API with timeout
            model_name = self._get_model_name(request.model)
            print(f"🤖 Calling OpenAI with model: {model_name}")
            
            # Configure temperature based on model capabilities
            api_params = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "timeout": float(TIMEOUT_SECONDS)
            }
            
            # GPT-5 only supports default temperature (1.0), others support custom temperature
            if model_name != "gpt-5":
                api_params["temperature"] = 0.1  # Low temperature for precise code changes
            
            response = client.chat.completions.create(**api_params)
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
                
                # Get senior review before applying changes
                reviewer = SeniorReviewer()
                print(f"🔍 Senior review in progress...")
                
                review_result = reviewer.review_changes(
                    original_content=backup_content,
                    modified_content=code_blocks[0],
                    file_path=file_path,
                    change_description=request.instructions,
                    agent_type=agent_type
                )
                
                print(f"📊 Review decision: {review_result.decision.value} (confidence: {review_result.confidence:.2f})")
                print(f"💭 Review reasoning: {review_result.reasoning[:100]}...")
                
                # Handle review decision with PR workflow
                if review_result.decision == ReviewDecision.APPROVE:
                    # Write new content
                    with open(full_path, 'w') as f:
                        f.write(code_blocks[0])
                    
                    # Create PR with approved changes
                    pr_result = self._create_pull_request_for_changes(
                        files=[str(file_path)],
                        agent_type=agent_type,
                        request=request,
                        review_result=review_result
                    )
                    
                    status = "approved_and_pr_created" if pr_result else "approved_pr_failed"
                    
                elif review_result.decision == ReviewDecision.REQUEST_CHANGES:
                    # Don't apply changes, return for revision
                    status = "requires_revision"
                    pr_result = None
                    print(f"🔄 Changes require revision: {', '.join(review_result.suggestions)}")
                    
                else:  # REJECT
                    # Don't apply changes, task failed
                    status = "rejected"
                    pr_result = None
                    print(f"❌ Changes rejected: {review_result.reasoning}")
                
                return {
                    "output": f"Review {status}: {file_path}",
                    "artifacts": {
                        "files_modified": [str(file_path)] if status.startswith("approved") else [],
                        "backup_content": backup_content,
                        "explanation": response_content,
                        "pr_info": pr_result,
                        "review_status": status,
                        "review_decision": review_result.decision.value,
                        "review_confidence": review_result.confidence,
                        "review_reasoning": review_result.reasoning,
                        "review_suggestions": review_result.suggestions,
                        "security_concerns": review_result.security_concerns
                    },
                    "files_modified": [str(file_path)] if status.startswith("approved") else []
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
        """Map friendly model names to OpenAI model names, preferring GPT-5."""
        model_mapping = {
            "gpt-5": "gpt-5",  # GPT-5 when available
            "gpt-4": "gpt-5",  # Upgrade GPT-4 requests to GPT-5
            "gpt-4o": "gpt-5",  # Upgrade GPT-4o requests to GPT-5
            "gpt-4-mini": "gpt-4o-mini",  # Keep mini versions
            "gpt-4o-mini": "gpt-4o-mini",
            "gpt-3.5": "gpt-3.5-turbo",
            "gpt-3.5-turbo": "gpt-3.5-turbo"
        }
        # Try GPT-5 first, fallback to GPT-4o if not available
        preferred_model = model_mapping.get(model, "gpt-5")
        return preferred_model
    
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
    
    def _create_pull_request_for_changes(
        self,
        files: List[str],
        agent_type: str, 
        request: SpawnRequest,
        review_result: Any
    ) -> Optional[Dict[str, Any]]:
        """Create a pull request for approved changes.
        
        Args:
            files: List of files that were modified
            agent_type: Type of agent that made changes
            request: Original spawn request
            review_result: Senior review result
            
        Returns:
            PR information if successful, None otherwise
        """
        try:
            # Initialize GitHub integration
            github = GitHubPRIntegration()
            
            if not github.is_configured():
                print("⚠️ GitHub integration not configured - committing directly")
                return self._commit_changes(files, agent_type, request)
            
            # Create feature branch
            branch_info = github.create_feature_branch(
                task_description=request.instructions,
                agent_type=agent_type
            )
            
            if not branch_info.created:
                print("⚠️ Failed to create branch - committing directly")
                return self._commit_changes(files, agent_type, request)
            
            # Create commit message
            commit_message = f"{agent_type} Agent: {request.instructions[:50]}"
            if len(request.instructions) > 50:
                commit_message += "..."
            
            commit_message += f"\n\nAuto-generated by Fresh autonomous system"
            commit_message += f"\n- Agent: {agent_type}"
            commit_message += f"\n- Model: {request.model}"
            commit_message += f"\n- Senior Review: {review_result.decision.value} (confidence: {review_result.confidence:.2f})"
            commit_message += f"\n- Files: {', '.join(files)}"
            
            # Commit and push changes
            push_success = github.commit_and_push_changes(
                branch_info=branch_info,
                files=files,
                commit_message=commit_message
            )
            
            if not push_success:
                print("⚠️ Failed to push changes")
                github.cleanup_on_failure(branch_info)
                return None
            
            # Create PR title and body
            pr_title = f"{agent_type} Agent: {request.instructions[:60]}"
            if len(request.instructions) > 60:
                pr_title += "..."
            
            pr_body = f"""# 🤖 Autonomous Agent Implementation

**Agent Type**: {agent_type}
**Task**: {request.instructions}

## 📋 Changes Made

{chr(10).join(f"- `{f}`" for f in files)}

## 🔍 Senior Review Summary

- **Decision**: {review_result.decision.value.upper()}
- **Confidence**: {review_result.confidence:.2f}
- **Quality Score**: {review_result.maintainability_score:.2f}

**Reasoning**: {review_result.reasoning}

### Suggestions Addressed
{chr(10).join(f"- {s}" for s in review_result.suggestions) if review_result.suggestions else "None"}

---

*This PR was automatically created by the Fresh autonomous development system.*
*All changes have been reviewed by a senior-level AI reviewer before submission.*
"""
            
            # Create pull request
            pr_info = github.create_pull_request(
                branch_info=branch_info,
                title=pr_title,
                body=pr_body,
                reviewer_result={
                    'review_decision': review_result.decision.value,
                    'review_confidence': review_result.confidence,
                    'review_reasoning': review_result.reasoning,
                    'review_suggestions': review_result.suggestions,
                    'security_concerns': review_result.security_concerns
                }
            )
            
            if pr_info:
                return {
                    "pr_number": pr_info.number,
                    "pr_url": pr_info.url,
                    "branch_name": pr_info.branch,
                    "pr_title": pr_info.title
                }
            else:
                github.cleanup_on_failure(branch_info)
                return None
                
        except Exception as e:
            print(f"⚠️ Failed to create PR: {e}")
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
