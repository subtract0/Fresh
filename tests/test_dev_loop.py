"""Tests for the autonomous development loop.

Tests the main loop that connects repository scanning,
agent spawning, and PR creation.
"""
from __future__ import annotations
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import asyncio

from ai.loop.dev_loop import (
    DevLoop,
    run_development_cycle,
    run_continuous_loop,
    process_task
)
from ai.loop.repo_scanner import Task, TaskType
from ai.agents.mother import AgentResult


class TestDevLoop:
    """Test the development loop functionality."""
    
    def test_dev_loop_initialization(self):
        """Test DevLoop initialization."""
        loop = DevLoop()
        
        assert loop is not None
        assert loop.mother_agent is not None
        assert loop.scanner is not None
        assert loop.processed_tasks == []
    
    @pytest.mark.asyncio
    async def test_single_development_cycle(self):
        """Test running a single development cycle."""
        loop = DevLoop()
        
        # Mock scanner to return test tasks
        test_tasks = [
            Task(
                type=TaskType.TODO,
                description="TODO: Test task",
                file_path="test.py",
                line_number=1,
                priority=2
            )
        ]
        
        with patch.object(loop.scanner, 'scan', return_value=test_tasks):
            with patch.object(loop.mother_agent, 'run') as mock_run:
                mock_run.return_value = AgentResult(
                    agent_name="test",
                    agent_type="Developer",
                    instructions="Fix TODO",
                    model="gpt-4",
                    output_type="code",
                    success=True,
                    output="Fixed"
                )
                
                results = await loop.run_cycle()
        
        assert len(results) == 1
        assert results[0].success is True
        assert len(loop.processed_tasks) == 1
    
    def test_process_single_task(self):
        """Test processing a single task."""
        loop = DevLoop()
        
        task = Task(
            type=TaskType.FIXME,
            description="FIXME: Critical bug",
            file_path="app.py",
            line_number=42,
            priority=5
        )
        
        with patch.object(loop.mother_agent, 'run') as mock_run:
            mock_run.return_value = AgentResult(
                agent_name="fixer",
                agent_type="Developer",
                instructions="Fix critical bug",
                model="gpt-4",
                output_type="code",
                success=True,
                output="Bug fixed"
            )
            
            result = loop.process_task(task)
        
        assert result.success is True
        assert result.output == "Bug fixed"
    
    @pytest.mark.asyncio
    async def test_skip_already_processed_tasks(self):
        """Test that already processed tasks are skipped."""
        loop = DevLoop()
        
        task = Task(
            type=TaskType.TODO,
            description="TODO: Already done",
            file_path="done.py",
            line_number=1
        )
        
        # Add to processed list
        loop.processed_tasks.append(task)
        
        # Mock scanner to return the same task
        with patch.object(loop.scanner, 'scan', return_value=[task]):
            with patch.object(loop.mother_agent, 'run') as mock_run:
                results = await loop.run_cycle()
        
        # Should not call mother agent for already processed task
        mock_run.assert_not_called()
        assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_task_filtering_by_type(self):
        """Test filtering tasks by type."""
        loop = DevLoop(task_types=[TaskType.FAILING_TEST])
        
        tasks = [
            Task(type=TaskType.TODO, description="TODO", file_path="a.py", line_number=1),
            Task(type=TaskType.FAILING_TEST, description="Test fail", file_path="test.py", line_number=1),
            Task(type=TaskType.FIXME, description="FIXME", file_path="b.py", line_number=1),
        ]
        
        filtered = loop.filter_tasks(tasks)
        
        assert len(filtered) == 1
        assert filtered[0].type == TaskType.FAILING_TEST
    
    @pytest.mark.asyncio
    async def test_max_tasks_limit(self):
        """Test that max_tasks limit is respected."""
        loop = DevLoop(max_tasks=2)
        
        tasks = [
            Task(type=TaskType.TODO, description=f"TODO {i}", file_path=f"f{i}.py", line_number=i)
            for i in range(5)
        ]
        
        with patch.object(loop.scanner, 'scan', return_value=tasks):
            with patch.object(loop.mother_agent, 'run') as mock_run:
                mock_run.return_value = AgentResult(
                    agent_name="test",
                    agent_type="Developer",
                    instructions="Fix",
                    model="gpt-4",
                    output_type="code",
                    success=True
                )
                
                results = await loop.run_cycle()
        
        assert len(results) == 2  # Should process only max_tasks
        assert mock_run.call_count == 2
    
    def test_error_handling_in_task_processing(self):
        """Test error handling when agent fails."""
        loop = DevLoop()
        
        task = Task(
            type=TaskType.TODO,
            description="TODO: Will fail",
            file_path="fail.py",
            line_number=1
        )
        
        with patch.object(loop.mother_agent, 'run') as mock_run:
            mock_run.return_value = AgentResult(
                agent_name="test",
                agent_type="Developer",
                instructions="Fix",
                model="gpt-4",
                output_type="code",
                success=False,
                error="Agent failed"
            )
            
            result = loop.process_task(task)
        
        assert result.success is False
        assert result.error == "Agent failed"
    
    @pytest.mark.asyncio
    async def test_save_and_load_processed_tasks(self, tmp_path):
        """Test saving and loading processed tasks."""
        loop = DevLoop(state_file=tmp_path / "state.json")
        
        # Add some processed tasks
        tasks = [
            Task(type=TaskType.TODO, description="Task 1", file_path="a.py", line_number=1),
            Task(type=TaskType.FIXME, description="Task 2", file_path="b.py", line_number=2),
        ]
        loop.processed_tasks = tasks
        
        # Save state
        loop.save_state()
        
        # Create new loop and load state
        new_loop = DevLoop(state_file=tmp_path / "state.json")
        new_loop.load_state()
        
        assert len(new_loop.processed_tasks) == 2
        assert new_loop.processed_tasks[0].description == "Task 1"
        assert new_loop.processed_tasks[1].description == "Task 2"
    
    def test_dry_run_mode(self):
        """Test dry run mode doesn't execute agents."""
        loop = DevLoop(dry_run=True)
        
        task = Task(
            type=TaskType.TODO,
            description="TODO: Dry run",
            file_path="dry.py",
            line_number=1
        )
        
        with patch.object(loop.mother_agent, 'run') as mock_run:
            result = loop.process_task(task)
        
        # Should not actually call mother agent in dry run
        mock_run.assert_not_called()
        assert result is None


class TestModuleFunctions:
    """Test module-level convenience functions."""
    
    @pytest.mark.asyncio
    async def test_run_development_cycle(self):
        """Test the run_development_cycle function."""
        with patch('ai.loop.dev_loop.DevLoop') as MockDevLoop:
            mock_loop = Mock()
            # Make run_cycle an async mock that returns a list
            async def mock_run_cycle():
                return []
            mock_loop.run_cycle = mock_run_cycle
            MockDevLoop.return_value = mock_loop
            
            results = await run_development_cycle()
            
            assert results == []
    
    def test_process_task_function(self):
        """Test the process_task function."""
        task = Task(
            type=TaskType.TODO,
            description="TODO: Test",
            file_path="test.py",
            line_number=1
        )
        
        with patch('ai.loop.dev_loop.DevLoop') as MockDevLoop:
            mock_loop = Mock()
            mock_result = AgentResult(
                agent_name="test",
                agent_type="Developer",
                instructions="Fix",
                model="gpt-4",
                output_type="code",
                success=True
            )
            mock_loop.process_task = Mock(return_value=mock_result)
            MockDevLoop.return_value = mock_loop
            
            result = process_task(task)
            
            assert result.success is True
    
    @pytest.mark.asyncio
    async def test_run_continuous_loop(self):
        """Test continuous loop with immediate stop."""
        with patch('ai.loop.dev_loop.DevLoop') as MockDevLoop:
            mock_loop = Mock()
            mock_loop.run_cycle = Mock(return_value=[])
            MockDevLoop.return_value = mock_loop
            
            # Run with stop_after=1 to test one iteration
            with patch('asyncio.sleep', new_callable=Mock):
                await run_continuous_loop(interval=1, stop_after=1)
            
            mock_loop.run_cycle.assert_called_once()


class TestIntegration:
    """Integration tests for the full development loop."""
    
    @pytest.mark.asyncio
    async def test_full_cycle_with_real_scanner(self, tmp_path):
        """Test full cycle with real scanner on test repo."""
        # Create test repository
        test_file = tmp_path / "app.py"
        test_file.write_text("# TODO: Implement feature\nprint('hello')")
        
        loop = DevLoop(repo_path=str(tmp_path))
        
        with patch.object(loop.mother_agent, 'run') as mock_run:
            mock_run.return_value = AgentResult(
                agent_name="test",
                agent_type="Developer",
                instructions="Implement feature",
                model="gpt-4",
                output_type="code",
                success=True,
                output="Feature implemented"
            )
            
            results = await loop.run_cycle()
        
        assert len(results) >= 1
        assert results[0].success is True
