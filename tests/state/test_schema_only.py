"""
Simple tests for Firestore schema without Firebase dependencies.
These tests validate the dataclass structure and serialization.
"""
import pytest
from datetime import datetime
from ai.state.firestore_schema import (
    AgentState, AgentMemoryState, CoordinationEvent, SystemState,
    AgentStatus, TaskStatus, CoordinationEventType,
    get_agent_state_doc_id, get_agent_memory_doc_id, get_coordination_event_doc_id
)


class TestFirestoreSchemaOnly:
    """Test Firestore schema without external dependencies."""
    
    def test_agent_state_creation(self):
        """Test AgentState creation and validation.""" 
        now = datetime.utcnow()
        
        agent_state = AgentState(
            agent_id="test_agent_001",
            agent_type="Father",
            session_id="session_123",
            status=AgentStatus.ACTIVE,
            created_at=now,
            last_updated=now,
            last_active=now,
            memory_context={"working_memory": "authentication system"},
            task_history=[{"task": "previous_task", "completed": True}],
            performance_metrics={"success_rate": 0.85},
            agent_config={"temperature": 0.2},
            tools_enabled=["SmartWriteMemory", "PersistentMemorySearch"],
            current_task="Plan development strategy",
            task_status=TaskStatus.IN_PROGRESS,
            collaboration_context={"project": "auth_system"}
        )
        
        assert agent_state.agent_id == "test_agent_001"
        assert agent_state.agent_type == "Father"
        assert agent_state.status == AgentStatus.ACTIVE
        assert agent_state.task_status == TaskStatus.IN_PROGRESS
        assert len(agent_state.tools_enabled) == 2
        assert agent_state.performance_metrics["success_rate"] == 0.85
    
    def test_agent_state_serialization(self):
        """Test AgentState to_dict and from_dict methods."""
        now = datetime.utcnow()
        
        original_state = AgentState(
            agent_id="test_agent_002",
            agent_type="Developer",
            session_id="session_456",
            status=AgentStatus.BUSY,
            created_at=now,
            last_updated=now,
            last_active=now,
            memory_context={"implementation": "jwt_tokens"},
            task_history=[],
            performance_metrics={},
            agent_config={},
            tools_enabled=[],
            current_task="Implement authentication"
        )
        
        # Test serialization
        state_dict = original_state.to_dict()
        assert isinstance(state_dict, dict)
        assert state_dict['agent_id'] == "test_agent_002"
        assert state_dict['status'] == "busy"  # Enum converted to string
        assert isinstance(state_dict['created_at'], str)  # Datetime converted to ISO string
        
        # Test deserialization
        restored_state = AgentState.from_dict(state_dict)
        assert restored_state.agent_id == original_state.agent_id
        assert restored_state.status == original_state.status
        assert restored_state.created_at == original_state.created_at
        assert restored_state.collaboration_context is None  # Default handling
    
    def test_coordination_event_creation(self):
        """Test CoordinationEvent creation and validation."""
        now = datetime.utcnow()
        
        event = CoordinationEvent(
            event_id="event_001",
            event_type=CoordinationEventType.SPAWN,
            timestamp=now,
            source_agent_id="father_001",
            source_agent_type="Father",
            context={"reason": "need implementation"},
            task_context={"feature": "authentication"},
            success=True,
            target_agent_id="developer_001",
            target_agent_type="Developer",
            duration_seconds=2.5
        )
        
        assert event.event_type == CoordinationEventType.SPAWN
        assert event.source_agent_type == "Father"
        assert event.success is True
        assert event.duration_seconds == 2.5
    
    def test_system_state_creation(self):
        """Test SystemState creation and management."""
        now = datetime.utcnow()
        
        system_state = SystemState(
            system_version="2.1.0",
            last_updated=now,
            active_sessions=["session_123", "session_456"],
            total_agents_spawned=42,
            current_agent_count=3,
            system_metrics={"uptime_hours": 24.5, "memory_usage": 0.65},
            error_counts={"connection_error": 2, "timeout_error": 1},
            global_config={"debug": False, "max_agents": 50},
            feature_flags={"unified_agents": True, "firestore_state": True},
            emergency_stop=False
        )
        
        assert system_state.system_version == "2.1.0"
        assert len(system_state.active_sessions) == 2
        assert system_state.total_agents_spawned == 42
        assert system_state.feature_flags["unified_agents"] is True
        assert system_state.emergency_stop is False
    
    def test_document_id_generation(self):
        """Test document ID generation functions."""
        # Agent state document IDs
        doc_id = get_agent_state_doc_id("Father", "agent_001", "session_123")
        assert doc_id == "Father_agent_001_session_123"
        
        # Agent memory document IDs
        memory_doc_id = get_agent_memory_doc_id("Developer", "agent_002")
        assert memory_doc_id == "Developer_agent_002"
        
        # Coordination event document IDs (with timestamp)
        test_time = datetime(2024, 1, 15, 10, 30, 45, 123456)
        event_doc_id = get_coordination_event_doc_id(test_time)
        assert event_doc_id == "event_20240115_103045_123456"
