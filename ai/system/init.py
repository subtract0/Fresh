"""Fresh Agent System Initialization and Coordination.

This module provides comprehensive initialization and coordination for all
agent system components, ensuring proper startup order, dependency resolution,
and graceful shutdown handling.

Cross-references:
    - Agent Spawner: ai/interface/agent_spawner.py for agent lifecycle
    - Execution Monitor: ai/execution/monitor.py for real-time execution
    - Status Coordinator: ai/coordination/status.py for status updates
    - GitHub Integration: ai/integration/github.py for PR automation
    - Performance Analytics: ai/analytics/performance.py for optimization
    - Telegram Bot: ai/interface/telegram_bot.py for user interface

Related:
    - System startup and shutdown coordination
    - Health monitoring and status checks
    - Configuration management and validation
    - Error recovery and graceful degradation
"""
from __future__ import annotations
import os
import asyncio
import logging
import signal
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path
import json

from ai.memory.store import get_store
from ai.tools.memory_tools import WriteMemory

logger = logging.getLogger(__name__)


@dataclass
class SystemComponent:
    """Represents a system component with its lifecycle management."""
    name: str
    instance: Any
    start_method: Optional[str] = None
    stop_method: Optional[str] = None
    health_check_method: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    status: str = "uninitialized"
    start_time: Optional[datetime] = None
    error_count: int = 0
    last_error: Optional[str] = None


@dataclass
class SystemStatus:
    """Overall system status information."""
    overall_health: str  # healthy, degraded, critical
    components: Dict[str, str]  # component_name -> status
    uptime_seconds: float
    active_agents: int
    active_executions: int
    recent_errors: List[str]
    performance_metrics: Dict[str, Any]


class FreshAgentSystem:
    """Coordinates initialization and lifecycle of all agent system components."""
    
    def __init__(self):
        self.components: Dict[str, SystemComponent] = {}
        self.start_time = datetime.now()
        self.shutdown_handlers: List[Callable] = []
        self.health_check_interval = 30  # seconds
        self._health_check_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()
        
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            asyncio.create_task(self.shutdown())
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    async def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize all system components in dependency order."""
        logger.info("Initializing Fresh Agent System...")
        
        config = config or {}
        
        try:
            # Record system initialization
            WriteMemory(
                content=f"Fresh Agent System initialization started at {datetime.now()}",
                tags=["system", "init", "startup"]
            ).run()
            
            # Initialize components in dependency order
            await self._register_components(config)
            await self._start_components()
            await self._verify_system_health()
            
            # Start health monitoring
            self._health_check_task = asyncio.create_task(self._health_monitoring_loop())
            
            logger.info("Fresh Agent System initialization completed successfully")
            
            WriteMemory(
                content=f"Fresh Agent System fully initialized with {len(self.components)} components",
                tags=["system", "init", "success"]
            ).run()
            
            return True
            
        except Exception as e:
            logger.error(f"System initialization failed: {e}")
            
            WriteMemory(
                content=f"Fresh Agent System initialization failed: {str(e)}",
                tags=["system", "init", "failure", "error"]
            ).run()
            
            await self.shutdown()
            return False
            
    async def _register_components(self, config: Dict[str, Any]):
        """Register all system components with their dependencies."""
        
        # Memory store (base dependency)
        self.components["memory_store"] = SystemComponent(
            name="memory_store",
            instance=get_store(),
            dependencies=[]
        )
        
        # Performance analytics (independent)
        try:
            from ai.analytics.performance import get_performance_analytics
            self.components["performance_analytics"] = SystemComponent(
                name="performance_analytics",
                instance=get_performance_analytics(),
                dependencies=["memory_store"]
            )
        except ImportError:
            logger.warning("Performance analytics module not available")
            
        # Status coordinator
        try:
            from ai.coordination.status import get_status_coordinator
            self.components["status_coordinator"] = SystemComponent(
                name="status_coordinator",
                instance=get_status_coordinator(),
                start_method="start_coordination",
                stop_method="stop_coordination",
                dependencies=["memory_store"]
            )
        except ImportError:
            logger.warning("Status coordinator module not available")
            
        # Execution monitor
        try:
            from ai.execution.monitor import get_execution_monitor
            self.components["execution_monitor"] = SystemComponent(
                name="execution_monitor",
                instance=get_execution_monitor(),
                start_method="start_monitoring",
                stop_method="stop_monitoring",
                dependencies=["memory_store", "status_coordinator"]
            )
        except ImportError:
            logger.warning("Execution monitor module not available")
            
        # GitHub integration
        try:
            from ai.integration.github import get_github_integration
            github_instance = get_github_integration()
            if github_instance.is_configured():
                self.components["github_integration"] = SystemComponent(
                    name="github_integration",
                    instance=github_instance,
                    dependencies=["memory_store"]
                )
            else:
                logger.info("GitHub integration not configured - skipping")
        except ImportError:
            logger.warning("GitHub integration module not available")
            
        # Agent spawner
        try:
            from ai.interface.agent_spawner import get_agent_spawner
            self.components["agent_spawner"] = SystemComponent(
                name="agent_spawner",
                instance=get_agent_spawner(),
                dependencies=["memory_store", "execution_monitor", "status_coordinator"]
            )
        except ImportError:
            logger.warning("Agent spawner module not available")
            
        # Telegram bot (if configured)
        try:
            telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
            if telegram_token:
                from ai.interface.telegram_bot import get_bot_instance
                bot_instance = get_bot_instance()
                if bot_instance:
                    self.components["telegram_bot"] = SystemComponent(
                        name="telegram_bot",
                        instance=bot_instance,
                        start_method="start",
                        stop_method="stop",
                        dependencies=["memory_store", "agent_spawner"]
                    )
            else:
                logger.info("Telegram bot token not configured - skipping bot initialization")
        except ImportError:
            logger.warning("Telegram bot module not available")
            
    async def _start_components(self):
        """Start components in dependency order."""
        started_components = set()
        
        def can_start(component: SystemComponent) -> bool:
            return all(dep in started_components for dep in component.dependencies)
        
        # Keep trying to start components until all are started or we hit an error
        max_iterations = len(self.components) * 2  # Prevent infinite loops
        iteration = 0
        
        while len(started_components) < len(self.components) and iteration < max_iterations:
            iteration += 1
            made_progress = False
            
            for name, component in self.components.items():
                if name in started_components or not can_start(component):
                    continue
                    
                try:
                    await self._start_component(component)
                    started_components.add(name)
                    made_progress = True
                    
                except Exception as e:
                    logger.error(f"Failed to start component {name}: {e}")
                    component.status = "failed"
                    component.last_error = str(e)
                    component.error_count += 1
                    
                    # For critical components, fail the entire system
                    if name in ["memory_store", "agent_spawner"]:
                        raise
                        
            if not made_progress:
                unstarted = [name for name in self.components if name not in started_components]
                logger.error(f"Unable to start components due to dependency issues: {unstarted}")
                break
                
    async def _start_component(self, component: SystemComponent):
        """Start a single component."""
        logger.info(f"Starting component: {component.name}")
        
        try:
            if component.start_method and hasattr(component.instance, component.start_method):
                start_func = getattr(component.instance, component.start_method)
                if asyncio.iscoroutinefunction(start_func):
                    await start_func()
                else:
                    start_func()
                    
            component.status = "running"
            component.start_time = datetime.now()
            logger.info(f"Component {component.name} started successfully")
            
        except Exception as e:
            component.status = "failed"
            component.last_error = str(e)
            component.error_count += 1
            raise
            
    async def _verify_system_health(self):
        """Verify that all critical components are healthy."""
        logger.info("Verifying system health...")
        
        critical_components = ["memory_store", "agent_spawner"]
        
        for component_name in critical_components:
            if component_name not in self.components:
                raise RuntimeError(f"Critical component {component_name} not available")
                
            component = self.components[component_name]
            if component.status != "running":
                raise RuntimeError(f"Critical component {component_name} is not running: {component.status}")
                
        # Test basic functionality
        try:
            # Test memory system
            WriteMemory(
                content="System health check - memory system operational",
                tags=["system", "health", "test"]
            ).run()
            
        except Exception as e:
            raise RuntimeError(f"Memory system health check failed: {e}")
            
        logger.info("System health verification completed")
        
    async def _health_monitoring_loop(self):
        """Continuous health monitoring loop."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_checks()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(5)  # Brief pause before retry
                
    async def _perform_health_checks(self):
        """Perform health checks on all components."""
        for name, component in self.components.items():
            try:
                if (component.health_check_method and 
                    hasattr(component.instance, component.health_check_method)):
                    
                    health_func = getattr(component.instance, component.health_check_method)
                    if asyncio.iscoroutinefunction(health_func):
                        result = await health_func()
                    else:
                        result = health_func()
                        
                    if not result:
                        logger.warning(f"Component {name} failed health check")
                        component.status = "unhealthy"
                    elif component.status == "unhealthy":
                        component.status = "running"  # Recovery
                        
            except Exception as e:
                logger.error(f"Health check failed for {name}: {e}")
                component.error_count += 1
                component.last_error = str(e)
                
    async def get_system_status(self) -> SystemStatus:
        """Get comprehensive system status."""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        # Component statuses
        component_statuses = {
            name: comp.status for name, comp in self.components.items()
        }
        
        # Overall health assessment
        failed_components = [name for name, status in component_statuses.items() if status == "failed"]
        unhealthy_components = [name for name, status in component_statuses.items() if status == "unhealthy"]
        
        if failed_components:
            overall_health = "critical"
        elif unhealthy_components:
            overall_health = "degraded"
        else:
            overall_health = "healthy"
            
        # Collect recent errors
        recent_errors = []
        for component in self.components.values():
            if component.last_error:
                recent_errors.append(f"{component.name}: {component.last_error}")
                
        # Active agents and executions (if available)
        active_agents = 0
        active_executions = 0
        
        if "agent_spawner" in self.components:
            try:
                spawner = self.components["agent_spawner"].instance
                agents = await spawner.list_active_agents() if hasattr(spawner, 'list_active_agents') else []
                active_agents = len(agents)
            except Exception:
                pass
                
        if "execution_monitor" in self.components:
            try:
                monitor = self.components["execution_monitor"].instance
                executions = monitor.list_active_executions() if hasattr(monitor, 'list_active_executions') else {}
                active_executions = len(executions)
            except Exception:
                pass
                
        # Performance metrics (simplified)
        performance_metrics = {
            "uptime_seconds": uptime,
            "component_count": len(self.components),
            "error_count": sum(comp.error_count for comp in self.components.values())
        }
        
        return SystemStatus(
            overall_health=overall_health,
            components=component_statuses,
            uptime_seconds=uptime,
            active_agents=active_agents,
            active_executions=active_executions,
            recent_errors=recent_errors[-10:],  # Last 10 errors
            performance_metrics=performance_metrics
        )
        
    async def restart_component(self, component_name: str) -> bool:
        """Restart a specific component."""
        if component_name not in self.components:
            logger.error(f"Component {component_name} not found")
            return False
            
        component = self.components[component_name]
        
        try:
            logger.info(f"Restarting component: {component_name}")
            
            # Stop component
            if (component.stop_method and 
                hasattr(component.instance, component.stop_method)):
                stop_func = getattr(component.instance, component.stop_method)
                if asyncio.iscoroutinefunction(stop_func):
                    await stop_func()
                else:
                    stop_func()
                    
            # Start component
            await self._start_component(component)
            
            WriteMemory(
                content=f"Component {component_name} restarted successfully",
                tags=["system", "restart", "recovery", component_name]
            ).run()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to restart component {component_name}: {e}")
            
            WriteMemory(
                content=f"Failed to restart component {component_name}: {str(e)}",
                tags=["system", "restart", "failure", component_name]
            ).run()
            
            return False
            
    def add_shutdown_handler(self, handler: Callable):
        """Add a shutdown handler function."""
        self.shutdown_handlers.append(handler)
        
    async def shutdown(self):
        """Gracefully shutdown all system components."""
        logger.info("Initiating system shutdown...")
        
        self._shutdown_event.set()
        
        # Cancel health monitoring
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
                
        # Execute custom shutdown handlers
        for handler in self.shutdown_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
            except Exception as e:
                logger.error(f"Shutdown handler failed: {e}")
                
        # Stop components in reverse dependency order
        shutdown_order = self._determine_shutdown_order()
        
        for component_name in shutdown_order:
            if component_name not in self.components:
                continue
                
            component = self.components[component_name]
            
            try:
                if (component.stop_method and 
                    hasattr(component.instance, component.stop_method)):
                    stop_func = getattr(component.instance, component.stop_method)
                    if asyncio.iscoroutinefunction(stop_func):
                        await stop_func()
                    else:
                        stop_func()
                        
                component.status = "stopped"
                logger.info(f"Component {component_name} stopped")
                
            except Exception as e:
                logger.error(f"Error stopping component {component_name}: {e}")
                
        # Record shutdown
        try:
            WriteMemory(
                content=f"Fresh Agent System shutdown completed at {datetime.now()}",
                tags=["system", "shutdown", "complete"]
            ).run()
        except Exception:
            pass  # Memory system may already be stopped
            
        logger.info("System shutdown completed")
        
    def _determine_shutdown_order(self) -> List[str]:
        """Determine the order to shutdown components (reverse of startup order)."""
        # Simple reverse dependency order
        shutdown_order = []
        processed = set()
        
        def add_to_shutdown_order(component_name: str):
            if component_name in processed or component_name not in self.components:
                return
                
            component = self.components[component_name]
            
            # First, add components that depend on this one
            for name, comp in self.components.items():
                if component_name in comp.dependencies and name not in processed:
                    add_to_shutdown_order(name)
                    
            shutdown_order.append(component_name)
            processed.add(component_name)
            
        # Process all components
        for component_name in self.components:
            add_to_shutdown_order(component_name)
            
        return shutdown_order


# Global system instance
_system_instance: Optional[FreshAgentSystem] = None

def get_system() -> FreshAgentSystem:
    """Get the global Fresh Agent System instance."""
    global _system_instance
    if _system_instance is None:
        _system_instance = FreshAgentSystem()
    return _system_instance


async def initialize_system(config: Optional[Dict[str, Any]] = None) -> bool:
    """Initialize the Fresh Agent System with optional configuration."""
    system = get_system()
    return await system.initialize(config)


async def shutdown_system():
    """Shutdown the Fresh Agent System gracefully."""
    system = get_system()
    await system.shutdown()


async def get_status() -> SystemStatus:
    """Get current system status."""
    system = get_system()
    return await system.get_system_status()

