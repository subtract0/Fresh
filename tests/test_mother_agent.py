"""Tests for the Mother Agent that spawns child agents.

This tests the core spawning interface that creates and manages
child agents for autonomous development tasks.
"""
from __future__ import annotations
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from ai.agents.mother import MotherAgent, AgentResult, SpawnRequest
from ai.memory.store import InMemoryMemoryStore


class TestMotherAgent:
    """Test Mother Agent spawning and lifecycle management."""
    
    def test_mother_agent_initialization(self):
        """Test Mother Agent can be initialized with memory store."""
        memory_store = InMemoryMemoryStore()
        mother = MotherAgent(memory_store=memory_store)
        
        assert mother is not None
        assert mother.memory_store == memory_store
        assert mother.spawn_history == []
    
    def test_run_with_basic_parameters(self):
        """Test run method with basic parameters."""
        mother = MotherAgent()
        
        result = mother.run(
            name="test_agent",
            instructions="Fix the bug in module X",
            model="gpt-4",
            output_type="code"
        )
        
        assert isinstance(result, AgentResult)
        assert result.agent_name == "test_agent"
        assert result.success is not None
        assert result.output is not None
        assert result.artifacts is not None
    
    def test_run_spawns_appropriate_agent_type(self):
        """Test that run method spawns the correct agent based on instructions."""
        mother = MotherAgent()
        
        # Test spawning for bug fix (should route to Developer)
        result = mother.run(
            name="bug_fixer",
            instructions="Fix TypeError in utils.py line 42",
            model="gpt-4",
            output_type="code"
        )
        
        assert result.agent_type in ["Developer", "Father"]
        assert "fix" in result.instructions.lower()
    
    def test_run_with_test_generation_task(self):
        """Test spawning for test generation tasks."""
        mother = MotherAgent()
        
        result = mother.run(
            name="test_creator",
            instructions="Write tests for the new authentication module",
            model="gpt-4",
            output_type="tests"
        )
        
        assert result.agent_type in ["QA", "Father"]
        assert result.output_type == "tests"
    
    def test_run_with_architecture_task(self):
        """Test spawning for architecture/design tasks."""
        mother = MotherAgent()
        
        result = mother.run(
            name="architect",
            instructions="Design the API structure for user management",
            model="gpt-4",
            output_type="design"
        )
        
        assert result.agent_type in ["Architect", "Father"]
        assert result.output_type == "design"
    
    def test_memory_persistence_on_spawn(self):
        """Test that spawn requests are persisted to memory."""
        memory_store = InMemoryMemoryStore()
        mother = MotherAgent(memory_store=memory_store)
        
        result = mother.run(
            name="memory_test",
            instructions="Implement caching layer",
            model="gpt-4",
            output_type="code"
        )
        
        # Check memory was written
        memories = memory_store.query(limit=10)
        assert len(memories) > 0
        
        # Check spawn history
        assert len(mother.spawn_history) == 1
        assert mother.spawn_history[0].name == "memory_test"
    
    def test_spawn_request_tracking(self):
        """Test that spawn requests are properly tracked."""
        mother = MotherAgent()
        
        # Spawn multiple agents
        results = []
        for i in range(3):
            result = mother.run(
                name=f"agent_{i}",
                instructions=f"Task {i}",
                model="gpt-4",
                output_type="code"
            )
            results.append(result)
        
        # Check spawn history
        assert len(mother.spawn_history) == 3
        for i, spawn in enumerate(mother.spawn_history):
            assert spawn.name == f"agent_{i}"
            assert spawn.instructions == f"Task {i}"
            assert spawn.timestamp is not None
    
    def test_error_handling_in_run(self):
        """Test error handling when agent spawning fails."""
        mother = MotherAgent()
        
        # Test with invalid parameters
        result = mother.run(
            name="",  # Invalid empty name
            instructions="Do something",
            model="gpt-4",
            output_type="code"
        )
        
        assert result.success is False
        assert result.error is not None
        assert "Invalid agent name" in result.error
    
    def test_model_selection(self):
        """Test different model selections."""
        mother = MotherAgent()
        
        models = ["gpt-4", "gpt-3.5-turbo", "claude-2"]
        
        for model in models:
            result = mother.run(
                name=f"agent_{model}",
                instructions="Simple task",
                model=model,
                output_type="code"
            )
            
            assert result.model == model
    
    def test_output_type_validation(self):
        """Test output type validation and defaults."""
        mother = MotherAgent()
        
        valid_types = ["code", "tests", "docs", "design", "review"]
        
        for output_type in valid_types:
            result = mother.run(
                name=f"agent_{output_type}",
                instructions="Task",
                model="gpt-4",
                output_type=output_type
            )
            
            assert result.output_type == output_type
    
    def test_integration_with_father_agent(self):
        """Test integration with Father agent for planning."""
        # Test without mocking for now - just verify routing
        mother = MotherAgent()
        
        result = mother.run(
            name="planner",
            instructions="Plan the refactoring of the authentication system",
            model="gpt-4",
            output_type="plan"
        )
        
        assert result.agent_type == "Father"
        assert result.success is True
    
    def test_spawn_history_limit(self):
        """Test that spawn history has a reasonable limit."""
        mother = MotherAgent(max_history=5)
        
        # Spawn more than the limit
        for i in range(10):
            mother.run(
                name=f"agent_{i}",
                instructions=f"Task {i}",
                model="gpt-4",
                output_type="code"
            )
        
        # Should only keep the most recent 5
        assert len(mother.spawn_history) == 5
        assert mother.spawn_history[0].name == "agent_5"
        assert mother.spawn_history[-1].name == "agent_9"
    
    def test_concurrent_spawn_safety(self):
        """Test that Mother Agent handles concurrent spawns safely."""
        import threading
        
        mother = MotherAgent()
        results = []
        
        def spawn_agent(idx):
            result = mother.run(
                name=f"concurrent_{idx}",
                instructions=f"Concurrent task {idx}",
                model="gpt-4",
                output_type="code"
            )
            results.append(result)
        
        threads = []
        for i in range(5):
            t = threading.Thread(target=spawn_agent, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # All spawns should succeed
        assert len(results) == 5
        assert all(r.success for r in results)
        assert len(mother.spawn_history) == 5
    
    def test_get_spawn_statistics(self):
        """Test getting statistics about spawned agents."""
        mother = MotherAgent()
        
        # Spawn various agents
        mother.run("dev1", "Fix bug", "gpt-4", "code")
        mother.run("qa1", "Write tests", "gpt-4", "tests")
        mother.run("dev2", "Add feature", "gpt-3.5-turbo", "code")
        
        stats = mother.get_statistics()
        
        assert stats["total_spawned"] == 3
        assert stats["by_type"]["code"] == 2
        assert stats["by_type"]["tests"] == 1
        assert stats["by_model"]["gpt-4"] == 2
        assert stats["by_model"]["gpt-3.5-turbo"] == 1
        assert "success_rate" in stats


class TestAgentResult:
    """Test the AgentResult data structure."""
    
    def test_agent_result_creation(self):
        """Test creating an AgentResult."""
        result = AgentResult(
            agent_name="test",
            agent_type="Developer",
            instructions="Fix bug",
            model="gpt-4",
            output_type="code",
            success=True,
            output="Bug fixed",
            artifacts={"files": ["fix.py"]},
            error=None,
            duration=1.5
        )
        
        assert result.agent_name == "test"
        assert result.success is True
        assert result.duration == 1.5
    
    def test_agent_result_to_dict(self):
        """Test converting AgentResult to dictionary."""
        result = AgentResult(
            agent_name="test",
            agent_type="QA",
            instructions="Write tests",
            model="gpt-4",
            output_type="tests",
            success=True,
            output="Tests written",
            artifacts={"test_files": ["test_module.py"]},
            error=None,
            duration=2.0
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["agent_name"] == "test"
        assert result_dict["agent_type"] == "QA"
        assert result_dict["success"] is True
        assert "timestamp" in result_dict


class TestSpawnRequest:
    """Test the SpawnRequest data structure."""
    
    def test_spawn_request_creation(self):
        """Test creating a SpawnRequest."""
        request = SpawnRequest(
            name="agent1",
            instructions="Do something",
            model="gpt-4",
            output_type="code"
        )
        
        assert request.name == "agent1"
        assert request.instructions == "Do something"
        assert request.model == "gpt-4"
        assert request.output_type == "code"
        assert request.timestamp is not None
    
    def test_spawn_request_validation(self):
        """Test SpawnRequest validation."""
        # Valid request
        request = SpawnRequest(
            name="valid_agent",
            instructions="Valid task",
            model="gpt-4",
            output_type="code"
        )
        assert request.is_valid()
        
        # Invalid request - empty name
        request = SpawnRequest(
            name="",
            instructions="Task",
            model="gpt-4",
            output_type="code"
        )
        assert not request.is_valid()
        
        # Invalid request - empty instructions
        request = SpawnRequest(
            name="agent",
            instructions="",
            model="gpt-4",
            output_type="code"
        )
        assert not request.is_valid()
