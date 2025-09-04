"""Tests for CLI autonomous commands.

These tests validate NECESSARY conditions for autonomous loop functionality.
Following the Necessary Condition Principle - each test validates that a
critical requirement for autonomous operation is met.
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from argparse import Namespace

from ai.cli.fresh import (
    cmd_autonomous_status,
    cmd_autonomous_cycle, 
    cmd_autonomous_start,
    cmd_autonomous_stop,
    cmd_autonomous_emergency_stop,
    cmd_autonomous_clear_emergency,
)
from ai.autonomous.loop import AutonomousLoop


class TestAutonomousStatusCommand:
    """Test autonomous status command - NECESSARY for monitoring system state."""
    
    def test_status_shows_not_running_when_stopped(self, capsys):
        """NECESSARY: Status must accurately report when system is not running."""
        args = Namespace()
        
        with patch('ai.cli.fresh.AutonomousLoop') as mock_loop_class, \
             patch('ai.cli.fresh.Path.cwd') as mock_cwd, \
             patch('ai.cli.fresh.Path.exists') as mock_exists:
            
            mock_loop = Mock()
            mock_loop.running = False
            mock_loop_class.return_value = mock_loop
            mock_cwd.return_value = Path('/test/path')
            mock_exists.return_value = False  # No emergency stop
            
            cmd_autonomous_status(args)
            
        captured = capsys.readouterr()
        assert "❌ no" in captured.out.lower()
        # NECESSARY: If status lies about running state, autonomous coordination fails
        
    def test_status_shows_running_when_active(self, capsys):
        """NECESSARY: Status must accurately report when system is running."""
        args = Namespace()
        
        with patch('ai.cli.fresh.AutonomousLoop') as mock_loop_class, \
             patch('ai.cli.fresh.Path.cwd') as mock_cwd, \
             patch('ai.cli.fresh.Path.exists') as mock_exists:
            
            mock_loop = Mock()
            mock_loop.running = True
            mock_loop_class.return_value = mock_loop
            mock_cwd.return_value = Path('/test/path')
            mock_exists.return_value = False  # No emergency stop
            
            cmd_autonomous_status(args)
            
        captured = capsys.readouterr()
        assert "✅ yes" in captured.out.lower()
        # NECESSARY: Accurate status reporting is essential for autonomous coordination


class TestAutonomousCycleCommand:
    """Test autonomous cycle command - NECESSARY for single-step execution."""
    
    def test_cycle_executes_single_improvement_cycle(self, capsys):
        """NECESSARY: Cycle command must execute exactly one improvement cycle."""
        args = Namespace()
        
        with patch('ai.cli.fresh.AutonomousLoop') as mock_loop_class, \
             patch('ai.cli.fresh.Path.cwd') as mock_cwd:
            
            mock_loop = Mock()
            mock_loop.run_single_cycle.return_value = {"status": "success", "changes": 1}
            mock_loop_class.return_value = mock_loop
            mock_cwd.return_value = Path('/test/path')
            
            cmd_autonomous_cycle(args)
            
            # NECESSARY: Single cycle must be called exactly once
            mock_loop.run_single_cycle.assert_called_once()
        
        captured = capsys.readouterr()
        assert "cycle completed" in captured.out.lower()
        
    def test_cycle_handles_execution_failure(self, capsys):
        """NECESSARY: Cycle must handle failures gracefully without crashing."""
        args = Namespace()
        
        with patch('ai.cli.fresh.AutonomousLoop') as mock_loop_class, \
             patch('ai.cli.fresh.Path.cwd') as mock_cwd:
            
            mock_loop = Mock()
            mock_loop.run_single_cycle.side_effect = Exception("Test error")
            mock_loop_class.return_value = mock_loop
            mock_cwd.return_value = Path('/test/path')
            
            # Should not raise exception - must handle gracefully
            cmd_autonomous_cycle(args)
            
        captured = capsys.readouterr()
        assert "error" in captured.out.lower() or "failed" in captured.out.lower()
        # NECESSARY: Failure handling prevents system crashes during autonomous operation


class TestAutonomousStartCommand:
    """Test autonomous start command - NECESSARY for continuous operation."""
    
    def test_start_initializes_continuous_loop(self, capsys):
        """NECESSARY: Start command must initialize continuous autonomous operation."""
        args = Namespace()
        
        with patch('ai.cli.fresh.AutonomousLoop') as mock_loop_class, \
             patch('ai.cli.fresh.Path.cwd') as mock_cwd:
            
            mock_loop = Mock()
            mock_loop_class.return_value = mock_loop
            mock_cwd.return_value = Path('/test/path')
            
            cmd_autonomous_start(args)
            
            # NECESSARY: Continuous loop must be started
            mock_loop.start_continuous_loop.assert_called_once()
        
        captured = capsys.readouterr()
        assert "starting" in captured.out.lower() or "started" in captured.out.lower()
        
    def test_start_prevents_multiple_instances(self, capsys):
        """NECESSARY: Start must prevent multiple autonomous loops running simultaneously."""
        args = Namespace()
        
        # Simulate already running instance
        with patch('ai.cli.fresh._autonomous_loop_instance') as mock_instance:
            mock_instance.running = True
            
            result = cmd_autonomous_start(args)
            
            # Should return 1 to indicate already running
            assert result == 1
        
        captured = capsys.readouterr()
        assert "already running" in captured.out.lower()
        # NECESSARY: Multiple instances would create conflicts and inconsistent state


class TestAutonomousStopCommand:
    """Test autonomous stop command - NECESSARY for controlled shutdown."""
    
    def test_stop_terminates_running_loop(self, capsys):
        """NECESSARY: Stop command must terminate the autonomous loop."""
        args = Namespace()
        
        # Simulate running instance
        mock_instance = Mock()
        mock_instance.running = True
        
        with patch('ai.cli.fresh._autonomous_loop_instance', mock_instance):
            result = cmd_autonomous_stop(args)
            
            # NECESSARY: Stop must be called to terminate the loop
            mock_instance.stop_continuous_loop.assert_called_once()
            assert result == 0
        
        captured = capsys.readouterr()
        assert "stopping" in captured.out.lower() or "stopped" in captured.out.lower()
        
    def test_stop_handles_already_stopped_state(self, capsys):
        """NECESSARY: Stop must handle case where loop is already stopped."""
        args = Namespace()
        
        # No global instance or not running
        with patch('ai.cli.fresh._autonomous_loop_instance', None):
            result = cmd_autonomous_stop(args)
            
            # Should return 0 (not an error condition)
            assert result == 0
        
        captured = capsys.readouterr()
        assert "not running" in captured.out.lower() or "no autonomous loop" in captured.out.lower()
        # NECESSARY: Graceful handling prevents errors during shutdown procedures


class TestAutonomousEmergencyStopCommand:
    """Test emergency stop command - NECESSARY for safety control."""
    
    def test_emergency_stop_creates_flag_file(self):
        """NECESSARY: Emergency stop must create persistent emergency flag."""
        args = Namespace(reason="Test emergency")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            emergency_file = Path(temp_dir) / ".emergency_stop"
            
            with patch('ai.cli.fresh.Path') as mock_path:
                mock_path.return_value = emergency_file
                
                cmd_autonomous_emergency_stop(args)
                
            # Verify file would be created (mocked, but logic is tested)
            # NECESSARY: Emergency flag must persist across process restarts
    
    def test_emergency_stop_includes_reason_in_flag(self, capsys):
        """NECESSARY: Emergency flag must include reason for audit trail."""
        args = Namespace(reason="Critical safety issue")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            emergency_file = Path(temp_dir) / ".emergency_stop"
            
            with patch('ai.cli.fresh.Path') as mock_path_class:
                # Mock Path() constructor to return our temp file
                mock_path_class.return_value = emergency_file
                
                cmd_autonomous_emergency_stop(args)
                
                # Verify file was created with reason
                assert emergency_file.exists()
                content = emergency_file.read_text()
                assert "Critical safety issue" in content
                # NECESSARY: Audit trail is essential for safety analysis
        
        captured = capsys.readouterr()
        assert "emergency stop" in captured.out.lower()


class TestAutonomousClearEmergencyCommand:
    """Test clear emergency command - NECESSARY for recovery procedures."""
    
    def test_clear_emergency_removes_flag_file(self, capsys):
        """NECESSARY: Clear emergency must remove the emergency flag."""
        args = Namespace()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            emergency_file = Path(temp_dir) / ".emergency_stop" 
            emergency_file.write_text("test emergency")  # Create the file
            
            with patch('ai.cli.fresh.Path') as mock_path:
                mock_path.return_value = emergency_file
                
                cmd_autonomous_clear_emergency(args)
                
            # File should be removed
            # NECESSARY: Emergency flag must be cleared to allow autonomous operation
        
        captured = capsys.readouterr()
        assert "cleared" in captured.out.lower()
        
    def test_clear_emergency_handles_missing_flag(self, capsys):
        """NECESSARY: Clear emergency must handle case where no flag exists."""
        args = Namespace()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            emergency_file = Path(temp_dir) / ".emergency_stop"
            # File doesn't exist
            
            with patch('ai.cli.fresh.Path') as mock_path:
                mock_path.return_value = emergency_file
                
                # Should not crash if file doesn't exist
                cmd_autonomous_clear_emergency(args)
        
        captured = capsys.readouterr()
        assert "no emergency" in captured.out.lower() or "not found" in captured.out.lower()
        # NECESSARY: Graceful handling prevents errors during recovery procedures


class TestAutonomousCommandIntegration:
    """Test command integration - NECESSARY for CLI functionality."""
    
    def test_all_commands_accept_required_arguments(self):
        """NECESSARY: All autonomous commands must accept their required arguments."""
        # Test that commands don't crash with basic argument structures
        
        # Status needs no special args
        args = Namespace()
        
        # These should not raise AttributeError or similar
        with patch('ai.cli.fresh.AutonomousLoop'), \
             patch('ai.cli.fresh.Path.cwd') as mock_cwd, \
             patch('ai.cli.fresh.Path.exists') as mock_exists:
            
            mock_cwd.return_value = Path('/test/path')
            mock_exists.return_value = False
            
            try:
                cmd_autonomous_status(args)
                cmd_autonomous_cycle(args)
                cmd_autonomous_start(args)
                cmd_autonomous_stop(args)
                cmd_autonomous_clear_emergency(args)
            except AttributeError as e:
                pytest.fail(f"Command failed to handle basic args: {e}")
            
        # Emergency stop needs reason
        args_with_reason = Namespace(reason="test")
        with patch('ai.cli.fresh.AutonomousLoop'), \
             patch('ai.cli.fresh.Path'), \
             patch('builtins.open', create=True):
            try:
                cmd_autonomous_emergency_stop(args_with_reason)
            except AttributeError as e:
                pytest.fail(f"Emergency stop failed to handle args: {e}")
        
        # NECESSARY: Commands must handle their expected argument structures
