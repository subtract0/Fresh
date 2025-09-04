"""
Integration tests for autonomous loop CLI integration.
Tests that the autonomous loop can be controlled via CLI.
"""

import pytest
import tempfile
import subprocess
import json
from pathlib import Path
from unittest.mock import patch

from ai.cli.fresh import FreshCLI
from ai.autonomous import AutonomousLoop
from ai.memory.intelligent_store import IntelligentMemoryStore


class TestAutonomousCLI:
    """Test CLI integration with autonomous loop."""
    
    @pytest.fixture
    def temp_repo(self):
        """Create temporary repository for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Initialize as git repo
        subprocess.run(["git", "init"], cwd=temp_dir, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=temp_dir, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_dir, check=True)
        
        # Create a simple Python file with issues
        (temp_dir / "test_code.py").write_text('''
def divide_numbers(a, b):
    return a / b  # Bug: no division by zero check

# TODO: Add proper error handling
def process_data(data):
    print(f"Processing {len(data)} items")  # Debug print left in
    return [item * 2 for item in data]
''')
        
        # Initial commit
        subprocess.run(["git", "add", "."], cwd=temp_dir, check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=temp_dir, check=True)
        
        yield temp_dir
        import shutil
        shutil.rmtree(temp_dir)
    
    def test_autonomous_loop_basic_functionality(self, temp_repo):
        """Test that autonomous loop can be created and run basic cycle."""
        # Create autonomous loop instance
        autonomous_loop = AutonomousLoop(
            working_directory=str(temp_repo),
            config={
                "max_improvements_per_cycle": 1,  # Keep it simple for testing
                "safety_level": "high"
            }
        )
        
        # Test initialization
        assert autonomous_loop.working_directory == temp_repo
        assert autonomous_loop.safety_controller is not None
        assert autonomous_loop.codebase_monitor is not None  
        assert autonomous_loop.improvement_engine is not None
        assert autonomous_loop.feedback_loop is not None
        
        # Test status before running
        status = autonomous_loop.get_status()
        assert status["running"] == False
        assert status["total_cycles"] == 0
        
        # Test discovery phase (shouldn't crash)
        opportunities = autonomous_loop._discovery_phase()
        assert isinstance(opportunities, list)
        
        # Should find some opportunities in our test code
        assert len(opportunities) > 0
    
    def test_autonomous_loop_status_reporting(self, temp_repo):
        """Test autonomous loop status reporting functionality."""
        autonomous_loop = AutonomousLoop(
            working_directory=str(temp_repo)
        )
        
        status = autonomous_loop.get_status()
        
        # Check status structure
        assert "running" in status
        assert "emergency_stopped" in status
        assert "current_cycle" in status
        assert "total_cycles" in status
        assert "recent_cycles" in status
        assert "health" in status
        assert "config" in status
        
        # Check initial values
        assert status["running"] == False
        assert status["emergency_stopped"] == False
        assert status["current_cycle"] is None
        assert status["total_cycles"] == 0
        assert isinstance(status["recent_cycles"], list)
        assert isinstance(status["health"], dict)
        assert isinstance(status["config"], dict)
    
    def test_autonomous_loop_cycle_execution(self, temp_repo):
        """Test running a single autonomous loop cycle."""
        autonomous_loop = AutonomousLoop(
            working_directory=str(temp_repo),
            config={
                "max_improvements_per_cycle": 1,  # Limit for testing
                "safety_level": "high"
            }
        )
        
        # Mock the improvement engine to avoid actual file changes
        with patch.object(autonomous_loop.improvement_engine, 'execute_improvement') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "description": "Test improvement",
                "files_changed": ["test_code.py"],
                "execution_type": "magic_fix",
                "critical_failure": False
            }
            
            # Run a single cycle
            result = autonomous_loop.run_single_cycle()
            
            # Check cycle result
            assert result.cycle_id.startswith("cycle_")
            assert isinstance(result.opportunities_found, int)
            assert isinstance(result.improvements_attempted, int)
            assert isinstance(result.improvements_successful, int)
            assert result.opportunities_found > 0  # Should find issues in test code
            
            # Check that cycle is stored in history
            assert len(autonomous_loop.cycle_history) == 1
            assert autonomous_loop.cycle_history[0].cycle_id == result.cycle_id
    
    def test_continuous_loop_start_stop(self, temp_repo):
        """Test starting and stopping continuous autonomous loop."""
        autonomous_loop = AutonomousLoop(
            working_directory=str(temp_repo),
            config={
                "scan_interval": 1,  # Very short interval for testing
                "max_improvements_per_cycle": 1
            }
        )
        
        # Should not be running initially
        assert not autonomous_loop.running
        
        # Start continuous loop
        autonomous_loop.start_continuous_loop()
        
        # Should be running
        assert autonomous_loop.running
        assert autonomous_loop._loop_thread is not None
        
        # Stop continuous loop quickly
        autonomous_loop.stop_continuous_loop()
        
        # Should be stopped
        assert not autonomous_loop.running
    
    def test_emergency_stop_functionality(self, temp_repo):
        """Test emergency stop functionality."""
        autonomous_loop = AutonomousLoop(
            working_directory=str(temp_repo)
        )
        
        # Should not be emergency stopped initially
        assert not autonomous_loop.safety_controller.is_emergency_stopped()
        
        # Activate emergency stop
        autonomous_loop.safety_controller.emergency_stop("Test emergency stop")
        
        # Should be emergency stopped
        assert autonomous_loop.safety_controller.is_emergency_stopped()
        
        # Should not be able to start continuous loop
        autonomous_loop.start_continuous_loop()
        assert not autonomous_loop.running
        
        # Clear emergency stop
        autonomous_loop.safety_controller.clear_emergency_stop()
        
        # Should not be emergency stopped
        assert not autonomous_loop.safety_controller.is_emergency_stopped()
    
    def test_feedback_loop_integration(self, temp_repo):
        """Test feedback loop integration."""
        autonomous_loop = AutonomousLoop(
            working_directory=str(temp_repo)
        )
        
        # Test that feedback loop is properly initialized
        assert autonomous_loop.feedback_loop is not None
        assert isinstance(autonomous_loop.feedback_loop.learned_patterns, list)
        assert isinstance(autonomous_loop.feedback_loop.execution_history, list)
        
        # Test feedback loop configuration
        assert autonomous_loop.feedback_loop.config is not None
        assert "min_confidence_threshold" in autonomous_loop.feedback_loop.config
        assert "max_patterns" in autonomous_loop.feedback_loop.config
        
        # Test that feedback loop can record results
        test_result = {
            "success": True,
            "execution_type": "magic_fix",
            "description": "Test fix",
            "files_changed": ["test_code.py"]
        }
        
        # Should not crash
        autonomous_loop.feedback_loop.record_success(test_result)
        
        # Should store in memory
        memories = autonomous_loop.feedback_loop.memory_store.query(
            tags=["feedback_loop", "success"]
        )
        assert len(memories) > 0
    
    def test_memory_integration(self, temp_repo):
        """Test memory integration across autonomous loop components."""
        memory_store = IntelligentMemoryStore()
        
        autonomous_loop = AutonomousLoop(
            working_directory=str(temp_repo),
            memory_store=memory_store
        )
        
        # All components should use the same memory store
        assert autonomous_loop.memory_store is memory_store
        assert autonomous_loop.safety_controller.memory_store is memory_store
        assert autonomous_loop.codebase_monitor.memory_store is memory_store
        assert autonomous_loop.improvement_engine.memory_store is memory_store
        assert autonomous_loop.feedback_loop.memory_store is memory_store
        
        # Test that running a cycle creates memories
        with patch.object(autonomous_loop.improvement_engine, 'execute_improvement') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "description": "Test improvement",
                "files_changed": ["test_code.py"],
                "critical_failure": False
            }
            
            # Run cycle
            result = autonomous_loop.run_single_cycle()
            
            # Should have created memory entries
            all_memories = memory_store.query(tags=[], limit=100)
            assert len(all_memories) > 0
    
    def test_component_interaction(self, temp_repo):
        """Test that autonomous loop components interact correctly."""
        autonomous_loop = AutonomousLoop(
            working_directory=str(temp_repo),
            config={"max_improvements_per_cycle": 1}
        )
        
        # Test discovery phase
        opportunities = autonomous_loop._discovery_phase()
        assert len(opportunities) > 0
        
        # Test that each opportunity has required fields
        for opp in opportunities:
            assert hasattr(opp, 'id')
            assert hasattr(opp, 'type')
            assert hasattr(opp, 'priority')
            assert hasattr(opp, 'description')
            assert hasattr(opp, 'safety_score')
            assert hasattr(opp, 'estimated_effort')
        
        # Test planning phase
        planned_improvements = autonomous_loop._planning_phase(opportunities[:1])  # Limit to 1
        
        # Should create valid improvement plans
        assert isinstance(planned_improvements, list)
        
        # Test that safety validation is working
        for plan in planned_improvements:
            assert "opportunity" in plan
            assert "safety_validated" in plan
            assert plan["safety_validated"] == True  # Should only include safe plans
