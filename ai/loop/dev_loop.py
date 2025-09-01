"""Autonomous development loop implementation.

This module implements the main development loop that:
1. Scans the repository for issues
2. Dispatches agents to fix them
3. Collects results and prepares for PR creation

Cross-references:
    - ADR-008: Autonomous Development Loop Architecture
    - Repository Scanner: ai/loop/repo_scanner.py
    - Mother Agent: ai/agents/mother.py
    - GitHub Integration: ai/integration/github.py
"""
from __future__ import annotations
import asyncio
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from ai.loop.repo_scanner import RepoScanner, Task, TaskType
from ai.agents.mother import MotherAgent, AgentResult
from ai.memory.store import get_store
from ai.tools.memory_tools import WriteMemory


logger = logging.getLogger(__name__)


class DevLoop:
    """Main development loop orchestrator.
    
    Coordinates repository scanning, agent spawning, and result collection
    for autonomous development cycles.
    """
    
    def __init__(
        self,
        repo_path: str = ".",
        max_tasks: int = 10,
        task_types: Optional[List[TaskType]] = None,
        state_file: Optional[Path] = None,
        dry_run: bool = False,
        use_dashboard: bool = False
    ):
        """Initialize development loop.
        
        Args:
            repo_path: Path to repository to scan
            max_tasks: Maximum tasks to process per cycle
            task_types: Types of tasks to process (None = all)
            state_file: File to persist processed tasks state
            dry_run: If True, scan but don't execute agents
        """
        self.repo_path = repo_path
        self.max_tasks = max_tasks
        self.task_types = task_types
        self.state_file = state_file
        self.dry_run = dry_run
        self.use_dashboard = use_dashboard
        
        # Initialize components
        self.scanner = RepoScanner(repo_path)
        self.mother_agent = MotherAgent()
        self.processed_tasks: List[Task] = []
        
        # Load previous state if exists
        if self.state_file:
            self.load_state()
    
    async def run_cycle(self) -> List[AgentResult]:
        """Run a single development cycle.
        
        Returns:
            List of agent results from processed tasks
        """
        logger.info(f"Starting development cycle for {self.repo_path}")
        
        # Update dashboard if enabled
        if self.use_dashboard:
            try:
                from ai.interface.console_dashboard import update_scan_status
                update_scan_status(True)
            except ImportError:
                pass
        
        # Scan repository
        tasks = self.scanner.scan()
        logger.info(f"Found {len(tasks)} tasks in repository")
        
        # Update dashboard with results
        if self.use_dashboard:
            try:
                from ai.interface.console_dashboard import update_scan_status
                update_scan_status(False, len(tasks))
            except ImportError:
                pass
        
        # Filter tasks
        tasks = self.filter_tasks(tasks)
        
        # Skip already processed tasks
        new_tasks = [t for t in tasks if t not in self.processed_tasks]
        logger.info(f"Processing {len(new_tasks)} new tasks")
        
        # Limit tasks per cycle
        tasks_to_process = new_tasks[:self.max_tasks]
        
        # Process tasks
        results = []
        for task in tasks_to_process:
            logger.info(f"Processing task: {task.description[:50]}...")
            
            # Update dashboard
            if self.use_dashboard:
                try:
                    from ai.interface.console_dashboard import update_task_progress
                    update_task_progress(task)
                except ImportError:
                    pass
            
            result = self.process_task(task)
            if result:
                results.append(result)
                
                # Update dashboard with result
                if self.use_dashboard:
                    try:
                        from ai.interface.console_dashboard import add_result, update_task_progress
                        add_result(result)
                        update_task_progress(None)  # Clear current task
                    except ImportError:
                        pass
            
                if result.success:
                    self.processed_tasks.append(task)
                    logger.info(f"✅ Task completed by {result.agent_type}")
                else:
                    logger.warning(f"❌ Task failed: {result.error}")
        
        # Save state
        if self.state_file:
            self.save_state()
        
        # Log to memory
        self._log_cycle_to_memory(len(tasks_to_process), len(results))
        
        return results
    
    def process_task(self, task: Task) -> Optional[AgentResult]:
        """Process a single task with appropriate agent.
        
        Args:
            task: Task to process
            
        Returns:
            Agent result from processing, or None if dry run
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Would process: {task.description}")
            return None
            
        # Determine output type based on task
        output_type = self._determine_output_type(task)
        
        # Update dashboard with agent type
        if self.use_dashboard:
            agent_type = self._determine_agent_type_for_task(task)
            try:
                from ai.interface.console_dashboard import update_task_progress
                update_task_progress(task, agent_type)
            except ImportError:
                pass
        
        # Spawn agent via Mother
        result = self.mother_agent.run(
            name=f"auto_{task.type.value.lower()}_{task.file_path.replace('/', '_')}",
            instructions=f"Fix the following issue:\n{task.description}\n\nFile: {task.file_path}:{task.line_number}",
            model="gpt-4",
            output_type=output_type
        )
        
        return result
    
    def filter_tasks(self, tasks: List[Task]) -> List[Task]:
        """Filter tasks based on configured types.
        
        Args:
            tasks: All tasks found
            
        Returns:
            Filtered list of tasks
        """
        if not self.task_types:
            return tasks
            
        return [t for t in tasks if t.type in self.task_types]
    
    def save_state(self) -> None:
        """Save processed tasks to state file."""
        if not self.state_file:
            return
            
        state = {
            "processed_tasks": [
                {
                    "type": t.type.value,
                    "description": t.description,
                    "file_path": t.file_path,
                    "line_number": t.line_number
                }
                for t in self.processed_tasks
            ],
            "last_run": datetime.now().isoformat()
        }
        
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self) -> None:
        """Load processed tasks from state file."""
        if not self.state_file or not self.state_file.exists():
            return
            
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                
            self.processed_tasks = [
                Task(
                    type=TaskType(t["type"]),
                    description=t["description"],
                    file_path=t["file_path"],
                    line_number=t["line_number"]
                )
                for t in state.get("processed_tasks", [])
            ]
            
            logger.info(f"Loaded {len(self.processed_tasks)} previously processed tasks")
        except Exception as e:
            logger.warning(f"Failed to load state: {e}")
    
    def _determine_output_type(self, task: Task) -> str:
        """Determine expected output type for task.
        
        Args:
            task: Task to process
            
        Returns:
            Output type (code/tests/docs/etc)
        """
        if task.type == TaskType.FAILING_TEST:
            return "tests"
        elif "test" in task.file_path.lower():
            return "tests"
        elif task.file_path.endswith(('.md', '.rst', '.txt')):
            return "docs"
        else:
            return "code"
    
    def _log_cycle_to_memory(self, tasks_found: int, tasks_processed: int) -> None:
        """Log cycle results to memory.
        
        Args:
            tasks_found: Number of tasks found
            tasks_processed: Number of tasks processed
        """
        WriteMemory(
            content=f"Development cycle completed: {tasks_processed}/{tasks_found} tasks processed",
            tags=["dev_loop", "cycle", "autonomous"]
        ).run()
    
    def _determine_agent_type_for_task(self, task: Task) -> str:
        """Determine which agent will handle the task.
        
        Args:
            task: Task to process
            
        Returns:
            Agent type name
        """
        output_type = self._determine_output_type(task)
        
        if output_type == "tests" or task.type == TaskType.FAILING_TEST:
            return "QA"
        elif output_type == "docs":
            return "Developer"
        elif task.type == TaskType.FIXME or task.type == TaskType.SYNTAX_ERROR:
            return "Developer"
        elif task.type == TaskType.TYPE_ERROR:
            return "Developer"
        else:
            return "Father"


# Module-level convenience functions

async def run_development_cycle(
    repo_path: str = ".",
    max_tasks: int = 10,
    task_types: Optional[List[TaskType]] = None
) -> List[AgentResult]:
    """Run a single development cycle.
    
    Args:
        repo_path: Repository path to scan
        max_tasks: Maximum tasks to process
        task_types: Types of tasks to process
        
    Returns:
        List of agent results
    """
    loop = DevLoop(repo_path, max_tasks, task_types)
    return await loop.run_cycle()


async def run_continuous_loop(
    interval: int = 300,
    repo_path: str = ".",
    max_tasks: int = 10,
    stop_after: Optional[int] = None
) -> None:
    """Run continuous development loop.
    
    Args:
        interval: Seconds between cycles
        repo_path: Repository path to scan
        max_tasks: Maximum tasks per cycle
        stop_after: Stop after N cycles (None = infinite)
    """
    loop = DevLoop(
        repo_path=repo_path,
        max_tasks=max_tasks,
        state_file=Path(".fresh/dev_loop_state.json")
    )
    
    cycles = 0
    while True:
        logger.info(f"Starting cycle {cycles + 1}")
        
        try:
            results = await loop.run_cycle()
            logger.info(f"Cycle completed with {len(results)} tasks processed")
        except Exception as e:
            logger.error(f"Cycle failed: {e}")
        
        cycles += 1
        
        if stop_after and cycles >= stop_after:
            logger.info(f"Stopping after {cycles} cycles")
            break
            
        logger.info(f"Waiting {interval} seconds until next cycle...")
        await asyncio.sleep(interval)


def process_task(
    task: Task,
    repo_path: str = "."
) -> Optional[AgentResult]:
    """Process a single task.
    
    Args:
        task: Task to process
        repo_path: Repository path
        
    Returns:
        Agent result or None
    """
    loop = DevLoop(repo_path)
    return loop.process_task(task)
