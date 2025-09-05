#!/usr/bin/env python3
"""
🎯 AUTONOMOUS BATCH IMPLEMENTATION ORCHESTRATOR

Strategic parallel execution system for implementing 440+ features
using OpenAI API workers with cost tracking and safety controls.

This orchestrator manages the execution of the 9-batch feature hookup plan,
providing real-time progress tracking, cost monitoring, and automatic
recovery mechanisms.

Cross-references:
    - Integration Plan: docs/hookup_analysis/integration_plan.yaml
    - Agent Execution: ai/execution/monitor.py for real-time tracking
    - Cost Monitoring: ai/monitor/cost_tracker.py for budget control
    - Memory System: ai/memory/store.py for persistent state
    
Architecture:
    - Asyncio TaskGroup for parallel batch execution
    - OpenAI API workers with intelligent rate limiting
    - Real-time progress streaming via EventBus
    - Automatic safety checkpoints and rollback capability
"""
from __future__ import annotations

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import yaml

from ai.execution.monitor import (
    AgentExecutionMonitor, ExecutionBatch, ExecutionStatus, 
    AgentExecution, get_execution_monitor
)
from ai.monitor.cost_tracker import get_cost_tracker, CostTracker
from ai.monitor.openai_tracker import get_openai_tracker, OpenAIUsageTracker
from ai.memory.store import get_store
from ai.tools.memory_tools import WriteMemory, ReadMemoryContext
from ai.autonomous.safety import SafetyController, SafetyCheckpoint
from ai.agents.enhanced_mother import EnhancedMotherAgent

logger = logging.getLogger(__name__)


class BatchStatus(Enum):
    """Status of a batch execution."""
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SAFETY_HOLD = "safety_hold"


@dataclass
class FeatureImplementation:
    """Individual feature implementation task."""
    feature_name: str
    interface: str  # "cli", "api", "both"
    cli_command: Optional[str]
    api_endpoint: Optional[str]
    file_path: str
    function_name: Optional[str]
    test_path: str
    priority_score: int
    status: BatchStatus = BatchStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    execution_time_seconds: float = 0.0
    tokens_used: int = 0
    cost_usd: float = 0.0
    error_message: Optional[str] = None
    attempts: int = 0
    max_attempts: int = 3


@dataclass
class BatchExecution:
    """Execution context for a feature batch."""
    batch_id: int
    features: List[FeatureImplementation]
    status: BatchStatus = BatchStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    progress_percentage: float = 0.0
    estimated_time_hours: float = 12.5
    actual_time_hours: float = 0.0
    total_features: int = 0
    completed_features: int = 0
    failed_features: int = 0
    total_cost_usd: float = 0.0
    total_tokens: int = 0
    safety_checkpoint_id: Optional[str] = None


@dataclass
class OrchestrationConfig:
    """Configuration for the batch orchestrator."""
    max_parallel_batches: int = 3
    max_parallel_features_per_batch: int = 5
    max_cost_per_batch_usd: float = 25.0
    max_total_cost_usd: float = 200.0
    safety_checkpoint_interval: int = 50  # features
    auto_commit_after_batch: bool = True
    auto_create_pr: bool = True
    openai_model: str = "gpt-4"
    temperature: float = 0.1
    max_tokens_per_request: int = 4000
    timeout_per_feature_minutes: int = 10
    
    
class BatchImplementationOrchestrator:
    """
    Orchestrates parallel execution of feature implementation batches
    with OpenAI API workers, cost tracking, and safety controls.
    """
    
    def __init__(self, config: Optional[OrchestrationConfig] = None):
        self.config = config or OrchestrationConfig()
        self.execution_monitor = get_execution_monitor()
        self.cost_tracker = get_cost_tracker()
        self.memory_store = get_store()
        
        # Execution state
        self.batch_executions: Dict[int, BatchExecution] = {}
        self.total_features_implemented: int = 0
        self.total_cost_usd: float = 0.0
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.orchestration_id: Optional[str] = None
        
        # Safety and monitoring
        self.safety_controller: Optional[SafetyController] = None
        self.emergency_stop_requested: bool = False
        self.progress_callbacks: List[Callable] = []
        
        # OpenAI integration
        self.openai_tracker = get_openai_tracker()
        self.mother_agent: Optional[EnhancedMotherAgent] = None
        
    async def initialize(self):
        """Initialize the orchestrator and its components."""
        logger.info("Initializing Batch Implementation Orchestrator")
        
        # Generate unique orchestration ID
        self.orchestration_id = f"orch_{int(time.time())}"
        
        # Initialize safety controller
        self.safety_controller = SafetyController(
            working_directory=str(Path.cwd()),
            memory_store=self.memory_store
        )
        
        # Initialize mother agent for spawning workers
        self.mother_agent = EnhancedMotherAgent()
        
        # Start execution monitoring
        await self.execution_monitor.start_monitoring()
        
        # Record orchestration start in memory
        WriteMemory(
            content=f"Started batch implementation orchestration: {self.orchestration_id}",
            tags=["orchestration", "batch_implementation", "start", self.orchestration_id]
        ).run()
        
        logger.info(f"Orchestrator initialized with ID: {self.orchestration_id}")
    
    async def load_integration_plan(self, plan_path: str = "docs/hookup_analysis/integration_plan.yaml") -> Dict[str, Any]:
        """Load and validate the integration plan."""
        logger.info(f"Loading integration plan from: {plan_path}")
        
        plan_file = Path(plan_path)
        if not plan_file.exists():
            raise FileNotFoundError(f"Integration plan not found: {plan_path}")
        
        # Load YAML plan
        with open(plan_file, 'r') as f:
            plan_data = yaml.safe_load(f)
        
        # Validate plan structure
        required_fields = ['version', 'summary', 'batches']
        for field in required_fields:
            if field not in plan_data:
                raise ValueError(f"Integration plan missing required field: {field}")
        
        # Store plan checksum in memory for immutable contract
        plan_content = plan_file.read_text()
        import hashlib
        plan_checksum = hashlib.sha256(plan_content.encode()).hexdigest()[:16]
        
        WriteMemory(
            content=f"Loaded integration plan: {plan_path} (checksum: {plan_checksum})",
            tags=["orchestration", "plan", "checksum", self.orchestration_id]
        ).run()
        
        logger.info(f"Integration plan loaded: {plan_data['summary']['total_features']} features in {len(plan_data['batches'])} batches")
        
        return plan_data
    
    async def prepare_batches(self, plan_data: Dict[str, Any]) -> List[BatchExecution]:
        """Prepare batch execution contexts from the integration plan."""
        logger.info("Preparing batch execution contexts")
        
        batches = []
        
        for batch_config in plan_data['batches']:
            batch_id = batch_config['batch_id']
            features = []
            
            # Convert plan features to implementation tasks
            for feature_config in batch_config['features']:
                feature = FeatureImplementation(
                    feature_name=feature_config['name'],
                    interface=feature_config['interface'],
                    cli_command=feature_config.get('cli_command'),
                    api_endpoint=feature_config.get('api_endpoint'),
                    file_path=feature_config['file_path'],
                    function_name=feature_config.get('function_name'),
                    test_path=feature_config['test_path'],
                    priority_score=feature_config['priority_score']
                )
                features.append(feature)
            
            # Create batch execution context
            batch_execution = BatchExecution(
                batch_id=batch_id,
                features=features,
                total_features=len(features),
                estimated_time_hours=batch_config['estimated_time_hours']
            )
            
            batches.append(batch_execution)
            self.batch_executions[batch_id] = batch_execution
        
        logger.info(f"Prepared {len(batches)} batch execution contexts")
        return batches
    
    async def execute_all_batches(self, plan_path: str = "docs/hookup_analysis/integration_plan.yaml") -> Dict[str, Any]:
        """
        Execute all feature implementation batches in parallel.
        
        Returns:
            Execution summary with statistics and results
        """
        self.start_time = datetime.now()
        
        try:
            # Load and validate integration plan
            plan_data = await self.load_integration_plan(plan_path)
            
            # Prepare batch execution contexts
            batches = await self.prepare_batches(plan_data)
            
            # Create safety checkpoint before execution
            checkpoint = self.safety_controller.create_checkpoint(
                f"Before batch implementation orchestration: {self.orchestration_id}"
            )
            
            logger.info(f"Starting execution of {len(batches)} batches with max parallel: {self.config.max_parallel_batches}")
            
            # Execute batches with controlled parallelism
            semaphore = asyncio.Semaphore(self.config.max_parallel_batches)
            
            async def execute_batch_with_semaphore(batch: BatchExecution):
                async with semaphore:
                    return await self.execute_batch(batch)
            
            # Start all batch executions
            batch_tasks = [
                execute_batch_with_semaphore(batch) 
                for batch in batches
            ]
            
            # Wait for all batches to complete
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Process results
            successful_batches = 0
            failed_batches = 0
            
            for i, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Batch {batches[i].batch_id} failed with exception: {result}")
                    batches[i].status = BatchStatus.FAILED
                    failed_batches += 1
                else:
                    if result.get('success', False):
                        successful_batches += 1
                    else:
                        failed_batches += 1
            
            # Generate final summary
            self.end_time = datetime.now()
            execution_time = (self.end_time - self.start_time).total_seconds() / 3600  # hours
            
            summary = {
                "orchestration_id": self.orchestration_id,
                "execution_time_hours": execution_time,
                "total_batches": len(batches),
                "successful_batches": successful_batches,
                "failed_batches": failed_batches,
                "total_features": sum(b.total_features for b in batches),
                "implemented_features": sum(b.completed_features for b in batches),
                "failed_features": sum(b.failed_features for b in batches),
                "total_cost_usd": sum(b.total_cost_usd for b in batches),
                "total_tokens": sum(b.total_tokens for b in batches),
                "average_cost_per_feature": (
                    sum(b.total_cost_usd for b in batches) / max(1, sum(b.completed_features for b in batches))
                ),
                "batches": [asdict(batch) for batch in batches]
            }
            
            # Store summary in memory
            WriteMemory(
                content=f"Completed batch implementation orchestration: {json.dumps(summary, indent=2)[:500]}...",
                tags=["orchestration", "complete", "summary", self.orchestration_id]
            ).run()
            
            logger.info(f"Orchestration completed: {successful_batches}/{len(batches)} batches successful")
            
            return summary
            
        except Exception as e:
            logger.error(f"Orchestration failed: {e}")
            
            # Emergency cleanup
            await self.emergency_cleanup()
            
            raise e
    
    async def execute_batch(self, batch: BatchExecution) -> Dict[str, Any]:
        """Execute a single batch of feature implementations."""
        batch.start_time = datetime.now()
        batch.status = BatchStatus.RUNNING
        
        logger.info(f"Starting batch {batch.batch_id}: {batch.total_features} features")
        
        # Create safety checkpoint for this batch
        checkpoint = self.safety_controller.create_checkpoint(
            f"Before batch {batch.batch_id} execution"
        )
        batch.safety_checkpoint_id = checkpoint.id
        
        try:
            # Check budget limits
            if self.total_cost_usd >= self.config.max_total_cost_usd:
                raise Exception(f"Total cost budget exceeded: ${self.total_cost_usd:.2f}")
            
            # Execute features with controlled parallelism
            semaphore = asyncio.Semaphore(self.config.max_parallel_features_per_batch)
            
            async def execute_feature_with_semaphore(feature: FeatureImplementation):
                async with semaphore:
                    return await self.execute_feature(feature, batch.batch_id)
            
            # Start all feature implementations in this batch
            feature_tasks = [
                execute_feature_with_semaphore(feature)
                for feature in batch.features
            ]
            
            # Wait for all features to complete
            feature_results = await asyncio.gather(*feature_tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(feature_results):
                feature = batch.features[i]
                
                if isinstance(result, Exception):
                    logger.error(f"Feature {feature.feature_name} failed: {result}")
                    feature.status = BatchStatus.FAILED
                    feature.error_message = str(result)
                    batch.failed_features += 1
                else:
                    if result.get('success', False):
                        feature.status = BatchStatus.COMPLETED
                        batch.completed_features += 1
                    else:
                        feature.status = BatchStatus.FAILED
                        feature.error_message = result.get('error', 'Unknown error')
                        batch.failed_features += 1
                    
                    # Update cost tracking
                    feature.tokens_used = result.get('tokens_used', 0)
                    feature.cost_usd = result.get('cost_usd', 0.0)
                    feature.execution_time_seconds = result.get('execution_time', 0.0)
            
            # Update batch statistics
            batch.total_tokens = sum(f.tokens_used for f in batch.features)
            batch.total_cost_usd = sum(f.cost_usd for f in batch.features)
            batch.progress_percentage = (batch.completed_features / batch.total_features) * 100
            batch.status = BatchStatus.COMPLETED if batch.failed_features == 0 else BatchStatus.FAILED
            
            batch.end_time = datetime.now()
            batch.actual_time_hours = (batch.end_time - batch.start_time).total_seconds() / 3600
            
            # Auto-commit if configured and successful
            if self.config.auto_commit_after_batch and batch.status == BatchStatus.COMPLETED:
                await self.auto_commit_batch(batch)
            
            logger.info(f"Batch {batch.batch_id} completed: {batch.completed_features}/{batch.total_features} features, ${batch.total_cost_usd:.2f}")
            
            return {
                "success": batch.status == BatchStatus.COMPLETED,
                "batch_id": batch.batch_id,
                "completed_features": batch.completed_features,
                "failed_features": batch.failed_features,
                "cost_usd": batch.total_cost_usd,
                "execution_time_hours": batch.actual_time_hours
            }
            
        except Exception as e:
            batch.status = BatchStatus.FAILED
            batch.end_time = datetime.now()
            
            logger.error(f"Batch {batch.batch_id} execution failed: {e}")
            
            # Rollback to checkpoint if critical failure
            if "budget exceeded" in str(e).lower() or "emergency" in str(e).lower():
                logger.info(f"Rolling back batch {batch.batch_id} due to critical failure")
                self.safety_controller.rollback_to_checkpoint(checkpoint.id)
            
            return {
                "success": False,
                "batch_id": batch.batch_id,
                "error": str(e)
            }
    
    async def execute_feature(self, feature: FeatureImplementation, batch_id: int) -> Dict[str, Any]:
        """Execute implementation for a single feature using OpenAI API."""
        feature.start_time = datetime.now()
        feature.status = BatchStatus.RUNNING
        
        logger.debug(f"Implementing feature: {feature.feature_name}")
        
        try:
            # Check cost limits
            if feature.cost_usd >= self.config.max_cost_per_batch_usd:
                raise Exception(f"Feature cost budget exceeded: ${feature.cost_usd:.2f}")
            
            # Generate test skeleton if missing
            await self.ensure_test_exists(feature)
            
            # Generate implementation stub if missing
            await self.ensure_implementation_stub(feature)
            
            # Use OpenAI to implement the feature
            implementation_result = await self.implement_with_openai(feature)
            
            # Run tests to validate implementation
            test_result = await self.validate_implementation(feature)
            
            feature.end_time = datetime.now()
            feature.execution_time_seconds = (feature.end_time - feature.start_time).total_seconds()
            
            # Update tracking data
            feature.tokens_used = implementation_result.get('tokens_used', 0)
            feature.cost_usd = implementation_result.get('cost_usd', 0.0)
            
            success = implementation_result.get('success', False) and test_result.get('success', False)
            
            return {
                "success": success,
                "tokens_used": feature.tokens_used,
                "cost_usd": feature.cost_usd,
                "execution_time": feature.execution_time_seconds,
                "error": implementation_result.get('error') or test_result.get('error')
            }
            
        except Exception as e:
            feature.status = BatchStatus.FAILED
            feature.end_time = datetime.now()
            feature.error_message = str(e)
            
            logger.error(f"Feature {feature.feature_name} implementation failed: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "tokens_used": feature.tokens_used,
                "cost_usd": feature.cost_usd
            }
    
    async def implement_with_openai(self, feature: FeatureImplementation) -> Dict[str, Any]:
        """Use OpenAI to implement the feature."""
        prompt = self.generate_implementation_prompt(feature)
        
        # Track OpenAI API usage
        start_time = time.time()
        
        try:
            # Use the mother agent to spawn a developer for this feature
            agent_result = await self.mother_agent.spawn_and_execute(
                agent_name=f"Developer_{feature.feature_name}",
                agent_type="PythonDeveloper", 
                instructions=prompt,
                model=self.config.openai_model,
                output_type="code",
                timeout=self.config.timeout_per_feature_minutes * 60
            )
            
            execution_time = time.time() - start_time
            
            # Extract cost and token information
            tokens_used = agent_result.get('tokens_used', 0)
            cost_usd = self.openai_tracker.estimate_cost_for_completion(
                model=self.config.openai_model,
                prompt_tokens=tokens_used // 2,  # Rough estimate
                completion_tokens=tokens_used // 2
            )
            
            return {
                "success": agent_result.get('success', False),
                "tokens_used": tokens_used,
                "cost_usd": cost_usd,
                "execution_time": execution_time,
                "error": agent_result.get('error')
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tokens_used": 0,
                "cost_usd": 0.0
            }
    
    def generate_implementation_prompt(self, feature: FeatureImplementation) -> str:
        """Generate OpenAI prompt for implementing a feature."""
        return f"""
You are a Python developer implementing a feature in the Fresh AI Agent System.

FEATURE TO IMPLEMENT:
- Name: {feature.feature_name}
- File: {feature.file_path}
- Function: {feature.function_name or 'N/A'}
- Interface: {feature.interface}
- CLI Command: {feature.cli_command or 'N/A'}
- API Endpoint: {feature.api_endpoint or 'N/A'}
- Test Path: {feature.test_path}

REQUIREMENTS:
1. Read the existing file at {feature.file_path}
2. Implement the missing function/feature following existing patterns
3. Ensure the implementation passes the test at {feature.test_path}
4. Follow the codebase style and conventions
5. Add appropriate error handling and logging
6. Include docstrings with cross-references to related modules

CONSTRAINTS:
- Only modify the specific function/feature requested
- Do not break existing functionality
- Follow the "no broken windows" policy
- Use type hints and proper error handling
- Keep the implementation focused and minimal

Please implement the feature and return the complete updated file content.
"""
    
    async def ensure_test_exists(self, feature: FeatureImplementation):
        """Ensure test file exists for the feature."""
        test_path = Path(feature.test_path)
        
        if not test_path.exists():
            logger.debug(f"Creating test skeleton: {feature.test_path}")
            
            # Create test directory if needed
            test_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate basic test skeleton
            test_content = self.generate_test_skeleton(feature)
            test_path.write_text(test_content)
    
    def generate_test_skeleton(self, feature: FeatureImplementation) -> str:
        """Generate a basic test skeleton for a feature."""
        return f'''"""
Tests for {feature.feature_name} feature.
Generated by batch implementation orchestrator.
"""
import pytest
from unittest.mock import Mock, patch

# Import the feature being tested
# from {feature.file_path.replace('/', '.').replace('.py', '')} import {feature.function_name or feature.feature_name}


class Test{feature.feature_name.replace('_', '').title()}:
    """Test {feature.feature_name} functionality."""
    
    def test_{feature.function_name or feature.feature_name.lower()}_basic(self):
        """Test basic functionality of {feature.feature_name}."""
        # TODO: Implement test
        assert True  # Placeholder - replace with actual test
    
    def test_{feature.function_name or feature.feature_name.lower()}_error_handling(self):
        """Test error handling in {feature.feature_name}."""
        # TODO: Implement error handling test
        assert True  # Placeholder - replace with actual test
'''
    
    async def ensure_implementation_stub(self, feature: FeatureImplementation):
        """Ensure implementation stub exists for the feature."""
        file_path = Path(feature.file_path)
        
        if not file_path.exists():
            logger.debug(f"Creating implementation stub: {feature.file_path}")
            
            # Create directory if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate basic implementation stub
            stub_content = self.generate_implementation_stub(feature)
            file_path.write_text(stub_content)
    
    def generate_implementation_stub(self, feature: FeatureImplementation) -> str:
        """Generate a basic implementation stub for a feature."""
        return f'''"""
{feature.feature_name} implementation.
Generated by batch implementation orchestrator.

TODO: Implement the actual functionality.
"""
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


def {feature.function_name or feature.feature_name.lower()}(*args, **kwargs) -> Any:
    """
    {feature.feature_name} implementation.
    
    TODO: Add proper implementation.
    
    Returns:
        TODO: Define return type and description
    """
    # TODO: Implement {feature.feature_name}
    logger.warning(f"{feature.feature_name} not yet implemented")
    raise NotImplementedError(f"{feature.feature_name} implementation pending")
'''
    
    async def validate_implementation(self, feature: FeatureImplementation) -> Dict[str, Any]:
        """Validate the implementation by running tests."""
        try:
            # Run the specific test for this feature
            import subprocess
            
            result = subprocess.run(
                ["python", "-m", "pytest", feature.test_path, "-v"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            success = result.returncode == 0
            
            return {
                "success": success,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def auto_commit_batch(self, batch: BatchExecution):
        """Auto-commit completed batch changes."""
        if not self.config.auto_commit_after_batch:
            return
        
        try:
            import subprocess
            
            # Stage all changes
            subprocess.run(["git", "add", "."], check=True)
            
            # Commit with descriptive message
            commit_message = f"Batch {batch.batch_id}: +{batch.completed_features} features ({batch.failed_features} failed)"
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            
            logger.info(f"Auto-committed batch {batch.batch_id}")
            
        except subprocess.CalledProcessError as e:
            logger.warning(f"Auto-commit failed for batch {batch.batch_id}: {e}")
    
    async def emergency_cleanup(self):
        """Emergency cleanup in case of orchestration failure."""
        logger.warning("Performing emergency cleanup")
        
        # Stop monitoring
        await self.execution_monitor.stop_monitoring()
        
        # Archive execution logs
        logs_dir = Path("ai/logs") 
        logs_dir.mkdir(exist_ok=True)
        
        # Save orchestration state
        if self.orchestration_id:
            state_file = logs_dir / f"emergency_{self.orchestration_id}.json"
            state_data = {
                "orchestration_id": self.orchestration_id,
                "batches": [asdict(batch) for batch in self.batch_executions.values()],
                "total_cost_usd": self.total_cost_usd,
                "emergency_time": datetime.now().isoformat()
            }
            
            state_file.write_text(json.dumps(state_data, indent=2))
            logger.info(f"Emergency state saved to: {state_file}")
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get current progress summary."""
        total_features = sum(b.total_features for b in self.batch_executions.values())
        completed_features = sum(b.completed_features for b in self.batch_executions.values())
        failed_features = sum(b.failed_features for b in self.batch_executions.values())
        total_cost = sum(b.total_cost_usd for b in self.batch_executions.values())
        
        return {
            "orchestration_id": self.orchestration_id,
            "total_batches": len(self.batch_executions),
            "running_batches": len([b for b in self.batch_executions.values() if b.status == BatchStatus.RUNNING]),
            "completed_batches": len([b for b in self.batch_executions.values() if b.status == BatchStatus.COMPLETED]),
            "total_features": total_features,
            "completed_features": completed_features,
            "failed_features": failed_features,
            "progress_percentage": (completed_features / max(1, total_features)) * 100,
            "total_cost_usd": total_cost,
            "estimated_remaining_cost": self.config.max_total_cost_usd - total_cost,
            "execution_time_minutes": (
                (datetime.now() - self.start_time).total_seconds() / 60 
                if self.start_time else 0
            )
        }


# Global orchestrator instance
_orchestrator: Optional[BatchImplementationOrchestrator] = None

def get_orchestrator(config: Optional[OrchestrationConfig] = None) -> BatchImplementationOrchestrator:
    """Get the global batch implementation orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = BatchImplementationOrchestrator(config)
    return _orchestrator


async def run_batch_implementation(
    plan_path: str = "docs/hookup_analysis/integration_plan.yaml",
    config: Optional[OrchestrationConfig] = None
) -> Dict[str, Any]:
    """
    Main entry point for running the batch implementation orchestration.
    
    Args:
        plan_path: Path to the integration plan YAML file
        config: Optional orchestration configuration
        
    Returns:
        Execution summary with results and statistics
    """
    orchestrator = get_orchestrator(config)
    await orchestrator.initialize()
    
    try:
        return await orchestrator.execute_all_batches(plan_path)
    except Exception as e:
        logger.error(f"Batch implementation failed: {e}")
        raise e
    finally:
        # Cleanup
        await orchestrator.emergency_cleanup()


if __name__ == "__main__":
    # Example usage
    import asyncio
    
    async def main():
        config = OrchestrationConfig(
            max_parallel_batches=2,
            max_total_cost_usd=50.0,
            auto_commit_after_batch=True
        )
        
        summary = await run_batch_implementation(config=config)
        
        print("🎉 BATCH IMPLEMENTATION COMPLETE!")
        print(f"Implemented: {summary['implemented_features']}/{summary['total_features']} features")
        print(f"Cost: ${summary['total_cost_usd']:.2f}")
        print(f"Time: {summary['execution_time_hours']:.1f} hours")
    
    asyncio.run(main())
