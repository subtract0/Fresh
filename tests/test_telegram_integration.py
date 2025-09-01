"""Integration tests for Telegram bot interface and agent spawning system.

Tests the complete workflow from user request through Father agent analysis
to agent spawning and deployment.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
from datetime import datetime

# Skip all tests if telegram dependencies not available
try:
    from ai.interface.telegram_bot import FatherDecisionMaker, FreshTelegramBot
    from ai.interface.agent_spawner import AgentSpawner, SpawnRequest, SpawnedAgent
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False


@pytest.mark.skipif(not TELEGRAM_AVAILABLE, reason="Telegram dependencies not available")
@pytest.fixture
def father_decision_maker():
    """Create FatherDecisionMaker instance for testing."""
    return FatherDecisionMaker()


@pytest.mark.skipif(not TELEGRAM_AVAILABLE, reason="Telegram dependencies not available")
@pytest.fixture
def agent_spawner():
    """Create AgentSpawner instance for testing."""
    return AgentSpawner()


@pytest.mark.skipif(not TELEGRAM_AVAILABLE, reason="Telegram dependencies not available")
@pytest.fixture
def mock_telegram_bot():
    """Create mock Telegram bot for testing."""
    return FreshTelegramBot("test_token", authorized_users=[12345])


@pytest.mark.skipif(not TELEGRAM_AVAILABLE, reason="Telegram dependencies not available")
class TestFatherDecisionMaker:
    """Test Father agent decision making logic."""
    
    @pytest.mark.asyncio
    async def test_analyze_development_request(self, father_decision_maker):
        """Test Father's analysis of a development request."""
        request = "Build a REST API for user authentication"
        
        decision = await father_decision_maker.analyze_request(request, "dev")
        
        assert decision["task_type"] == "development"
        assert len(decision["agents"]) >= 2  # Should spawn multiple agents
        assert any("architect" in agent["type"].lower() for agent in decision["agents"])
        assert any("developer" in agent["type"].lower() for agent in decision["agents"])
        assert decision["confidence"] in ["high", "medium", "low"]
        
    @pytest.mark.asyncio
    async def test_analyze_documentation_request(self, father_decision_maker):
        """Test Father's analysis of a documentation request."""
        request = "Create API documentation with examples"
        
        decision = await father_decision_maker.analyze_request(request, "docs")
        
        assert decision["task_type"] == "documentation"
        assert any("researcher" in agent["type"].lower() for agent in decision["agents"])
        assert any("documenter" in agent["type"].lower() for agent in decision["agents"])
        
    @pytest.mark.asyncio
    async def test_analyze_bug_fix_request(self, father_decision_maker):
        """Test Father's analysis of a bug fix request."""
        request = "Fix memory leak in agent spawning process"
        
        decision = await father_decision_maker.analyze_request(request, "bug")
        
        assert decision["task_type"] == "bugfix"
        assert len(decision["agents"]) >= 1
        assert any("debugger" in agent["type"].lower() for agent in decision["agents"])
        
    @pytest.mark.asyncio
    async def test_decision_includes_required_fields(self, father_decision_maker):
        """Test that Father's decisions include all required fields."""
        request = "Add user authentication"
        
        decision = await father_decision_maker.analyze_request(request)
        
        required_fields = ["task_type", "agents", "execution_plan", "estimated_time", "confidence"]
        for field in required_fields:
            assert field in decision
            
        # Test agent structure
        for agent in decision["agents"]:
            agent_fields = ["type", "quantity", "role", "instructions", "tools"]
            for field in agent_fields:
                assert field in agent


@pytest.mark.skipif(not TELEGRAM_AVAILABLE, reason="Telegram dependencies not available")
class TestAgentSpawner:
    """Test agent spawning and management functionality."""
    
    @pytest.mark.asyncio
    async def test_process_spawn_request(self, agent_spawner):
        """Test processing a complete spawn request."""
        spawn_request = SpawnRequest(
            request_id="test_001",
            user_request="Build user authentication API",
            task_analysis={"task_type": "development", "confidence": "high"},
            proposed_agents=[
                {
                    "type": "Architect",
                    "quantity": 1,
                    "role": "API Design",
                    "instructions": "Design authentication API structure",
                    "tools": ["WriteMemory", "CreateADR"]
                },
                {
                    "type": "Developer",
                    "quantity": 1, 
                    "role": "Implementation",
                    "instructions": "Implement authentication endpoints",
                    "tools": ["WriteMemory", "CallMCPTool"]
                }
            ]
        )
        
        result = await agent_spawner.process_spawn_request(spawn_request)
        
        assert result["request_id"] == "test_001"
        assert len(result["spawned_agents"]) == 2
        assert result["deployment_status"] in ["completed", "in_progress"]
        
    def test_agent_spawning_creates_correct_structure(self, agent_spawner):
        """Test that spawned agents have correct structure."""
        spawn_request = SpawnRequest(
            request_id="test_002", 
            user_request="Create documentation",
            task_analysis={"task_type": "documentation"},
            proposed_agents=[{
                "type": "Documenter",
                "quantity": 1,
                "role": "Documentation Creator", 
                "instructions": "Create comprehensive docs",
                "tools": ["WriteMemory"]
            }]
        )
        
        # Test that we can create agent configurations
        asyncio.run(self._test_agent_config_creation(agent_spawner, spawn_request))
        
    async def _test_agent_config_creation(self, agent_spawner, spawn_request):
        """Helper method for testing agent configuration creation."""
        configs = await agent_spawner._create_agent_configurations(spawn_request)
        
        assert len(configs) == 1
        config = configs[0]
        assert "documenter" in config.name.lower()
        assert config.active is True
        assert "WriteMemory" in config.tools
        
    def test_spawn_status_tracking(self, agent_spawner):
        """Test spawn request status tracking."""
        request_id = "test_003"
        
        # Initially no status
        status = agent_spawner.get_spawn_status(request_id)
        assert status is None
        
        # Add spawned agent
        spawned_agent = SpawnedAgent(
            agent_id="agent_001",
            agent_type="TestAgent",
            role="Testing",
            instructions="Test instructions",
            tools=["WriteMemory"],
            parent_task=request_id
        )
        agent_spawner.spawned_agents["agent_001"] = spawned_agent
        agent_spawner.active_spawn_requests[request_id] = MagicMock()
        
        status = agent_spawner.get_spawn_status(request_id)
        assert status is not None
        assert status["request_id"] == request_id
        assert len(status["agents"]) == 1


@pytest.mark.skipif(not TELEGRAM_AVAILABLE, reason="Telegram dependencies not available")
class TestTelegramBotIntegration:
    """Test complete Telegram bot integration."""
    
    def test_bot_initialization(self, mock_telegram_bot):
        """Test bot initialization with configuration."""
        assert mock_telegram_bot.token == "test_token"
        assert 12345 in mock_telegram_bot.authorized_users
        assert isinstance(mock_telegram_bot.father, FatherDecisionMaker)
        
    def test_user_authorization(self, mock_telegram_bot):
        """Test user authorization logic."""
        assert mock_telegram_bot.is_authorized(12345) is True
        assert mock_telegram_bot.is_authorized(99999) is False
        
        # Test bot with no restrictions
        open_bot = FreshTelegramBot("test_token", authorized_users=None)
        assert open_bot.is_authorized(99999) is True
        
    @pytest.mark.asyncio
    async def test_request_processing_flow(self, mock_telegram_bot):
        """Test the complete request processing flow."""
        # Mock the update and context objects
        mock_update = MagicMock()
        mock_update.effective_user.id = 12345
        mock_update.message.text = "Build a user authentication system"
        mock_update.message.reply_text = AsyncMock()
        
        session = {
            "state": "awaiting_request", 
            "task_type": "dev",
            "timestamp": datetime.now()
        }
        
        # Mock Father's decision
        with patch.object(mock_telegram_bot.father, 'analyze_request', new_callable=AsyncMock) as mock_analyze:
            mock_analyze.return_value = {
                "task_type": "development",
                "agents": [{"type": "Developer", "role": "Implementation", "instructions": "Build auth", "tools": ["WriteMemory"]}],
                "execution_plan": ["Design", "Implement", "Test"],
                "estimated_time": "30 minutes",
                "confidence": "high"
            }
            
            await mock_telegram_bot._process_user_request(
                mock_update, 
                "Build a user authentication system",
                session
            )
            
            # Verify Father was called with correct parameters
            mock_analyze.assert_called_once()
            
            # Verify response was formatted and sent
            mock_update.message.reply_text.assert_called()


@pytest.mark.skipif(not TELEGRAM_AVAILABLE, reason="Telegram dependencies not available")
class TestEndToEndWorkflow:
    """Test complete end-to-end workflow."""
    
    @pytest.mark.asyncio
    async def test_complete_development_workflow(self):
        """Test complete workflow from Telegram request to agent deployment."""
        # 1. Father analyzes request
        father = FatherDecisionMaker()
        decision = await father.analyze_request(
            "Create a web scraper tool for documentation",
            "development request"
        )
        
        # 2. Create spawn request from decision
        spawn_request = SpawnRequest(
            request_id="integration_test_001",
            user_request="Create a web scraper tool for documentation", 
            task_analysis=decision,
            proposed_agents=decision["agents"]
        )
        
        # 3. Process spawn request
        spawner = AgentSpawner()
        result = await spawner.process_spawn_request(spawn_request)
        
        # 4. Verify complete workflow
        assert result["request_id"] == "integration_test_001"
        assert len(result["spawned_agents"]) > 0
        assert result["deployment_status"] in ["completed", "in_progress"]
        
        # 5. Verify spawned agents are tracked
        active_agents = spawner.list_active_agents()
        assert len(active_agents) > 0
        
        # 6. Verify spawn history
        history = spawner.get_spawn_history()
        assert len(history) > 0
        assert history[-1]["request_id"] == "integration_test_001"


@pytest.mark.skipif(not TELEGRAM_AVAILABLE, reason="Telegram dependencies not available")
class TestErrorHandling:
    """Test error handling and edge cases."""
    
    @pytest.mark.asyncio
    async def test_invalid_spawn_request_handling(self, agent_spawner):
        """Test handling of invalid spawn requests."""
        # Empty proposed agents
        spawn_request = SpawnRequest(
            request_id="error_test_001",
            user_request="Invalid request",
            task_analysis={"task_type": "unknown"},
            proposed_agents=[]
        )
        
        result = await agent_spawner.process_spawn_request(spawn_request)
        
        # Should handle gracefully without crashing
        assert result["request_id"] == "error_test_001"
        assert result["deployment_status"] in ["failed", "completed"]
        
    @pytest.mark.asyncio
    async def test_father_decision_with_edge_cases(self, father_decision_maker):
        """Test Father's decision making with edge cases."""
        # Empty request
        decision = await father_decision_maker.analyze_request("", "")
        assert "task_type" in decision
        
        # Very long request  
        long_request = "a" * 1000
        decision = await father_decision_maker.analyze_request(long_request, "")
        assert "task_type" in decision
        
        # Request with special characters
        special_request = "Create API with @#$%^&*() characters"
        decision = await father_decision_maker.analyze_request(special_request, "")
        assert "task_type" in decision


@pytest.mark.integration
@pytest.mark.skipif(not TELEGRAM_AVAILABLE, reason="Telegram dependencies not available")
class TestRealWorldScenarios:
    """Test realistic user scenarios."""
    
    @pytest.mark.asyncio
    async def test_api_development_scenario(self):
        """Test realistic API development scenario."""
        father = FatherDecisionMaker()
        spawner = AgentSpawner()
        
        request = "Build a REST API for a blog system with CRUD operations for posts, comments, and user authentication"
        
        # Father analyzes complex request
        decision = await father.analyze_request(request, "development")
        
        # Should recognize complexity and spawn appropriate team
        assert decision["task_type"] == "development"
        assert len(decision["agents"]) >= 3  # Complex request needs multiple agents
        
        # Should include architecture planning
        agent_types = [agent["type"].lower() for agent in decision["agents"]]
        assert any("architect" in agent_type for agent_type in agent_types)
        
        # Create and process spawn request
        spawn_request = SpawnRequest(
            request_id="blog_api_001",
            user_request=request,
            task_analysis=decision,
            proposed_agents=decision["agents"]
        )
        
        result = await spawner.process_spawn_request(spawn_request)
        
        # Verify successful deployment
        assert result["deployment_status"] in ["completed", "in_progress"]
        assert len(result["spawned_agents"]) >= 3
        
    @pytest.mark.asyncio
    async def test_documentation_scenario(self):
        """Test realistic documentation scenario."""
        father = FatherDecisionMaker()
        
        request = "Create comprehensive API documentation with examples, authentication guide, and troubleshooting section"
        
        decision = await father.analyze_request(request, "documentation")
        
        # Should recognize as documentation task
        assert decision["task_type"] == "documentation"
        
        # Should include research and documentation agents
        agent_types = [agent["type"].lower() for agent in decision["agents"]]
        assert any("researcher" in agent_type or "documenter" in agent_type for agent_type in agent_types)
