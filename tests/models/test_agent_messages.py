"""
Tests for Pydantic Agent Message Models

Validates schema validation, type safety, and message factory functionality.
"""
import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from ai.models.agent_messages import (
    AgentMessage, MessageType, Priority,
    TaskAssignment, TaskResult, SpawnRequest, SpawnResponse,
    HandoffMessage, ErrorReport, MessageFactory
)


class TestAgentMessage:
    """Test base agent message validation."""
    
    def test_valid_agent_message(self):
        """Test creating a valid agent message."""
        msg = AgentMessage(
            message_id="test_123",
            message_type=MessageType.TASK_ASSIGNMENT,
            sender="Father",
            recipient="Developer",
            payload={"task": "test"}
        )
        
        assert msg.message_id == "test_123"
        assert msg.sender == "Father"
        assert msg.recipient == "Developer"
        assert msg.priority == Priority.MEDIUM  # Default
        assert isinstance(msg.timestamp, datetime)
    
    def test_invalid_agent_name(self):
        """Test validation of agent names."""
        with pytest.raises(ValidationError) as exc_info:
            AgentMessage(
                message_id="test_123",
                message_type=MessageType.TASK_ASSIGNMENT,
                sender="InvalidAgent",
                recipient="Developer"
            )
        
        errors = exc_info.value.errors()
        assert any(e['loc'] == ('sender',) for e in errors)
    
    def test_empty_message_id(self):
        """Test validation of empty message ID."""
        with pytest.raises(ValidationError) as exc_info:
            AgentMessage(
                message_id="",
                message_type=MessageType.TASK_ASSIGNMENT,
                sender="Father",
                recipient="Developer"
            )
        
        errors = exc_info.value.errors()
        assert any(e['loc'] == ('message_id',) for e in errors)


class TestTaskAssignment:
    """Test task assignment schema."""
    
    def test_valid_task_assignment(self):
        """Test creating a valid task assignment."""
        task = TaskAssignment(
            task_id="task_001",
            task_type="bug_fix",
            description="Fix authentication bug in login module",
            file_path="auth/login.py",
            line_number=42
        )
        
        assert task.task_id == "task_001"
        assert task.task_type == "bug_fix"
        assert task.line_number == 42
    
    def test_short_description_validation(self):
        """Test description length validation."""
        with pytest.raises(ValidationError) as exc_info:
            TaskAssignment(
                task_id="task_001",
                task_type="bug_fix",
                description="Fix bug"  # Too short
            )
        
        errors = exc_info.value.errors()
        assert any("at least 10 characters" in str(e) for e in errors)
    
    def test_invalid_line_number(self):
        """Test line number validation."""
        with pytest.raises(ValidationError) as exc_info:
            TaskAssignment(
                task_id="task_001",
                task_type="bug_fix",
                description="Fix authentication bug",
                line_number=0  # Invalid (must be >= 1)
            )
        
        errors = exc_info.value.errors()
        assert any(e['loc'] == ('line_number',) for e in errors)


class TestTaskResult:
    """Test task result schema."""
    
    def test_successful_task_result(self):
        """Test creating a successful task result."""
        result = TaskResult(
            task_id="task_001",
            success=True,
            result_type="code",
            output="def fixed_function():\n    return True",
            files_modified=["auth/login.py"],
            duration_seconds=45.5
        )
        
        assert result.success is True
        assert result.output is not None
        assert len(result.files_modified) == 1
    
    def test_successful_task_without_output(self):
        """Test that successful tasks can have None output."""
        # This should NOT raise an error - None output is allowed
        result = TaskResult(
            task_id="task_001",
            success=True,
            result_type="code",
            output=None  # None output is allowed for successful tasks
        )
        assert result.success is True
        assert result.output is None
    
    def test_failed_task_result(self):
        """Test creating a failed task result."""
        result = TaskResult(
            task_id="task_001",
            success=False,
            result_type="code",
            error="Unable to fix the bug: dependency not found"
        )
        
        assert result.success is False
        assert result.error is not None
        assert result.output is None  # OK for failed tasks


class TestSpawnRequest:
    """Test spawn request schema."""
    
    def test_valid_spawn_request(self):
        """Test creating a valid spawn request."""
        spawn = SpawnRequest(
            agent_type="Developer",
            agent_name="dev_001",
            instructions="Implement authentication module",
            tools=["WriteCode", "RunTests"]
        )
        
        assert spawn.agent_type == "Developer"
        assert spawn.model == "gpt-4"  # Default
        assert len(spawn.tools) == 2
    
    def test_invalid_agent_type(self):
        """Test validation of agent type."""
        with pytest.raises(ValidationError) as exc_info:
            SpawnRequest(
                agent_type="InvalidType",
                agent_name="test",
                instructions="Test instructions"
            )
        
        errors = exc_info.value.errors()
        assert any("Invalid agent type" in str(e) for e in errors)


class TestErrorReport:
    """Test error report schema."""
    
    def test_valid_error_report(self):
        """Test creating a valid error report."""
        error = ErrorReport(
            error_id="err_001",
            error_type="RuntimeError",
            severity="high",
            message="Failed to connect to database",
            stack_trace="Traceback...",
            recovery_attempted=True,
            recovery_successful=False
        )
        
        assert error.severity == "high"
        assert error.recovery_attempted is True
        assert error.recovery_successful is False
    
    def test_severity_validation(self):
        """Test severity level validation."""
        with pytest.raises(ValidationError) as exc_info:
            ErrorReport(
                error_id="err_001",
                error_type="RuntimeError",
                severity="EXTREME",  # Invalid severity
                message="Test error"
            )
        
        errors = exc_info.value.errors()
        assert any("Invalid severity" in str(e) for e in errors)


class TestMessageFactory:
    """Test message factory functionality."""
    
    def test_create_task_assignment(self):
        """Test creating task assignment via factory."""
        msg = MessageFactory.create_task_assignment(
            sender="Father",
            recipient="Developer",
            task_id="task_001",
            task_type="feature",
            description="Implement user authentication system",
            file_path="auth/system.py"
        )
        
        assert msg.message_type == MessageType.TASK_ASSIGNMENT
        assert msg.sender == "Father"
        assert msg.recipient == "Developer"
        assert msg.payload["task_id"] == "task_001"
        assert msg.payload["file_path"] == "auth/system.py"
    
    def test_create_task_result(self):
        """Test creating task result via factory."""
        msg = MessageFactory.create_task_result(
            sender="Developer",
            recipient="Father",
            task_id="task_001",
            success=True,
            result_type="code",
            output="Implementation complete",
            duration_seconds=120.5
        )
        
        assert msg.message_type == MessageType.TASK_RESULT
        assert msg.payload["success"] is True
        assert msg.payload["duration_seconds"] == 120.5
        assert msg.priority == Priority.MEDIUM  # Success = medium priority
    
    def test_create_error_report(self):
        """Test creating error report via factory."""
        msg = MessageFactory.create_error_report(
            sender="Developer",
            error_type="CompilationError",
            severity="critical",
            message="Failed to compile module",
            stack_trace="Line 42: SyntaxError"
        )
        
        assert msg.message_type == MessageType.ERROR_REPORT
        assert msg.recipient == "System"
        assert msg.priority == Priority.CRITICAL
        assert msg.payload["severity"] == "critical"
    
    def test_critical_task_priority(self):
        """Test that critical tasks get high priority."""
        msg = MessageFactory.create_task_assignment(
            sender="Father",
            recipient="Developer",
            task_id="urgent_001",
            task_type="bug_fix",
            description="CRITICAL: Fix security vulnerability immediately"
        )
        
        assert msg.priority == Priority.HIGH  # "critical" in description


class TestMessageSerialization:
    """Test message serialization for storage/transmission."""
    
    def test_message_to_dict(self):
        """Test converting message to dictionary."""
        msg = AgentMessage(
            message_id="test_123",
            message_type=MessageType.STATUS_UPDATE,
            sender="Developer",
            recipient="Father",
            payload={"status": "active", "progress": 50}
        )
        
        data = msg.model_dump()
        
        assert data["message_id"] == "test_123"
        assert data["message_type"] == "status_update"
        assert data["payload"]["progress"] == 50
        assert "timestamp" in data
    
    def test_message_to_json(self):
        """Test converting message to JSON."""
        msg = AgentMessage(
            message_id="test_123",
            message_type=MessageType.HANDOFF,
            sender="Architect",
            recipient="Developer",
            session_id="session_001",
            payload={"task_id": "task_001", "reason": "Implementation needed"}
        )
        
        json_str = msg.model_dump_json()
        
        assert "test_123" in json_str
        assert "handoff" in json_str
        assert "session_001" in json_str
    
    def test_message_from_dict(self):
        """Test creating message from dictionary."""
        data = {
            "message_id": "test_456",
            "message_type": "memory_query",
            "sender": "QA",
            "recipient": "System",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "priority": "low",
            "payload": {"query": "Find test patterns"}
        }
        
        msg = AgentMessage.model_validate(data)
        
        assert msg.message_id == "test_456"
        assert msg.message_type == MessageType.MEMORY_QUERY
        assert msg.priority == Priority.LOW
