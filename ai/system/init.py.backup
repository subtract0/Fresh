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
                    \n                try:\n                    await self._start_component(component)\n                    started_components.add(name)\n                    made_progress = True\n                    \n                except Exception as e:\n                    logger.error(f\"Failed to start component {name}: {e}\")\n                    component.status = \"failed\"\n                    component.last_error = str(e)\n                    component.error_count += 1\n                    \n                    # For critical components, fail the entire system\n                    if name in [\"memory_store\", \"agent_spawner\"]:\n                        raise\n                        \n            if not made_progress:\n                unstarted = [name for name in self.components if name not in started_components]\n                logger.error(f\"Unable to start components due to dependency issues: {unstarted}\")\n                break\n                \n    async def _start_component(self, component: SystemComponent):\n        \"\"\"Start a single component.\"\"\"\n        logger.info(f\"Starting component: {component.name}\")\n        \n        try:\n            if component.start_method and hasattr(component.instance, component.start_method):\n                start_func = getattr(component.instance, component.start_method)\n                if asyncio.iscoroutinefunction(start_func):\n                    await start_func()\n                else:\n                    start_func()\n                    \n            component.status = \"running\"\n            component.start_time = datetime.now()\n            logger.info(f\"Component {component.name} started successfully\")\n            \n        except Exception as e:\n            component.status = \"failed\"\n            component.last_error = str(e)\n            component.error_count += 1\n            raise\n            \n    async def _verify_system_health(self):\n        \"\"\"Verify that all critical components are healthy.\"\"\"\n        logger.info(\"Verifying system health...\")\n        \n        critical_components = [\"memory_store\", \"agent_spawner\"]\n        \n        for component_name in critical_components:\n            if component_name not in self.components:\n                raise RuntimeError(f\"Critical component {component_name} not available\")\n                \n            component = self.components[component_name]\n            if component.status != \"running\":\n                raise RuntimeError(f\"Critical component {component_name} is not running: {component.status}\")\n                \n        # Test basic functionality\n        try:\n            # Test memory system\n            WriteMemory(\n                content=\"System health check - memory system operational\",\n                tags=[\"system\", \"health\", \"test\"]\n            ).run()\n            \n        except Exception as e:\n            raise RuntimeError(f\"Memory system health check failed: {e}\")\n            \n        logger.info(\"System health verification completed\")\n        \n    async def _health_monitoring_loop(self):\n        \"\"\"Continuous health monitoring loop.\"\"\"\n        while not self._shutdown_event.is_set():\n            try:\n                await asyncio.sleep(self.health_check_interval)\n                await self._perform_health_checks()\n                \n            except asyncio.CancelledError:\n                break\n            except Exception as e:\n                logger.error(f\"Health monitoring error: {e}\")\n                await asyncio.sleep(5)  # Brief pause before retry\n                \n    async def _perform_health_checks(self):\n        \"\"\"Perform health checks on all components.\"\"\"\n        for name, component in self.components.items():\n            try:\n                if (component.health_check_method and \n                    hasattr(component.instance, component.health_check_method)):\n                    \n                    health_func = getattr(component.instance, component.health_check_method)\n                    if asyncio.iscoroutinefunction(health_func):\n                        result = await health_func()\n                    else:\n                        result = health_func()\n                        \n                    if not result:\n                        logger.warning(f\"Component {name} failed health check\")\n                        component.status = \"unhealthy\"\n                    elif component.status == \"unhealthy\":\n                        component.status = \"running\"  # Recovery\n                        \n            except Exception as e:\n                logger.error(f\"Health check failed for {name}: {e}\")\n                component.error_count += 1\n                component.last_error = str(e)\n                \n    async def get_system_status(self) -> SystemStatus:\n        \"\"\"Get comprehensive system status.\"\"\"\n        uptime = (datetime.now() - self.start_time).total_seconds()\n        \n        # Component statuses\n        component_statuses = {\n            name: comp.status for name, comp in self.components.items()\n        }\n        \n        # Overall health assessment\n        failed_components = [name for name, status in component_statuses.items() if status == \"failed\"]\n        unhealthy_components = [name for name, status in component_statuses.items() if status == \"unhealthy\"]\n        \n        if failed_components:\n            overall_health = \"critical\"\n        elif unhealthy_components:\n            overall_health = \"degraded\"\n        else:\n            overall_health = \"healthy\"\n            \n        # Collect recent errors\n        recent_errors = []\n        for component in self.components.values():\n            if component.last_error:\n                recent_errors.append(f\"{component.name}: {component.last_error}\")\n                \n        # Active agents and executions (if available)\n        active_agents = 0\n        active_executions = 0\n        \n        if \"agent_spawner\" in self.components:\n            try:\n                spawner = self.components[\"agent_spawner\"].instance\n                agents = await spawner.list_active_agents() if hasattr(spawner, 'list_active_agents') else []\n                active_agents = len(agents)\n            except Exception:\n                pass\n                \n        if \"execution_monitor\" in self.components:\n            try:\n                monitor = self.components[\"execution_monitor\"].instance\n                executions = monitor.list_active_executions() if hasattr(monitor, 'list_active_executions') else {}\n                active_executions = len(executions)\n            except Exception:\n                pass\n                \n        # Performance metrics (simplified)\n        performance_metrics = {\n            \"uptime_seconds\": uptime,\n            \"component_count\": len(self.components),\n            \"error_count\": sum(comp.error_count for comp in self.components.values())\n        }\n        \n        return SystemStatus(\n            overall_health=overall_health,\n            components=component_statuses,\n            uptime_seconds=uptime,\n            active_agents=active_agents,\n            active_executions=active_executions,\n            recent_errors=recent_errors[-10:],  # Last 10 errors\n            performance_metrics=performance_metrics\n        )\n        \n    async def restart_component(self, component_name: str) -> bool:\n        \"\"\"Restart a specific component.\"\"\"\n        if component_name not in self.components:\n            logger.error(f\"Component {component_name} not found\")\n            return False\n            \n        component = self.components[component_name]\n        \n        try:\n            logger.info(f\"Restarting component: {component_name}\")\n            \n            # Stop component\n            if (component.stop_method and \n                hasattr(component.instance, component.stop_method)):\n                stop_func = getattr(component.instance, component.stop_method)\n                if asyncio.iscoroutinefunction(stop_func):\n                    await stop_func()\n                else:\n                    stop_func()\n                    \n            # Start component\n            await self._start_component(component)\n            \n            WriteMemory(\n                content=f\"Component {component_name} restarted successfully\",\n                tags=[\"system\", \"restart\", \"recovery\", component_name]\n            ).run()\n            \n            return True\n            \n        except Exception as e:\n            logger.error(f\"Failed to restart component {component_name}: {e}\")\n            \n            WriteMemory(\n                content=f\"Failed to restart component {component_name}: {str(e)}\",\n                tags=[\"system\", \"restart\", \"failure\", component_name]\n            ).run()\n            \n            return False\n            \n    def add_shutdown_handler(self, handler: Callable):\n        \"\"\"Add a shutdown handler function.\"\"\"\n        self.shutdown_handlers.append(handler)\n        \n    async def shutdown(self):\n        \"\"\"Gracefully shutdown all system components.\"\"\"\n        logger.info(\"Initiating system shutdown...\")\n        \n        self._shutdown_event.set()\n        \n        # Cancel health monitoring\n        if self._health_check_task:\n            self._health_check_task.cancel()\n            try:\n                await self._health_check_task\n            except asyncio.CancelledError:\n                pass\n                \n        # Execute custom shutdown handlers\n        for handler in self.shutdown_handlers:\n            try:\n                if asyncio.iscoroutinefunction(handler):\n                    await handler()\n                else:\n                    handler()\n            except Exception as e:\n                logger.error(f\"Shutdown handler failed: {e}\")\n                \n        # Stop components in reverse dependency order\n        shutdown_order = self._determine_shutdown_order()\n        \n        for component_name in shutdown_order:\n            if component_name not in self.components:\n                continue\n                \n            component = self.components[component_name]\n            \n            try:\n                if (component.stop_method and \n                    hasattr(component.instance, component.stop_method)):\n                    stop_func = getattr(component.instance, component.stop_method)\n                    if asyncio.iscoroutinefunction(stop_func):\n                        await stop_func()\n                    else:\n                        stop_func()\n                        \n                component.status = \"stopped\"\n                logger.info(f\"Component {component_name} stopped\")\n                \n            except Exception as e:\n                logger.error(f\"Error stopping component {component_name}: {e}\")\n                \n        # Record shutdown\n        try:\n            WriteMemory(\n                content=f\"Fresh Agent System shutdown completed at {datetime.now()}\",\n                tags=[\"system\", \"shutdown\", \"complete\"]\n            ).run()\n        except Exception:\n            pass  # Memory system may already be stopped\n            \n        logger.info(\"System shutdown completed\")\n        \n    def _determine_shutdown_order(self) -> List[str]:\n        \"\"\"Determine the order to shutdown components (reverse of startup order).\"\"\"\n        # Simple reverse dependency order\n        shutdown_order = []\n        processed = set()\n        \n        def add_to_shutdown_order(component_name: str):\n            if component_name in processed or component_name not in self.components:\n                return\n                \n            component = self.components[component_name]\n            \n            # First, add components that depend on this one\n            for name, comp in self.components.items():\n                if component_name in comp.dependencies and name not in processed:\n                    add_to_shutdown_order(name)\n                    \n            shutdown_order.append(component_name)\n            processed.add(component_name)\n            \n        # Process all components\n        for component_name in self.components:\n            add_to_shutdown_order(component_name)\n            \n        return shutdown_order\n\n\n# Global system instance\n_system_instance: Optional[FreshAgentSystem] = None\n\ndef get_system() -> FreshAgentSystem:\n    \"\"\"Get the global Fresh Agent System instance.\"\"\"\n    global _system_instance\n    if _system_instance is None:\n        _system_instance = FreshAgentSystem()\n    return _system_instance\n\n\nasync def initialize_system(config: Optional[Dict[str, Any]] = None) -> bool:\n    \"\"\"Initialize the Fresh Agent System with optional configuration.\"\"\"\n    system = get_system()\n    return await system.initialize(config)\n\n\nasync def shutdown_system():\n    \"\"\"Shutdown the Fresh Agent System gracefully.\"\"\"\n    system = get_system()\n    await system.shutdown()\n\n\nasync def get_status() -> SystemStatus:\n    \"\"\"Get current system status.\"\"\"\n    system = get_system()\n    return await system.get_system_status()"
