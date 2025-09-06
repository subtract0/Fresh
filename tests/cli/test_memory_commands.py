#!/usr/bin/env python3
"""
Tests for Memory Management CLI Commands

Testing the autonomous hookup of memory-related features following TDD principles.
These tests define the expected behavior for memory CLI commands.
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import os
import sys
from io import StringIO

from ai.cli.fresh import main
from ai.memory.intelligent_store import IntelligentMemoryStore
try:
    from ai.tools.enhanced_memory_tools import SmartWriteMemory, SemanticSearchMemory
except ImportError:
    SmartWriteMemory = None
    SemanticSearchMemory = None


class TestMemoryCommandGroup:
    """Test suite for memory CLI command group."""
    
    def test_memory_help_command(self, monkeypatch, capsys):
        """Test that 'fresh memory --help' shows memory management options."""
        monkeypatch.setattr(sys, 'argv', ['fresh', 'memory', '--help'])
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert 'memory management' in captured.out.lower()
        assert 'write' in captured.out.lower()
        assert 'search' in captured.out.lower()
        assert 'analytics' in captured.out.lower()
    
    def test_memory_write_command_basic(self):
        """Test basic memory write command."""
        with patch('ai.memory.store.get_store') as mock_store:
            mock_memory_store = Mock()
            mock_store.return_value = mock_memory_store
            mock_memory_store.write.return_value = Mock(id='mem_123')
            
            result = main(['memory', 'write', 'Test memory content', '--tags', 'test,demo'])
            
            mock_memory_store.write.assert_called_once()
            args, kwargs = mock_memory_store.write.call_args
            # Check that content is passed as keyword argument
            assert kwargs.get('content') == 'Test memory content'
            assert 'test' in kwargs.get('tags', [])
    
    def test_memory_search_command(self):
        """Test memory search command."""
        with patch('ai.memory.store.get_store') as mock_store:
            mock_memory_store = Mock()
            mock_store.return_value = mock_memory_store
            mock_memory_store.query.return_value = [
                Mock(id='mem_1', content='Test result 1', tags=['tag1'], importance_score=0.8),
                Mock(id='mem_2', content='Test result 2', tags=['tag2'], importance_score=0.6)
            ]
            
            exit_code = main(['memory', 'search', 'test query', '--limit', '10'])
            
            mock_memory_store.query.assert_called_once()
            # CLI should succeed
            assert exit_code == 0
    
    def test_memory_analytics_command(self, capsys):
        """Test memory analytics command."""
        with patch('ai.memory.intelligent_store.IntelligentMemoryStore') as mock_cls:
            mock_store = Mock()
            mock_cls.return_value = mock_store
            mock_store.get_memory_analytics.return_value = {
                'total_memories': 150,
                'memory_types': {'KNOWLEDGE': 50, 'TASK': 30, 'GOAL': 20},
                'average_importance': 0.65
            }
            
            exit_code = main(['memory', 'analytics', '--json'])
            
            mock_store.get_memory_analytics.assert_called_once()
            assert exit_code == 0
            
            # Parse JSON output
            captured = capsys.readouterr()
            result = json.loads(captured.out)
            assert 'total_memories' in result
            assert result['total_memories'] == 150
    
    def test_memory_optimize_command(self, capsys):
        """Test memory optimization command."""
        with patch('ai.memory.intelligent_store.IntelligentMemoryStore') as mock_cls:
            mock_store = Mock()
            mock_cls.return_value = mock_store
            mock_store.optimize_memory.return_value = {
                'removed_count': 25,
                'remaining_count': 125,
                'space_saved_mb': 2.3
            }
            
            exit_code = main(['memory', 'optimize', '--dry-run', '--json'])
            
            mock_store.optimize_memory.assert_called_once_with(dry_run=True, threshold=0.3)
            assert exit_code == 0
            
            # Parse JSON output
            captured = capsys.readouterr()
            result = json.loads(captured.out)
            assert result['removed_count'] == 25
    
    def test_memory_backup_command(self):
        """Test memory backup command."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
            temp_path = temp_file.name
            
        try:
            with patch('ai.memory.store.get_store') as mock_store:
                mock_memory_store = Mock()
                mock_store.return_value = mock_memory_store
                mock_memory_store.query.return_value = [
                    Mock(id='mem_1', content='Memory 1', to_dict=lambda: {'id': 'mem_1', 'content': 'Memory 1'}),
                    Mock(id='mem_2', content='Memory 2', to_dict=lambda: {'id': 'mem_2', 'content': 'Memory 2'})
                ]
                
                exit_code = main(['memory', 'backup', temp_path])
                
                assert exit_code == 0
                assert os.path.exists(temp_path)
                
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestEnhancedMemoryTools:
    """Test suite for enhanced memory tools integration."""
    
    def test_smart_write_memory_tool_accessible(self, capsys):
        """Test that SmartWriteMemory tool is accessible through CLI."""
        if SmartWriteMemory is None:
            pytest.skip("SmartWriteMemory not available")
            
        with patch.object(SmartWriteMemory, 'run') as mock_run:
            mock_run.return_value = "Memory stored with ID: mem_456"
            
            exit_code = main(['memory', 'smart-write', 'Advanced memory content', '--auto-classify'])
            
            mock_run.assert_called_once()
            assert exit_code == 0
            
            # Check captured output
            captured = capsys.readouterr()
            assert 'Memory stored with ID:' in captured.out
    
    def test_semantic_search_memory_tool_accessible(self, capsys):
        """Test that SemanticSearchMemory tool is accessible through CLI.""" 
        if SemanticSearchMemory is None:
            pytest.skip("SemanticSearchMemory not available")
            
        with patch.object(SemanticSearchMemory, 'run') as mock_run:
            mock_run.return_value = [
                {'id': 'mem_1', 'content': 'Related memory 1', 'relevance_score': 0.89},
                {'id': 'mem_2', 'content': 'Related memory 2', 'relevance_score': 0.76}
            ]
            
            exit_code = main(['memory', 'semantic-search', 'machine learning concepts'])
            
            mock_run.assert_called_once()
            assert exit_code == 0
            
            # Check captured output
            captured = capsys.readouterr()
            assert 'Semantic search results' in captured.out
            assert 'Related memory 1' in captured.out


class TestMemoryCommandValidation:
    """Test input validation for memory commands."""
    
    def test_memory_write_requires_content(self):
        """Test that memory write command requires content."""
        with pytest.raises(SystemExit):
            main(['memory', 'write'])
    
    def test_memory_search_requires_query(self):
        """Test that memory search command requires query."""
        with pytest.raises(SystemExit):
            main(['memory', 'search'])
    
    def test_memory_backup_requires_path(self):
        """Test that memory backup command requires output path."""
        with pytest.raises(SystemExit):
            main(['memory', 'backup'])
    
    def test_memory_command_invalid_subcommand(self):
        """Test handling of invalid memory subcommands."""
        with pytest.raises(SystemExit):
            main(['memory', 'invalid-command'])


class TestMemoryJSONOutput:
    """Test JSON output formatting for memory commands."""
    
    def test_memory_search_json_output(self, capsys):
        """Test that memory search can output JSON format."""
        with patch('ai.memory.store.get_store') as mock_store:
            mock_memory_store = Mock()
            mock_store.return_value = mock_memory_store
            mock_memory_store.query.return_value = [
                Mock(id='mem_1', content='Test 1', to_dict=lambda: {'id': 'mem_1', 'content': 'Test 1'}),
                Mock(id='mem_2', content='Test 2', to_dict=lambda: {'id': 'mem_2', 'content': 'Test 2'})
            ]
            
            main(['memory', 'search', 'test', '--json'])
            
            captured = capsys.readouterr()
            result = json.loads(captured.out)
            assert 'memories' in result
            assert len(result['memories']) == 2
    
    def test_memory_analytics_json_output(self, capsys):
        """Test that memory analytics outputs valid JSON."""
        with patch('ai.memory.intelligent_store.IntelligentMemoryStore') as mock_cls:
            mock_store = Mock()
            mock_cls.return_value = mock_store
            mock_store.get_memory_analytics.return_value = {
                'total_memories': 100,
                'memory_types': {'KNOWLEDGE': 40, 'TASK': 30, 'GOAL': 30},
                'average_importance': 0.72
            }
            
            main(['memory', 'analytics', '--json'])
            
            captured = capsys.readouterr()
            result = json.loads(captured.out)
            assert 'total_memories' in result
            assert 'memory_types' in result