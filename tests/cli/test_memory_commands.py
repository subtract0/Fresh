"""Tests for autonomous memory CLI commands.

This module tests the intelligent memory system CLI commands that were
autonomously added to provide CLI access to the initialize_intelligent_memory
function and related memory management capabilities.

Following state-of-the-art testing practices and user rules.
"""
from __future__ import annotations
import pytest
import json
import subprocess
from unittest.mock import Mock, patch, MagicMock
import os
from pathlib import Path

from ai.cli.fresh import cmd_memory_init, cmd_memory_status, cmd_memory_analytics


class TestMemoryInitCommand:
    """Test the memory init command functionality."""
    
    def test_init_dry_run_mode(self):
        """Test dry run shows what would be initialized without doing it."""
        args = Mock()
        args.dry_run = True
        args.enhanced_firestore = True
        args.force = False
        
        with patch.dict(os.environ, {
            'FIREBASE_PROJECT_ID': 'test-project',
            'FIREBASE_CLIENT_EMAIL': 'test@example.com', 
            'FIREBASE_PRIVATE_KEY': 'test-key'
        }):
            with patch('builtins.print') as mock_print:
                result = cmd_memory_init(args)
                
                assert result == 0
                # Verify dry run output
                calls = [call.args[0] for call in mock_print.call_args_list]
                assert any('DRY RUN' in call for call in calls)
                assert any('Enhanced Firestore: Yes' in call for call in calls)
                assert any('Firebase credentials: Configured' in call for call in calls)
    
    def test_init_without_firebase_credentials(self):
        """Test initialization falls back when Firebase credentials missing."""
        args = Mock()
        args.dry_run = False
        args.enhanced_firestore = True
        args.force = False
        
        with patch.dict(os.environ, {}, clear=True):
            with patch('ai.enhanced_agency.initialize_intelligent_memory') as mock_init:
                with patch('ai.memory.store.get_store') as mock_get_store:
                    with patch('ai.tools.memory_tools.WriteMemory') as mock_write:
                        mock_store = Mock()
                        mock_store.__class__.__name__ = 'IntelligentMemoryStore'
                        mock_get_store.return_value = mock_store
                        
                        mock_write_instance = Mock()
                        mock_write_instance.run = Mock()
                        mock_write.return_value = mock_write_instance
                        
                        with patch('builtins.print') as mock_print:
                            result = cmd_memory_init(args)
                            
                            assert result == 0
                            mock_init.assert_called_once_with(use_enhanced_firestore=True)
                            mock_write_instance.run.assert_called_once()
    
    def test_init_handles_initialization_error(self):
        """Test initialization handles errors gracefully."""
        args = Mock()
        args.dry_run = False
        args.enhanced_firestore = False
        args.force = False
        
        with patch('ai.enhanced_agency.initialize_intelligent_memory', side_effect=Exception("Init failed")):
            with patch('builtins.print') as mock_print:
                result = cmd_memory_init(args)
                
                assert result == 1
                calls = [call.args[0] for call in mock_print.call_args_list]
                assert any('Memory initialization failed: Init failed' in call for call in calls)
    
    def test_init_force_mode(self):
        """Test force mode warns about reinitialization.""" 
        args = Mock()
        args.dry_run = False
        args.enhanced_firestore = False
        args.force = True
        
        with patch('ai.enhanced_agency.initialize_intelligent_memory'):
            with patch('ai.memory.store.get_store'):
                with patch('ai.tools.memory_tools.WriteMemory'):
                    with patch('builtins.print') as mock_print:
                        result = cmd_memory_init(args)
                        
                        assert result == 0
                        calls = [call.args[0] for call in mock_print.call_args_list]
                        assert any('Force mode: Reinitializing' in call for call in calls)


class TestMemoryStatusCommand:
    """Test the memory status command functionality."""
    
    def test_status_basic_memory_store(self):
        """Test status with basic memory store."""
        args = Mock()
        args.verbose = False
        
        mock_store = Mock()
        mock_store.__class__.__name__ = 'InMemoryMemoryStore'
        mock_store._items = ['item1', 'item2', 'item3']
        
        with patch('ai.memory.store.get_store', return_value=mock_store):
            with patch('builtins.print') as mock_print:
                result = cmd_memory_status(args)
                
                assert result == 0
                calls = [call.args[0] for call in mock_print.call_args_list]
                assert any('Memory System Status' in call for call in calls)
                assert any('InMemoryMemoryStore' in call for call in calls)
                assert any('Stored Items: 3' in call for call in calls)
    
    def test_status_intelligent_memory_store(self):
        """Test status with intelligent memory store showing enhanced features."""
        args = Mock()
        args.verbose = False
        
        from ai.memory.intelligent_store import IntelligentMemoryStore
        mock_store = Mock(spec=IntelligentMemoryStore)
        mock_store.__class__.__name__ = 'IntelligentMemoryStore' 
        mock_store._items = ['item1', 'item2']
        mock_store.get_analytics = Mock(return_value={'total_memories': 2, 'avg_importance': 0.6})
        
        with patch('ai.memory.store.get_store', return_value=mock_store):
            with patch('builtins.print') as mock_print:
                result = cmd_memory_status(args)
                
                assert result == 0
                calls = [call.args[0] for call in mock_print.call_args_list]
                assert any('Intelligent Features:' in call for call in calls)
                assert any('Semantic Search' in call for call in calls)
                assert any('Analytics:' in call for call in calls)
    
    def test_status_verbose_mode(self):
        """Test verbose mode shows environment details."""
        args = Mock()
        args.verbose = True
        
        mock_store = Mock()
        mock_store.__class__.__name__ = 'InMemoryMemoryStore'
        mock_store._items = []
        
        with patch('ai.memory.store.get_store', return_value=mock_store):
            with patch.dict(os.environ, {
                'FIREBASE_PROJECT_ID': 'test-project-123',
                'FIREBASE_CLIENT_EMAIL': 'test@example.com',
                'FIREBASE_PRIVATE_KEY': 'test-key'
            }, clear=True):
                with patch('builtins.print') as mock_print:
                    result = cmd_memory_status(args)
                    
                    assert result == 0
                    calls = [call.args[0] for call in mock_print.call_args_list]
                    assert any('Environment:' in call for call in calls)
                    assert any('test-project-123' in call for call in calls)
    
    def test_status_handles_error(self):
        """Test status command handles errors gracefully."""
        args = Mock()
        args.verbose = False
        
        with patch('ai.memory.store.get_store', side_effect=Exception("Store error")):
            with patch('builtins.print') as mock_print:
                result = cmd_memory_status(args)
                
                assert result == 1
                calls = [call.args[0] for call in mock_print.call_args_list]
                assert any('Failed to get memory status: Store error' in call for call in calls)


class TestMemoryAnalyticsCommand:
    """Test the memory analytics command functionality."""
    
    def test_analytics_non_intelligent_store(self):
        """Test analytics warns when intelligent memory not available."""
        args = Mock()
        args.format = 'summary'
        
        mock_store = Mock()
        mock_store.__class__.__name__ = 'InMemoryMemoryStore'
        
        with patch('ai.memory.store.get_store', return_value=mock_store):
            with patch('builtins.print') as mock_print:
                result = cmd_memory_analytics(args)
                
                assert result == 1
                calls = [call.args[0] for call in mock_print.call_args_list]
                assert any('Analytics not available for InMemoryMemoryStore' in call for call in calls)
                assert any("Use 'fresh memory init'" in call for call in calls)
    
    def test_analytics_json_format(self):
        """Test analytics outputs JSON format correctly."""
        args = Mock()
        args.format = 'json'
        
        from ai.memory.intelligent_store import IntelligentMemoryStore
        mock_store = Mock(spec=IntelligentMemoryStore)
        mock_analytics = {
            'total_memories': 10,
            'memory_types': {'context': 5, 'insight': 3, 'decision': 2},
            'importance_stats': {'average': 0.65, 'high_importance': 3}
        }
        mock_store.get_analytics = Mock(return_value=mock_analytics)
        
        with patch('ai.memory.store.get_store', return_value=mock_store):
            with patch('builtins.print') as mock_print:
                result = cmd_memory_analytics(args)
                
                assert result == 0
                # Verify JSON output
                printed_json = mock_print.call_args_list[-1].args[0] 
                parsed = json.loads(printed_json)
                assert parsed['total_memories'] == 10
                assert parsed['memory_types']['context'] == 5
    
    def test_analytics_summary_format(self):
        """Test analytics summary format shows key metrics."""
        args = Mock()
        args.format = 'summary'
        
        from ai.memory.intelligent_store import IntelligentMemoryStore
        mock_store = Mock(spec=IntelligentMemoryStore) 
        mock_analytics = {
            'total_memories': 15,
            'memory_types': {'context': 10, 'insight': 5},
            'importance_stats': {'average': 0.72, 'high_importance': 8},
            'top_keywords': ['python', 'autonomous', 'memory', 'agent', 'development']
        }
        mock_store.get_analytics = Mock(return_value=mock_analytics)
        
        with patch('ai.memory.store.get_store', return_value=mock_store):
            with patch('builtins.print') as mock_print:
                result = cmd_memory_analytics(args)
                
                assert result == 0
                calls = [call.args[0] for call in mock_print.call_args_list]
                assert any('Total Memories: 15' in call for call in calls)
                assert any('context: 10' in call for call in calls)
                assert any('Average: 0.72' in call for call in calls)
                assert any('python, autonomous, memory' in call for call in calls)
    
    def test_analytics_table_format(self):
        """Test analytics table format displays structured data."""
        args = Mock()
        args.format = 'table'
        
        from ai.memory.intelligent_store import IntelligentMemoryStore
        mock_store = Mock(spec=IntelligentMemoryStore)
        mock_analytics = {
            'basic_stats': {'total': 20, 'classified': 18},
            'performance': {'avg_response_time': 0.15}
        }
        mock_store.get_analytics = Mock(return_value=mock_analytics)
        
        with patch('ai.memory.store.get_store', return_value=mock_store):
            with patch('builtins.print') as mock_print:
                result = cmd_memory_analytics(args)
                
                assert result == 0
                calls = [call.args[0] for call in mock_print.call_args_list]
                assert any('basic_stats:' in call for call in calls)
                assert any('total                20' in call for call in calls)
    
    def test_analytics_handles_error(self):
        """Test analytics handles errors gracefully."""
        args = Mock()
        args.format = 'summary'
        
        from ai.memory.intelligent_store import IntelligentMemoryStore
        mock_store = Mock(spec=IntelligentMemoryStore)
        mock_store.get_analytics = Mock(side_effect=Exception("Analytics error"))
        
        with patch('ai.memory.store.get_store', return_value=mock_store):
            with patch('builtins.print') as mock_print:
                result = cmd_memory_analytics(args)
                
                assert result == 1
                calls = [call.args[0] for call in mock_print.call_args_list]
                assert any('Analytics error: Analytics error' in call for call in calls)


class TestMemoryCommandIntegration:
    """Integration tests for memory commands."""
    
    @pytest.mark.skipif(not os.getenv("INTEGRATION_TESTS"), reason="Integration tests disabled")
    def test_memory_cli_help(self):
        """Test that memory CLI help works."""
        result = subprocess.run(['poetry', 'run', 'python', '-m', 'ai.cli.fresh', 'memory', '--help'], 
                              cwd=Path(__file__).parent.parent.parent,
                              capture_output=True, text=True)
        assert result.returncode == 0
        assert 'Intelligent memory system management' in result.stdout
        assert 'init' in result.stdout
        assert 'status' in result.stdout  
        assert 'analytics' in result.stdout
    
    @pytest.mark.skipif(not os.getenv("INTEGRATION_TESTS"), reason="Integration tests disabled")
    def test_memory_init_help(self):
        """Test memory init command help."""
        result = subprocess.run(['poetry', 'run', 'python', '-m', 'ai.cli.fresh', 'memory', 'init', '--help'],
                              cwd=Path(__file__).parent.parent.parent,
                              capture_output=True, text=True)
        assert result.returncode == 0
        assert 'Initialize intelligent memory system' in result.stdout
        assert '--enhanced-firestore' in result.stdout
        assert '--dry-run' in result.stdout
        assert '--force' in result.stdout
