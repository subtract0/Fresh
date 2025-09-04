"""Tests for CLI feature management commands.

These tests validate NECESSARY conditions for the self-documenting loop functionality.
Following the Necessary Condition Principle - each test validates that a
critical requirement for feature management is met.
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from argparse import Namespace

from ai.cli.fresh import (
    cmd_feature_inventory,
    cmd_feature_validate, 
    cmd_feature_hook_missing,
)


class TestFeatureInventoryCommand:
    """Test feature inventory command - NECESSARY for self-documenting loop."""
    
    def test_inventory_executes_feature_scanner(self, capsys):
        """NECESSARY: Inventory command must execute the feature scanner."""
        args = Namespace()
        
        with patch('ai.cli.fresh.subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = "Feature scan completed successfully"
            mock_result.stderr = ""
            mock_run.return_value = mock_result
            
            result = cmd_feature_inventory(args)
            
            # NECESSARY: Must call the feature scanner subprocess
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            # Check if the script path contains feature_inventory.py
            args_list = call_args[0][0]  # Get the first positional argument (the command list)
            assert len(args_list) >= 2, f"Expected at least 2 args, got {len(args_list)}: {args_list}"
            assert 'feature_inventory.py' in str(args_list[1])  # Script path
            assert result == 0
        
    def test_inventory_handles_scanner_failure(self, capsys):
        """NECESSARY: Inventory must handle scanner failures gracefully."""
        args = Namespace()
        
        with patch('ai.cli.fresh.subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 1
            mock_result.stdout = "Scan output"
            mock_result.stderr = "Scanner error"
            mock_run.return_value = mock_result
            
            result = cmd_feature_inventory(args)
            
            # NECESSARY: Must return failure code when scanner fails
            assert result == 1
        
        captured = capsys.readouterr()
        assert "scanner error" in captured.out.lower() or "error" in captured.out.lower()
        
    def test_inventory_shows_scanner_output(self, capsys):
        """NECESSARY: Inventory must show scanner output to user."""
        args = Namespace()
        
        expected_output = "🚀 Feature scan results: 100 features analyzed"
        
        with patch('ai.cli.fresh.subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = expected_output
            mock_result.stderr = ""
            mock_run.return_value = mock_result
            
            cmd_feature_inventory(args)
        
        captured = capsys.readouterr()
        assert expected_output in captured.out
        # NECESSARY: User must see scanner output to understand system state


class TestFeatureValidateCommand:
    """Test feature validate command - NECESSARY for quality gates."""
    
    def test_validate_runs_inventory_first(self, capsys):
        """NECESSARY: Validate must run inventory to get current state."""
        args = Namespace()
        
        with patch('ai.cli.fresh.cmd_feature_inventory') as mock_inventory:
            mock_inventory.return_value = 0  # Success
            
            cmd_feature_validate(args)
            
            # NECESSARY: Must run inventory to get current state
            mock_inventory.assert_called_once_with(args)
    
    def test_validate_fails_when_inventory_fails(self, capsys):
        """NECESSARY: Validate must fail when inventory indicates quality issues."""
        args = Namespace()
        
        with patch('ai.cli.fresh.cmd_feature_inventory') as mock_inventory:
            mock_inventory.return_value = 1  # Quality issues found
            
            result = cmd_feature_validate(args)
            
            # NECESSARY: Must fail when quality is below threshold
            assert result == 1
        
        captured = capsys.readouterr()
        assert "validation failed" in captured.out.lower()
        # NECESSARY: Clear feedback about validation failure
    
    def test_validate_succeeds_when_quality_acceptable(self, capsys):
        """NECESSARY: Validate must succeed when quality meets standards."""
        args = Namespace()
        
        with patch('ai.cli.fresh.cmd_feature_inventory') as mock_inventory:
            mock_inventory.return_value = 0  # Quality acceptable
            
            result = cmd_feature_validate(args)
            
            # NECESSARY: Must succeed when quality is acceptable
            assert result == 0
        
        captured = capsys.readouterr()
        assert "meet quality standards" in captured.out.lower()


class TestFeatureHookMissingCommand:
    """Test feature hook missing command - NECESSARY for preventing broken windows."""
    
    def test_hook_missing_loads_inventory_json(self, capsys):
        """NECESSARY: Hook missing must load feature inventory to analyze features."""
        args = Namespace()
        
        # Create mock inventory data
        mock_inventory = {
            "features": [
                {
                    "name": "TestFeature",
                    "implemented": True,
                    "hooked_up": False,
                    "module_path": "test/module.py",
                    "description": "Test feature description"
                }
            ]
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            json_path = Path(temp_dir) / "docs" / "feature_inventory.json"
            json_path.parent.mkdir(parents=True)
            
            with open(json_path, 'w') as f:
                json.dump(mock_inventory, f)
            
            # Mock the Path by patching the specific path used in the command
            with patch('builtins.open', create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_inventory)
                
                with patch.object(Path, 'exists') as mock_exists:
                    mock_exists.return_value = True
                    
                    result = cmd_feature_hook_missing(args)
                    
                    # Should successfully process the inventory
                    assert result == 0
        
        captured = capsys.readouterr()
        assert "testfeature" in captured.out.lower()
        # NECESSARY: Must analyze inventory data to identify unhooked features
    
    def test_hook_missing_handles_missing_inventory(self, capsys):
        """NECESSARY: Hook missing must handle case where inventory doesn't exist."""
        args = Namespace()
        
        with patch('ai.cli.fresh.Path') as mock_path:
            mock_path.return_value = Path("/nonexistent/feature_inventory.json")
            
            result = cmd_feature_hook_missing(args)
            
            # Should fail gracefully when inventory is missing
            assert result == 1
        
        captured = capsys.readouterr()
        assert "no feature inventory found" in captured.out.lower()
        # NECESSARY: Clear guidance when prerequisite data is missing
    
    def test_hook_missing_reports_when_all_hooked_up(self, capsys):
        """NECESSARY: Hook missing must report success when no features need hookup."""
        args = Namespace()
        
        # Create mock inventory with all features hooked up
        mock_inventory = {
            "features": [
                {
                    "name": "HookedFeature",
                    "implemented": True,
                    "hooked_up": True,
                    "module_path": "test/module.py",
                    "description": "Already hooked up feature"
                }
            ]
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            json_path = Path(temp_dir) / "docs" / "feature_inventory.json"
            json_path.parent.mkdir(parents=True)
            
            with open(json_path, 'w') as f:
                json.dump(mock_inventory, f)
            
            # Mock the Path by patching the specific path used in the command
            with patch('builtins.open', create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_inventory)
                
                with patch.object(Path, 'exists') as mock_exists:
                    mock_exists.return_value = True
                    
                    result = cmd_feature_hook_missing(args)
                    
                    assert result == 0
        
        captured = capsys.readouterr()
        assert "all implemented features are properly hooked up" in captured.out.lower()
        # NECESSARY: Positive confirmation when system is in good state
    
    def test_hook_missing_provides_specific_suggestions(self, capsys):
        """NECESSARY: Hook missing must provide actionable suggestions for fixes."""
        args = Namespace()
        
        # Create mock inventory with features that need different types of hookup
        mock_inventory = {
            "features": [
                {
                    "name": "CommandFeature", 
                    "implemented": True,
                    "hooked_up": False,
                    "module_path": "test/commands.py",
                    "description": "A command feature"
                },
                {
                    "name": "LoopEngine",
                    "implemented": True, 
                    "hooked_up": False,
                    "module_path": "test/loop.py",
                    "description": "A loop engine"
                }
            ]
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            json_path = Path(temp_dir) / "docs" / "feature_inventory.json"
            json_path.parent.mkdir(parents=True)
            
            with open(json_path, 'w') as f:
                json.dump(mock_inventory, f)
            
            # Mock the Path by patching the specific path used in the command
            with patch('builtins.open', create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_inventory)
                
                with patch.object(Path, 'exists') as mock_exists:
                    mock_exists.return_value = True
                    
                    cmd_feature_hook_missing(args)
        
        captured = capsys.readouterr()
        # NECESSARY: Must provide specific actionable suggestions
        assert "add cli command" in captured.out.lower()
        assert "autonomous loop integration" in captured.out.lower()


class TestFeatureCommandIntegration:
    """Test feature command integration - NECESSARY for CLI functionality."""
    
    def test_all_feature_commands_accept_basic_args(self):
        """NECESSARY: All feature commands must handle basic argument structure."""
        args = Namespace()
        
        # These should not crash with basic args
        with patch('ai.cli.fresh.subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = "success"
            mock_result.stderr = ""
            mock_run.return_value = mock_result
            
            try:
                # Should not raise exception
                cmd_feature_inventory(args)
            except AttributeError as e:
                pytest.fail(f"Feature inventory failed to handle basic args: {e}")
        
        with patch('ai.cli.fresh.cmd_feature_inventory') as mock_inventory:
            mock_inventory.return_value = 0
            
            try:
                # Should not raise exception
                cmd_feature_validate(args)
            except AttributeError as e:
                pytest.fail(f"Feature validate failed to handle basic args: {e}")
        
        # Hook missing needs inventory file
        with patch('ai.cli.fresh.Path') as mock_path:
            mock_path.return_value = Path("/nonexistent/path")
            
            try:
                # Should not raise exception (should handle missing file gracefully)
                result = cmd_feature_hook_missing(args)
                assert result == 1  # Expected failure for missing file
            except AttributeError as e:
                pytest.fail(f"Feature hook missing failed to handle basic args: {e}")
        
        # NECESSARY: Commands must handle their expected argument structures


class TestSelfDocumentingLoopIntegration:
    """Test self-documenting loop integration - NECESSARY for autonomous quality."""
    
    def test_feature_commands_support_autonomous_workflow(self):
        """NECESSARY: Feature commands must integrate with autonomous development workflow."""
        
        # Test that commands can be called programmatically (not just CLI)
        args = Namespace()
        
        with patch('ai.cli.fresh.subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0  # Quality acceptable
            mock_result.stdout = "Quality scan passed"
            mock_result.stderr = ""
            mock_run.return_value = mock_result
            
            # Should be callable from autonomous loop
            result = cmd_feature_inventory(args)
            assert result == 0
            
            # Should provide return codes for automated decision making  
            result = cmd_feature_validate(args)
            assert result == 0
        
        # NECESSARY: Commands must be automatable for autonomous loop integration
