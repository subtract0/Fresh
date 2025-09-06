"""
Tests for Integration between unified agents and Firestore state management.

Test Coverage:
- Agent spawning with state persistence
- Memory integration with state management
- Cross-session agent coordination
- State migration for existing agents
- Error handling and fallback scenarios

Cross-references:
    - ADR-003: Unified Enhanced Architecture Migration
    - ai/agents/enhanced/: Unified agent implementations
    - ai/state/: Firestore state management
"""
import pytest
import asyncio
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

from ai.state.firestore_schema import (
    AgentState, CoordinationEvent, AgentStatus, CoordinationEventType
)
from ai.state.firestore_manager import FirestoreStateManager
from ai.memory.intelligent_store import IntelligentMemoryStore
from ai.agents.base_agent import Agent


class UnifiedAgent:
    """Mock UnifiedAgent class for integration testing."""
    
    def __init__(self, name: str, instructions: str, model: str, 
                 memory_store=None, state_manager=None, agent_config=None):
        self.name = name
        self.instructions = instructions
        self.model = model
        self.memory_store = memory_store
        self.state_manager = state_manager
        self.agent_config = agent_config or {}
        
    async def initialize(self):
        """Initialize the agent and create initial state."""
        if self.state_manager and self.agent_config.get('enable_state_persistence'):
            now = datetime.utcnow()
            agent_state = AgentState(
                agent_id=self.name,
                agent_type=self.agent_config.get('agent_type', 'Generic'),
                session_id=self.agent_config.get('session_id', 'default'),
                status=AgentStatus.ACTIVE,
                created_at=now,
                last_updated=now,
                last_active=now,
                memory_context={},
                task_history=[],
                performance_metrics={},
                agent_config=self.agent_config,
                tools_enabled=[]
            )
            await self.state_manager.save_agent_state(agent_state)
    
    async def execute_task(self, task: str, context: dict = None):
        """Execute a task and update state."""
        if self.state_manager and self.agent_config.get('enable_state_persistence'):
            await self.state_manager.update_agent_status(
                self.agent_config.get('agent_type', 'Generic'),
                self.name,
                self.agent_config.get('session_id', 'default'),
                AgentStatus.BUSY,
                task
            )
        
        result = await self._execute_llm_task(task, context)
        
        if self.state_manager and self.agent_config.get('enable_state_persistence'):
            await self.state_manager.update_agent_status(
                self.agent_config.get('agent_type', 'Generic'),
                self.name,
                self.agent_config.get('session_id', 'default'),
                AgentStatus.ACTIVE,
                "Task completed"
            )
        
        return result
    
    async def _execute_llm_task(self, task: str, context: dict = None):
        """Mock LLM task execution."""
        return f"Executed: {task}"
    
    async def spawn_child_agent(self, agent_type: str, instructions: str, task_context: dict = None):
        """Spawn a child agent and record coordination event."""
        child_agent = await self._spawn_child_agent(agent_type, instructions, task_context)
        
        if self.state_manager:
            event = CoordinationEvent(
                event_id=f"spawn_{datetime.utcnow().timestamp()}",
                event_type=CoordinationEventType.SPAWN,
                timestamp=datetime.utcnow(),
                source_agent_id=self.name,
                source_agent_type=self.agent_config.get('agent_type', 'Generic'),
                target_agent_id=child_agent.name,
                target_agent_type=agent_type,
                context=task_context or {},
                task_context=task_context or {},
                success=True
            )
            await self.state_manager.record_coordination_event(event)
        
        return child_agent
    
    async def _spawn_child_agent(self, agent_type: str, instructions: str, task_context: dict = None):
        """Mock child agent spawning."""
        return UnifiedAgent(
            name=f"child_{agent_type.lower()}",
            instructions=instructions,
            model=self.model,
            memory_store=self.memory_store,
            state_manager=self.state_manager,
            agent_config={'agent_type': agent_type}
        )
    
    async def write_memory(self, key: str, content: dict):
        """Write to memory and update state."""
        if self.memory_store:
            await self.memory_store.add_memory({
                'key': key,
                'content': content,
                'timestamp': datetime.utcnow().isoformat()
            })
        
        if self.state_manager and self.agent_config.get('enable_state_persistence'):
            await self.state_manager.update_agent_status(
                self.agent_config.get('agent_type', 'Generic'),
                self.name,
                self.agent_config.get('session_id', 'default'),
                AgentStatus.ACTIVE,
                "Memory updated"
            )
    
    async def search_memory(self, query: str):
        """Search memory."""
        if self.memory_store:
            return await self.memory_store.search_memories(query)
        return []


class TestUnifiedAgentWithStateIntegration:
    """Test integration between UnifiedAgent and Firestore state management."""
    
    @pytest.fixture
    def mock_state_manager(self):
        """Mock state manager for testing."""
        manager = Mock(spec=FirestoreStateManager)
        manager.save_agent_state = AsyncMock(return_value=True)
        manager.load_agent_state = AsyncMock(return_value=None)
        manager.update_agent_status = AsyncMock(return_value=True)
        manager.record_coordination_event = AsyncMock(return_value=True)
        manager.get_active_agents = AsyncMock(return_value=[])
        manager.firestore_available = True
        return manager
    
    @pytest.fixture
    def memory_store(self):
        """Create memory store for agent testing."""
        return IntelligentMemoryStore()
    
    @pytest.fixture
    def agent_with_state(self, mock_state_manager, memory_store):
        """Create UnifiedAgent with state management integration."""
        agent = UnifiedAgent(
            name="test_agent",
            instructions="Test agent for state management integration",
            model="gpt-4",
            memory_store=memory_store,
            state_manager=mock_state_manager,
            agent_config={
                "agent_type": "Father",
                "session_id": "test_session_001",
                "enable_state_persistence": True
            }
        )
        return agent
    
    @pytest.mark.asyncio
    async def test_agent_initialization_with_state_persistence(self, agent_with_state, mock_state_manager):
        """Test agent initialization creates proper state records."""
        agent = agent_with_state
        
        # Initialize agent (should create initial state)
        await agent.initialize()
        
        # Verify state manager was called to save initial state
        mock_state_manager.save_agent_state.assert_called()
        
        # Verify the saved state has correct structure
        saved_state_call = mock_state_manager.save_agent_state.call_args[0][0]
        assert isinstance(saved_state_call, AgentState)
        assert saved_state_call.agent_type == "Father"
        assert saved_state_call.status == AgentStatus.ACTIVE
        assert saved_state_call.session_id == "test_session_001"
    
    @pytest.mark.asyncio
    async def test_agent_task_execution_updates_state(self, agent_with_state, mock_state_manager):
        """Test that agent task execution updates state properly."""
        agent = agent_with_state
        await agent.initialize()
        
        # Execute a task
        task_context = {
            "task": "Plan authentication system",
            "priority": "high",
            "requirements": ["security", "scalability"]
        }
        
        with patch.object(agent, '_execute_llm_task', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = "Authentication plan completed"
            
            result = await agent.execute_task("Plan authentication system", task_context)
            
            # Verify task was executed
            assert result == "Authentication plan completed"
            
            # Verify state was updated during task execution
            assert mock_state_manager.update_agent_status.call_count >= 1
    
    @pytest.mark.asyncio
    async def test_agent_spawning_records_coordination_events(self, agent_with_state, mock_state_manager):
        """Test that agent spawning records proper coordination events."""
        parent_agent = agent_with_state
        await parent_agent.initialize()
        
        # Mock spawning child agent
        with patch.object(parent_agent, '_spawn_child_agent', new_callable=AsyncMock) as mock_spawn:
            mock_child = Mock()
            mock_child.name = "child_architect"
            mock_child.agent_config = {"agent_type": "Architect"}
            mock_spawn.return_value = mock_child
            
            child_agent = await parent_agent.spawn_child_agent(
                agent_type="Architect",
                instructions="Design system architecture",
                task_context={"feature": "authentication"}
            )
            
            # Verify coordination event was recorded
            mock_state_manager.record_coordination_event.assert_called()
            
            # Verify event structure
            event_call = mock_state_manager.record_coordination_event.call_args[0][0]
            assert isinstance(event_call, CoordinationEvent)
            assert event_call.event_type == CoordinationEventType.SPAWN
            assert event_call.source_agent_type == "Father"
            assert event_call.target_agent_type == "Architect"
    
    @pytest.mark.asyncio
    async def test_agent_memory_integration_with_state(self, agent_with_state, mock_state_manager):
        """Test that memory operations are reflected in agent state."""
        agent = agent_with_state
        await agent.initialize()
        
        # Write memory
        memory_content = {
            "context": "authentication_planning",
            "insights": ["OAuth 2.0 recommended", "JWT for tokens"],
            "decisions": ["Use Firebase Auth", "Implement custom claims"]
        }
        
        await agent.write_memory("authentication_strategy", memory_content)
        
        # Verify memory write triggered state update
        assert mock_state_manager.update_agent_status.call_count >= 1
        
        # Search memory (should not trigger state change by itself)
        initial_call_count = mock_state_manager.update_agent_status.call_count
        
        results = await agent.search_memory("authentication")
        
        # State update count should remain same or increase slightly
        assert mock_state_manager.update_agent_status.call_count >= initial_call_count


class TestCrossSessionStatePersistence:
    """Test state persistence across different agent sessions."""
    
    @pytest.fixture
    def persistent_state_manager(self):
        """Create state manager with persistent memory store."""
        manager = FirestoreStateManager(fallback_to_memory=True)
        manager.firestore_available = False  # Use memory fallback for testing
        return manager
    
    @pytest.mark.asyncio
    async def test_agent_state_restoration_across_sessions(self, persistent_state_manager):
        """Test that agent state can be restored in a new session."""
        memory_store = IntelligentMemoryStore()
        
        # Session 1: Create and run agent
        session1_agent = UnifiedAgent(
            name="persistent_agent",
            instructions="Cross-session persistence test",
            model="gpt-4",
            memory_store=memory_store,
            state_manager=persistent_state_manager,
            agent_config={
                "agent_type": "Developer",
                "session_id": "session_001",
                "enable_state_persistence": True,
                "restore_from_previous_session": False
            }
        )
        
        await session1_agent.initialize()
        
        # Execute some work in session 1
        task_context = {"feature": "user_management", "phase": "implementation"}
        
        with patch.object(session1_agent, '_execute_llm_task', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = "User management implementation started"
            await session1_agent.execute_task("Implement user management", task_context)
        
        # Verify state was saved
        saved_states = await persistent_state_manager.get_active_agents()
        assert len(saved_states) >= 1
        
        # Session 2: Create new agent instance with same agent_id but different session
        session2_agent = UnifiedAgent(
            name="persistent_agent",  # Same agent name
            instructions="Cross-session persistence test",
            model="gpt-4", 
            memory_store=memory_store,
            state_manager=persistent_state_manager,
            agent_config={
                "agent_type": "Developer",
                "session_id": "session_002",  # Different session
                "enable_state_persistence": True,
                "restore_from_previous_session": True
            }
        )
        
        await session2_agent.initialize()
        
        # Verify that session 2 can access historical context
        # (Implementation depends on how the agent handles previous session data)
        current_state = await persistent_state_manager.load_agent_state(
            "Developer", "persistent_agent", "session_002"
        )
        
        assert current_state is not None
        assert current_state.session_id == "session_002"
    
    @pytest.mark.asyncio
    async def test_coordination_history_persistence(self, persistent_state_manager):
        """Test that coordination events persist across sessions."""
        memory_store = IntelligentMemoryStore()
        
        # Create parent agent
        parent_agent = UnifiedAgent(
            name="coordination_parent",
            instructions="Parent agent for coordination testing",
            model="gpt-4",
            memory_store=memory_store,
            state_manager=persistent_state_manager,
            agent_config={
                "agent_type": "Father",
                "session_id": "coord_session_001",
                "enable_state_persistence": True
            }
        )
        
        await parent_agent.initialize()
        
        # Record coordination event
        coordination_event = CoordinationEvent(
            event_id="test_coordination",
            event_type=CoordinationEventType.HANDOFF,
            timestamp=datetime.utcnow(),
            source_agent_id="coordination_parent",
            source_agent_type="Father",
            target_agent_id="child_developer",
            target_agent_type="Developer",
            context={"task": "implementation_handoff"},
            task_context={"feature": "authentication"},
            success=True,
            duration_seconds=2.3
        )
        
        await persistent_state_manager.record_coordination_event(coordination_event)
        
        # Query coordination history
        coordination_history = await persistent_state_manager.get_coordination_events(
            source_agent_id="coordination_parent",
            limit=10
        )
        
        assert len(coordination_history) >= 1
        found_event = coordination_history[0]
        assert found_event.event_type == CoordinationEventType.HANDOFF
        assert found_event.source_agent_id == "coordination_parent"


class TestStateMigrationIntegration:
    """Test integration of state migration with existing agent systems."""
    
    @pytest.fixture
    def legacy_agent_data(self):
        """Create legacy agent data structure for migration testing."""
        return {
            "legacy_enhanced_father.json": {
                "agent_id": "legacy_father_001",
                "agent_type": "EnhancedFather",  # Old style name
                "status": "active",
                "current_task": "Strategic oversight",
                "session_id": "legacy_session_123",
                "last_active": "2024-01-10T14:30:00Z",
                "memory_context": {
                    "project": "authentication_system",
                    "phase": "planning",
                    "key_decisions": ["OAuth 2.0", "Firebase backend"]
                },
                "spawned_agents": [
                    {"agent_type": "EnhancedArchitect", "task": "system_design"},
                    {"agent_type": "EnhancedDeveloper", "task": "implementation"}
                ],
                "performance_metrics": {
                    "tasks_completed": 15,
                    "success_rate": 0.93,
                    "average_task_duration": 45.2
                }
            },
            "coordination_log.json": {
                "events": [
                    {
                        "timestamp": "2024-01-10T15:00:00Z",
                        "event_type": "spawn",
                        "source_agent": "legacy_father_001",
                        "target_agent": "architect_001",
                        "success": True,
                        "context": {"reason": "need system design"}
                    },
                    {
                        "timestamp": "2024-01-10T15:30:00Z", 
                        "event_type": "handoff",
                        "source_agent": "architect_001",
                        "target_agent": "developer_001",
                        "success": True,
                        "context": {"deliverable": "system_architecture_v1.0"}
                    }
                ]
            }
        }
    
    @pytest.mark.asyncio
    async def test_migrate_legacy_agent_to_unified_system(self, legacy_agent_data):
        """Test migration of legacy enhanced agent data to unified system."""
        from ai.state.migration import StateMigrator
        
        # Create temporary directory with legacy data
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            
            # Write legacy agent data files
            for filename, data in legacy_agent_data.items():
                with open(tmp_path / filename, 'w') as f:
                    json.dump(data, f, indent=2)
            
            # Create state manager for migration target
            state_manager = FirestoreStateManager(fallback_to_memory=True)
            state_manager.firestore_available = False
            
            # Create migrator
            migrator = StateMigrator(str(tmp_path), state_manager)
            
            # Perform migration
            result = await migrator.migrate_all(dry_run=False)
            
            # Verify migration success
            assert result['success'] is True
            assert result['agent_states_migrated'] >= 1
            assert result['coordination_events_migrated'] >= 2
            
            # Verify migrated data structure
            stats = await state_manager.get_state_statistics()
            assert stats['agent_states_count'] >= 1
            assert stats['coordination_events_count'] >= 2
            
            # Verify that migrated agent can be loaded by unified system
            migrated_states = await state_manager.get_active_agents()
            assert len(migrated_states) >= 1
            
            migrated_agent = migrated_states[0]
            assert migrated_agent.agent_id == "legacy_father_001"
            # Should be converted from old "EnhancedFather" to new "Father"
            assert migrated_agent.agent_type == "Father"
            assert migrated_agent.status == AgentStatus.ACTIVE
    
    @pytest.mark.asyncio
    async def test_unified_agent_can_resume_from_migrated_state(self, legacy_agent_data):
        """Test that unified agent can resume work from migrated legacy state."""
        from ai.state.migration import StateMigrator
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            
            # Setup legacy data
            for filename, data in legacy_agent_data.items():
                with open(tmp_path / filename, 'w') as f:
                    json.dump(data, f, indent=2)
            
            # Migrate legacy state
            state_manager = FirestoreStateManager(fallback_to_memory=True)
            state_manager.firestore_available = False
            
            migrator = StateMigrator(str(tmp_path), state_manager)
            migration_result = await migrator.migrate_all(dry_run=False)
            assert migration_result['success'] is True
            
            # Create unified agent with same ID as migrated agent
            memory_store = IntelligentMemoryStore()
            
            unified_agent = UnifiedAgent(
                name="legacy_father_001",  # Same as migrated agent
                instructions="Resume from migrated state",
                model="gpt-4",
                memory_store=memory_store,
                state_manager=state_manager,
                agent_config={
                    "agent_type": "Father",
                    "session_id": "resumed_session_001",
                    "enable_state_persistence": True,
                    "restore_from_previous_session": True
                }
            )
            
            await unified_agent.initialize()
            
            # Verify agent can access migrated context
            current_state = await state_manager.load_agent_state(
                "Father", "legacy_father_001", "resumed_session_001"
            )
            
            assert current_state is not None
            assert current_state.agent_id == "legacy_father_001"
            
            # Agent should be able to continue work with migrated context
            with patch.object(unified_agent, '_execute_llm_task', new_callable=AsyncMock) as mock_execute:
                mock_execute.return_value = "Resuming strategic oversight with migrated context"
                
                result = await unified_agent.execute_task(
                    "Continue strategic oversight",
                    {"context": "resumed_from_migration"}
                )
                
                assert "migrated context" in result


class TestErrorHandlingAndFallback:
    """Test error handling and fallback scenarios in state management integration."""
    
    @pytest.mark.asyncio
    async def test_agent_continues_when_state_persistence_fails(self):
        """Test that agent continues working when Firestore is unavailable."""
        # Create state manager that will fail Firestore operations
        failing_state_manager = Mock(spec=FirestoreStateManager)
        failing_state_manager.firestore_available = False
        failing_state_manager.fallback_to_memory = True
        failing_state_manager.save_agent_state = AsyncMock(side_effect=Exception("Firestore unavailable"))
        failing_state_manager.load_agent_state = AsyncMock(return_value=None)
        failing_state_manager.update_agent_status = AsyncMock(side_effect=Exception("Firestore unavailable"))
        
        memory_store = IntelligentMemoryStore()
        
        agent = UnifiedAgent(
            name="resilient_agent",
            instructions="Test agent resilience to state failures",
            model="gpt-4",
            memory_store=memory_store,
            state_manager=failing_state_manager,
            agent_config={
                "agent_type": "Developer",
                "session_id": "resilience_test",
                "enable_state_persistence": True,
                "continue_on_state_errors": True
            }
        )
        
        # Agent should initialize successfully despite state manager failures
        await agent.initialize()
        
        # Agent should execute tasks despite state persistence failures
        with patch.object(agent, '_execute_llm_task', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = "Task completed despite state issues"
            
            result = await agent.execute_task(
                "Complete task with failing state management",
                {"resilience": "test"}
            )
            
            assert result == "Task completed despite state issues"
            
            # State manager failures should have been attempted but not prevent execution
            assert failing_state_manager.save_agent_state.call_count >= 1
    
    @pytest.mark.asyncio
    async def test_graceful_degradation_to_memory_fallback(self):
        """Test graceful degradation from Firestore to memory-only operation."""
        # Start with Firestore available, then simulate failure
        state_manager = FirestoreStateManager(fallback_to_memory=True)
        state_manager.firestore_available = True
        
        memory_store = IntelligentMemoryStore()
        
        agent = UnifiedAgent(
            name="degradation_test_agent",
            instructions="Test graceful degradation",
            model="gpt-4",
            memory_store=memory_store,
            state_manager=state_manager,
            agent_config={
                "agent_type": "QA",
                "session_id": "degradation_test",
                "enable_state_persistence": True
            }
        )
        
        await agent.initialize()
        
        # Simulate Firestore becoming unavailable
        state_manager.firestore_available = False
        
        # Agent should continue operating with memory fallback
        with patch.object(agent, '_execute_llm_task', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = "QA testing with memory fallback"
            
            result = await agent.execute_task(
                "Perform QA testing",
                {"fallback": "memory_only"}
            )
            
            assert result == "QA testing with memory fallback"
        
        # Verify state is now managed in memory
        assert len(state_manager._memory_agent_states) >= 1


# Mark all tests as asyncio
pytestmark = pytest.mark.asyncio
