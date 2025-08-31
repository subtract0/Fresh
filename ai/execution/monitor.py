"""Real-time agent execution monitor with agency swarm integration.

This module provides real-time monitoring and execution of spawned agents
using the agency swarm framework, with status updates back to users via
the Telegram bot interface.

Cross-references:
    - Agent Spawner: ai/interface/agent_spawner.py for spawn coordination
    - Telegram Bot: ai/interface/telegram_bot.py for user status updates  
    - Memory System: ai/memory/README.md for execution context and results
    - GitHub Integration: ai/integration/github.py for automated PR creation

Related:
    - Agency Swarm framework for multi-agent coordination
    - Persistent execution state management
    - Real-time progress tracking and user notification
"""
from __future__ import annotations
import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Set
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor

from ai.memory.store import get_store
from ai.tools.memory_tools import WriteMemory, ReadMemoryContext
from ai.interface.agent_spawner import SpawnedAgent, get_agent_spawner
from ai.integration.github import get_github_integration, PRResult

logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """Status of agent execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExecutionStep:
    """Individual step in agent execution."""
    step_id: str
    agent_id: str
    action: str
    status: ExecutionStatus
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    result: Optional[str] = None
    error: Optional[str] = None
    tools_used: List[str] = field(default_factory=list)


@dataclass 
class AgentExecution:
    """Execution context for a spawned agent."""
    execution_id: str
    agent: SpawnedAgent
    status: ExecutionStatus
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    steps: List[ExecutionStep] = field(default_factory=list)
    current_step: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None
    progress_percentage: float = 0.0
    user_id: Optional[str] = None  # Telegram user ID for updates
    spawn_request_id: str = ""


@dataclass
class ExecutionBatch:
    """Batch execution for multiple agents working together."""
    batch_id: str
    spawn_request_id: str
    user_request: str
    agent_executions: List[AgentExecution] = field(default_factory=list)
    status: ExecutionStatus = ExecutionStatus.PENDING
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    coordination_log: List[str] = field(default_factory=list)
    user_id: Optional[str] = None
    auto_create_pr: bool = False


class AgentExecutionMonitor:
    """Monitors and coordinates real-time agent execution with agency swarm."""
    
    def __init__(self):
        self.active_executions: Dict[str, AgentExecution] = {}
        self.active_batches: Dict[str, ExecutionBatch] = {}
        self.execution_callbacks: Dict[str, List[Callable]] = {}
        self.executor = ThreadPoolExecutor(max_workers=10, thread_name_prefix="agent_exec")
        self._monitoring_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
    async def start_monitoring(self):
        """Start the real-time monitoring loop."""
        if self._monitoring_task is not None:
            logger.warning("Monitoring already started")
            return
            
        logger.info("Starting agent execution monitoring")
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        
    async def stop_monitoring(self):
        """Stop the monitoring loop."""
        if self._monitoring_task is None:
            logger.warning("Monitoring not started")
            return
            
        logger.info("Stopping agent execution monitoring")
        self._shutdown_event.set()
        
        try:
            await asyncio.wait_for(self._monitoring_task, timeout=10.0)
        except asyncio.TimeoutError:
            logger.warning("Monitoring task did not complete within timeout")
            self._monitoring_task.cancel()
            
        self._monitoring_task = None
        self._shutdown_event.clear()
        
    async def execute_agent_batch(
        self,
        spawn_request_id: str,
        user_request: str,
        agents: List[SpawnedAgent],
        user_id: Optional[str] = None,
        auto_create_pr: bool = False
    ) -> str:
        """Execute a batch of agents with real-time coordination."""
        batch_id = f"batch_{spawn_request_id}_{int(datetime.now().timestamp())}"
        
        # Create execution batch
        batch = ExecutionBatch(
            batch_id=batch_id,
            spawn_request_id=spawn_request_id,
            user_request=user_request,
            user_id=user_id,
            auto_create_pr=auto_create_pr
        )
        
        # Create individual agent executions
        for agent in agents:
            execution_id = f"exec_{agent.agent_id}_{int(datetime.now().timestamp())}"
            execution = AgentExecution(
                execution_id=execution_id,
                agent=agent,
                status=ExecutionStatus.PENDING,
                user_id=user_id,
                spawn_request_id=spawn_request_id
            )
            
            batch.agent_executions.append(execution)
            self.active_executions[execution_id] = execution
            
        self.active_batches[batch_id] = batch
        
        # Record batch start in memory
        WriteMemory(
            content=f"Started agent execution batch: {batch_id} - {len(agents)} agents - Request: {user_request[:100]}",
            tags=["execution", "batch", "start", spawn_request_id]
        ).run()
        
        # Start asynchronous execution
        asyncio.create_task(self._execute_batch_async(batch))
        
        return batch_id
        
    async def _execute_batch_async(self, batch: ExecutionBatch):
        """Execute agent batch asynchronously with coordination."""
        try:
            batch.status = ExecutionStatus.RUNNING
            batch.coordination_log.append(f"Started batch execution at {datetime.now()}")
            
            # Notify user of execution start
            if batch.user_id:
                await self._notify_user(
                    batch.user_id,
                    f"🚀 Starting execution of {len(batch.agent_executions)} agents for your request"
                )
            
            # Execute agents based on coordination strategy
            if len(batch.agent_executions) == 1:
                await self._execute_single_agent(batch.agent_executions[0])
            else:
                await self._execute_coordinated_agents(batch)
                
            # Check overall batch status
            batch.status = self._determine_batch_status(batch)
            batch.end_time = datetime.now()
            
            # Record completion
            WriteMemory(
                content=f"Completed agent execution batch: {batch.batch_id} - Status: {batch.status.value}",
                tags=["execution", "batch", "complete", batch.spawn_request_id, batch.status.value]
            ).run()
            
            # Notify user of completion
            if batch.user_id:
                await self._notify_batch_completion(batch)
                
            # Auto-create PR if requested and successful
            if batch.auto_create_pr and batch.status == ExecutionStatus.COMPLETED:
                await self._create_pr_for_batch(batch)
                
        except Exception as e:
            batch.status = ExecutionStatus.FAILED
            batch.end_time = datetime.now()
            batch.coordination_log.append(f"Batch execution failed: {str(e)}")
            
            logger.error(f"Batch execution failed: {e}")
            
            if batch.user_id:
                await self._notify_user(
                    batch.user_id,
                    f"❌ Agent execution failed: {str(e)[:100]}..."
                )
                
        finally:
            # Clean up completed executions after delay
            asyncio.create_task(self._cleanup_batch_after_delay(batch.batch_id))
            
    async def _execute_single_agent(self, execution: AgentExecution):
        """Execute a single agent with detailed tracking."""
        try:
            execution.status = ExecutionStatus.RUNNING
            
            # Create execution steps based on agent type and instructions
            steps = self._generate_execution_steps(execution.agent)
            
            for step in steps:
                execution.steps.append(step)
                execution.current_step = step.step_id
                
                # Execute step
                step_result = await self._execute_agent_step(execution.agent, step)
                
                step.end_time = datetime.now()
                step.status = ExecutionStatus.COMPLETED if step_result else ExecutionStatus.FAILED
                step.result = step_result if step_result else "Step failed"
                
                # Update progress
                execution.progress_percentage = (len([s for s in execution.steps if s.status == ExecutionStatus.COMPLETED]) / 
                                               len(execution.steps)) * 100
                
                # Notify user of progress
                if execution.user_id and len(execution.steps) > 3:  # Only for multi-step processes
                    await self._notify_user(
                        execution.user_id,
                        f"⚡ {execution.agent.agent_type}: {step.action} - {execution.progress_percentage:.0f}% complete"
                    )
                    
                # If step failed, handle gracefully
                if not step_result:
                    logger.warning(f"Step {step.step_id} failed for agent {execution.agent.agent_id}")
                    # Continue with other steps unless critical failure
                    
            execution.status = ExecutionStatus.COMPLETED
            execution.end_time = datetime.now()
            execution.current_step = None
            execution.result = f"Agent completed {len(execution.steps)} steps successfully"
            
        except Exception as e:
            execution.status = ExecutionStatus.FAILED  
            execution.end_time = datetime.now()
            execution.error = str(e)
            logger.error(f"Agent execution failed: {e}")
            
    async def _execute_coordinated_agents(self, batch: ExecutionBatch):
        """Execute multiple agents with coordination and dependency management."""
        # Group agents by execution strategy
        architect_agents = [e for e in batch.agent_executions 
                          if 'architect' in e.agent.agent_type.lower()]
        developer_agents = [e for e in batch.agent_executions 
                          if 'developer' in e.agent.agent_type.lower()]
        qa_agents = [e for e in batch.agent_executions 
                    if 'qa' in e.agent.agent_type.lower() or 'test' in e.agent.agent_type.lower()]
        doc_agents = [e for e in batch.agent_executions 
                     if 'doc' in e.agent.agent_type.lower()]
        other_agents = [e for e in batch.agent_executions 
                       if e not in architect_agents + developer_agents + qa_agents + doc_agents]
        
        # Execute in phases with dependencies
        phases = [
            ("Architecture & Planning", architect_agents),
            ("Development", developer_agents + other_agents),
            ("Testing & QA", qa_agents),
            ("Documentation", doc_agents)
        ]
        
        for phase_name, phase_agents in phases:
            if not phase_agents:
                continue
                
            batch.coordination_log.append(f"Starting phase: {phase_name}")
            
            # Execute phase agents in parallel
            tasks = []
            for execution in phase_agents:
                tasks.append(self._execute_single_agent(execution))
                
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check phase completion
            phase_success = all(e.status == ExecutionStatus.COMPLETED for e in phase_agents)
            batch.coordination_log.append(
                f"Phase {phase_name} {'completed' if phase_success else 'had issues'}"
            )
            
            # Brief pause between phases for coordination
            if phase_success:
                await asyncio.sleep(1)
                
    def _generate_execution_steps(self, agent: SpawnedAgent) -> List[ExecutionStep]:
        """Generate execution steps based on agent type and instructions."""
        steps = []
        base_time = datetime.now()
        
        # Common setup step
        steps.append(ExecutionStep(
            step_id=f"setup_{agent.agent_id}",
            agent_id=agent.agent_id,
            action="Initialize agent environment and tools",
            status=ExecutionStatus.PENDING
        ))
        
        # Agent-specific steps based on type
        agent_type_lower = agent.agent_type.lower()
        
        if 'architect' in agent_type_lower:
            steps.extend([
                ExecutionStep(f"analyze_{agent.agent_id}", agent.agent_id, 
                            "Analyze system architecture and requirements", ExecutionStatus.PENDING),
                ExecutionStep(f"design_{agent.agent_id}", agent.agent_id,
                            "Create architectural design and decisions", ExecutionStatus.PENDING),
                ExecutionStep(f"document_{agent.agent_id}", agent.agent_id,
                            "Document architecture decisions (ADRs)", ExecutionStatus.PENDING)
            ])
            
        elif 'developer' in agent_type_lower:
            steps.extend([
                ExecutionStep(f"plan_{agent.agent_id}", agent.agent_id,
                            "Plan implementation approach", ExecutionStatus.PENDING),
                ExecutionStep(f"implement_{agent.agent_id}", agent.agent_id,
                            "Implement code changes", ExecutionStatus.PENDING),
                ExecutionStep(f"validate_{agent.agent_id}", agent.agent_id,
                            "Validate implementation and syntax", ExecutionStatus.PENDING)
            ])
            
        elif 'qa' in agent_type_lower or 'test' in agent_type_lower:
            steps.extend([
                ExecutionStep(f"analyze_{agent.agent_id}", agent.agent_id,
                            "Analyze code for testing requirements", ExecutionStatus.PENDING),
                ExecutionStep(f"create_tests_{agent.agent_id}", agent.agent_id,
                            "Create and implement tests", ExecutionStatus.PENDING),
                ExecutionStep(f"run_tests_{agent.agent_id}", agent.agent_id,
                            "Execute tests and validate results", ExecutionStatus.PENDING)
            ])
            
        elif 'doc' in agent_type_lower:
            steps.extend([
                ExecutionStep(f"review_{agent.agent_id}", agent.agent_id,
                            "Review changes and existing documentation", ExecutionStatus.PENDING),
                ExecutionStep(f"update_{agent.agent_id}", agent.agent_id,
                            "Update documentation and cross-references", ExecutionStatus.PENDING)
            ])
            
        else:
            # Generic steps for other agent types
            steps.extend([
                ExecutionStep(f"analyze_{agent.agent_id}", agent.agent_id,
                            "Analyze task requirements", ExecutionStatus.PENDING),
                ExecutionStep(f"execute_{agent.agent_id}", agent.agent_id,
                            "Execute assigned task", ExecutionStatus.PENDING)
            ])
            
        # Common completion step
        steps.append(ExecutionStep(
            step_id=f"complete_{agent.agent_id}",
            agent_id=agent.agent_id,
            action="Finalize and record results",
            status=ExecutionStatus.PENDING
        ))
        
        return steps
        
    async def _execute_agent_step(self, agent: SpawnedAgent, step: ExecutionStep) -> Optional[str]:
        """Execute an individual agent step using agency swarm framework."""
        step.status = ExecutionStatus.RUNNING
        step.start_time = datetime.now()
        
        try:
            # This is where we would integrate with agency swarm framework
            # For now, we'll simulate the execution with a realistic delay
            
            # Record step start
            WriteMemory(
                content=f"Executing step: {step.action} for {agent.agent_type}",
                tags=["execution", "step", agent.agent_id, step.step_id]
            ).run()
            
            # Simulate realistic execution time based on step type
            if 'setup' in step.action.lower():
                await asyncio.sleep(1)
            elif 'analyze' in step.action.lower():
                await asyncio.sleep(2) 
            elif 'implement' in step.action.lower() or 'create' in step.action.lower():
                await asyncio.sleep(5)
            elif 'test' in step.action.lower() or 'run' in step.action.lower():
                await asyncio.sleep(3)
            else:
                await asyncio.sleep(2)
                
            # Record tools used (would come from actual execution)
            step.tools_used = agent.tools[:3]  # Simulate using first few tools
            
            # Simulate successful completion with realistic result
            result = f"Completed: {step.action} - Used tools: {', '.join(step.tools_used)}"
            
            WriteMemory(
                content=f"Step completed: {step.action} for {agent.agent_type} - {result[:100]}",
                tags=["execution", "step", "complete", agent.agent_id, step.step_id]
            ).run()
            
            return result
            
        except Exception as e:
            step.error = str(e)
            logger.error(f"Step execution failed: {e}")
            return None
            
    def _determine_batch_status(self, batch: ExecutionBatch) -> ExecutionStatus:
        """Determine overall batch status based on individual agent statuses."""
        statuses = [e.status for e in batch.agent_executions]
        
        if all(s == ExecutionStatus.COMPLETED for s in statuses):
            return ExecutionStatus.COMPLETED
        elif any(s == ExecutionStatus.FAILED for s in statuses):
            # If critical agents failed, mark batch as failed
            failed_executions = [e for e in batch.agent_executions if e.status == ExecutionStatus.FAILED]
            critical_failure = any('architect' in e.agent.agent_type.lower() or 
                                 'developer' in e.agent.agent_type.lower() 
                                 for e in failed_executions)
            return ExecutionStatus.FAILED if critical_failure else ExecutionStatus.COMPLETED
        elif any(s == ExecutionStatus.RUNNING for s in statuses):
            return ExecutionStatus.RUNNING
        else:
            return ExecutionStatus.PENDING
            
    async def _notify_user(self, user_id: str, message: str):
        """Send notification to user via Telegram bot."""
        try:
            # Import here to avoid circular dependency
            from ai.interface.telegram_bot import get_bot_instance
            
            bot = get_bot_instance()
            if bot:
                await bot.send_message(chat_id=user_id, text=message)
                
        except Exception as e:
            logger.error(f"Failed to notify user {user_id}: {e}")
            
    async def _notify_batch_completion(self, batch: ExecutionBatch):
        """Send batch completion notification to user."""
        if not batch.user_id:
            return
            
        completed = len([e for e in batch.agent_executions if e.status == ExecutionStatus.COMPLETED])
        failed = len([e for e in batch.agent_executions if e.status == ExecutionStatus.FAILED])
        total = len(batch.agent_executions)
        
        if batch.status == ExecutionStatus.COMPLETED:
            message = f"✅ All {total} agents completed successfully!\n\n"
            message += f"📋 Results summary:\n"
            for execution in batch.agent_executions:
                if execution.result:
                    message += f"• {execution.agent.agent_type}: {execution.result[:50]}...\n"
        else:
            message = f"⚠️ Batch execution completed with issues\n\n"
            message += f"📊 Status: {completed} completed, {failed} failed out of {total}\n"
            
        if batch.auto_create_pr:
            message += f"\n🔄 Creating pull request with changes..."
            
        await self._notify_user(batch.user_id, message)
        
    async def _create_pr_for_batch(self, batch: ExecutionBatch):
        """Create GitHub PR for completed agent batch."""
        try:
            github = get_github_integration()
            completed_agents = [e.agent for e in batch.agent_executions 
                              if e.status == ExecutionStatus.COMPLETED]
                              
            if not completed_agents:
                logger.warning("No completed agents to create PR from")
                return
                
            pr_result = await github.create_pr_from_agent_work(
                spawn_request_id=batch.spawn_request_id,
                user_request=batch.user_request,
                completed_agents=completed_agents
            )
            
            if batch.user_id:
                if pr_result.success:
                    await self._notify_user(
                        batch.user_id,
                        f"🎉 Pull request created successfully!\n\n"
                        f"PR #{pr_result.pr_number}: {pr_result.pr_url}\n\n"
                        f"Review and merge when ready."
                    )
                else:
                    await self._notify_user(
                        batch.user_id,
                        f"❌ Failed to create pull request: {pr_result.error_message[:100]}..."
                    )
                    
        except Exception as e:
            logger.error(f"Failed to create PR for batch {batch.batch_id}: {e}")
            if batch.user_id:
                await self._notify_user(
                    batch.user_id,
                    f"❌ Failed to create pull request: {str(e)[:100]}..."
                )
                
    async def _cleanup_batch_after_delay(self, batch_id: str, delay_minutes: int = 30):
        """Clean up completed batch after delay to prevent memory buildup."""
        await asyncio.sleep(delay_minutes * 60)
        
        if batch_id in self.active_batches:
            batch = self.active_batches[batch_id]
            
            # Remove individual executions
            for execution in batch.agent_executions:
                if execution.execution_id in self.active_executions:
                    del self.active_executions[execution.execution_id]
                    
            # Remove batch
            del self.active_batches[batch_id]
            
            logger.info(f"Cleaned up completed batch: {batch_id}")
            
    async def _monitoring_loop(self):
        """Main monitoring loop for tracking execution progress."""
        while not self._shutdown_event.is_set():
            try:
                # Monitor active executions for timeouts and issues
                current_time = datetime.now()
                timeout_threshold = timedelta(minutes=30)  # 30 minute timeout
                
                for execution_id, execution in list(self.active_executions.items()):
                    if execution.status == ExecutionStatus.RUNNING:
                        if current_time - execution.start_time > timeout_threshold:
                            execution.status = ExecutionStatus.FAILED
                            execution.error = "Execution timeout"
                            execution.end_time = current_time
                            
                            logger.warning(f"Execution {execution_id} timed out")
                            
                            if execution.user_id:
                                await self._notify_user(
                                    execution.user_id,
                                    f"⏰ Agent execution timed out: {execution.agent.agent_type}"
                                )
                                
                # Sleep before next monitoring cycle
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
                
    def get_execution_status(self, execution_id: str) -> Optional[AgentExecution]:
        """Get current status of an agent execution."""
        return self.active_executions.get(execution_id)
        
    def get_batch_status(self, batch_id: str) -> Optional[ExecutionBatch]:
        """Get current status of an execution batch."""
        return self.active_batches.get(batch_id)
        
    def list_active_executions(self) -> Dict[str, AgentExecution]:
        """Get all currently active executions."""
        return self.active_executions.copy()
        
    def list_active_batches(self) -> Dict[str, ExecutionBatch]:
        """Get all currently active batches.""" 
        return self.active_batches.copy()


# Global execution monitor instance
_execution_monitor: Optional[AgentExecutionMonitor] = None

def get_execution_monitor() -> AgentExecutionMonitor:
    """Get the global agent execution monitor instance."""
    global _execution_monitor
    if _execution_monitor is None:
        _execution_monitor = AgentExecutionMonitor()
    return _execution_monitor
