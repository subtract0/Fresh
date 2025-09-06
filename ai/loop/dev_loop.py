"""Autonomous development loop implementation with Firestore state management.

This module implements the main development loop with robust Firestore-based
state persistence, replacing fragile JSON file state management.

Cross-references:
    - ADR-003: Unified Enhanced Architecture Migration
    - ADR-008: Autonomous Development Loop Architecture
    - ai/state/: Firestore state management
"""
from __future__ import annotations
import asyncio
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from ai.loop.repo_scanner import RepoScanner, Task, TaskType
from ai.agents.mother import MotherAgent, AgentResult
from ai.memory.store import get_store
from ai.tools.memory_tools import WriteMemory
from ai.state.firestore_manager import get_state_manager
from ai.state.firestore_schema import SystemState, AgentState, AgentStatus, TaskStatus


logger = logging.getLogger(__name__)


class DevLoop:
    """Main development loop orchestrator with Firestore state management.
    
    Coordinates repository scanning, agent spawning, and result collection
    for autonomous development cycles with persistent state in Firestore.
    """
    
    def __init__(
        self,
        repo_path: str = ".",
        max_tasks: int = 10,
        task_types: Optional[List[TaskType]] = None,
        dry_run: bool = False,
        use_dashboard: bool = False
    ):
        """Initialize development loop with Firestore state.
        
        Args:
            repo_path: Path to repository to scan
            max_tasks: Maximum tasks to process per cycle
            task_types: Types of tasks to process (None = all)
            dry_run: If True, scan but don't execute agents
            use_dashboard: Enable dashboard updates
        """
        self.repo_path = repo_path
        self.max_tasks = max_tasks
        self.task_types = task_types
        self.dry_run = dry_run
        self.use_dashboard = use_dashboard
        
        # Initialize components
        self.scanner = RepoScanner(repo_path)
        self.mother_agent = MotherAgent()
        self.processed_tasks: List[Task] = []
        
        # Initialize Firestore state manager
        self.state_manager = get_state_manager()
        self.session_id = f"dev_loop_{datetime.now(timezone.utc).isoformat()}"
    
    async def run_cycle(self) -> List[AgentResult]:
        """Run a single development cycle with Firestore state persistence.
        
        Returns:
            List of agent results from processed tasks
        """
        logger.info(f"Starting development cycle for {self.repo_path}")
        
        # Load previous state from Firestore
        await self.load_state()
        
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
            
            result = await self.process_task(task)
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
        
        # Save state to Firestore
        await self.save_state()
        
        # Log to memory
        self._log_cycle_to_memory(len(tasks_to_process), len(results))
        
        return results
    
    async def process_task(self, task: Task) -> Optional[AgentResult]:
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
        agent_type = self._determine_agent_type_for_task(task)
        
        # Create agent state in Firestore
        agent_state = AgentState(
            agent_id=f"auto_{task.type.value.lower()}_{task.file_path.replace('/', '_')}",
            agent_type=agent_type,
            session_id=self.session_id,
            status=AgentStatus.ACTIVE,
            current_task=task.description,
            task_status=TaskStatus.IN_PROGRESS,
            created_at=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc),
            last_active=datetime.now(timezone.utc),
            memory_context={"task_type": task.type.value, "file": task.file_path},
            task_history=[],
            performance_metrics={},
            agent_config={"output_type": output_type},
            tools_enabled=[]
        )
        
        await self.state_manager.save_agent_state(agent_state)
        
        # Update dashboard with agent type
        if self.use_dashboard:
            try:
                from ai.interface.console_dashboard import update_task_progress
                update_task_progress(task, agent_type)
            except ImportError:
                pass
        
        # Spawn agent via Mother
        result = self.mother_agent.run(
            name=agent_state.agent_id,
            instructions=f"Fix the following issue:\n{task.description}\n\nFile: {task.file_path}:{task.line_number}",
            model="gpt-4",
            output_type=output_type
        )
        
        # Update agent state with result
        agent_state.status = AgentStatus.IDLE if result.success else AgentStatus.ERROR
        agent_state.task_status = TaskStatus.COMPLETED if result.success else TaskStatus.FAILED
        agent_state.last_updated = datetime.now(timezone.utc)
        agent_state.task_history.append({
            "task": task.description,
            "result": "success" if result.success else "failed",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        await self.state_manager.save_agent_state(agent_state)
        
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
    
    async def save_state(self) -> None:
        """Save processed tasks state to Firestore."""
        try:
            # Get or create system state
            system_state = await self.state_manager.get_system_state()
            if not system_state:
                system_state = SystemState(
                    system_version="2.2.0",
                    last_updated=datetime.now(timezone.utc),
                    active_sessions=[self.session_id],
                    total_agents_spawned=0,
                    current_agent_count=0,
                    system_metrics={},
                    error_counts={},
                    global_config={},
                    feature_flags={"unified_agents": True, "firestore_state": True}
                )
            
            # Update processed tasks in system state
            system_state.global_config['dev_loop_processed_tasks'] = [
                {
                    'type': task.type.value,
                    'description': task.description,
                    'file_path': task.file_path,
                    'line_number': task.line_number
                }
                for task in self.processed_tasks
            ]
            system_state.last_updated = datetime.now(timezone.utc)
            
            # Add session if not present
            if self.session_id not in system_state.active_sessions:
                system_state.active_sessions.append(self.session_id)
            
            await self.state_manager.update_system_state(system_state)
            logger.info(f"Saved state to Firestore with {len(self.processed_tasks)} processed tasks")
            
        except Exception as e:
            logger.warning(f"Failed to save state to Firestore: {e}")
    
    async def load_state(self) -> None:
        """Load previously processed tasks state from Firestore."""
        try:
            system_state = await self.state_manager.get_system_state()
            if not system_state:
                logger.info("No previous state found in Firestore")
                return
            
            # Reconstruct tasks from system state
            processed_tasks_data = system_state.global_config.get('dev_loop_processed_tasks', [])
            for task_data in processed_tasks_data:
                task = Task(
                    type=TaskType[task_data['type']],
                    description=task_data['description'],
                    file_path=task_data['file_path'],
                    line_number=task_data['line_number']
                )
                self.processed_tasks.append(task)
            
            logger.info(f"Loaded {len(self.processed_tasks)} processed tasks from Firestore")
            
        except Exception as e:
            logger.warning(f"Failed to load state from Firestore: {e}")
    
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
    """Run a single development cycle with Firestore state.
    
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
    """Run continuous development loop with Firestore state.
    
    Args:
        interval: Seconds between cycles
        repo_path: Repository path to scan
        max_tasks: Maximum tasks per cycle
        stop_after: Stop after N cycles (None = infinite)
    """
    loop = DevLoop(
        repo_path=repo_path,
        max_tasks=max_tasks
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
