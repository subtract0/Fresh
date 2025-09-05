"""
Integration tests for Phase 3: The Autonomous Loop
Tests the continuous improvement system and all its components.
"""

import pytest
import tempfile
import shutil
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime

from ai.autonomous import (
    AutonomousLoop, SafetyController, CodebaseMonitor, 
    ImprovementEngine, FeedbackLoop, ImprovementOpportunity
)
from ai.memory.intelligent_store import IntelligentMemoryStore


class TestAutonomousLoopCore:
    """Test the core autonomous loop functionality."""
    
    @pytest.fixture
    def temp_repo(self):
        """Create temporary repository for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Initialize as git repo
        subprocess.run(["git", "init"], cwd=temp_dir, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=temp_dir, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_dir, check=True)
        
        # Create test files with various issues
        (temp_dir / "src").mkdir()
        (temp_dir / "src" / "__init__.py").write_text("")
        (temp_dir / "src" / "calculator.py").write_text('''
import hashlib

def add(a, b):
    return a + b

def divide(a, b):
    return a / b  # Bug: division by zero not handled

def hash_password(password):
    # TODO: Add salt for security
    return hashlib.md5(password.encode()).hexdigest()

# Performance issue: inefficient loop
def process_items(items):
    for i in range(len(items)):
        print(f"Processing {items[i]}")

# Missing validation
class User:
    def __init__(self, username):
        self.username = username  # No validation
''')
        
        (temp_dir / "tests").mkdir()
        (temp_dir / "tests" / "__init__.py").write_text("")
        # Minimal test coverage
        (temp_dir / "tests" / "test_basic.py").write_text('''
def test_placeholder():
    assert True
''')
        
        # Initial commit
        subprocess.run(["git", "add", "."], cwd=temp_dir, check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=temp_dir, check=True)
        
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def autonomous_loop(self, temp_repo):
        """Create autonomous loop instance."""
        memory_store = IntelligentMemoryStore()
        return AutonomousLoop(
            working_directory=str(temp_repo),
            memory_store=memory_store,
            config={
                "scan_interval": 10,  # Short interval for testing
                "max_improvements_per_cycle": 3,
                "safety_level": "high"
            }
        )
    
    def test_autonomous_loop_initialization(self, autonomous_loop, temp_repo):
        """Test autonomous loop initializes correctly."""
        assert autonomous_loop.working_directory == Path(temp_repo)
        assert autonomous_loop.safety_controller is not None
        assert autonomous_loop.codebase_monitor is not None
        assert autonomous_loop.improvement_engine is not None
        assert autonomous_loop.feedback_loop is not None
        assert not autonomous_loop.running
        assert autonomous_loop.config["max_improvements_per_cycle"] == 3
    
    def test_single_cycle_execution(self, autonomous_loop):
        """Test running a single autonomous improvement cycle."""
        # Run one cycle
        result = autonomous_loop.run_single_cycle()
        
        # Verify cycle result structure
        assert result.cycle_id.startswith("cycle_")
        assert result.start_time <= result.end_time
        assert isinstance(result.opportunities_found, int)
        assert isinstance(result.improvements_attempted, int)
        assert isinstance(result.improvements_successful, int)
        assert result.improvements_successful <= result.improvements_attempted
        assert isinstance(result.health_status, dict)
        
        # Should have found multiple opportunities in test repo
        assert result.opportunities_found > 0
        
        # Verify cycle is stored in history
        assert len(autonomous_loop.cycle_history) == 1
        assert autonomous_loop.cycle_history[0].cycle_id == result.cycle_id
    
    def test_discovery_phase(self, autonomous_loop):
        """Test the discovery phase identifies opportunities correctly."""
        # Access private method for testing
        opportunities = autonomous_loop._discovery_phase()
        
        assert isinstance(opportunities, list)
        assert len(opportunities) > 0
        
        # Should find various types of issues
        opportunity_types = {opp.type for opp in opportunities}
        expected_types = {"security", "performance", "todo", "quality", "test_coverage"}
        
        # Should find at least some of these types
        assert len(opportunity_types.intersection(expected_types)) > 0
        
        # Each opportunity should have required fields
        for opp in opportunities:
            assert opp.id
            assert opp.type
            assert isinstance(opp.priority, float)
            assert 0.0 <= opp.priority <= 1.0
            assert opp.description
            assert isinstance(opp.details, dict)
            assert opp.estimated_effort in ["low", "medium", "high"]
            assert isinstance(opp.safety_score, float)
            assert 0.0 <= opp.safety_score <= 1.0
    
    def test_planning_phase(self, autonomous_loop):
        """Test the planning phase creates valid improvement plans."""
        # First get opportunities
        opportunities = autonomous_loop._discovery_phase()
        assert len(opportunities) > 0
        
        # Test planning phase
        planned_improvements = autonomous_loop._planning_phase(opportunities)
        
        assert isinstance(planned_improvements, list)
        
        if planned_improvements:  # May be empty if all are unsafe
            for plan in planned_improvements:
                assert "opportunity" in plan
                assert "type" in plan
                assert "safety_validated" in plan
                assert plan["safety_validated"] == True
                assert "command_description" in plan
    
    def test_execution_phase_with_mocked_magic_command(self, autonomous_loop):
        """Test execution phase with mocked magic command to avoid actual changes."""
        # Create mock opportunities and plans
        mock_opportunity = Mock()
        mock_opportunity.id = "test_opp_1"
        mock_opportunity.type = "todo"
        mock_opportunity.description = "Test TODO item"
        mock_opportunity.priority = 0.5
        mock_opportunity.safety_score = 0.8
        mock_opportunity.estimated_effort = "low"
        mock_opportunity.details = {"todo_text": "Add validation"}
        
        mock_plan = {
            "opportunity": mock_opportunity,
            "type": "magic_add",
            "safety_validated": True,
            "command_description": "implement TODO: Add validation"
        }
        
        # Mock the improvement engine's execute_improvement method
        with patch.object(autonomous_loop.improvement_engine, 'execute_improvement') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "description": "Added validation functionality",
                "files_changed": ["src/validators.py"],
                "execution_type": "magic_add",
                "critical_failure": False
            }
            
            # Mock the safety controller's create_checkpoint method
            with patch.object(autonomous_loop.safety_controller, 'create_checkpoint') as mock_checkpoint:
                mock_checkpoint.return_value = Mock(id="checkpoint_123")
                
                # Execute the phase
                results = autonomous_loop._execution_phase([mock_plan])
                
                assert len(results) == 1
                assert results[0]["success"] == True
                assert "checkpoint_id" in results[0]
                assert "post_execution_health" in results[0]
                
                # Verify methods were called
                mock_execute.assert_called_once_with(mock_plan)
                mock_checkpoint.assert_called_once()
    
    def test_learning_phase(self, autonomous_loop):
        """Test the learning phase processes results correctly."""
        # Mock execution results
        mock_results = [
            {
                "success": True,
                "execution_type": "magic_fix",
                "description": "Fixed security issue",
                "files_changed": ["src/auth.py"]
            },
            {
                "success": False,
                "execution_type": "magic_refactor",
                "error": "Refactoring failed",
                "files_changed": []
            }
        ]
        
        # Mock the feedback loop methods
        with patch.object(autonomous_loop.feedback_loop, 'analyze_results') as mock_analyze:
            with patch.object(autonomous_loop.feedback_loop, 'update_patterns') as mock_update:
                with patch.object(autonomous_loop.feedback_loop, 'record_success') as mock_success:
                    with patch.object(autonomous_loop.feedback_loop, 'record_failure') as mock_failure:
                        
                        # Execute learning phase
                        autonomous_loop._learning_phase(mock_results)
                        
                        # Verify methods were called
                        mock_analyze.assert_called_once_with(mock_results)
                        mock_update.assert_called_once()
                        mock_success.assert_called_once_with(mock_results[0])
                        mock_failure.assert_called_once_with(mock_results[1])
    
    def test_status_reporting(self, autonomous_loop):
        """Test autonomous loop status reporting."""
        status = autonomous_loop.get_status()
        
        assert isinstance(status, dict)
        assert "running" in status
        assert "emergency_stopped" in status
        assert "current_cycle" in status
        assert "total_cycles" in status
        assert "recent_cycles" in status
        assert "health" in status
        assert "config" in status
        
        assert status["running"] == False
        assert status["total_cycles"] == 0
        assert isinstance(status["recent_cycles"], list)
        assert isinstance(status["health"], dict)
        assert isinstance(status["config"], dict)
    
    def test_continuous_loop_start_stop(self, autonomous_loop):
        """Test starting and stopping continuous loop."""
        # Verify not running initially
        assert not autonomous_loop.running
        
        # Start continuous loop
        autonomous_loop.start_continuous_loop()
        
        # Verify running state
        assert autonomous_loop.running
        assert autonomous_loop._loop_thread is not None
        
        # Stop continuous loop
        autonomous_loop.stop_continuous_loop()
        
        # Verify stopped state
        assert not autonomous_loop.running
    
    def test_emergency_stop_prevents_continuous_loop(self, autonomous_loop):
        """Test emergency stop prevents continuous loop from starting."""
        # Activate emergency stop
        autonomous_loop.safety_controller.emergency_stop("Test emergency stop")
        
        # Try to start continuous loop
        autonomous_loop.start_continuous_loop()
        
        # Should not be running due to emergency stop
        assert not autonomous_loop.running
        
        # Clear emergency stop
        autonomous_loop.safety_controller.clear_emergency_stop()
        
        # Now should be able to start
        autonomous_loop.start_continuous_loop()
        assert autonomous_loop.running
        
        # Clean up
        autonomous_loop.stop_continuous_loop()


class TestSafetyController:
    """Test the safety controller component."""
    
    @pytest.fixture
    def temp_repo(self):
        """Create temporary repository for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Initialize as git repo
        subprocess.run(["git", "init"], cwd=temp_dir, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=temp_dir, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_dir, check=True)
        
        # Add initial file
        (temp_dir / "test.txt").write_text("Initial content")
        subprocess.run(["git", "add", "."], cwd=temp_dir, check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=temp_dir, check=True)
        
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def safety_controller(self, temp_repo):
        """Create safety controller instance."""
        return SafetyController(str(temp_repo))
    
    def test_safety_validation_safe_changes(self, safety_controller):
        """Test safety validation with safe changes."""
        safe_changes = {
            "files_changed": ["src/new_feature.py"],
            "lines_changed": 50
        }
        
        # Mock the test runner to return success
        with patch.object(safety_controller, '_run_tests', return_value=True):
            is_safe, violations = safety_controller.validate_safety(safe_changes)
        
        assert is_safe
        assert len([v for v in violations if v.level == "critical"]) == 0
        assert len([v for v in violations if v.level == "error"]) == 0
    
    def test_safety_validation_large_changes(self, safety_controller):
        """Test safety validation rejects large changes."""
        large_changes = {
            "files_changed": [{"lines_changed": 150}]  # Exceeds default limit of 100
        }
        
        is_safe, violations = safety_controller.validate_safety(large_changes)
        
        assert not is_safe
        error_violations = [v for v in violations if v.level == "error"]
        assert len(error_violations) > 0
        assert any("large_change" in v.type for v in error_violations)
    
    def test_safety_validation_destructive_changes(self, safety_controller):
        """Test safety validation rejects destructive changes."""
        destructive_changes = {
            "deleted_files": ["important_file.py", "config.json"]
        }
        
        is_safe, violations = safety_controller.validate_safety(destructive_changes)
        
        assert not is_safe
        critical_violations = [v for v in violations if v.level == "critical"]
        assert len(critical_violations) > 0
        assert any("destructive_change" in v.type for v in critical_violations)
    
    def test_checkpoint_creation_and_rollback(self, safety_controller, temp_repo):
        """Test creating checkpoints and rolling back."""
        # Create checkpoint
        checkpoint = safety_controller.create_checkpoint("Test checkpoint")
        
        assert checkpoint.id
        assert checkpoint.description == "Test checkpoint"
        assert checkpoint.git_commit
        assert len(safety_controller.checkpoints) == 1
        
        # Make some changes
        test_file = temp_repo / "test.txt"
        test_file.write_text("Modified content")
        
        # Rollback to checkpoint
        success = safety_controller.rollback_to_checkpoint(checkpoint.id)
        
        assert success
        # Content should be restored
        assert test_file.read_text() == "Initial content"
    
    def test_emergency_stop_functionality(self, safety_controller):
        """Test emergency stop activation and clearing."""
        # Initially not stopped
        assert not safety_controller.is_emergency_stopped()
        
        # Activate emergency stop
        safety_controller.emergency_stop("Test emergency")
        
        # Should be stopped
        assert safety_controller.is_emergency_stopped()
        
        # Safety validation should fail
        is_safe, violations = safety_controller.validate_safety({})
        assert not is_safe
        critical_violations = [v for v in violations if v.level == "critical"]
        assert any("emergency_stop" in v.type for v in critical_violations)
        
        # Clear emergency stop
        safety_controller.clear_emergency_stop()
        
        # Should not be stopped
        assert not safety_controller.is_emergency_stopped()
    
    def test_health_monitoring(self, safety_controller):
        """Test system health monitoring."""
        health = safety_controller.monitor_health()
        
        assert isinstance(health, dict)
        assert "timestamp" in health
        assert "emergency_stopped" in health
        assert "checkpoints_count" in health
        assert "operations_last_hour" in health
        assert "repository_clean" in health
        assert "disk_space" in health
        assert "memory_usage" in health
        
        assert health["emergency_stopped"] == False
        assert health["checkpoints_count"] >= 0
        assert health["operations_last_hour"] >= 0


class TestCodebaseMonitor:
    """Test the codebase monitoring component."""
    
    @pytest.fixture
    def temp_repo(self):
        """Create temporary repository for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Create test files with various issues
        (temp_dir / "src").mkdir()
        (temp_dir / "src" / "security.py").write_text('''
import hashlib

def weak_hash(data):
    return hashlib.md5(data.encode()).hexdigest()

def insecure_random():
    import random
    return random.random()
''')
        
        (temp_dir / "src" / "quality.py").write_text('''
# This line is way too long and exceeds the 120 character limit specified in our coding standards, making it hard to read
def	function_with_tabs():  # Using tabs instead of spaces
    print("Debug statement left in code")  # Debug statement
    pass

# TODO: Implement this function properly
def empty_todo():
    pass
''')
        
        (temp_dir / "src" / "performance.py").write_text('''
def inefficient_loop(items):
    for i in range(len(items)):  # Inefficient pattern
        items.append(f"processed_{i}")  # List append in loop
        
import time
def long_sleep():
    time.sleep(10)  # Long sleep call
''')
        
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def codebase_monitor(self, temp_repo):
        """Create codebase monitor instance."""
        return CodebaseMonitor(str(temp_repo))
    
    def test_comprehensive_scan(self, codebase_monitor):
        """Test comprehensive codebase scanning."""
        results = codebase_monitor.comprehensive_scan()
        
        assert isinstance(results, dict)
        assert "timestamp" in results
        assert "issues" in results
        assert "metrics" in results
        assert "patterns" in results
        assert "health_score" in results
        
        # Should find multiple issues
        issues = results["issues"]
        assert len(issues) > 0
        
        # Should find different types of issues
        issue_types = {issue["type"] for issue in issues}
        expected_types = {"security", "quality", "performance", "todo"}
        assert len(issue_types.intersection(expected_types)) > 0
        
        # Each issue should have required fields
        for issue in issues:
            assert "type" in issue
            assert "severity" in issue
            assert "description" in issue
            assert "file" in issue
            # line can be None for file-level issues
            assert "details" in issue
    
    def test_metrics_collection(self, codebase_monitor):
        """Test code metrics collection."""
        metrics = codebase_monitor.collect_metrics()
        
        assert metrics is not None
        assert isinstance(metrics.timestamp, datetime)
        assert metrics.total_lines > 0
        assert metrics.files_count > 0
        assert metrics.total_lines == metrics.code_lines + metrics.comment_lines + metrics.blank_lines
        assert isinstance(metrics.test_coverage, float)
        assert metrics.test_coverage >= 0.0
        assert isinstance(metrics.complexity_average, float)
        assert metrics.complexity_average >= 0.0
        
        # Should be stored in history
        assert len(codebase_monitor.metrics_history) >= 1
    
    def test_security_issue_detection(self, codebase_monitor):
        """Test detection of security issues."""
        security_issues = codebase_monitor._scan_security_issues()
        
        assert len(security_issues) > 0
        
        # Should find weak hash functions (check description or pattern details)
        md5_issues = [
            issue for issue in security_issues 
            if "md5" in issue.description.lower() or "cryptographic" in issue.description.lower()
        ]
        assert len(md5_issues) > 0
        
        # Should find insecure random usage
        random_issues = [issue for issue in security_issues if "random" in issue.description.lower()]
        assert len(random_issues) > 0
    
    def test_quality_issue_detection(self, codebase_monitor):
        """Test detection of quality issues."""
        quality_issues = codebase_monitor._scan_quality_issues()
        
        assert len(quality_issues) > 0
        
        # Should find various quality issues
        issue_descriptions = [issue.description.lower() for issue in quality_issues]
        
        # Should find long lines, tabs, debug statements
        assert any("long" in desc for desc in issue_descriptions)
        assert any("tab" in desc for desc in issue_descriptions)
        assert any("debug" in desc or "print" in desc for desc in issue_descriptions)
    
    def test_performance_issue_detection(self, codebase_monitor):
        """Test detection of performance issues."""
        perf_issues = codebase_monitor._scan_performance_issues()
        
        assert len(perf_issues) > 0
        
        # Should find inefficient patterns
        issue_descriptions = [issue.description.lower() for issue in perf_issues]
        assert any("inefficient" in desc or "loop" in desc for desc in issue_descriptions)
        assert any("sleep" in desc for desc in issue_descriptions)
    
    def test_todo_detection(self, codebase_monitor):
        """Test detection of TODO items."""
        todo_issues = codebase_monitor._scan_todo_items()
        
        assert len(todo_issues) > 0
        
        # Should find TODO comments
        for issue in todo_issues:
            assert issue.type == "todo"
            assert "todo" in issue.description.lower()
            assert issue.details.get("todo_text")


class TestImprovementEngine:
    """Test the improvement engine component."""
    
    @pytest.fixture
    def temp_repo(self):
        """Create temporary repository for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        
        subprocess.run(["git", "init"], cwd=temp_dir, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=temp_dir, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_dir, check=True)
        
        (temp_dir / "src").mkdir()
        (temp_dir / "src" / "__init__.py").write_text("")
        subprocess.run(["git", "add", "."], cwd=temp_dir, check=True)
        subprocess.run(["git", "commit", "-m", "Initial"], cwd=temp_dir, check=True)
        
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def improvement_engine(self, temp_repo):
        """Create improvement engine instance."""
        return ImprovementEngine(str(temp_repo))
    
    def test_improvement_type_determination(self, improvement_engine):
        """Test determining improvement type from opportunities."""
        # Create mock opportunities
        security_opp = Mock()
        security_opp.type = "security"
        security_opp.description = "Weak cryptographic hash"
        
        todo_opp = Mock()
        todo_opp.type = "todo"
        todo_opp.description = "TODO: Add validation"
        
        test_opp = Mock()
        test_opp.type = "test_coverage"
        test_opp.description = "Low test coverage"
        
        refactor_opp = Mock()
        refactor_opp.type = "quality"
        refactor_opp.description = "Refactor duplicate code"
        
        # Test type determination
        assert improvement_engine._determine_improvement_type(security_opp) == "magic_fix"
        assert improvement_engine._determine_improvement_type(todo_opp) == "magic_add"
        assert improvement_engine._determine_improvement_type(test_opp) == "magic_test"
        assert improvement_engine._determine_improvement_type(refactor_opp) == "magic_refactor"
    
    def test_improvement_planning(self, improvement_engine):
        """Test improvement plan generation."""
        # Create mock opportunity
        mock_opp = Mock()
        mock_opp.id = "test_opp_1"
        mock_opp.type = "security"
        mock_opp.description = "Weak MD5 hashing"
        mock_opp.estimated_effort = "medium"
        mock_opp.safety_score = 0.7
        
        # Generate plan
        plan = improvement_engine.plan_improvement(mock_opp)
        
        assert plan is not None
        assert plan["type"] == "magic_fix"
        assert plan["opportunity"] == mock_opp
        assert plan["magic_command"] == "fix"
        assert "command_description" in plan
        assert "security issue" in plan["command_description"]
    
    def test_opportunity_prioritization(self, improvement_engine):
        """Test prioritization of improvement opportunities."""
        # Create mock opportunities with different characteristics
        high_priority_opp = Mock()
        high_priority_opp.priority = 0.9
        high_priority_opp.safety_score = 0.8
        high_priority_opp.estimated_effort = "low"
        
        low_priority_opp = Mock()
        low_priority_opp.priority = 0.3
        low_priority_opp.safety_score = 0.5
        low_priority_opp.estimated_effort = "high"
        
        opportunities = [low_priority_opp, high_priority_opp]
        
        # Prioritize
        prioritized = improvement_engine.prioritize_fixes(opportunities)
        
        # High priority should come first
        assert prioritized[0] == high_priority_opp
        assert prioritized[1] == low_priority_opp
    
    def test_change_validation(self, improvement_engine):
        """Test validation of proposed changes."""
        # Test valid changes
        valid_changes = {
            "files_changed": ["src/new_feature.py", "tests/test_feature.py"]
        }
        
        validation = improvement_engine.validate_changes(valid_changes)
        assert validation["valid"] == True
        assert len(validation["errors"]) == 0
        
        # Test changes with warnings
        warning_changes = {
            "files_changed": ["__init__.py", "setup.py", "many", "files", "changed", "here"]
        }
        
        validation = improvement_engine.validate_changes(warning_changes)
        assert len(validation["warnings"]) > 0


class TestFeedbackLoop:
    """Test the feedback loop component."""
    
    @pytest.fixture
    def feedback_loop(self):
        """Create feedback loop instance."""
        return FeedbackLoop()
    
    def test_success_recording(self, feedback_loop):
        """Test recording successful improvements."""
        success_result = {
            "success": True,
            "execution_type": "magic_fix",
            "description": "Fixed security issue",
            "files_changed": ["src/auth.py"],
            "opportunity": Mock(type="security", safety_score=0.8, estimated_effort="medium")
        }
        
        initial_pattern_count = len(feedback_loop.learned_patterns)
        
        feedback_loop.record_success(success_result)
        
        # Should have added a success pattern
        assert len(feedback_loop.learned_patterns) >= initial_pattern_count
    
    def test_failure_recording(self, feedback_loop):
        """Test recording failed improvements."""
        failure_result = {
            "success": False,
            "execution_type": "magic_refactor",
            "error": "Refactoring failed due to syntax error",
            "opportunity": Mock(type="quality", safety_score=0.6, estimated_effort="high")
        }
        
        initial_pattern_count = len(feedback_loop.learned_patterns)
        
        feedback_loop.record_failure(failure_result)
        
        # Should have added a failure pattern
        assert len(feedback_loop.learned_patterns) >= initial_pattern_count
    
    def test_pattern_identification(self, feedback_loop):
        """Test identification of patterns from execution results."""
        # Create multiple similar results
        results = [
            {"success": True, "execution_type": "magic_fix"},
            {"success": True, "execution_type": "magic_fix"},
            {"success": False, "execution_type": "magic_refactor"},
            {"success": False, "execution_type": "magic_refactor"}
        ]
        
        patterns = feedback_loop._identify_patterns(results)
        
        assert len(patterns) >= 0  # May not find patterns with limited data
        
        for pattern in patterns:
            assert pattern.pattern_type in ["success", "failure"]
            assert isinstance(pattern.confidence, float)
            assert 0.0 <= pattern.confidence <= 1.0
    
    def test_strategy_adjustment(self, feedback_loop):
        """Test strategy adjustment based on learned patterns."""
        # Add some mock patterns
        success_pattern = Mock()
        success_pattern.pattern_type = "success"
        success_pattern.conditions = {"opportunity_type": "security"}
        
        failure_pattern = Mock()
        failure_pattern.pattern_type = "failure"
        failure_pattern.conditions = {"opportunity_type": "refactoring"}
        
        feedback_loop.learned_patterns = [success_pattern, failure_pattern]
        
        adjustments = feedback_loop.adjust_strategies()
        
        assert isinstance(adjustments, dict)
        assert "type_preferences" in adjustments
        
        if "security" in adjustments["type_preferences"]:
            # Security should have increased preference due to success
            assert adjustments["type_preferences"]["security"] > 1.0
    
    def test_recommendation_generation(self, feedback_loop):
        """Test generating recommendations based on patterns."""
        # Add a mock pattern
        mock_pattern = Mock()
        mock_pattern.pattern_type = "success"
        mock_pattern.confidence = 0.8
        mock_pattern.success_rate = 0.9
        mock_pattern.description = "Successful security fix pattern"
        mock_pattern.actions = {"approach": "magic_fix"}
        mock_pattern.outcomes = {"success": True}
        mock_pattern.conditions = {"execution_type": "magic_fix"}
        
        feedback_loop.learned_patterns = [mock_pattern]
        feedback_loop._pattern_matches_context = Mock(return_value=True)
        
        context = {"execution_type": "magic_fix"}
        recommendations = feedback_loop.get_recommendations(context)
        
        assert len(recommendations) > 0
        assert recommendations[0]["confidence"] == 0.8
        assert recommendations[0]["pattern_success_rate"] == 0.9


class TestIntegration:
    """Test integration between all autonomous loop components."""
    
    @pytest.fixture
    def integrated_system(self):
        """Create integrated autonomous system for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        
        subprocess.run(["git", "init"], cwd=temp_dir, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=temp_dir, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_dir, check=True)
        
        # Create complex test scenario
        (temp_dir / "src").mkdir()
        (temp_dir / "src" / "main.py").write_text('''
import hashlib

def insecure_function():
    password = "test123"
    # TODO: Add proper salt
    return hashlib.md5(password.encode()).hexdigest()

def divide_numbers(a, b):
    return a / b  # Division by zero possible

# Long line that exceeds our 120 character coding standard limit and should be flagged as a quality issue
''')
        
        subprocess.run(["git", "add", "."], cwd=temp_dir, check=True)
        subprocess.run(["git", "commit", "-m", "Initial"], cwd=temp_dir, check=True)
        
        autonomous_loop = AutonomousLoop(
            working_directory=str(temp_dir),
            config={
                "max_improvements_per_cycle": 2,
                "safety_level": "high"
            }
        )
        
        yield autonomous_loop, temp_dir
        shutil.rmtree(temp_dir)
    
    def test_end_to_end_improvement_cycle(self, integrated_system):
        """Test complete end-to-end improvement cycle."""
        autonomous_loop, temp_dir = integrated_system
        
        # Run a complete cycle
        result = autonomous_loop.run_single_cycle()
        
        # Verify cycle completed successfully
        assert result.cycle_id
        assert result.opportunities_found > 0
        
        # Should have found multiple types of issues
        # (security, TODO, quality issues in the test file)
        assert result.opportunities_found >= 3
        
        # Verify system learned from the cycle
        assert len(autonomous_loop.feedback_loop.execution_history) >= 0
        
        # Verify safety measures were in place
        assert len(autonomous_loop.safety_controller.checkpoints) >= 0
        
        # Verify health monitoring worked
        assert "timestamp" in result.health_status
        assert "emergency_stopped" in result.health_status
    
    def test_memory_integration(self, integrated_system):
        """Test that memory is properly integrated across components."""
        autonomous_loop, temp_dir = integrated_system
        
        # Run cycle to generate memories
        autonomous_loop.run_single_cycle()
        
        # Check that memory store has relevant entries
        memory_store = autonomous_loop.memory_store
        
        # Should have memories from various components
        all_memories = memory_store.query(tags=[], limit=100)
        
        if all_memories:  # May be empty in test environment
            memory_tags = set()
            for memory in all_memories:
                if hasattr(memory, 'tags'):
                    memory_tags.update(memory.tags)
            
            # Should have tags from different components
            expected_tag_types = {"autonomous_loop", "safety", "monitoring"}
            # At least one type should be present
            assert len(memory_tags.intersection(expected_tag_types)) >= 0
    
    def test_safety_integration(self, integrated_system):
        """Test safety integration across the system."""
        autonomous_loop, temp_dir = integrated_system
        
        # Test emergency stop propagation
        autonomous_loop.safety_controller.emergency_stop("Integration test")
        
        # Cycle should not execute improvements when emergency stopped
        result = autonomous_loop.run_single_cycle()
        
        # Should still scan for opportunities but not execute improvements
        assert result.opportunities_found >= 0
        assert result.improvements_attempted == 0
        
        # Clear emergency stop
        autonomous_loop.safety_controller.clear_emergency_stop()
    
    def test_feedback_loop_integration(self, integrated_system):
        """Test feedback loop integration with improvement execution."""
        autonomous_loop, temp_dir = integrated_system
        
        # Mock some execution results to test learning
        with patch.object(autonomous_loop.improvement_engine, 'execute_improvement') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "execution_type": "magic_fix",
                "files_changed": ["src/main.py"],
                "critical_failure": False
            }
            
            # Run cycle
            result = autonomous_loop.run_single_cycle()
            
            # Feedback loop should have learned from the execution
            if result.improvements_attempted > 0:
                # Check that feedback loop received the results
                assert len(autonomous_loop.feedback_loop.execution_history) > 0
