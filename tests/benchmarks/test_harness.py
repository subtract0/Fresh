"""Tests for Benchmark Harness

Validates the benchmark harness functionality for measuring learning effectiveness.
"""
import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

from ai.benchmarks.harness import (
    BenchmarkHarness,
    BenchmarkTask,
    BenchmarkResult,
    TaskDifficulty,
    TaskCategory,
    LearningMetrics
)
from ai.agents.mother import AgentResult


class TestBenchmarkHarness:
    """Test benchmark harness functionality."""
    
    @pytest.fixture
    def harness(self, tmp_path):
        """Create a test harness with temporary results directory."""
        return BenchmarkHarness(
            use_persistent_memory=False,
            results_dir=tmp_path / "test_results"
        )
    
    @pytest.fixture
    def sample_task(self):
        """Create a sample benchmark task."""
        return BenchmarkTask(
            task_id="test_001",
            category=TaskCategory.BUG_FIX,
            difficulty=TaskDifficulty.EASY,
            description="Fix test bug",
            expected_solution_pattern="null check",
            validation_criteria=["adds null check", "handles error"],
            sample_code="def test(): return obj.value"
        )
    
    def test_harness_initialization(self, harness):
        """Test harness initializes correctly."""
        assert harness.memory_type == "in_memory"
        assert harness.results == []
        assert harness.tasks == []
        assert harness.results_dir.exists()
    
    def test_load_standard_tasks(self, harness):
        """Test loading standard benchmark tasks."""
        harness.load_standard_tasks()
        
        assert len(harness.tasks) > 0
        
        # Check task variety
        difficulties = set(t.difficulty for t in harness.tasks)
        assert TaskDifficulty.EASY in difficulties
        assert TaskDifficulty.MEDIUM in difficulties
        assert TaskDifficulty.HARD in difficulties
        
        categories = set(t.category for t in harness.tasks)
        assert TaskCategory.BUG_FIX in categories
        assert TaskCategory.REFACTORING in categories
    
    @pytest.mark.asyncio
    async def test_run_single_task(self, harness, sample_task):
        """Test running a single benchmark task."""
        with patch.object(harness.mother_agent, 'run') as mock_run:
            mock_run.return_value = AgentResult(
                agent_name="test_agent",
                agent_type="Developer",
                instructions="Fix bug",
                model="gpt-4",
                output_type="code",
                success=True,
                output="if obj is not None: return obj.value"
            )
            
            result = await harness.run_task(sample_task, attempt_number=1)
        
        assert result.task_id == "test_001"
        # Success depends on validation - check validation instead
        assert result.attempt_number == 1
        assert len(result.validation_passed) == 1  # Only "adds null check" passes
        assert len(result.validation_failed) == 1  # "handles error" fails
        # Overall success is False since not all criteria passed
        assert result.success is False
    
    @pytest.mark.asyncio
    async def test_task_validation(self, harness, sample_task):
        """Test solution validation logic."""
        # Test successful validation
        solution = "if obj is not None:\n    return obj.value\nelse:\n    handle_error()"
        passed, failed = harness._validate_solution(sample_task, solution)
        
        assert "adds null check" in passed
        assert "handles error" in passed
        assert len(failed) == 0
        
        # Test failed validation
        bad_solution = "return obj.value"
        passed, failed = harness._validate_solution(sample_task, bad_solution)
        
        assert len(passed) == 0
        assert len(failed) == 2
    
    @pytest.mark.asyncio
    async def test_run_benchmark_suite(self, harness):
        """Test running complete benchmark suite."""
        # Create simple test tasks
        harness.tasks = [
            BenchmarkTask(
                task_id=f"test_{i}",
                category=TaskCategory.BUG_FIX,
                difficulty=TaskDifficulty.EASY,
                description=f"Test task {i}",
                expected_solution_pattern="pattern",
                validation_criteria=["criterion"]
            )
            for i in range(3)
        ]
        
        with patch.object(harness.mother_agent, 'run') as mock_run:
            mock_run.return_value = AgentResult(
                agent_name="test",
                agent_type="Developer",
                instructions="test",
                model="gpt-4",
                output_type="code",
                success=True,
                output="solution"
            )
            
            metrics = await harness.run_benchmark_suite(iterations=2)
        
        assert metrics["total_tasks"] == 3
        assert metrics["total_attempts"] == 6  # 3 tasks * 2 iterations
        assert len(metrics["task_metrics"]) == 3
        assert "aggregate_metrics" in metrics
    
    def test_calculate_metrics(self, harness):
        """Test metrics calculation."""
        # Add mock results
        harness.results = [
            BenchmarkResult(
                task_id="task_1",
                session_id="test",
                attempt_number=1,
                success=False,
                time_taken_seconds=10.0,
                agent_type="Developer",
                memory_hits=0,
                memory_queries=10
            ),
            BenchmarkResult(
                task_id="task_1",
                session_id="test",
                attempt_number=2,
                success=True,
                time_taken_seconds=8.0,
                agent_type="Developer",
                memory_hits=5,
                memory_queries=10
            ),
            BenchmarkResult(
                task_id="task_1",
                session_id="test",
                attempt_number=3,
                success=True,
                time_taken_seconds=6.0,
                agent_type="Developer",
                memory_hits=8,
                memory_queries=10
            )
        ]
        
        tasks = [
            BenchmarkTask(
                task_id="task_1",
                category=TaskCategory.BUG_FIX,
                difficulty=TaskDifficulty.MEDIUM,
                description="Test",
                expected_solution_pattern="pattern",
                validation_criteria=[]
            )
        ]
        
        metrics = harness._calculate_metrics(tasks)
        
        assert metrics["total_attempts"] == 3
        task_metric = metrics["task_metrics"][0]
        assert task_metric["success_rate"] == 2/3
        assert task_metric["time_improvement_percentage"] == 40.0  # (10-6)/10 * 100
        assert task_metric["memory_utilization_rate"] == 13/30  # Total hits/queries
    
    def test_learning_score_calculation(self, harness):
        """Test learning effectiveness score calculation."""
        task_metrics = [
            {
                "first_attempt_success": False,
                "last_attempt_success": True,
                "time_improvement_percentage": 30.0,
                "memory_utilization_rate": 0.5,
                "success_rate": 0.8,
                "difficulty": "medium"
            },
            {
                "first_attempt_success": True,
                "last_attempt_success": True,
                "time_improvement_percentage": 20.0,
                "memory_utilization_rate": 0.7,
                "success_rate": 1.0,
                "difficulty": "hard"
            }
        ]
        
        score = harness._calculate_learning_score(task_metrics)
        
        assert 0 <= score <= 100
        # Score may be close to 50 with these metrics
        assert score > 40  # Should show some positive learning
    
    @pytest.mark.asyncio
    async def test_compare_memory_modes(self, harness):
        """Test comparison between memory modes."""
        with patch.object(harness.mother_agent, 'run') as mock_run:
            # Simulate improving performance with memory
            call_count = 0
            
            def side_effect(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                # Better success rate with memory (second run)
                success = call_count > 6  # Fail first run, succeed second
                return AgentResult(
                    agent_name="test",
                    agent_type="Developer",
                    instructions="test",
                    model="gpt-4",
                    output_type="code",
                    success=success,
                    output="solution" if success else None
                )
            
            mock_run.side_effect = side_effect
            
            # Use minimal tasks for speed
            harness.tasks = [
                BenchmarkTask(
                    task_id="compare_test",
                    category=TaskCategory.BUG_FIX,
                    difficulty=TaskDifficulty.EASY,
                    description="Test",
                    expected_solution_pattern="pattern",
                    validation_criteria=["test"]
                )
            ]
            
            comparison = await harness.compare_memory_modes(iterations=2)
        
        assert "without_memory" in comparison
        assert "with_memory" in comparison
        assert "improvement" in comparison
        
        # Memory mode should show improvement
        assert comparison["with_memory"]["overall_success_rate"] >= \
               comparison["without_memory"]["overall_success_rate"]
    
    def test_save_results(self, harness, tmp_path):
        """Test saving results to file."""
        harness.results = [
            BenchmarkResult(
                task_id="save_test",
                session_id="test",
                attempt_number=1,
                success=True,
                time_taken_seconds=5.0,
                agent_type="Developer"
            )
        ]
        
        metrics = {
            "session_id": "test",
            "memory_type": "in_memory",
            "total_tasks": 1,
            "total_attempts": 1,
            "task_metrics": [],
            "aggregate_metrics": {}
        }
        
        filepath = tmp_path / "test_save.json"
        harness._save_results(filepath, metrics)
        
        assert filepath.exists()
        
        # Verify content
        import json
        with open(filepath) as f:
            saved = json.load(f)
        
        assert saved["session_id"] == "test"
        assert "detailed_results" in saved
        assert len(saved["detailed_results"]) == 1


class TestBenchmarkDataStructures:
    """Test benchmark data structures."""
    
    def test_benchmark_task_creation(self):
        """Test creating benchmark tasks."""
        task = BenchmarkTask(
            task_id="struct_test",
            category=TaskCategory.REFACTORING,
            difficulty=TaskDifficulty.MEDIUM,
            description="Refactor code",
            expected_solution_pattern="pattern",
            validation_criteria=["criterion1", "criterion2"],
            metadata={"key": "value"}
        )
        
        assert task.task_id == "struct_test"
        assert task.category == TaskCategory.REFACTORING
        assert task.difficulty == TaskDifficulty.MEDIUM
        assert len(task.validation_criteria) == 2
        assert task.metadata["key"] == "value"
    
    def test_benchmark_result_creation(self):
        """Test creating benchmark results."""
        result = BenchmarkResult(
            task_id="result_test",
            session_id="session_123",
            attempt_number=1,
            success=True,
            time_taken_seconds=3.14,
            agent_type="QA",
            validation_passed=["test1"],
            validation_failed=["test2"],
            memory_hits=5,
            memory_queries=10
        )
        
        assert result.task_id == "result_test"
        assert result.success is True
        assert result.memory_hits == 5
        assert result.memory_queries == 10
        assert isinstance(result.timestamp, datetime)
    
    def test_learning_metrics_creation(self):
        """Test creating learning metrics."""
        metrics = LearningMetrics(
            task_id="metrics_test",
            initial_success_rate=0.3,
            current_success_rate=0.8,
            improvement_percentage=166.67,
            average_time_reduction=25.0,
            memory_utilization_rate=0.6,
            pattern_recognition_score=0.75,
            cross_session_retention=0.9
        )
        
        assert metrics.task_id == "metrics_test"
        assert metrics.improvement_percentage == 166.67
        assert metrics.pattern_recognition_score == 0.75


class TestBenchmarkIntegration:
    """Integration tests for benchmark harness."""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_full_benchmark_flow(self, tmp_path):
        """Test complete benchmark flow end-to-end."""
        harness = BenchmarkHarness(
            use_persistent_memory=False,
            results_dir=tmp_path
        )
        
        # Load tasks
        harness.load_standard_tasks()
        
        # Filter to easy tasks for speed
        easy_tasks = [
            t for t in harness.tasks 
            if t.difficulty == TaskDifficulty.EASY
        ][:2]  # Just 2 tasks
        harness.tasks = easy_tasks
        
        with patch.object(harness.mother_agent, 'run') as mock_run:
            mock_run.return_value = AgentResult(
                agent_name="test",
                agent_type="Developer",
                instructions="test",
                model="gpt-4",
                output_type="code",
                success=True,
                output="if obj is not None: return obj.value"
            )
            
            metrics = await harness.run_benchmark_suite(
                iterations=2,
                difficulties=[TaskDifficulty.EASY]
            )
        
        assert metrics["total_tasks"] == 2
        assert metrics["total_attempts"] == 4
        assert "learning_effectiveness_score" in metrics["aggregate_metrics"]
        
        # Check results were saved
        results_files = list(tmp_path.glob("*.json"))
        assert len(results_files) > 0
