"""
Tests for Firestore State Management System

Comprehensive tests for the unified agent architecture state management
migration from JSON files to Firestore-based state persistence.

Test Coverage:
- Firestore schema validation
- State manager operations
- Migration utilities
- Fallback behavior
- Cross-session state persistence

Cross-references:
    - ADR-003: Unified Enhanced Architecture Migration
    - ai/state/: Firestore state management implementation
"""
import pytest
import asyncio
import json
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path

# Import state management components
from ai.state.firestore_schema import (
    AgentState, AgentMemoryState, CoordinationEvent, SystemState,
    AgentStatus, TaskStatus, CoordinationEventType,
    get_agent_state_doc_id, get_agent_memory_doc_id, get_coordination_event_doc_id
)
from ai.state.firestore_manager import FirestoreStateManager, get_state_manager
from ai.state.migration import StateMigrator, migrate_from_directory


class TestFirestoreSchema:
    """Test the Firestore schema data models and serialization."""
    
    def test_agent_state_creation(self):
        """Test AgentState creation and validation."""
        now = datetime.utcnow()
        
        agent_state = AgentState(
            agent_id="test_agent_001",
            agent_type="Father",
            session_id="session_123",
            status=AgentStatus.ACTIVE,
            current_task="Plan development strategy",
            task_status=TaskStatus.IN_PROGRESS,
            created_at=now,
            last_updated=now,
            last_active=now,
            memory_context={"working_memory": "authentication system"},
            task_history=[{"task": "previous_task", "completed": True}],
            performance_metrics={"success_rate": 0.85},
            agent_config={"temperature": 0.2},
            tools_enabled=["SmartWriteMemory", "PersistentMemorySearch"],
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
            current_task="Implement authentication",
            created_at=now,
            last_updated=now,
            last_active=now,
            memory_context={"implementation": "jwt_tokens"},
            task_history=[],
            performance_metrics={},
            agent_config={},
            tools_enabled=[]
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
        assert restored_state.collaboration_context == {}  # Default handling
    
    def test_coordination_event_creation(self):
        """Test CoordinationEvent creation and validation."""
        now = datetime.utcnow()
        
        event = CoordinationEvent(
            event_id="event_001",
            event_type=CoordinationEventType.SPAWN,
            timestamp=now,
            source_agent_id="father_001",
            source_agent_type="Father",
            target_agent_id="developer_001",
            target_agent_type="Developer",
            context={"reason": "need implementation"},
            task_context={"feature": "authentication"},
            success=True,
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


class TestFirestoreStateManager:
    """Test the Firestore state manager functionality."""
    
    @pytest.fixture
    def mock_firestore(self):
        """Mock Firestore client for testing."""
        with patch('ai.state.firestore_manager.firebase_admin') as mock_admin:
            mock_admin._apps = []
            mock_admin.initialize_app = Mock()
            
            with patch('ai.state.firestore_manager.firestore') as mock_firestore:
                mock_client = Mock()
                mock_firestore.client.return_value = mock_client
                
                # Mock collection and document operations
                mock_doc_ref = Mock()
                mock_doc_ref.set = Mock()
                mock_doc_ref.update = Mock()
                mock_doc_ref.get = Mock()
                
                mock_collection = Mock()
                mock_collection.document.return_value = mock_doc_ref
                mock_collection.where.return_value = mock_collection
                mock_collection.stream.return_value = []
                
                mock_client.collection.return_value = mock_collection
                
                yield {
                    'client': mock_client,
                    'collection': mock_collection,
                    'doc_ref': mock_doc_ref
                }
    
    @pytest.fixture
    def state_manager(self, mock_firestore):
        """Create a state manager with mocked Firestore."""
        with patch.dict(os.environ, {
            'FIREBASE_PROJECT_ID': 'test-project',
            'FIREBASE_CLIENT_EMAIL': 'test@test.iam.gserviceaccount.com',
            'FIREBASE_PRIVATE_KEY': 'test-private-key'
        }):
            manager = FirestoreStateManager()
            # Force Firestore to be available for testing
            manager.firestore_available = True
            manager.db = mock_firestore['client']
            return manager
    
    def test_firestore_initialization_success(self, mock_firestore):
        """Test successful Firestore initialization."""
        with patch.dict(os.environ, {
            'FIREBASE_PROJECT_ID': 'test-project',
            'FIREBASE_CLIENT_EMAIL': 'test@test.iam.gserviceaccount.com',
            'FIREBASE_PRIVATE_KEY': 'test-private-key'
        }):
            manager = FirestoreStateManager()
            # Should have attempted Firestore initialization
            assert manager.project_id == 'test-project'
    
    def test_firestore_initialization_fallback(self):
        """Test fallback to memory when Firestore initialization fails."""
        with patch.dict(os.environ, {}, clear=True):
            # No Firebase credentials - should fall back to memory
            manager = FirestoreStateManager()
            assert manager.fallback_to_memory is True
            assert manager.firestore_available is False
    
    @pytest.mark.asyncio
    async def test_save_agent_state_firestore(self, state_manager, mock_firestore):
        """Test saving agent state to Firestore."""
        now = datetime.utcnow()
        
        agent_state = AgentState(
            agent_id="test_agent",
            agent_type="Architect",
            session_id="session_test",
            status=AgentStatus.ACTIVE,
            current_task="Design system architecture",
            created_at=now,
            last_updated=now,
            last_active=now,
            memory_context={},
            task_history=[],
            performance_metrics={},
            agent_config={},
            tools_enabled=[]
        )
        
        # Mock successful Firestore operation
        mock_firestore['doc_ref'].set.return_value = None
        
        result = await state_manager.save_agent_state(agent_state)
        
        assert result is True
        mock_firestore['client'].collection.assert_called_with('agent_states')
        mock_firestore['collection'].document.assert_called()
        mock_firestore['doc_ref'].set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_save_agent_state_fallback(self):
        """Test saving agent state with memory fallback."""
        # Create manager without Firestore
        manager = FirestoreStateManager(fallback_to_memory=True)
        manager.firestore_available = False
        
        now = datetime.utcnow()
        agent_state = AgentState(
            agent_id="test_agent",
            agent_type="QA",
            session_id="session_test",
            status=AgentStatus.IDLE,
            created_at=now,
            last_updated=now,
            last_active=now,
            memory_context={},
            task_history=[],
            performance_metrics={},
            agent_config={},
            tools_enabled=[]
        )
        
        result = await manager.save_agent_state(agent_state)
        
        assert result is True
        # Should be stored in memory
        doc_id = get_agent_state_doc_id("QA", "test_agent", "session_test")
        assert doc_id in manager._memory_agent_states
    
    @pytest.mark.asyncio
    async def test_load_agent_state_firestore(self, state_manager, mock_firestore):
        """Test loading agent state from Firestore."""
        now = datetime.utcnow()
        
        # Mock Firestore document
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            'agent_id': 'test_agent',
            'agent_type': 'Developer',
            'session_id': 'session_test',
            'status': 'active',
            'created_at': now.isoformat(),
            'last_updated': now.isoformat(),
            'last_active': now.isoformat(),
            'memory_context': {},
            'task_history': [],
            'performance_metrics': {},
            'agent_config': {},
            'tools_enabled': []
        }
        mock_firestore['doc_ref'].get.return_value = mock_doc
        
        result = await state_manager.load_agent_state("Developer", "test_agent", "session_test")
        
        assert result is not None
        assert isinstance(result, AgentState)
        assert result.agent_id == "test_agent"
        assert result.agent_type == "Developer"
        assert result.status == AgentStatus.ACTIVE
    
    @pytest.mark.asyncio
    async def test_get_active_agents(self, state_manager, mock_firestore):
        """Test querying active agents."""
        # Mock Firestore query results
        mock_doc1 = Mock()
        mock_doc1.to_dict.return_value = {
            'agent_id': 'agent_1',
            'agent_type': 'Father',
            'session_id': 'session_123',
            'status': 'active',
            'created_at': datetime.utcnow().isoformat(),
            'last_updated': datetime.utcnow().isoformat(),
            'last_active': datetime.utcnow().isoformat(),
            'memory_context': {},
            'task_history': [],
            'performance_metrics': {},
            'agent_config': {},
            'tools_enabled': []
        }
        
        mock_firestore['collection'].stream.return_value = [mock_doc1]
        
        active_agents = await state_manager.get_active_agents()
        
        assert len(active_agents) == 1
        assert active_agents[0].agent_id == "agent_1"
        assert active_agents[0].status == AgentStatus.ACTIVE
    
    @pytest.mark.asyncio
    async def test_record_coordination_event(self, state_manager, mock_firestore):
        """Test recording coordination events."""
        now = datetime.utcnow()
        
        event = CoordinationEvent(
            event_id="test_event",
            event_type=CoordinationEventType.HANDOFF,
            timestamp=now,
            source_agent_id="father_001",
            source_agent_type="Father", 
            target_agent_id="developer_001",
            target_agent_type="Developer",
            context={"task": "implementation"},
            task_context={"feature": "auth"},
            success=True
        )
        
        result = await state_manager.record_coordination_event(event)
        
        assert result is True
        mock_firestore['client'].collection.assert_called_with('coordination')
        mock_firestore['doc_ref'].set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_state_statistics(self, state_manager, mock_firestore):
        """Test getting state statistics."""
        # Mock agent states query
        mock_agent_doc = Mock()
        mock_agent_doc.to_dict.return_value = {'status': 'active'}
        mock_firestore['collection'].stream.return_value = [mock_agent_doc, mock_agent_doc]
        
        stats = await state_manager.get_state_statistics()
        
        assert stats['firestore_available'] is True
        assert stats['agent_states_count'] == 2
        assert stats['active_agents_count'] == 2
        assert 'coordination_events_count' in stats


class TestStateMigration:
    """Test state migration from JSON to Firestore."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory with test JSON files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            
            # Create test agent state file
            agent_data = {
                "agent_id": "legacy_agent_001",
                "agent_type": "Father",
                "status": "active",
                "current_task": "Strategic planning",
                "session_id": "legacy_session",
                "last_active": "2024-01-15T10:30:00Z",
                "memory_context": {"project": "migration_test"},
                "performance_metrics": {"success_rate": 0.9}
            }
            
            with open(tmp_path / "agent_state.json", "w") as f:
                json.dump(agent_data, f, indent=2)
            
            # Create test coordination log
            coord_data = {
                "events": [
                    {
                        "event_type": "spawn",
                        "source_agent_id": "father_001",
                        "source_agent_type": "Father",
                        "target_agent_id": "architect_001",
                        "target_agent_type": "Architect",
                        "timestamp": "2024-01-15T10:35:00Z",
                        "success": True,
                        "context": {"reason": "need architecture"}
                    }
                ]
            }
            
            with open(tmp_path / "coordination.json", "w") as f:
                json.dump(coord_data, f, indent=2)
            
            # Create test system config
            system_data = {
                "version": "2.0.0",
                "total_agents": 5,
                "feature_flags": {"unified_agents": True},
                "emergency_stop": False
            }
            
            with open(tmp_path / "config.json", "w") as f:
                json.dump(system_data, f, indent=2)
            
            yield tmp_path
    
    @pytest.fixture
    def mock_state_manager(self):
        """Mock state manager for migration testing."""
        mock_manager = Mock(spec=FirestoreStateManager)
        mock_manager.save_agent_state = AsyncMock(return_value=True)
        mock_manager.record_coordination_event = AsyncMock(return_value=True)
        mock_manager.update_system_state = AsyncMock(return_value=True)
        mock_manager.get_state_statistics = AsyncMock(return_value={
            'agent_states_count': 1,
            'coordination_events_count': 1,
            'active_agents_count': 1,
            'error_agents_count': 0
        })
        return mock_manager
    
    def test_migrator_initialization(self, temp_dir):
        """Test StateMigrator initialization."""
        migrator = StateMigrator(str(temp_dir))
        
        assert migrator.source_dir == temp_dir
        assert migrator.firestore_manager is not None
        assert isinstance(migrator.migration_log, list)
    
    @pytest.mark.asyncio
    async def test_migrate_all_dry_run(self, temp_dir, mock_state_manager):
        """Test complete migration in dry run mode."""
        migrator = StateMigrator(str(temp_dir), mock_state_manager)
        
        result = await migrator.migrate_all(dry_run=True)
        
        assert result['dry_run'] is True
        assert result['success'] is True
        assert result['agent_states_migrated'] >= 1
        assert result['coordination_events_migrated'] >= 1
        assert result['system_config_migrated'] >= 1
        assert len(result['errors']) == 0
        
        # Should not have called actual save methods in dry run
        mock_state_manager.save_agent_state.assert_not_called()
        mock_state_manager.record_coordination_event.assert_not_called()
        mock_state_manager.update_system_state.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_migrate_all_actual(self, temp_dir, mock_state_manager):
        """Test complete migration with actual saves."""
        migrator = StateMigrator(str(temp_dir), mock_state_manager)
        
        result = await migrator.migrate_all(dry_run=False)
        
        assert result['dry_run'] is False
        assert result['success'] is True
        assert result['agent_states_migrated'] >= 1
        
        # Should have called actual save methods
        mock_state_manager.save_agent_state.assert_called()
        mock_state_manager.record_coordination_event.assert_called()
        mock_state_manager.update_system_state.assert_called()
    
    def test_extract_agent_states_from_json(self, temp_dir):
        """Test agent state extraction from various JSON formats."""
        migrator = StateMigrator(str(temp_dir))
        
        # Test direct agent state format
        direct_data = {
            "agent_id": "direct_agent",
            "agent_type": "Developer",
            "status": "busy"
        }
        
        states = migrator._extract_agent_states_from_json(direct_data, "test.json")
        assert len(states) == 1
        assert states[0].agent_id == "direct_agent"
        assert states[0].status == AgentStatus.BUSY
        
        # Test nested agents format
        nested_data = {
            "agents": {
                "agent_1": {"agent_id": "agent_1", "agent_type": "QA", "status": "idle"},
                "agent_2": {"agent_id": "agent_2", "agent_type": "Architect", "status": "active"}
            }
        }
        
        states = migrator._extract_agent_states_from_json(nested_data, "test.json")
        assert len(states) == 2
        assert any(s.agent_id == "agent_1" for s in states)
        assert any(s.agent_id == "agent_2" for s in states)
    
    @pytest.mark.asyncio
    async def test_validate_migration(self, temp_dir, mock_state_manager):
        """Test migration validation."""
        migrator = StateMigrator(str(temp_dir), mock_state_manager)
        
        # Mock successful system state retrieval
        mock_state_manager.get_system_state = AsyncMock(return_value=Mock())
        
        validation = await migrator.validate_migration()
        
        assert 'timestamp' in validation
        assert 'statistics' in validation
        assert validation['success'] is True
        assert len(validation['issues']) == 0
    
    @pytest.mark.asyncio
    async def test_migrate_from_directory_convenience(self, temp_dir):
        """Test convenience function for directory migration."""
        with patch('ai.state.migration.StateMigrator') as mock_migrator_class:
            mock_migrator = Mock()
            mock_migrator.migrate_all = AsyncMock(return_value={'success': True})
            mock_migrator_class.return_value = mock_migrator
            
            result = await migrate_from_directory(str(temp_dir), dry_run=True)
            
            assert result['success'] is True
            mock_migrator_class.assert_called_once_with(str(temp_dir))
            mock_migrator.migrate_all.assert_called_once_with(True)


class TestIntegration:
    """Integration tests for complete state management workflow."""
    
    @pytest.mark.asyncio
    async def test_agent_lifecycle_state_management(self):
        """Test complete agent lifecycle state management."""
        # Use in-memory fallback for testing
        manager = FirestoreStateManager(fallback_to_memory=True)
        manager.firestore_available = False
        
        now = datetime.utcnow()
        
        # 1. Create and save agent state
        agent_state = AgentState(
            agent_id="lifecycle_test_agent",
            agent_type="Developer",
            session_id="integration_test",
            status=AgentStatus.ACTIVE,
            current_task="Integration testing",
            created_at=now,
            last_updated=now,
            last_active=now,
            memory_context={"test_context": "integration"},
            task_history=[],
            performance_metrics={},
            agent_config={},
            tools_enabled=["TestTool"]
        )
        
        save_result = await manager.save_agent_state(agent_state)
        assert save_result is True
        
        # 2. Load agent state
        loaded_state = await manager.load_agent_state(
            "Developer", "lifecycle_test_agent", "integration_test"
        )
        assert loaded_state is not None
        assert loaded_state.agent_id == "lifecycle_test_agent"
        assert loaded_state.current_task == "Integration testing"
        
        # 3. Update agent status
        update_result = await manager.update_agent_status(
            "Developer", "lifecycle_test_agent", "integration_test",
            AgentStatus.BUSY, "Running integration tests"
        )
        assert update_result is True
        
        # 4. Record coordination event
        event = CoordinationEvent(
            event_id="integration_event",
            event_type=CoordinationEventType.COLLABORATION,
            timestamp=now,
            source_agent_id="lifecycle_test_agent",
            source_agent_type="Developer",
            context={"test": "integration"},
            task_context={"phase": "testing"},
            success=True
        )
        
        event_result = await manager.record_coordination_event(event)
        assert event_result is True
        
        # 5. Get statistics
        stats = await manager.get_state_statistics()
        assert stats['agent_states_count'] >= 1
        assert stats['coordination_events_count'] >= 1
    
    @pytest.mark.asyncio
    async def test_cross_session_state_persistence(self):
        """Test state persistence across sessions."""
        manager = FirestoreStateManager(fallback_to_memory=True)
        manager.firestore_available = False
        
        now = datetime.utcnow()
        
        # Session 1: Create agent state
        session1_state = AgentState(
            agent_id="cross_session_agent",
            agent_type="Father",
            session_id="session_001",
            status=AgentStatus.ACTIVE,
            current_task="Strategic planning",
            created_at=now,
            last_updated=now,
            last_active=now,
            memory_context={"project": "cross_session_test"},
            task_history=[{"task": "session1_task", "completed": True}],
            performance_metrics={"tasks_completed": 1},
            agent_config={},
            tools_enabled=[]
        )
        
        await manager.save_agent_state(session1_state)
        
        # Session 2: Create new session for same agent
        session2_state = AgentState(
            agent_id="cross_session_agent",
            agent_type="Father",
            session_id="session_002",
            status=AgentStatus.ACTIVE,
            current_task="Continue planning",
            created_at=now,
            last_updated=now,
            last_active=now,
            memory_context={"project": "cross_session_test"},
            task_history=[{"task": "session2_task", "completed": False}],
            performance_metrics={"tasks_completed": 2},
            agent_config={},
            tools_enabled=[]
        )
        
        await manager.save_agent_state(session2_state)
        
        # Verify both sessions exist independently
        session1_loaded = await manager.load_agent_state(
            "Father", "cross_session_agent", "session_001"
        )
        session2_loaded = await manager.load_agent_state(
            "Father", "cross_session_agent", "session_002"
        )
        
        assert session1_loaded is not None
        assert session2_loaded is not None
        assert session1_loaded.session_id != session2_loaded.session_id
        assert session1_loaded.performance_metrics["tasks_completed"] == 1
        assert session2_loaded.performance_metrics["tasks_completed"] == 2


# Test fixtures for pytest
@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# Integration test marker for running full integration tests
pytestmark = pytest.mark.asyncio
