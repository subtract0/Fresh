"""
Automated Self-Documenting Loop Service

Implements continuous monitoring and documentation of the codebase to ensure:
1. All implemented features are properly hooked up
2. No feature bloat exists (unnecessary features are identified)
3. All features have adequate test coverage
4. Documentation stays synchronized with code

This service runs as part of the autonomous development loop to maintain
code quality and prevent "broken windows".
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging

from ai.memory.intelligent_store import IntelligentMemoryStore


@dataclass
class SelfDocumentingLoopResult:
    """Result of a self-documenting loop cycle."""
    cycle_id: str
    timestamp: str
    feature_count: int
    unhooked_features: int
    untested_features: int
    unnecessary_features: int
    quality_score: float
    critical_issues: List[str]
    recommendations: List[str]
    actions_taken: List[str]
    success: bool


class SelfDocumentingLoopService:
    """
    Service that continuously monitors and documents codebase features.
    
    Implements the "Self-Documenting Loop" rule by:
    - Running feature inventories periodically
    - Identifying broken windows (unhooked features, missing tests)
    - Automatically suggesting fixes
    - Maintaining synchronized documentation
    """
    
    def __init__(self, 
                 root_path: Path,
                 memory_store: Optional[IntelligentMemoryStore] = None,
                 config: Optional[Dict[str, Any]] = None):
        """Initialize the self-documenting loop service."""
        self.root_path = root_path
        self.memory_store = memory_store or IntelligentMemoryStore()
        
        # Configuration
        default_config = {
            "check_interval": 3600,  # Check every hour
            "quality_threshold": 0.7,  # Minimum acceptable quality score
            "auto_fix_enabled": False,  # Whether to automatically fix issues
            "alert_on_regression": True,  # Alert on quality regressions
            "max_unhooked_features": 5,  # Max unhooked features before alert
        }
        self.config = {**default_config, **(config or {})}
        
        # State tracking
        self.running = False
        self.last_check_time: Optional[datetime] = None
        self.last_quality_score: float = 1.0
        self.cycle_history: List[SelfDocumentingLoopResult] = []
        
        # Initialize logging
        self.logger = logging.getLogger(__name__)
        
    async def start_monitoring(self):
        """Start the self-documenting loop monitoring."""
        if self.running:
            self.logger.warning("Self-documenting loop is already running")
            return
            
        self.running = True
        self.logger.info("Starting self-documenting loop monitoring")
        
        try:
            while self.running:
                await self._run_cycle()
                
                # Wait for next cycle
                await asyncio.sleep(self.config["check_interval"])
                
        except asyncio.CancelledError:
            self.logger.info("Self-documenting loop monitoring cancelled")
        except Exception as e:
            self.logger.error(f"Error in self-documenting loop: {e}")
        finally:
            self.running = False
    
    def stop_monitoring(self):
        """Stop the self-documenting loop monitoring."""
        self.running = False
        self.logger.info("Stopping self-documenting loop monitoring")
    
    async def _run_cycle(self) -> SelfDocumentingLoopResult:
        """Run a single self-documenting loop cycle."""
        cycle_id = f"sdl_{int(datetime.now().timestamp())}"
        self.logger.info(f"Starting self-documenting loop cycle: {cycle_id}")
        
        result = SelfDocumentingLoopResult(
            cycle_id=cycle_id,
            timestamp=datetime.now().isoformat(),
            feature_count=0,
            unhooked_features=0,
            untested_features=0,
            unnecessary_features=0,
            quality_score=0.0,
            critical_issues=[],
            recommendations=[],
            actions_taken=[],
            success=False
        )
        
        try:
            # Step 1: Run feature inventory
            inventory_result = await self._run_feature_inventory()
            
            if not inventory_result:
                result.critical_issues.append("Failed to run feature inventory")
                return result
            
            # Step 2: Analyze results
            result = await self._analyze_inventory(result, inventory_result)
            
            # Step 3: Take automated actions if enabled
            if self.config["auto_fix_enabled"]:
                await self._take_automated_actions(result)
            
            # Step 4: Alert on critical issues
            await self._check_for_alerts(result)
            
            # Step 5: Store results in memory
            await self._store_cycle_result(result)
            
            result.success = True
            self.cycle_history.append(result)
            
            self.logger.info(
                f"Self-documenting loop cycle {cycle_id} complete: "
                f"{result.feature_count} features, "
                f"quality score {result.quality_score:.2f}"
            )
            
        except Exception as e:
            self.logger.error(f"Error in self-documenting loop cycle: {e}")
            result.critical_issues.append(f"Cycle error: {str(e)}")
        
        self.last_check_time = datetime.now()
        return result
    
    async def _run_feature_inventory(self) -> Optional[Dict[str, Any]]:
        """Run the feature inventory script."""
        try:
            script_path = self.root_path / "scripts" / "feature_inventory.py"
            
            if not script_path.exists():
                self.logger.error("Feature inventory script not found")
                return None
            
            # Run the script
            process = await asyncio.create_subprocess_exec(
                sys.executable, str(script_path),
                cwd=str(self.root_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                self.logger.error(f"Feature inventory failed: {stderr.decode()}")
                return None
            
            # Load the JSON result
            json_path = self.root_path / "docs" / "feature_inventory.json"
            if json_path.exists():
                with open(json_path, 'r') as f:
                    return json.load(f)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error running feature inventory: {e}")
            return None
    
    async def _analyze_inventory(self, 
                                result: SelfDocumentingLoopResult, 
                                inventory: Dict[str, Any]) -> SelfDocumentingLoopResult:
        """Analyze the feature inventory results."""
        result.feature_count = inventory.get("total_features", 0)
        result.quality_score = inventory.get("quality_summary", {}).get("average_quality_score", 0.0)
        
        # Count issues
        unhooked = [f for f in inventory.get("features", []) 
                   if f.get("implemented", False) and not f.get("hooked_up", False)]
        untested = [f for f in inventory.get("features", []) 
                   if f.get("implemented", False) and not f.get("tested", False)]
        unnecessary = [f for f in inventory.get("features", []) 
                      if not f.get("necessary", True)]
        
        result.unhooked_features = len(unhooked)
        result.untested_features = len(untested)
        result.unnecessary_features = len(unnecessary)
        
        # Identify critical issues
        if result.quality_score < self.config["quality_threshold"]:
            result.critical_issues.append(
                f"Quality score ({result.quality_score:.2f}) below threshold ({self.config['quality_threshold']})"
            )
        
        if result.unhooked_features > self.config["max_unhooked_features"]:
            result.critical_issues.append(
                f"Too many unhooked features ({result.unhooked_features})"
            )
        
        # Generate recommendations
        if unhooked:
            result.recommendations.append(
                f"Hook up {len(unhooked)} unconnected features to CLI/API interfaces"
            )
        
        if untested:
            result.recommendations.append(
                f"Add test coverage for {len(untested)} untested features"
            )
        
        if unnecessary:
            result.recommendations.append(
                f"Review and consider removing {len(unnecessary)} potentially unnecessary features"
            )
        
        # Check for regressions
        if self.config["alert_on_regression"] and result.quality_score < self.last_quality_score - 0.1:
            result.critical_issues.append(
                f"Quality regression detected: {self.last_quality_score:.2f} → {result.quality_score:.2f}"
            )
        
        self.last_quality_score = result.quality_score
        return result
    
    async def _take_automated_actions(self, result: SelfDocumentingLoopResult):
        """Take automated actions to fix issues (if enabled)."""
        # For now, we only log what actions would be taken
        # In the future, we could implement automated fixes
        
        if result.unhooked_features > 0:
            action = f"Would auto-generate CLI commands for {result.unhooked_features} unhooked features"
            result.actions_taken.append(action)
            self.logger.info(f"Auto-fix: {action}")
        
        if result.untested_features > 0:
            action = f"Would auto-generate test stubs for {result.untested_features} untested features"
            result.actions_taken.append(action)
            self.logger.info(f"Auto-fix: {action}")
    
    async def _check_for_alerts(self, result: SelfDocumentingLoopResult):
        """Check if we should alert about critical issues."""
        if result.critical_issues:
            # Store alert in memory
            alert_content = f"Self-documenting loop alert: {len(result.critical_issues)} critical issues found"
            
            try:
                self.memory_store.write(
                    content=alert_content,
                    tags=["self_documenting_loop", "alert", "critical", result.cycle_id]
                )
            except Exception as e:
                self.logger.error(f"Failed to store alert: {e}")
            
            # Log critical issues
            self.logger.warning(f"Critical issues detected in cycle {result.cycle_id}:")
            for issue in result.critical_issues:
                self.logger.warning(f"  - {issue}")
    
    async def _store_cycle_result(self, result: SelfDocumentingLoopResult):
        """Store the cycle result in memory."""
        try:
            content = (
                f"Self-documenting loop cycle {result.cycle_id}: "
                f"{result.feature_count} features, quality {result.quality_score:.2f}"
            )
            
            self.memory_store.write(
                content=content,
                tags=["self_documenting_loop", "cycle_result", result.cycle_id]
            )
            
        except Exception as e:
            self.logger.error(f"Failed to store cycle result: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the self-documenting loop."""
        recent_cycles = self.cycle_history[-5:] if self.cycle_history else []
        
        return {
            "running": self.running,
            "last_check_time": self.last_check_time.isoformat() if self.last_check_time else None,
            "last_quality_score": self.last_quality_score,
            "total_cycles": len(self.cycle_history),
            "recent_cycles": [asdict(c) for c in recent_cycles],
            "config": self.config
        }
    
    async def force_check(self) -> SelfDocumentingLoopResult:
        """Force an immediate self-documenting loop check."""
        self.logger.info("Forcing immediate self-documenting loop check")
        return await self._run_cycle()


# Singleton instance for use in autonomous loop
_self_documenting_service: Optional[SelfDocumentingLoopService] = None


def get_self_documenting_service(root_path: Path, 
                                memory_store: Optional[IntelligentMemoryStore] = None) -> SelfDocumentingLoopService:
    """Get or create the self-documenting loop service."""
    global _self_documenting_service
    
    if _self_documenting_service is None:
        _self_documenting_service = SelfDocumentingLoopService(
            root_path=root_path,
            memory_store=memory_store
        )
    
    return _self_documenting_service


async def main():
    """Main function for testing the self-documenting loop."""
    root_path = Path(__file__).parent.parent.parent
    
    service = SelfDocumentingLoopService(root_path)
    
    # Run a single cycle
    result = await service.force_check()
    
    print(f"Self-documenting loop result:")
    print(f"  Features: {result.feature_count}")
    print(f"  Quality Score: {result.quality_score:.2f}")
    print(f"  Critical Issues: {len(result.critical_issues)}")
    print(f"  Recommendations: {len(result.recommendations)}")
    
    if result.critical_issues:
        print("Critical Issues:")
        for issue in result.critical_issues:
            print(f"  - {issue}")
    
    if result.recommendations:
        print("Recommendations:")
        for rec in result.recommendations:
            print(f"  - {rec}")


if __name__ == "__main__":
    asyncio.run(main())
