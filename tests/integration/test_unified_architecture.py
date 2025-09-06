"""Integration Tests for Unified Architecture

Validates that all components of the unified enhanced architecture work together:
- Unified agents (no more dual system)
- Pydantic message validation
- Firestore state persistence
- Benchmark harness
- Cross-component communication

Cross-references:
    - ADR-003: Unified Enhanced Architecture Migration
    - ai/agents/agents.py: Unified agent implementations
    - ai/models/agent_messages.py: Pydantic schemas
    - ai/state/: Firestore state management
    - ai/benchmarks/: Learning measurement
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
from pathlib import Path
import json

from ai.agents import Father, Architect, Developer, QA
from ai.agents.mother import MotherAgent, AgentResult
from ai.models.agent_messages import (
    MessageFactory,
    AgentMessage,
    MessageType,
    Priority,
    TaskAssignment,
    TaskResult
)
from ai.state.firestore_manager import FirestoreStateManager
from ai.state.firestore_schema import SystemState, AgentState, AgentStatus
from ai.benchmarks.harness import BenchmarkHarness, BenchmarkTask, TaskCategory, TaskDifficulty
from ai.memory.store import InMemoryMemoryStore, set_memory_store
from ai.loop.dev_loop import DevLoop


class TestUnifiedArchitectureIntegration:
    """Test unified architecture components working together."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment with in-memory stores."""
        set_memory_store(InMemoryMemoryStore())
        # Reset any global state
        yield
        # Cleanup if needed
    
    def test_unified_agents_exist(self):
        """Verify all unified agents can be instantiated."""
        # Create all agents - should use unified implementation
        father = Father()
        architect = Architect()
        developer = Developer()
        qa = QA()
        
        assert father.name == "Father"
        assert architect.name == "Architect"
        assert developer.name == "Developer"
        assert qa.name == "QA"
        
        # Verify no "enhanced" terminology
        for agent in [father, architect, developer, qa]:
            assert "enhanced" not in agent.description.lower()
    
    def test_pydantic_message_validation(self):
        """Test Pydantic message schemas work correctly."""
        # Create a task assignment message
        msg = MessageFactory.create_task_assignment(
            sender="Father",
            recipient="Developer",
            task_id="test_001",
            task_type="bug_fix",
            description="Fix critical authentication bug in login module",
            file_path="auth/login.py",
            line_number=42
        )
        
        assert msg.message_type == MessageType.TASK_ASSIGNMENT
        assert msg.sender == "Father"
        assert msg.recipient == "Developer"
        assert msg.priority == Priority.HIGH  # "critical" in description
        
        # Verify payload structure
        task_data = TaskAssignment.model_validate(msg.payload)
        assert task_data.task_id == "test_001"
        assert task_data.line_number == 42
    
    def test_invalid_message_validation(self):
        """Test that invalid messages are rejected."""
        from pydantic import ValidationError
        
        # Invalid agent name should fail
        with pytest.raises(ValidationError) as exc_info:
            AgentMessage(
                message_id="test_123",
                message_type=MessageType.TASK_ASSIGNMENT,
                sender="InvalidAgent",  # Not in valid agents list
                recipient="Developer"
            )
        
        errors = exc_info.value.errors()
        assert any(e['loc'] == ('sender',) for e in errors)
    
    @pytest.mark.asyncio
    async def test_firestore_state_persistence(self):
        """Test Firestore state manager with mocked backend."""
        with patch('google.cloud.firestore') as mock_firestore:
            # Setup mock Firestore
            mock_db = Mock()
            mock_firestore.Client.return_value = mock_db
            mock_collection = Mock()
            mock_db.collection.return_value = mock_collection
            mock_doc = Mock()
            mock_collection.document.return_value = mock_doc
            mock_doc.get.return_value = Mock(exists=False)
            
            # Create state manager
            state_manager = FirestoreStateManager()
            
            # Create and save agent state
            agent_state = AgentState(
                agent_id="test_agent_001",
                agent_type="Developer",
                session_id="test_session",
                status=AgentStatus.ACTIVE,
                current_task="Fix bug",
                created_at=datetime.now(timezone.utc),
                last_updated=datetime.now(timezone.utc),
                last_active=datetime.now(timezone.utc),
                memory_context={"test": "data"},
                task_history=[],
                performance_metrics={},
                agent_config={},
                tools_enabled=[]
            )
            
            await state_manager.save_agent_state(agent_state)
            
            # Verify Firestore was called
            mock_doc.set.assert_called_once()
            saved_data = mock_doc.set.call_args[0][0]
            assert saved_data['agent_id'] == "test_agent_001"
            assert saved_data['status'] == "active"
    
    @pytest.mark.asyncio
    async def test_mother_agent_with_unified_agents(self):
        """Test MotherAgent spawning unified agents."""
        mother = MotherAgent()
        
        with patch.object(mother, 'spawn_agent') as mock_spawn:
            mock_spawn.return_value = Mock(
                run=Mock(return_value="Test output")
            )
            
            result = mother.run(
                name="test_task",
                instructions="Fix authentication bug",
                model="gpt-4",
                output_type="code"
            )
            
            assert isinstance(result, AgentResult)
            assert result.agent_name == "test_task"
            # MotherAgent should determine Developer for bug fix
            assert result.agent_type in ["Developer", "QA", "Architect"]
    
    @pytest.mark.asyncio
    async def test_dev_loop_with_firestore_state(self):
        """Test development loop using Firestore state."""
        with patch('google.cloud.firestore'):
            dev_loop = DevLoop(
                repo_path=".",
                max_tasks=1,
                dry_run=True  # Don't actually spawn agents
            )
            
            # Mock scanner to return a test task
            from ai.loop.repo_scanner import Task, TaskType
            test_task = Task(
                type=TaskType.TODO,
                description="TODO: Implement feature",
                file_path="test.py",
                line_number=1,
                priority=3
            )
            
            with patch.object(dev_loop.scanner, 'scan', return_value=[test_task]):
                results = await dev_loop.run_cycle()
            
            # In dry run, no results but task should be processed
            assert len(results) == 0  # Dry run returns no results
            assert dev_loop.session_id.startswith("dev_loop_")
    
    @pytest.mark.asyncio
    async def test_benchmark_harness_integration(self):
        """Test benchmark harness can evaluate unified agents."""
        harness = BenchmarkHarness(
            use_persistent_memory=False,
            results_dir=Path("/tmp/test_benchmarks")
        )
        
        # Create a simple benchmark task
        task = BenchmarkTask(
            task_id="integration_test",
            category=TaskCategory.BUG_FIX,
            difficulty=TaskDifficulty.EASY,
            description="Fix null pointer",
            expected_solution_pattern="null check",
            validation_criteria=["adds null check"],
            sample_code="def test(): return obj.value"
        )
        
        with patch.object(harness.mother_agent, 'run') as mock_run:
            mock_run.return_value = AgentResult(
                agent_name="test",
                agent_type="Developer",
                instructions="Fix bug",
                model="gpt-4",
                output_type="code",
                success=True,
                output="if obj is not None: return obj.value"
            )
            
            result = await harness.run_task(task, attempt_number=1)
        
        assert result.task_id == "integration_test"
        assert result.success is True
        assert len(result.validation_passed) > 0
    
    def test_message_factory_integration(self):
        """Test MessageFactory creates valid messages for all types."""
        # Task assignment
        task_msg = MessageFactory.create_task_assignment(
            sender="Father",
            recipient="Developer",
            task_id="task_001",
            task_type="feature",
            description="Implement new authentication system"
        )
        
        assert task_msg.message_type == MessageType.TASK_ASSIGNMENT
        assert TaskAssignment.model_validate(task_msg.payload)
        
        # Task result
        result_msg = MessageFactory.create_task_result(
            sender="Developer",
            recipient="Father",
            task_id="task_001",
            success=True,
            result_type="code",
            output="Implementation complete"
        )
        
        assert result_msg.message_type == MessageType.TASK_RESULT
        assert TaskResult.model_validate(result_msg.payload)
        
        # Error report
        error_msg = MessageFactory.create_error_report(
            sender="QA",
            error_type="TestFailure",
            severity="high",
            message="Test suite failing"
        )
        
        assert error_msg.message_type == MessageType.ERROR_REPORT
        assert error_msg.priority == Priority.HIGH
    
    def test_cross_component_communication(self):
        """Test components can communicate via validated messages."""
        # Simulate Father sending task to Developer
        father_msg = MessageFactory.create_task_assignment(
            sender="Father",
            recipient="Developer",
            task_id="cross_comm_001",
            task_type="refactor",
            description="Refactor authentication module for better security"
        )
        
        # Developer processes and responds
        dev_response = MessageFactory.create_task_result(
            sender="Developer",
            recipient="Father",
            task_id="cross_comm_001",
            success=True,
            result_type="code",
            output="Refactored auth module",
            duration_seconds=120.5
        )
        
        # Validate message chain
        assert father_msg.payload["task_id"] == dev_response.payload["task_id"]
        assert dev_response.payload["success"] is True
        
        # QA could report an issue
        qa_report = MessageFactory.create_error_report(
            sender="QA",
            error_type="SecurityVulnerability",
            severity="critical",
            message="Found SQL injection vulnerability in refactored code",
            stack_trace="auth/module.py:45"
        )
        
        assert qa_report.priority == Priority.CRITICAL
    
    @pytest.mark.asyncio
    async def test_end_to_end_task_flow(self):
        """Test complete task flow through unified architecture."""
        # 1. Create task via scanner
        from ai.loop.repo_scanner import Task, TaskType
        task = Task(
            type=TaskType.FIXME,
            description="FIXME: Critical security issue",
            file_path="auth/security.py",
            line_number=100,
            priority=5
        )
        
        # 2. Create task assignment message
        assignment = MessageFactory.create_task_assignment(
            sender="Father",
            recipient="Developer",
            task_id="e2e_001",
            task_type="bug_fix",
            description=task.description,
            file_path=task.file_path,
            line_number=task.line_number
        )
        
        # 3. Mock agent processing
        mock_agent_result = AgentResult(
            agent_name="dev_agent",
            agent_type="Developer",
            instructions=assignment.payload["description"],
            model="gpt-4",
            output_type="code",
            success=True,
            output="Security issue fixed with proper validation"
        )
        
        # 4. Create result message
        result = MessageFactory.create_task_result(
            sender="Developer",
            recipient="Father",
            task_id="e2e_001",
            success=mock_agent_result.success,
            result_type="code",
            output=mock_agent_result.output
        )
        
        # 5. Validate flow
        assert assignment.payload["task_id"] == result.payload["task_id"]
        assert result.payload["success"] is True
        assert "fixed" in result.payload["output"].lower()


class TestUnifiedArchitectureStability:
    """Test that unified architecture is stable and consistent."""
    
    def test_no_legacy_imports(self):
        """Ensure no imports of deleted legacy files."""
        # These should not be importable
        legacy_modules = [
            "ai.agents.Father",
            "ai.agents.Architect",
            "ai.agents.Developer",
            "ai.agents.QA",
            "ai.agents.enhanced_agents"  # Renamed to agents.py
        ]
        
        for module_name in legacy_modules:
            with pytest.raises(ImportError):
                import importlib
                importlib.import_module(module_name)
    
    def test_no_enhanced_terminology(self):
        """Verify 'enhanced' terminology has been removed."""
        # Check agent descriptions
        agents = [Father(), Architect(), Developer(), QA()]
        
        for agent in agents:
            assert "enhanced" not in agent.name.lower()
            # Description might mention "enhanced capabilities" which is OK
            # but shouldn't use "EnhancedFather" etc.
            assert "EnhancedFather" not in str(agent.__class__)
            assert "EnhancedDeveloper" not in str(agent.__class__)
    
    def test_firestore_fallback_to_memory(self):
        """Test graceful fallback when Firestore unavailable."""
        with patch('google.cloud.firestore', side_effect=ImportError):
            # Should fall back to in-memory without crashing
            from ai.loop.dev_loop import DevLoop
            
            loop = DevLoop()
            assert loop.state_manager is not None  # Some state manager exists
    
    def test_message_timestamp_timezone_aware(self):
        """Verify all timestamps are timezone-aware."""
        msg = MessageFactory.create_task_assignment(
            sender="Father",
            recipient="Developer",
            task_id="tz_test",
            task_type="test",
            description="Test timezone awareness"
        )
        
        # Timestamp should be timezone-aware
        assert msg.timestamp.tzinfo is not None
        assert msg.timestamp.tzinfo.utcoffset(None) is not None


class TestBackwardCompatibility:
    """Ensure backward compatibility where needed."""
    
    def test_mother_agent_still_works(self):
        """MotherAgent should still function with unified agents."""
        mother = MotherAgent()
        
        # Should be able to determine agent type
        agent_type = mother._determine_agent_type(
            "Fix the authentication bug in login.py",
            "code"  # output_type parameter
        )
        assert agent_type in ["Developer", "QA", "Architect", "Father"]
    
    def test_agency_can_be_built(self):
        """Agency structure should still be buildable."""
        from ai.agency import build_agency
        
        # Mock the agent classes to avoid instantiation issues
        with patch('ai.agency.Father'), \
             patch('ai.agency.Architect'), \
             patch('ai.agency.Developer'), \
             patch('ai.agency.QA'), \
             patch('ai.agency.Reviewer'), \
             patch('agency_swarm.Agency') as mock_agency:
            
            agency = build_agency()
            mock_agency.assert_called_once()
