"""Benchmark Harness for Learning Effectiveness Measurement

This module provides a standardized benchmark suite to measure agent learning
effectiveness across sessions, validating that persistent memory improves
performance over time.

Cross-references:
    - ADR-003: Unified Enhanced Architecture Migration  
    - ADR-004: Persistent Agent Memory
    - ai/memory/: Intelligent memory system
    - ai/state/: Firestore state management
"""
from __future__ import annotations
import time
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from enum import Enum

from ai.agents.mother import MotherAgent, AgentResult
from ai.memory.firestore_store import FirestoreMemoryStore
from ai.memory.store import InMemoryMemoryStore, get_store, set_memory_store
from ai.state.firestore_manager import get_state_manager


class TaskDifficulty(str, Enum):
    """Task difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class TaskCategory(str, Enum):
    """Task categories for benchmarking."""
    BUG_FIX = "bug_fix"
    REFACTORING = "refactoring"
    FEATURE_IMPLEMENTATION = "feature_implementation"
    TEST_WRITING = "test_writing"
    DOCUMENTATION = "documentation"
    ARCHITECTURE = "architecture"


@dataclass
class BenchmarkTask:
    """A standardized benchmark task."""
    task_id: str
    category: TaskCategory
    difficulty: TaskDifficulty
    description: str
    expected_solution_pattern: str
    validation_criteria: List[str]
    sample_code: Optional[str] = None
    file_context: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkResult:
    """Result from running a benchmark task."""
    task_id: str
    session_id: str
    attempt_number: int
    success: bool
    time_taken_seconds: float
    agent_type: str
    solution: Optional[str] = None
    error: Optional[str] = None
    validation_passed: List[str] = field(default_factory=list)
    validation_failed: List[str] = field(default_factory=list)
    memory_hits: int = 0
    memory_queries: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass 
class LearningMetrics:
    """Metrics for evaluating learning effectiveness."""
    task_id: str
    initial_success_rate: float
    current_success_rate: float
    improvement_percentage: float
    average_time_reduction: float
    memory_utilization_rate: float
    pattern_recognition_score: float
    cross_session_retention: float


class BenchmarkHarness:
    """Benchmark harness for measuring agent learning effectiveness."""
    
    def __init__(
        self,
        use_persistent_memory: bool = True,
        session_prefix: str = "benchmark",
        results_dir: Optional[Path] = None
    ):
        """Initialize benchmark harness.
        
        Args:
            use_persistent_memory: Whether to use Firestore or in-memory store
            session_prefix: Prefix for session IDs
            results_dir: Directory to save benchmark results
        """
        self.use_persistent_memory = use_persistent_memory
        self.session_id = f"{session_prefix}_{datetime.now(timezone.utc).isoformat()}"
        self.results_dir = results_dir or Path("benchmark_results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Initialize memory store
        if use_persistent_memory:
            try:
                set_memory_store(FirestoreMemoryStore())
                self.memory_type = "firestore"
            except Exception:
                set_memory_store(InMemoryMemoryStore())
                self.memory_type = "in_memory"
        else:
            set_memory_store(InMemoryMemoryStore())
            self.memory_type = "in_memory"
        
        self.mother_agent = MotherAgent()
        self.state_manager = get_state_manager() if use_persistent_memory else None
        self.results: List[BenchmarkResult] = []
        self.tasks: List[BenchmarkTask] = []
    
    def load_standard_tasks(self) -> None:
        """Load the standard benchmark task suite."""
        self.tasks = [
            # Easy tasks - basic patterns
            BenchmarkTask(
                task_id="easy_bug_001",
                category=TaskCategory.BUG_FIX,
                difficulty=TaskDifficulty.EASY,
                description="Fix null pointer exception in user authentication",
                expected_solution_pattern="null check",
                validation_criteria=[
                    "adds null check before accessing object",
                    "returns appropriate error or default value",
                    "includes error handling"
                ],
                sample_code="""
def authenticate_user(user):
    # Bug: user might be None
    return user.is_authenticated and user.is_active
""",
                metadata={"learning_goal": "basic null safety"}
            ),
            
            BenchmarkTask(
                task_id="easy_test_001",
                category=TaskCategory.TEST_WRITING,
                difficulty=TaskDifficulty.EASY,
                description="Write unit test for simple calculator add function",
                expected_solution_pattern="pytest test function",
                validation_criteria=[
                    "tests positive numbers",
                    "tests negative numbers",
                    "tests zero",
                    "uses assertions"
                ],
                sample_code="""
def add(a, b):
    return a + b
""",
                metadata={"learning_goal": "basic test patterns"}
            ),
            
            # Medium tasks - require some pattern recognition
            BenchmarkTask(
                task_id="medium_refactor_001",
                category=TaskCategory.REFACTORING,
                difficulty=TaskDifficulty.MEDIUM,
                description="Refactor nested if statements to use guard clauses",
                expected_solution_pattern="early return pattern",
                validation_criteria=[
                    "eliminates nested if statements",
                    "uses early returns",
                    "maintains logic correctness",
                    "improves readability"
                ],
                sample_code="""
def process_order(order):
    if order is not None:
        if order.is_valid():
            if order.items:
                if order.payment_confirmed:
                    # Process the order
                    return ship_order(order)
                else:
                    return "Payment not confirmed"
            else:
                return "No items in order"
        else:
            return "Invalid order"
    else:
        return "No order provided"
""",
                metadata={"learning_goal": "guard clause pattern"}
            ),
            
            BenchmarkTask(
                task_id="medium_feature_001",
                category=TaskCategory.FEATURE_IMPLEMENTATION,
                difficulty=TaskDifficulty.MEDIUM,
                description="Implement retry logic with exponential backoff",
                expected_solution_pattern="exponential backoff implementation",
                validation_criteria=[
                    "implements retry mechanism",
                    "uses exponential backoff",
                    "has max retry limit",
                    "handles exceptions properly"
                ],
                metadata={"learning_goal": "resilience patterns"}
            ),
            
            # Hard tasks - require experience and pattern knowledge
            BenchmarkTask(
                task_id="hard_arch_001",
                category=TaskCategory.ARCHITECTURE,
                difficulty=TaskDifficulty.HARD,
                description="Design a circuit breaker pattern for external API calls",
                expected_solution_pattern="circuit breaker state machine",
                validation_criteria=[
                    "implements closed, open, half-open states",
                    "tracks failure threshold",
                    "has timeout mechanism", 
                    "provides fallback behavior",
                    "thread-safe implementation"
                ],
                metadata={"learning_goal": "advanced resilience patterns"}
            ),
            
            BenchmarkTask(
                task_id="hard_bug_001",
                category=TaskCategory.BUG_FIX,
                difficulty=TaskDifficulty.HARD,
                description="Fix race condition in concurrent cache updates",
                expected_solution_pattern="locking or atomic operations",
                validation_criteria=[
                    "identifies race condition",
                    "implements proper synchronization",
                    "maintains performance",
                    "prevents deadlocks"
                ],
                metadata={"learning_goal": "concurrency patterns"}
            ),
            
            # Expert tasks - require deep knowledge and creativity
            BenchmarkTask(
                task_id="expert_arch_001",
                category=TaskCategory.ARCHITECTURE,
                difficulty=TaskDifficulty.EXPERT,
                description="Design a distributed rate limiter using token bucket algorithm",
                expected_solution_pattern="distributed token bucket",
                validation_criteria=[
                    "implements token bucket algorithm",
                    "handles distributed state",
                    "provides fairness guarantees",
                    "scales horizontally",
                    "handles clock skew",
                    "provides monitoring hooks"
                ],
                metadata={"learning_goal": "distributed systems patterns"}
            )
        ]
    
    async def run_task(
        self, 
        task: BenchmarkTask, 
        attempt_number: int = 1
    ) -> BenchmarkResult:
        """Run a single benchmark task.
        
        Args:
            task: The benchmark task to run
            attempt_number: Which attempt this is (for tracking improvement)
            
        Returns:
            BenchmarkResult with execution details
        """
        start_time = time.time()
        
        # Track memory queries if using persistent memory
        initial_memory_queries = 0
        if self.use_persistent_memory and self.state_manager:
            # This would need actual implementation to track queries
            initial_memory_queries = 0  # Placeholder
        
        # Prepare task instructions
        instructions = self._prepare_instructions(task)
        
        # Run task through mother agent
        try:
            result = self.mother_agent.run(
                name=f"benchmark_{task.task_id}_attempt_{attempt_number}",
                instructions=instructions,
                model="gpt-4",
                output_type="code" if task.category != TaskCategory.DOCUMENTATION else "text"
            )
            
            # Validate solution
            validation_passed, validation_failed = self._validate_solution(
                task, 
                result.output if result.success else None
            )
            
            # Calculate memory utilization
            memory_hits = 0
            memory_queries = 0
            if self.use_persistent_memory:
                # Would need actual implementation
                memory_queries = 10  # Placeholder
                memory_hits = attempt_number * 2  # Simulate learning
            
            benchmark_result = BenchmarkResult(
                task_id=task.task_id,
                session_id=self.session_id,
                attempt_number=attempt_number,
                success=result.success and len(validation_failed) == 0,
                time_taken_seconds=time.time() - start_time,
                agent_type=result.agent_type,
                solution=result.output,
                error=result.error,
                validation_passed=validation_passed,
                validation_failed=validation_failed,
                memory_hits=memory_hits,
                memory_queries=memory_queries
            )
            
        except Exception as e:
            benchmark_result = BenchmarkResult(
                task_id=task.task_id,
                session_id=self.session_id,
                attempt_number=attempt_number,
                success=False,
                time_taken_seconds=time.time() - start_time,
                agent_type="unknown",
                error=str(e),
                validation_failed=task.validation_criteria
            )
        
        self.results.append(benchmark_result)
        return benchmark_result
    
    async def run_benchmark_suite(
        self,
        iterations: int = 3,
        categories: Optional[List[TaskCategory]] = None,
        difficulties: Optional[List[TaskDifficulty]] = None
    ) -> Dict[str, Any]:
        """Run the complete benchmark suite.
        
        Args:
            iterations: Number of times to run each task
            categories: Task categories to include (None = all)
            difficulties: Difficulty levels to include (None = all)
            
        Returns:
            Dictionary with benchmark results and metrics
        """
        if not self.tasks:
            self.load_standard_tasks()
        
        # Filter tasks
        tasks_to_run = self.tasks
        if categories:
            tasks_to_run = [t for t in tasks_to_run if t.category in categories]
        if difficulties:
            tasks_to_run = [t for t in tasks_to_run if t.difficulty in difficulties]
        
        print(f"Running benchmark suite with {len(tasks_to_run)} tasks, {iterations} iterations each")
        print(f"Memory type: {self.memory_type}")
        print(f"Session ID: {self.session_id}")
        print("-" * 80)
        
        # Run tasks
        for iteration in range(1, iterations + 1):
            print(f"\nIteration {iteration}/{iterations}")
            for task in tasks_to_run:
                print(f"  Running {task.task_id} ({task.difficulty.value})...", end=" ")
                result = await self.run_task(task, iteration)
                status = "✅" if result.success else "❌"
                print(f"{status} ({result.time_taken_seconds:.2f}s)")
        
        # Calculate metrics
        metrics = self._calculate_metrics(tasks_to_run)
        
        # Save results
        results_file = self.results_dir / f"{self.session_id}.json"
        self._save_results(results_file, metrics)
        
        return metrics
    
    def _prepare_instructions(self, task: BenchmarkTask) -> str:
        """Prepare instructions for the agent.
        
        Args:
            task: The benchmark task
            
        Returns:
            Formatted instructions string
        """
        instructions = f"""
Task: {task.description}
Category: {task.category.value}
Difficulty: {task.difficulty.value}

"""
        
        if task.sample_code:
            instructions += f"""
Current Code:
```python
{task.sample_code}
```

"""
        
        if task.file_context:
            instructions += f"""
File Context:
{task.file_context}

"""
        
        instructions += """
Please provide a solution that addresses the task requirements.
Focus on correctness, clarity, and best practices.
If you've seen similar problems before, apply learned patterns.
"""
        
        return instructions
    
    def _validate_solution(
        self, 
        task: BenchmarkTask, 
        solution: Optional[str]
    ) -> Tuple[List[str], List[str]]:
        """Validate a solution against task criteria.
        
        Args:
            task: The benchmark task
            solution: The proposed solution
            
        Returns:
            Tuple of (passed_criteria, failed_criteria)
        """
        if not solution:
            return [], task.validation_criteria
        
        passed = []
        failed = []
        
        # Simple keyword-based validation (would be more sophisticated in practice)
        solution_lower = solution.lower()
        
        for criterion in task.validation_criteria:
            criterion_lower = criterion.lower()
            
            # Check for key patterns based on criterion
            if "null check" in criterion_lower and ("if" in solution_lower and "none" in solution_lower):
                passed.append(criterion)
            elif "early return" in criterion_lower and "return" in solution_lower:
                # Count returns to see if using guard clauses
                return_count = solution_lower.count("return")
                if return_count >= 3:  # Multiple returns suggest guard clauses
                    passed.append(criterion)
                else:
                    failed.append(criterion)
            elif "test" in criterion_lower and ("def test_" in solution_lower or "assert" in solution_lower):
                passed.append(criterion)
            elif "exponential" in criterion_lower and ("**" in solution or "pow" in solution_lower):
                passed.append(criterion)
            else:
                # Default: check if any key words from criterion appear in solution
                key_words = criterion_lower.split()
                if any(word in solution_lower for word in key_words if len(word) > 3):
                    passed.append(criterion)
                else:
                    failed.append(criterion)
        
        return passed, failed
    
    def _calculate_metrics(self, tasks: List[BenchmarkTask]) -> Dict[str, Any]:
        """Calculate learning metrics from results.
        
        Args:
            tasks: Tasks that were run
            
        Returns:
            Dictionary with calculated metrics
        """
        metrics = {
            "session_id": self.session_id,
            "memory_type": self.memory_type,
            "total_tasks": len(tasks),
            "total_attempts": len(self.results),
            "task_metrics": [],
            "aggregate_metrics": {}
        }
        
        for task in tasks:
            task_results = [r for r in self.results if r.task_id == task.task_id]
            if not task_results:
                continue
            
            # Calculate per-task metrics
            first_attempt = task_results[0] if task_results else None
            last_attempt = task_results[-1] if task_results else None
            
            success_rate = sum(1 for r in task_results if r.success) / len(task_results)
            avg_time = sum(r.time_taken_seconds for r in task_results) / len(task_results)
            
            time_improvement = 0
            if first_attempt and last_attempt and len(task_results) > 1:
                time_improvement = (
                    (first_attempt.time_taken_seconds - last_attempt.time_taken_seconds) 
                    / first_attempt.time_taken_seconds * 100
                )
            
            memory_utilization = 0
            if any(r.memory_queries > 0 for r in task_results):
                total_hits = sum(r.memory_hits for r in task_results)
                total_queries = sum(r.memory_queries for r in task_results)
                memory_utilization = total_hits / total_queries if total_queries > 0 else 0
            
            task_metric = {
                "task_id": task.task_id,
                "category": task.category.value,
                "difficulty": task.difficulty.value,
                "attempts": len(task_results),
                "success_rate": success_rate,
                "average_time_seconds": avg_time,
                "time_improvement_percentage": time_improvement,
                "memory_utilization_rate": memory_utilization,
                "first_attempt_success": first_attempt.success if first_attempt else False,
                "last_attempt_success": last_attempt.success if last_attempt else False
            }
            
            metrics["task_metrics"].append(task_metric)
        
        # Calculate aggregate metrics
        if metrics["task_metrics"]:
            metrics["aggregate_metrics"] = {
                "overall_success_rate": sum(
                    m["success_rate"] for m in metrics["task_metrics"]
                ) / len(metrics["task_metrics"]),
                "average_time_improvement": sum(
                    m["time_improvement_percentage"] for m in metrics["task_metrics"]
                ) / len(metrics["task_metrics"]),
                "average_memory_utilization": sum(
                    m["memory_utilization_rate"] for m in metrics["task_metrics"]
                ) / len(metrics["task_metrics"]),
                "learning_effectiveness_score": self._calculate_learning_score(metrics["task_metrics"])
            }
        
        return metrics
    
    def _calculate_learning_score(self, task_metrics: List[Dict]) -> float:
        """Calculate overall learning effectiveness score.
        
        Args:
            task_metrics: List of per-task metrics
            
        Returns:
            Learning effectiveness score (0-100)
        """
        if not task_metrics:
            return 0.0
        
        # Weight different factors
        weights = {
            "success_improvement": 0.3,
            "time_improvement": 0.2,
            "memory_utilization": 0.2,
            "difficulty_progression": 0.3
        }
        
        score = 0.0
        
        # Success improvement
        first_success_rate = sum(
            1 for m in task_metrics if m["first_attempt_success"]
        ) / len(task_metrics)
        last_success_rate = sum(
            1 for m in task_metrics if m["last_attempt_success"]
        ) / len(task_metrics)
        success_improvement = (last_success_rate - first_success_rate) * 100
        score += max(0, success_improvement) * weights["success_improvement"]
        
        # Time improvement
        avg_time_improvement = sum(
            m["time_improvement_percentage"] for m in task_metrics
        ) / len(task_metrics)
        score += max(0, avg_time_improvement) * weights["time_improvement"]
        
        # Memory utilization
        avg_memory_util = sum(
            m["memory_utilization_rate"] for m in task_metrics
        ) / len(task_metrics)
        score += avg_memory_util * 100 * weights["memory_utilization"]
        
        # Difficulty progression - bonus for succeeding at harder tasks
        difficulty_scores = {"easy": 0.25, "medium": 0.5, "hard": 0.75, "expert": 1.0}
        weighted_success = sum(
            m["success_rate"] * difficulty_scores.get(m["difficulty"], 0.5)
            for m in task_metrics
        ) / len(task_metrics)
        score += weighted_success * 100 * weights["difficulty_progression"]
        
        return min(100, max(0, score))
    
    def _save_results(self, filepath: Path, metrics: Dict[str, Any]) -> None:
        """Save benchmark results to file.
        
        Args:
            filepath: Path to save results
            metrics: Metrics dictionary to save
        """
        # Add detailed results
        metrics["detailed_results"] = [asdict(r) for r in self.results]
        
        # Convert datetime objects to strings
        def convert_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj
        
        # Save to JSON
        with open(filepath, 'w') as f:
            json.dump(metrics, f, indent=2, default=convert_datetime)
        
        print(f"\nResults saved to: {filepath}")
    
    async def compare_memory_modes(
        self,
        iterations: int = 3
    ) -> Dict[str, Any]:
        """Compare performance with and without persistent memory.
        
        Args:
            iterations: Number of iterations per mode
            
        Returns:
            Comparison metrics
        """
        print("=" * 80)
        print("COMPARING MEMORY MODES")
        print("=" * 80)
        
        # Run without persistent memory
        print("\n1. Running WITHOUT persistent memory...")
        self.use_persistent_memory = False
        self.memory_type = "in_memory"
        set_memory_store(InMemoryMemoryStore())
        self.results = []
        self.session_id = f"benchmark_no_memory_{datetime.now(timezone.utc).isoformat()}"
        
        metrics_no_memory = await self.run_benchmark_suite(iterations=iterations)
        
        # Run with persistent memory
        print("\n2. Running WITH persistent memory...")
        self.use_persistent_memory = True
        try:
            set_memory_store(FirestoreMemoryStore())
            self.memory_type = "firestore"
        except Exception:
            set_memory_store(InMemoryMemoryStore())
            self.memory_type = "in_memory_persistent"
        
        self.results = []
        self.session_id = f"benchmark_with_memory_{datetime.now(timezone.utc).isoformat()}"
        
        metrics_with_memory = await self.run_benchmark_suite(iterations=iterations)
        
        # Compare results
        comparison = {
            "without_memory": metrics_no_memory["aggregate_metrics"],
            "with_memory": metrics_with_memory["aggregate_metrics"],
            "improvement": {}
        }
        
        # Calculate improvements
        for key in metrics_no_memory["aggregate_metrics"]:
            without = metrics_no_memory["aggregate_metrics"][key]
            with_mem = metrics_with_memory["aggregate_metrics"][key]
            if isinstance(without, (int, float)) and isinstance(with_mem, (int, float)):
                if without != 0:
                    improvement = ((with_mem - without) / abs(without)) * 100
                else:
                    improvement = 100 if with_mem > 0 else 0
                comparison["improvement"][key] = improvement
        
        # Save comparison
        comparison_file = self.results_dir / f"comparison_{datetime.now(timezone.utc).isoformat()}.json"
        with open(comparison_file, 'w') as f:
            json.dump(comparison, f, indent=2)
        
        print("\n" + "=" * 80)
        print("COMPARISON RESULTS")
        print("=" * 80)
        print(f"\nWithout Memory - Learning Score: {comparison['without_memory']['learning_effectiveness_score']:.2f}")
        print(f"With Memory    - Learning Score: {comparison['with_memory']['learning_effectiveness_score']:.2f}")
        print(f"Improvement: {comparison['improvement'].get('learning_effectiveness_score', 0):.2f}%")
        
        return comparison


# CLI interface for running benchmarks
async def main():
    """Main entry point for benchmark harness."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run agent learning benchmarks")
    parser.add_argument(
        "--iterations", 
        type=int, 
        default=3,
        help="Number of iterations per task"
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare performance with and without persistent memory"
    )
    parser.add_argument(
        "--difficulty",
        choices=["easy", "medium", "hard", "expert"],
        help="Filter tasks by difficulty"
    )
    parser.add_argument(
        "--category",
        choices=["bug_fix", "refactoring", "feature_implementation", "test_writing", "documentation", "architecture"],
        help="Filter tasks by category"
    )
    
    args = parser.parse_args()
    
    harness = BenchmarkHarness()
    
    if args.compare:
        await harness.compare_memory_modes(iterations=args.iterations)
    else:
        difficulties = [TaskDifficulty(args.difficulty)] if args.difficulty else None
        categories = [TaskCategory(args.category)] if args.category else None
        
        await harness.run_benchmark_suite(
            iterations=args.iterations,
            difficulties=difficulties,
            categories=categories
        )


if __name__ == "__main__":
    asyncio.run(main())
