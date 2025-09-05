"""Unit tests for Enhanced Agent Orchestration System components.

Tests individual components of the orchestration system including:
- EnhancedMotherAgent task decomposition
- Specialized research agents  
- Parallel execution logic
- Error recovery mechanisms
- MCP integration fallbacks
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

from ai.agents.enhanced_mother import EnhancedMotherAgent, TaskComplexity, TaskDecomposition, OrchestrationResult
from ai.agents.research_agents import MarketResearchAgent, TechnicalAssessmentAgent, OpportunityScoringAgent
from ai.memory.intelligent_store import IntelligentMemoryStore


class TestEnhancedMotherAgent:
    """Test cases for EnhancedMotherAgent orchestration logic."""
    
    @pytest.fixture
    def enhanced_mother(self):
        """Create EnhancedMotherAgent instance for testing."""
        memory_store = Mock(spec=IntelligentMemoryStore)
        return EnhancedMotherAgent(memory_store=memory_store)
    
    def test_initialization(self, enhanced_mother):
        """Test EnhancedMotherAgent initializes correctly."""
        assert enhanced_mother is not None
        assert len(enhanced_mother.specialized_agents) == 5
        assert "MarketResearcher" in enhanced_mother.specialized_agents
        assert "TechnicalAssessor" in enhanced_mother.specialized_agents
        assert "OpportunityScorer" in enhanced_mother.specialized_agents
        assert enhanced_mother.orchestration_history == []
    
    def test_business_opportunity_decomposition(self, enhanced_mother):
        """Test complex task decomposition for business opportunities."""
        command = "Find autonomous deployment opportunities"
        constraints = {"budget": "under_$500", "timeline": "same_day"}
        
        # Test the decomposition logic
        decomposition = enhanced_mother._create_business_opportunity_decomposition(command, constraints)
        
        assert isinstance(decomposition, TaskDecomposition)
        assert decomposition.complexity == TaskComplexity.COMPLEX
        assert len(decomposition.subtasks) == 6  # All phases covered
        assert decomposition.estimated_duration == "3-6 hours with 5-6 specialized agents"
        
        # Verify task structure
        task_types = [task["agent_type"] for task in decomposition.subtasks]
        assert "MarketResearcher" in task_types
        assert "TechnicalAssessor" in task_types
        assert "OpportunityScorer" in task_types
        
        # Verify priorities are set
        priorities = [task["priority"] for task in decomposition.subtasks]
        assert min(priorities) == 1  # Start with priority 1
        assert max(priorities) == 5  # End with priority 5
        
        # Verify success criteria
        assert len(decomposition.success_criteria) >= 4
        assert any("opportunities" in criterion.lower() for criterion in decomposition.success_criteria)
    
    def test_clarification_system(self, enhanced_mother):
        """Test intelligent clarification generation."""
        command = "Research market opportunities"  # Intentionally vague
        constraints = {}  # No constraints provided
        
        decomposition = enhanced_mother._create_business_opportunity_decomposition(command, constraints)
        
        # Should generate clarifications for ambiguous command
        assert len(decomposition.clarifications) >= 1
        
        # Check for specific clarification types
        questions = [c.question for c in decomposition.clarifications]
        assert any("products" in q.lower() for q in questions)
        
        # Verify clarifications have options
        for clarification in decomposition.clarifications:
            if clarification.required:
                assert clarification.options is not None
                assert len(clarification.options) >= 2
    
    def test_orchestration_statistics(self, enhanced_mother):
        """Test orchestration performance statistics."""
        # Initially empty
        stats = enhanced_mother.get_orchestration_statistics()
        assert stats["total_orchestrations"] == 0
        
        # Add mock orchestration result
        mock_result = OrchestrationResult(
            task_id="test-123",
            original_command="test command",
            agents_spawned=5,
            execution_time=10.5,
            success=True
        )
        enhanced_mother.orchestration_history.append(mock_result)
        
        # Check updated statistics
        stats = enhanced_mother.get_orchestration_statistics()
        assert stats["total_orchestrations"] == 1
        assert stats["success_rate"] == 1.0
        assert stats["avg_agents_per_orchestration"] == 5
        assert stats["avg_execution_time"] == 10.5
        assert stats["total_agents_spawned"] == 5


class TestMarketResearchAgent:
    """Test cases for MarketResearchAgent functionality."""
    
    @pytest.fixture
    def market_agent(self):
        """Create MarketResearchAgent for testing."""
        memory_store = Mock(spec=IntelligentMemoryStore)
        return MarketResearchAgent(memory_store=memory_store)
    
    def test_initialization(self, market_agent):
        """Test MarketResearchAgent initializes correctly."""
        assert market_agent.name == "MarketResearcher"
        assert "market research specialist" in market_agent.instructions.lower()
        assert market_agent.research_history == []
    
    @pytest.mark.asyncio
    async def test_market_trends_research(self, market_agent):
        """Test market trends research functionality."""
        domain = "autonomous software deployment"
        focus_areas = ["SaaS", "automation"]
        
        with patch.object(market_agent, '_perform_exa_search') as mock_search:
            mock_search.return_value = {
                "results": [{"url": "test.com", "title": "Test Article", "content": "Test content"}],
                "query": "test query",
                "numResults": 5
            }
            
            with patch.object(market_agent, '_analyze_market_data') as mock_analyze:
                mock_analyze.return_value = ["Test insight 1", "Test insight 2"]
                
                result = await market_agent.research_market_trends(domain, focus_areas, 5)
                
                assert result.success == True
                assert result.agent_type == "MarketResearcher"
                assert len(result.insights) == 2
                assert len(result.sources) >= 0
                assert result.execution_time >= 0
    
    @pytest.mark.asyncio 
    async def test_competitor_analysis(self, market_agent):
        """Test competitor analysis functionality."""
        domain = "AI agent platforms"
        
        with patch.object(market_agent, '_perform_exa_search') as mock_search:
            mock_search.return_value = {"results": [{"url": "competitor.com"}]}
            
            with patch.object(market_agent, '_extract_companies_from_results') as mock_extract:
                mock_extract.return_value = ["CompanyA", "CompanyB"]
                
                with patch.object(market_agent, '_research_company') as mock_research:
                    mock_research.return_value = {"name": "CompanyA", "funding": "$5M"}
                    
                    with patch.object(market_agent, '_generate_competitive_insights') as mock_insights:
                        mock_insights.return_value = ["Competitive insight 1"]
                        
                        result = await market_agent.analyze_competitors(domain, num_results=5)
                        
                        assert result.success == True
                        assert result.agent_type == "MarketResearcher"
                        assert "competitors" in result.data
                        assert len(result.insights) >= 1


class TestTechnicalAssessmentAgent:
    """Test cases for TechnicalAssessmentAgent functionality."""
    
    @pytest.fixture
    def tech_agent(self):
        """Create TechnicalAssessmentAgent for testing."""
        memory_store = Mock(spec=IntelligentMemoryStore)
        return TechnicalAssessmentAgent(memory_store=memory_store)
    
    def test_initialization(self, tech_agent):
        """Test TechnicalAssessmentAgent initializes correctly."""
        assert tech_agent.name == "TechnicalAssessor"
        assert "technical assessment specialist" in tech_agent.instructions.lower()
    
    @pytest.mark.asyncio
    async def test_codebase_capabilities_assessment(self, tech_agent):
        """Test codebase capabilities assessment."""
        project_path = "/test/project"
        
        # Mock the file system scanning
        with patch('pathlib.Path.glob') as mock_glob:
            # Mock agent files
            mock_glob.side_effect = [
                [Path("mother.py"), Path("developer.py")],  # agent files
                [Path("intelligent_store.py")],  # memory files  
                [Path("mcp_client.py")],  # MCP files
                [Path("fresh.py")],  # CLI files
                [],  # git files
                [Path("test1.py"), Path("test2.py")],  # test files
                [Path("README.md")]  # doc files
            ]
            
            # Mock file reading for CLI commands
            with patch('pathlib.Path.read_text') as mock_read:
                mock_read.return_value = "def cmd_scan(): pass\ndef cmd_spawn(): pass"
                
                result = await tech_agent.assess_codebase_capabilities(project_path)
                
                assert result.success == True
                assert result.agent_type == "TechnicalAssessor"
                assert "capabilities" in result.data
                assert "deployment_opportunities" in result.data
                
                capabilities = result.data["capabilities"]
                assert "agent_orchestration" in capabilities
                assert "memory_system" in capabilities
                assert "cli_interface" in capabilities


class TestOpportunityScoringAgent:
    """Test cases for OpportunityScoringAgent functionality."""
    
    @pytest.fixture
    def scoring_agent(self):
        """Create OpportunityScoringAgent for testing."""
        memory_store = Mock(spec=IntelligentMemoryStore)
        return OpportunityScoringAgent(memory_store=memory_store)
    
    def test_initialization(self, scoring_agent):
        """Test OpportunityScoringAgent initializes correctly."""
        assert scoring_agent.name == "OpportunityScorer"
        assert "opportunity evaluation specialist" in scoring_agent.instructions.lower()
    
    @pytest.mark.asyncio
    async def test_opportunity_scoring(self, scoring_agent):
        """Test opportunity scoring functionality."""
        market_data = {"growth_rate": 0.25}
        technical_data = {
            "deployment_opportunities": [
                {
                    "name": "AI Research Assistant SaaS",
                    "deployment_complexity": "low",
                    "estimated_dev_time": "4-6 hours"
                },
                {
                    "name": "Agent Platform",
                    "deployment_complexity": "medium", 
                    "estimated_dev_time": "8-12 hours"
                }
            ]
        }
        
        result = await scoring_agent.score_opportunities(market_data, technical_data)
        
        assert result.success == True
        assert result.agent_type == "OpportunityScorer"
        assert "scored_opportunities" in result.data
        
        scored_opps = result.data["scored_opportunities"]
        assert len(scored_opps) == 2
        
        # Check scoring structure
        for opp in scored_opps:
            assert "score" in opp
            assert "total_score" in opp["score"]
            assert "grade" in opp["score"]
            assert "criteria_scores" in opp["score"]
            assert 0 <= opp["score"]["total_score"] <= 10
    
    def test_scoring_criteria(self, scoring_agent):
        """Test individual scoring criteria."""
        opportunity = {
            "name": "AI Research Assistant SaaS",
            "deployment_complexity": "low",
            "estimated_dev_time": "4-6 hours"
        }
        market_data = {"growth_rate": 0.25}
        
        # Test market potential scoring
        score = scoring_agent._score_market_potential(opportunity, market_data)
        assert 0 <= score <= 10
        assert score >= 8.0  # SaaS should score high
        
        # Test technical feasibility scoring
        score = scoring_agent._score_technical_feasibility(opportunity)
        assert score == 9.0  # Low complexity should score high
        
        # Test time to market scoring
        score = scoring_agent._score_time_to_market(opportunity)
        assert score == 8.5  # 4-6 hours should score high
        
        # Test grade conversion
        grade = scoring_agent._score_to_grade(8.5)
        assert grade == "A+"
        
        grade = scoring_agent._score_to_grade(7.2)
        assert grade == "B+"


class TestMCPIntegration:
    """Test cases for MCP integration fallbacks."""
    
    @pytest.mark.asyncio
    async def test_mcp_fallback_mechanism(self):
        """Test MCP integration falls back gracefully."""
        memory_store = Mock(spec=IntelligentMemoryStore)
        market_agent = MarketResearchAgent(memory_store=memory_store)
        
        # Test search fallback
        result = await market_agent._perform_exa_search("test query", 5)
        
        # Should return simulation data when MCP not available
        assert "results" in result
        assert result["query"] == "test query"
        assert result["numResults"] == 5
        assert len(result["results"]) == 5
    
    @pytest.mark.asyncio
    async def test_company_research_fallback(self):
        """Test company research fallback."""
        memory_store = Mock(spec=IntelligentMemoryStore)
        market_agent = MarketResearchAgent(memory_store=memory_store)
        
        # Test company research fallback
        result = await market_agent._research_company("TestCorp")
        
        # Should return simulation data
        assert result["name"] == "TestCorp"
        assert "funding" in result
        assert "description" in result


@pytest.mark.asyncio
async def test_parallel_execution_logic():
    """Test parallel execution within orchestration phases."""
    memory_store = Mock(spec=IntelligentMemoryStore)
    enhanced_mother = EnhancedMotherAgent(memory_store=memory_store)
    
    # Mock the agent execution
    with patch.object(enhanced_mother, '_execute_single_task') as mock_execute:
        # Mock successful results
        mock_execute.return_value = {
            "agent_type": "TestAgent",
            "success": True,
            "output": "test output"
        }
        
        # Test parallel execution with multiple tasks
        phase_tasks = [
            {"id": "task1", "agent_type": "MarketResearcher", "description": "test1"},
            {"id": "task2", "agent_type": "TechnicalAssessor", "description": "test2"}
        ]
        
        results = await enhanced_mother._execute_task_phase(phase_tasks, {})
        
        # Should execute both tasks
        assert len(results) == 2
        assert "task1" in results
        assert "task2" in results
        assert mock_execute.call_count == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
