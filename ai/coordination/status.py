"""Enhanced status update system for real-time agent coordination.

This module provides comprehensive status tracking and real-time updates
for agent coordination, including progress tracking, dependency management,
and user notification integration.

Cross-references:
    - Execution Monitor: ai/execution/monitor.py for execution status
    - Telegram Bot: ai/interface/telegram_bot.py for user notifications
    - Memory System: ai/memory/README.md for status persistence
    - Agent Spawner: ai/interface/agent_spawner.py for agent lifecycle

Related:
    - Real-time progress tracking across agent teams
    - Dependency resolution and coordination messaging
    - Status aggregation and reporting for complex workflows
"""
from __future__ import annotations
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import threading
from collections import defaultdict, deque

from ai.memory.store import get_store
from ai.tools.memory_tools import WriteMemory, ReadMemoryContext
from ai.execution.monitor import ExecutionStatus, AgentExecution, ExecutionBatch

logger = logging.getLogger(__name__)


class StatusLevel(Enum):
    """Status update severity levels."""
    DEBUG = "debug"
    INFO = "info" 
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class UpdateType(Enum):
    """Types of status updates."""
    PROGRESS = "progress"
    MILESTONE = "milestone"
    DEPENDENCY = "dependency"
    ERROR = "error"
    COMPLETION = "completion"
    USER_NOTIFICATION = "user_notification"


@dataclass
class StatusUpdate:
    """Individual status update record."""
    update_id: str
    timestamp: datetime
    source_id: str  # Agent ID, batch ID, etc.
    update_type: UpdateType
    level: StatusLevel
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    progress_percentage: Optional[float] = None
    dependencies: List[str] = field(default_factory=list)
    affected_agents: List[str] = field(default_factory=list)
    user_visible: bool = False
    requires_action: bool = False


@dataclass
class CoordinationContext:
    """Context for coordinating related status updates."""
    context_id: str
    spawn_request_id: str
    related_agents: Set[str] = field(default_factory=set)
    dependency_graph: Dict[str, List[str]] = field(default_factory=dict)
    milestones: Dict[str, bool] = field(default_factory=dict)
    coordination_log: deque = field(default_factory=lambda: deque(maxlen=100))
    user_id: Optional[str] = None
    last_user_update: Optional[datetime] = None
    update_frequency: timedelta = field(default_factory=lambda: timedelta(minutes=2))


@dataclass
class StatusSummary:
    """Aggregated status summary for reporting."""
    context_id: str
    overall_progress: float
    phase_status: Dict[str, str]
    active_agents: int
    completed_agents: int
    failed_agents: int
    recent_updates: List[StatusUpdate]
    next_milestones: List[str]
    estimated_completion: Optional[datetime]
    blocking_dependencies: List[str]


class StatusCoordinator:
    """Coordinates status updates and notifications across agent teams."""
    
    def __init__(self):
        self.contexts: Dict[str, CoordinationContext] = {}
        self.status_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.update_subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.notification_queue: asyncio.Queue = asyncio.Queue()
        self._processing_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
    async def start_coordination(self):
        """Start the status coordination system."""
        if self._processing_task is not None:
            logger.warning("Status coordination already started")
            return
            
        logger.info("Starting status coordination system")
        self._processing_task = asyncio.create_task(self._process_notifications())
        
    async def stop_coordination(self):
        """Stop the status coordination system."""
        if self._processing_task is None:
            logger.warning("Status coordination not started")
            return
            
        logger.info("Stopping status coordination system")
        self._shutdown_event.set()
        
        try:
            await asyncio.wait_for(self._processing_task, timeout=5.0)
        except asyncio.TimeoutError:
            logger.warning("Processing task did not complete within timeout")
            self._processing_task.cancel()
            
        self._processing_task = None
        self._shutdown_event.clear()
        
    def register_context(
        self,
        context_id: str,
        spawn_request_id: str,
        agent_ids: List[str],
        user_id: Optional[str] = None,
        dependency_graph: Optional[Dict[str, List[str]]] = None
    ) -> CoordinationContext:
        """Register a new coordination context for status tracking."""
        context = CoordinationContext(
            context_id=context_id,
            spawn_request_id=spawn_request_id,
            related_agents=set(agent_ids),
            dependency_graph=dependency_graph or {},
            user_id=user_id
        )
        
        # Define standard milestones based on agent types
        context.milestones = self._generate_standard_milestones(agent_ids)
        
        self.contexts[context_id] = context
        
        # Record context registration
        WriteMemory(
            content=f"Registered status coordination context: {context_id} with {len(agent_ids)} agents",
            tags=["coordination", "context", "register", spawn_request_id]
        ).run()
        
        return context
        
    async def update_status(
        self,
        context_id: str,
        source_id: str,
        update_type: UpdateType,
        message: str,
        level: StatusLevel = StatusLevel.INFO,
        progress: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
        user_visible: bool = False,
        dependencies: Optional[List[str]] = None
    ) -> str:
        """Add a status update and coordinate notifications."""
        update_id = f"update_{context_id}_{int(datetime.now().timestamp() * 1000)}"
        
        update = StatusUpdate(
            update_id=update_id,
            timestamp=datetime.now(),
            source_id=source_id,
            update_type=update_type,
            level=level,
            message=message,
            details=details or {},
            progress_percentage=progress,
            dependencies=dependencies or [],
            user_visible=user_visible
        )
        
        # Add to history
        self.status_history[context_id].append(update)
        
        # Update coordination context
        if context_id in self.contexts:
            context = self.contexts[context_id]
            context.coordination_log.append(update)
            
            # Check for milestone completion
            await self._check_milestones(context, update)
            
            # Resolve dependencies
            await self._resolve_dependencies(context, update)
            
            # Queue for user notification if needed
            if user_visible or self._should_notify_user(context, update):
                await self.notification_queue.put((context, update))
                
        # Notify subscribers
        for callback in self.update_subscribers.get(context_id, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(update)
                else:
                    callback(update)
            except Exception as e:
                logger.error(f"Error in status update callback: {e}")
                
        # Record in memory system for persistence
        WriteMemory(
            content=f"Status update: {source_id} - {message[:100]}",
            tags=["status", "update", context_id, source_id, level.value]
        ).run()
        
        return update_id
        
    async def update_agent_progress(
        self,
        context_id: str,
        agent_id: str,
        step_name: str,
        progress: float,
        details: Optional[str] = None
    ):
        """Update progress for a specific agent and step."""
        message = f"{step_name}: {progress:.1f}% complete"
        if details:
            message += f" - {details}"
            
        await self.update_status(
            context_id=context_id,
            source_id=agent_id,
            update_type=UpdateType.PROGRESS,
            message=message,
            progress=progress,
            user_visible=(progress % 25 == 0)  # Notify on quarter milestones
        )
        
    async def report_milestone(
        self,
        context_id: str,
        milestone_name: str,
        agent_id: str,
        success: bool = True,
        details: Optional[str] = None
    ):
        """Report completion of a milestone."""
        status = "completed" if success else "failed"
        message = f"Milestone '{milestone_name}' {status}"
        if details:
            message += f": {details}"
            
        await self.update_status(
            context_id=context_id,
            source_id=agent_id,
            update_type=UpdateType.MILESTONE,
            message=message,
            level=StatusLevel.INFO if success else StatusLevel.ERROR,
            user_visible=True
        )
        
        # Update milestone tracking
        if context_id in self.contexts:
            self.contexts[context_id].milestones[milestone_name] = success
            
    async def report_dependency_issue(
        self,
        context_id: str,
        agent_id: str,
        blocked_by: List[str],
        issue_description: str
    ):
        """Report a dependency blocking issue."""
        message = f"Blocked by dependencies: {', '.join(blocked_by)} - {issue_description}"
        
        await self.update_status(
            context_id=context_id,
            source_id=agent_id,
            update_type=UpdateType.DEPENDENCY,
            message=message,
            level=StatusLevel.WARNING,
            dependencies=blocked_by,
            user_visible=True
        )
        
    async def get_status_summary(self, context_id: str) -> Optional[StatusSummary]:
        """Get an aggregated status summary for a coordination context."""
        if context_id not in self.contexts:
            return None
            
        context = self.contexts[context_id]
        updates = list(self.status_history[context_id])
        
        # Calculate overall progress
        progress_updates = [u for u in updates if u.progress_percentage is not None]
        overall_progress = 0.0
        if progress_updates:
            # Weight recent updates more heavily
            weights = [min(1.0, 1.0 / ((datetime.now() - u.timestamp).seconds / 60 + 1)) 
                      for u in progress_updates]
            weighted_sum = sum(p.progress_percentage * w for p, w in zip(progress_updates, weights))
            weight_sum = sum(weights)
            overall_progress = weighted_sum / weight_sum if weight_sum > 0 else 0.0
            
        # Analyze agent status
        agent_statuses = self._analyze_agent_statuses(updates, context.related_agents)
        
        # Get recent important updates
        recent_updates = [u for u in updates[-10:] if u.user_visible or u.level.value in ["warning", "error"]]
        
        # Identify blocking dependencies
        blocking_deps = self._identify_blocking_dependencies(context, updates)
        
        # Estimate completion time
        estimated_completion = self._estimate_completion(context, updates)
        
        return StatusSummary(
            context_id=context_id,
            overall_progress=overall_progress,
            phase_status=self._get_phase_status(context),
            active_agents=agent_statuses["active"],
            completed_agents=agent_statuses["completed"],
            failed_agents=agent_statuses["failed"],
            recent_updates=recent_updates,
            next_milestones=self._get_next_milestones(context),
            estimated_completion=estimated_completion,
            blocking_dependencies=blocking_deps
        )
        
    def subscribe_to_updates(self, context_id: str, callback: Callable):
        """Subscribe to status updates for a specific context."""
        self.update_subscribers[context_id].append(callback)
        
    def unsubscribe_from_updates(self, context_id: str, callback: Callable):
        """Unsubscribe from status updates."""
        if context_id in self.update_subscribers:
            try:
                self.update_subscribers[context_id].remove(callback)
            except ValueError:
                pass
                
    def _generate_standard_milestones(self, agent_ids: List[str]) -> Dict[str, bool]:
        """Generate standard milestones based on agent types."""
        milestones = {
            "initialization_complete": False,
            "planning_complete": False,
            "implementation_started": False,
            "testing_started": False,
            "all_agents_complete": False
        }
        
        # Add agent-specific milestones
        for agent_id in agent_ids:
            milestones[f"{agent_id}_complete"] = False
            
        return milestones
        
    async def _check_milestones(self, context: CoordinationContext, update: StatusUpdate):
        """Check if the update indicates milestone completion."""
        # Auto-detect milestone completion based on update content
        message_lower = update.message.lower()
        
        if "initialization" in message_lower and "complete" in message_lower:
            context.milestones["initialization_complete"] = True
            
        elif "planning" in message_lower and "complete" in message_lower:
            context.milestones["planning_complete"] = True
            
        elif update.update_type == UpdateType.COMPLETION:
            # Mark agent-specific completion
            agent_milestone = f"{update.source_id}_complete"
            if agent_milestone in context.milestones:
                context.milestones[agent_milestone] = True
                
            # Check if all agents are complete
            all_complete = all(context.milestones.get(f"{agent_id}_complete", False) 
                             for agent_id in context.related_agents)
            if all_complete:
                context.milestones["all_agents_complete"] = True
                
    async def _resolve_dependencies(self, context: CoordinationContext, update: StatusUpdate):
        """Check and resolve dependencies based on the update."""
        if update.update_type != UpdateType.COMPLETION:
            return
            
        completed_agent = update.source_id
        
        # Check what dependencies this completion resolves
        for agent_id, deps in context.dependency_graph.items():
            if completed_agent in deps:
                # Remove resolved dependency
                deps.remove(completed_agent)
                
                # Notify if all dependencies are now resolved
                if not deps:
                    await self.update_status(
                        context_id=context.context_id,
                        source_id=agent_id,
                        update_type=UpdateType.DEPENDENCY,
                        message=f"All dependencies resolved, ready to proceed",
                        level=StatusLevel.INFO,
                        user_visible=True
                    )
                    
    def _should_notify_user(self, context: CoordinationContext, update: StatusUpdate) -> bool:
        """Determine if user should be notified about this update."""
        if not context.user_id:
            return False
            
        # Always notify for errors and critical issues
        if update.level in [StatusLevel.ERROR, StatusLevel.CRITICAL]:
            return True
            
        # Throttle routine updates based on frequency setting
        if context.last_user_update:
            time_since_last = datetime.now() - context.last_user_update
            if time_since_last < context.update_frequency:
                return False
                
        # Notify for milestones and significant progress
        if update.update_type in [UpdateType.MILESTONE, UpdateType.COMPLETION]:
            return True
            
        # Notify for significant progress jumps
        if (update.progress_percentage is not None and 
            update.progress_percentage > 0 and 
            update.progress_percentage % 25 == 0):
            return True
            
        return False
        
    async def _process_notifications(self):
        """Process queued notifications for users."""
        while not self._shutdown_event.is_set():
            try:
                # Wait for notification with timeout
                try:
                    context, update = await asyncio.wait_for(
                        self.notification_queue.get(), timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                    
                # Send notification to user
                if context.user_id:
                    await self._send_user_notification(context, update)
                    context.last_user_update = datetime.now()
                    
            except Exception as e:
                logger.error(f"Error processing notifications: {e}")
                await asyncio.sleep(1)
                
    async def _send_user_notification(self, context: CoordinationContext, update: StatusUpdate):
        """Send notification to user via Telegram."""
        try:
            from ai.interface.telegram_bot import get_bot_instance
            
            bot = get_bot_instance()
            if not bot:
                return
                
            # Format message based on update type
            if update.update_type == UpdateType.PROGRESS:
                emoji = "⚡"
            elif update.update_type == UpdateType.MILESTONE:
                emoji = "🎯"
            elif update.update_type == UpdateType.COMPLETION:
                emoji = "✅"
            elif update.level == StatusLevel.ERROR:
                emoji = "❌"
            elif update.level == StatusLevel.WARNING:
                emoji = "⚠️"
            else:
                emoji = "ℹ️"
                
            message = f"{emoji} {update.message}"
            
            # Add progress info if available
            if update.progress_percentage is not None:
                progress_bar = self._create_progress_bar(update.progress_percentage)
                message += f"\n\n{progress_bar} {update.progress_percentage:.1f}%"
                
            await bot.send_message(chat_id=context.user_id, text=message)
            
        except Exception as e:
            logger.error(f"Failed to send user notification: {e}")
            
    def _create_progress_bar(self, percentage: float, length: int = 10) -> str:
        """Create a visual progress bar."""
        filled = int(percentage / 100 * length)
        bar = "█" * filled + "░" * (length - filled)
        return f"[{bar}]"
        
    def _analyze_agent_statuses(self, updates: List[StatusUpdate], agent_ids: Set[str]) -> Dict[str, int]:
        """Analyze current status of all agents."""
        agent_statuses = {agent_id: "unknown" for agent_id in agent_ids}
        
        for update in reversed(updates):  # Most recent first
            if update.source_id in agent_ids:
                if update.update_type == UpdateType.COMPLETION:
                    agent_statuses[update.source_id] = "completed"
                elif update.level == StatusLevel.ERROR:
                    agent_statuses[update.source_id] = "failed"
                elif update.progress_percentage is not None and update.progress_percentage > 0:
                    agent_statuses[update.source_id] = "active"
                    
        # Count statuses
        return {
            "active": sum(1 for s in agent_statuses.values() if s == "active"),
            "completed": sum(1 for s in agent_statuses.values() if s == "completed"),
            "failed": sum(1 for s in agent_statuses.values() if s == "failed"),
            "unknown": sum(1 for s in agent_statuses.values() if s == "unknown")
        }
        
    def _get_phase_status(self, context: CoordinationContext) -> Dict[str, str]:
        """Get status of different execution phases."""
        phases = {
            "Planning": "completed" if context.milestones.get("planning_complete") else "pending",
            "Implementation": "active" if context.milestones.get("implementation_started") else "pending",
            "Testing": "active" if context.milestones.get("testing_started") else "pending",
            "Completion": "completed" if context.milestones.get("all_agents_complete") else "pending"
        }
        
        return phases
        
    def _get_next_milestones(self, context: CoordinationContext) -> List[str]:
        """Get the next milestones that are not yet completed."""
        return [name for name, completed in context.milestones.items() if not completed][:3]
        
    def _identify_blocking_dependencies(
        self, 
        context: CoordinationContext, 
        updates: List[StatusUpdate]
    ) -> List[str]:
        """Identify dependencies that are currently blocking progress."""
        blocking = []
        
        for agent_id, deps in context.dependency_graph.items():
            if deps:  # Has unresolved dependencies
                # Check if agent is trying to proceed
                recent_updates = [u for u in updates[-10:] if u.source_id == agent_id]
                if recent_updates:
                    blocking.extend([f"{agent_id} blocked by {', '.join(deps)}"])
                    
        return blocking
        
    def _estimate_completion(
        self, 
        context: CoordinationContext, 
        updates: List[StatusUpdate]
    ) -> Optional[datetime]:
        """Estimate completion time based on progress velocity."""
        progress_updates = [u for u in updates if u.progress_percentage is not None]
        
        if len(progress_updates) < 2:
            return None
            
        # Calculate progress velocity (percentage per minute)
        recent_updates = progress_updates[-5:]  # Use last 5 progress updates
        
        if len(recent_updates) < 2:
            return None
            
        time_diff = (recent_updates[-1].timestamp - recent_updates[0].timestamp).total_seconds() / 60
        progress_diff = recent_updates[-1].progress_percentage - recent_updates[0].progress_percentage
        
        if time_diff <= 0 or progress_diff <= 0:
            return None
            
        velocity = progress_diff / time_diff  # percentage per minute
        current_progress = recent_updates[-1].progress_percentage
        remaining_progress = 100 - current_progress
        
        if velocity > 0:
            minutes_remaining = remaining_progress / velocity
            return datetime.now() + timedelta(minutes=minutes_remaining)
            
        return None


# Global status coordinator instance
_status_coordinator: Optional[StatusCoordinator] = None

def get_status_coordinator() -> StatusCoordinator:
    """Get the global status coordinator instance."""
    global _status_coordinator
    if _status_coordinator is None:
        _status_coordinator = StatusCoordinator()
    return _status_coordinator
