"""
Autonomous Loop Core
Main autonomous loop engine that orchestrates continuous improvement.
"""

import time
import asyncio
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
import json

from ai.autonomous.safety import SafetyController, SafetyViolation
from ai.cli.magic import MagicCommand
from ai.memory.intelligent_store import IntelligentMemoryStore


@dataclass
class ImprovementOpportunity:
    """Represents an improvement opportunity identified by the system."""
    id: str
    type: str  # "security", "performance", "quality", "test_coverage"
    priority: float  # 0.0 to 1.0
    description: str
    details: Dict[str, Any]
    estimated_effort: str  # "low", "medium", "high"
    safety_score: float  # 0.0 to 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass  
class CycleResult:
    """Results from a complete autonomous loop cycle."""
    cycle_id: str
    start_time: datetime
    end_time: datetime
    opportunities_found: int
    improvements_attempted: int
    improvements_successful: int
    safety_violations: List[SafetyViolation]
    health_status: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["start_time"] = self.start_time.isoformat()
        result["end_time"] = self.end_time.isoformat()
        result["safety_violations"] = [asdict(v) for v in self.safety_violations]
        return result


class AutonomousLoop:
    """
    Main autonomous loop engine that orchestrates continuous improvement.
    Implements a four-phase cycle: Discovery → Planning → Execution → Learning
    """
    
    def __init__(self, 
                 working_directory: str,
                 memory_store: Optional[IntelligentMemoryStore] = None,
                 config: Optional[Dict[str, Any]] = None):
        """Initialize the autonomous loop."""
        self.working_directory = Path(working_directory)
        self.memory_store = memory_store or IntelligentMemoryStore()
        
        # Configuration
        default_config = {
            "scan_interval": 3600,  # seconds
            "max_improvements_per_cycle": 5,
            "safety_level": "high",
            "enabled": True,
            "continuous_mode": False,
        }
        self.config = {**default_config, **(config or {})}
        
        # Initialize components (import here to avoid circular imports)
        self.safety_controller = SafetyController(
            working_directory=str(self.working_directory),
            memory_store=self.memory_store
        )
        
        # Import components dynamically to avoid circular imports
        from ai.autonomous.monitor import CodebaseMonitor
        from ai.autonomous.engine import ImprovementEngine
        from ai.autonomous.feedback import FeedbackLoop
        
        self.codebase_monitor = CodebaseMonitor(
            working_directory=str(self.working_directory),
            memory_store=self.memory_store
        )
        
        self.improvement_engine = ImprovementEngine(
            working_directory=str(self.working_directory),
            memory_store=self.memory_store,
            magic_command=MagicCommand(
                working_directory=str(self.working_directory),
                memory_store=self.memory_store
            )
        )
        
        self.feedback_loop = FeedbackLoop(memory_store=self.memory_store)
        
        # State tracking
        self.running = False
        self.current_cycle = None
        self.cycle_history: List[CycleResult] = []
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Thread for continuous operation
        self._loop_thread = None
        self._stop_event = threading.Event()
        
    def start_continuous_loop(self, callback: Optional[Callable[[CycleResult], None]] = None):
        """
        Start the autonomous loop in continuous mode.
        
        Args:
            callback: Optional callback function called after each cycle
        """
        if self.running:
            self.logger.warning("Autonomous loop is already running")
            return
        
        if self.safety_controller.is_emergency_stopped():
            self.logger.error("Cannot start autonomous loop: emergency stop is active")
            return
        
        self.running = True
        self._stop_event.clear()
        
        self.logger.info("Starting autonomous loop in continuous mode")
        
        # Start loop thread
        self._loop_thread = threading.Thread(
            target=self._continuous_loop_worker,
            args=(callback,),
            daemon=True
        )
        self._loop_thread.start()
    
    def stop_continuous_loop(self):
        """Stop the continuous autonomous loop."""
        if not self.running:
            self.logger.warning("Autonomous loop is not running")
            return
        
        self.logger.info("Stopping autonomous loop...")
        self.running = False
        self._stop_event.set()
        
        if self._loop_thread:
            self._loop_thread.join(timeout=30)
            if self._loop_thread.is_alive():
                self.logger.warning("Loop thread did not stop cleanly")
    
    def run_single_cycle(self) -> CycleResult:
        """
        Run a single autonomous improvement cycle.
        
        Returns:
            CycleResult with details about the cycle execution
        """
        cycle_id = f"cycle_{int(time.time())}"
        start_time = datetime.now()
        
        self.logger.info(f"Starting autonomous cycle: {cycle_id}")
        
        # Initialize cycle result
        result = CycleResult(
            cycle_id=cycle_id,
            start_time=start_time,
            end_time=start_time,  # Will be updated
            opportunities_found=0,
            improvements_attempted=0,
            improvements_successful=0,
            safety_violations=[],
            health_status={}
        )
        
        self.current_cycle = result
        
        try:
            # Phase A: Discovery & Monitoring
            self.logger.info("Phase A: Discovery & Monitoring")
            opportunities = self._discovery_phase()
            result.opportunities_found = len(opportunities)
            
            # Phase B: Planning & Validation  
            self.logger.info("Phase B: Planning & Validation")
            planned_improvements = self._planning_phase(opportunities)
            
            # Phase C: Execution & Monitoring
            self.logger.info("Phase C: Execution & Monitoring") 
            execution_results = self._execution_phase(planned_improvements)
            result.improvements_attempted = len(execution_results)
            result.improvements_successful = sum(1 for r in execution_results if r.get("success"))
            
            # Phase D: Learning & Adaptation
            self.logger.info("Phase D: Learning & Adaptation")
            self._learning_phase(execution_results)
            
            # Final health check
            result.health_status = self.safety_controller.monitor_health()
            
        except Exception as e:
            self.logger.error(f"Error in autonomous cycle: {e}")
            result.health_status = {"error": str(e)}
            
        finally:
            result.end_time = datetime.now()
            self.cycle_history.append(result)
            self.current_cycle = None
            
            # Store cycle result in memory
            try:
                self.memory_store.write(
                    content=f"Autonomous cycle completed: {cycle_id}",
                    tags=["autonomous_loop", "cycle_result", cycle_id]
                )
            except:
                self.logger.warning("Failed to store cycle result in memory")
        
        duration = (result.end_time - result.start_time).total_seconds()
        self.logger.info(
            f"Completed cycle {cycle_id} in {duration:.1f}s: "
            f"{result.opportunities_found} opportunities, "
            f"{result.improvements_successful}/{result.improvements_attempted} successful improvements"
        )
        
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the autonomous loop."""
        health = self.safety_controller.monitor_health()
        
        recent_cycles = self.cycle_history[-5:] if self.cycle_history else []
        
        return {
            "running": self.running,
            "emergency_stopped": self.safety_controller.is_emergency_stopped(),
            "current_cycle": self.current_cycle.cycle_id if self.current_cycle else None,
            "total_cycles": len(self.cycle_history),
            "recent_cycles": [c.to_dict() for c in recent_cycles],
            "health": health,
            "config": self.config
        }
    
    def _continuous_loop_worker(self, callback: Optional[Callable[[CycleResult], None]]):
        """Worker function for continuous loop execution."""
        while self.running and not self._stop_event.is_set():
            try:
                # Check if emergency stop is active
                if self.safety_controller.is_emergency_stopped():
                    self.logger.warning("Emergency stop detected, pausing autonomous loop")
                    self._stop_event.wait(60)  # Wait 1 minute before checking again
                    continue
                
                # Run a cycle
                result = self.run_single_cycle()
                
                # Call callback if provided
                if callback:
                    try:
                        callback(result)
                    except Exception as e:
                        self.logger.error(f"Callback error: {e}")
                
                # Wait for next cycle
                scan_interval = self.config["scan_interval"]
                self.logger.info(f"Waiting {scan_interval}s until next cycle")
                
                if self._stop_event.wait(scan_interval):
                    break
                    
            except Exception as e:
                self.logger.error(f"Error in continuous loop: {e}")
                # Wait before retrying
                self._stop_event.wait(60)
        
        self.logger.info("Continuous loop worker stopped")
    
    def _discovery_phase(self) -> List[ImprovementOpportunity]:
        """
        Phase A: Discovery & Monitoring
        Identify improvement opportunities in the codebase.
        """
        opportunities = []
        
        try:
            # Scan for issues and opportunities
            scan_results = self.codebase_monitor.comprehensive_scan()
            
            # Convert scan results to opportunities
            for issue in scan_results.get("issues", []):
                opportunity = ImprovementOpportunity(
                    id=f"issue_{hash(issue['description'])}",
                    type=issue.get("type", "quality"),
                    priority=self._calculate_priority(issue),
                    description=issue["description"],
                    details=issue,
                    estimated_effort=self._estimate_effort(issue),
                    safety_score=self._calculate_safety_score(issue)
                )
                opportunities.append(opportunity)
            
            # Track metrics and patterns
            metrics = self.codebase_monitor.collect_metrics()
            patterns = self.codebase_monitor.analyze_patterns()
            
            self.logger.info(f"Discovery phase found {len(opportunities)} opportunities")
            
        except Exception as e:
            self.logger.error(f"Error in discovery phase: {e}")
        
        return opportunities
    
    def _planning_phase(self, opportunities: List[ImprovementOpportunity]) -> List[Dict[str, Any]]:
        """
        Phase B: Planning & Validation
        Plan and validate improvements before execution.
        """
        planned_improvements = []
        
        try:
            # Sort opportunities by priority and safety
            sorted_opportunities = sorted(
                opportunities,
                key=lambda x: (x.priority * x.safety_score),
                reverse=True
            )
            
            # Plan improvements for top opportunities
            max_improvements = self.config["max_improvements_per_cycle"]
            
            for opportunity in sorted_opportunities[:max_improvements]:
                improvement_plan = self.improvement_engine.plan_improvement(opportunity)
                
                if improvement_plan:
                    # Validate safety
                    is_safe, violations = self.safety_controller.validate_safety(improvement_plan)
                    
                    if is_safe:
                        improvement_plan["opportunity"] = opportunity
                        improvement_plan["safety_validated"] = True
                        planned_improvements.append(improvement_plan)
                    else:
                        self.logger.warning(f"Skipping unsafe improvement: {opportunity.id}")
                        for violation in violations:
                            self.logger.warning(f"  {violation.level}: {violation.message}")
            
            self.logger.info(f"Planning phase prepared {len(planned_improvements)} improvements")
            
        except Exception as e:
            self.logger.error(f"Error in planning phase: {e}")
        
        return planned_improvements
    
    def _execution_phase(self, planned_improvements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Phase C: Execution & Monitoring
        Execute planned improvements with safety monitoring.
        """
        execution_results = []
        
        for improvement in planned_improvements:
            try:
                # Create safety checkpoint
                checkpoint = self.safety_controller.create_checkpoint(
                    f"Before improvement: {improvement['opportunity'].description}"
                )
                
                # Execute improvement
                result = self.improvement_engine.execute_improvement(improvement)
                result["checkpoint_id"] = checkpoint.id
                
                # Monitor health after change
                health = self.safety_controller.monitor_health()
                result["post_execution_health"] = health
                
                execution_results.append(result)
                
                if result.get("success"):
                    self.logger.info(f"Successfully executed improvement: {improvement['opportunity'].id}")
                else:
                    self.logger.warning(f"Improvement execution failed: {improvement['opportunity'].id}")
                    
                    # Consider rollback if critical failure
                    if result.get("critical_failure"):
                        self.logger.info(f"Rolling back due to critical failure")
                        self.safety_controller.rollback_to_checkpoint(checkpoint.id)
                
            except Exception as e:
                self.logger.error(f"Error executing improvement: {e}")
                execution_results.append({
                    "success": False,
                    "error": str(e),
                    "opportunity": improvement["opportunity"]
                })
        
        return execution_results
    
    def _learning_phase(self, execution_results: List[Dict[str, Any]]):
        """
        Phase D: Learning & Adaptation
        Learn from results and adapt strategies.
        """
        try:
            # Analyze outcomes
            self.feedback_loop.analyze_results(execution_results)
            
            # Update patterns and strategies
            self.feedback_loop.update_patterns()
            
            # Learn from successful and failed improvements
            for result in execution_results:
                if result.get("success"):
                    self.feedback_loop.record_success(result)
                else:
                    self.feedback_loop.record_failure(result)
            
            self.logger.info("Learning phase completed")
            
        except Exception as e:
            self.logger.error(f"Error in learning phase: {e}")
    
    def _calculate_priority(self, issue: Dict[str, Any]) -> float:
        """Calculate priority score for an issue (0.0 to 1.0)."""
        priority_weights = {
            "security": 1.0,
            "performance": 0.8,
            "bug": 0.7,
            "quality": 0.6,
            "test_coverage": 0.4,
            "todo": 0.3
        }
        
        issue_type = issue.get("type", "quality").lower()
        base_priority = priority_weights.get(issue_type, 0.5)
        
        # Adjust based on severity if available
        severity = issue.get("severity", "medium").lower()
        severity_multiplier = {
            "critical": 1.0,
            "high": 0.8,
            "medium": 0.6,
            "low": 0.4
        }
        
        return base_priority * severity_multiplier.get(severity, 0.6)
    
    def _estimate_effort(self, issue: Dict[str, Any]) -> str:
        """Estimate effort required for an issue."""
        # Simple heuristic based on issue type and complexity
        issue_type = issue.get("type", "quality").lower()
        
        if issue_type in ["todo", "quality"]:
            return "low"
        elif issue_type in ["bug", "test_coverage"]:
            return "medium"
        else:
            return "high"
    
    def _calculate_safety_score(self, issue: Dict[str, Any]) -> float:
        """Calculate safety score for an issue (0.0 to 1.0)."""
        # Higher score = safer to fix
        issue_type = issue.get("type", "quality").lower()
        
        safety_scores = {
            "todo": 0.9,
            "test_coverage": 0.8,
            "quality": 0.7,
            "performance": 0.6,
            "bug": 0.5,
            "security": 0.4  # Security fixes can be risky
        }
        
        return safety_scores.get(issue_type, 0.5)
