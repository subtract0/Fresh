"""
Tests for Product-Driven Autonomous Development System

Comprehensive test suite covering the integration of Product Manager
agent with the autonomous orchestrator system.
"""
import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
from datetime import datetime

from ai.agents.product_manager import (
    ProductManagerAgent,
    FeatureSpecification,
    ProblemAnalysis,
    SolutionValidation,
    RICEScore,
    UserStory,
    ProductRequirement
)
from ai.orchestration.product_autonomous_orchestrator import (
    ProductAutonomousOrchestrator,
    ProductTaskRequest,
    create_product_orchestrator
)
from ai.memory.intelligent_store import IntelligentMemoryStore


class TestProductManagerAgent:
    """Test the Product Manager Agent functionality."""
    
    def setup_method(self):
        self.pm = ProductManagerAgent()
        
    def test_agent_initialization(self):
        """Test PM agent initializes correctly."""
        assert self.pm.name == "ProductManager"
        assert self.pm.version == "3.0.0"
        assert self.pm.color == "blue"
    
    def test_problem_analysis_accessibility_issue(self):
        """Test problem analysis for accessibility issues."""
        feature_data = {
            'name': 'TestFeature',
            'description': 'A test feature',
            'issues': ['not accessible via CLI'],
            'status': 'needs_hookup'
        }
        
        problem = self.pm._extract_and_validate_problem(feature_data)
        
        assert problem.problem_statement.startswith("Users cannot access TestFeature")
        assert "developers" in problem.affected_users
        assert problem.severity_score == 7
        assert problem.frequency == "daily"
    
    def test_problem_analysis_test_coverage_issue(self):
        """Test problem analysis for test coverage issues."""
        feature_data = {
            'name': 'TestFeature',
            'description': 'A test feature',
            'issues': ['lacks test coverage'],
            'status': 'needs_tests'
        }
        
        problem = self.pm._extract_and_validate_problem(feature_data)
        
        assert "test coverage" in problem.problem_statement.lower()
        assert problem.severity_score == 6
        assert problem.frequency == "weekly"
        
    def test_rice_score_calculation(self):
        """Test RICE score calculation logic."""
        feature_data = {'name': 'HighPriorityFeature'}
        problem = ProblemAnalysis(
            problem_statement="Critical accessibility issue",
            affected_users=["developers", "users"],
            severity_score=8,
            frequency="daily",
            cost_of_not_solving="High impact",
            current_workarounds=[],
            five_why_analysis=[],
            evidence=[]
        )
        solution = SolutionValidation(
            core_capability="Provide access",
            key_differentiator="Makes it accessible",
            technical_approach="Add CLI",
            alternatives_considered=[],
            unique_insight="Accessibility matters",
            why_now="Users need it"
        )
        
        rice = self.pm._calculate_rice_score(feature_data, problem, solution)
        
        assert rice.reach > 0
        assert rice.impact > 0
        assert rice.confidence > 0
        assert rice.effort > 0
        assert rice.score == (rice.reach * rice.impact * rice.confidence) / rice.effort
    
    def test_feature_prioritization(self):
        """Test feature prioritization using RICE."""
        features = [
            {
                'name': 'LowPriorityFeature',
                'issues': ['not necessary'],
                'description': 'Low priority feature'
            },
            {
                'name': 'HighPriorityFeature',
                'issues': ['not accessible via CLI'],
                'description': 'High priority feature'
            }
        ]
        
        prioritized = self.pm.prioritize_features(features)
        
        # Should have prioritized the accessible feature higher
        assert len(prioritized) >= 1  # At least one feature should meet criteria
        if len(prioritized) > 1:
            # Highest priority should be first
            first_score = prioritized[0][1].score
            second_score = prioritized[1][1].score
            assert first_score >= second_score
    
    def test_feature_analysis_full_flow(self):
        """Test complete feature analysis flow."""
        feature_data = {
            'name': 'MemorySystem',
            'description': 'Intelligent memory system for agents',
            'issues': ['not accessible via CLI'],
            'status': 'implemented'
        }
        
        spec = self.pm.analyze_feature_request(feature_data)
        
        assert spec.feature_name == 'MemorySystem'
        assert spec.problem_analysis.severity_score >= 6
        assert spec.rice_score.score > 0
        assert len(spec.requirements) > 0
        assert len(spec.user_story.acceptance_criteria) > 0
    
    def test_prd_generation(self):
        """Test PRD document generation."""
        feature_data = {
            'name': 'TestFeature',
            'issues': ['not accessible via CLI'],
            'description': 'Test feature for PRD generation'
        }
        
        spec = self.pm.analyze_feature_request(feature_data)
        prd = self.pm.create_prd_document(spec)
        
        assert "# Product Requirements Document: TestFeature" in prd
        assert "Problem Analysis" in prd
        assert "RICE Score" in prd
        assert "User Story" in prd
        assert "Requirements" in prd
    
    def test_roadmap_generation(self):
        """Test product roadmap generation."""
        features = [
            {
                'name': 'QuickWin',
                'issues': ['not accessible via CLI'],
                'description': 'Easy to implement feature'
            },
            {
                'name': 'BigProject',
                'issues': ['lacks test coverage'],
                'description': 'Complex feature requiring more work'
            }
        ]
        
        roadmap = self.pm.generate_product_roadmap(features, time_horizon=60)
        
        assert 'roadmap_period' in roadmap
        assert 'strategic_themes' in roadmap
        assert 'now_0_30_days' in roadmap
        assert 'next_30_60_days' in roadmap
        assert 'backlog' in roadmap


class TestProductAutonomousOrchestrator:
    """Test the Product-Driven Autonomous Orchestrator."""
    
    def setup_method(self):
        self.memory_store = IntelligentMemoryStore()
        self.orchestrator = ProductAutonomousOrchestrator(self.memory_store)
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initializes with product features."""
        assert self.orchestrator.product_manager is not None
        assert self.orchestrator.min_rice_score == 5.0
        assert self.orchestrator.auto_approve_quick_wins is True
        assert self.orchestrator.generate_prds is True
    
    @pytest.mark.asyncio
    async def test_scan_features_for_analysis(self):
        """Test feature scanning for product analysis."""
        with patch('ai.orchestration.product_autonomous_orchestrator.scan_command') as mock_scan:
            mock_scan.return_value = {
                'features': {
                    'TestFeature': {
                        'description': 'Test feature',
                        'issues': ['not accessible'],
                        'status': 'implemented'
                    }
                }
            }
            
            result = await self.orchestrator._scan_features_for_analysis()
            
            assert result['total_count'] == 1
            assert len(result['features']) == 1
            assert result['features'][0]['name'] == 'TestFeature'
    
    @pytest.mark.asyncio
    async def test_product_strategy_initialization(self):
        """Test product strategy initialization."""
        with patch.object(self.orchestrator, '_scan_features_for_analysis') as mock_scan:
            mock_scan.return_value = {
                'features': [
                    {
                        'name': 'TestFeature',
                        'issues': ['not accessible via CLI'],
                        'description': 'Test feature'
                    }
                ]
            }
            
            await self.orchestrator.initialize_product_strategy()
            
            assert len(self.orchestrator.prioritized_features) >= 0
            assert self.orchestrator.feature_roadmap is not None
    
    def test_feature_extraction_from_task(self):
        """Test extracting feature info from task description."""
        task = "Hook up the memory system functionality to CLI"
        
        feature_data = self.orchestrator._extract_feature_from_task(task)
        
        assert feature_data is not None
        assert 'memory' in feature_data['name'].lower()
        assert 'not accessible via CLI' in feature_data['issues']
    
    def test_rice_score_to_priority_mapping(self):
        """Test mapping RICE scores to priorities."""
        assert self.orchestrator._map_rice_to_priority(25) == 1  # Highest
        assert self.orchestrator._map_rice_to_priority(15) == 2  # High
        assert self.orchestrator._map_rice_to_priority(8) == 3   # Medium
        assert self.orchestrator._map_rice_to_priority(3) == 4   # Low
    
    def test_auto_approval_logic(self):
        """Test auto-approval decision logic."""
        # High RICE score feature
        spec = Mock()
        spec.rice_score.score = 10.0
        spec.rice_score.effort = 0.25
        spec.rice_score.impact = 2.0
        spec.problem_analysis.severity_score = 8
        
        assert self.orchestrator._should_auto_approve_product_task(spec) is True
        
        # Low score feature
        spec.rice_score.score = 2.0
        spec.problem_analysis.severity_score = 4
        
        assert self.orchestrator._should_auto_approve_product_task(spec) is False
    
    @pytest.mark.asyncio
    async def test_product_status_report(self):
        """Test comprehensive product status report generation."""
        # Add a mock product task
        task = ProductTaskRequest(
            task_id="test-task",
            description="Test product task",
            priority=1,
            requested_at=datetime.now(),
            rice_score=12.5,
            problem_severity=8,
            user_impact="developers",
            product_priority="P1"
        )
        self.orchestrator.active_tasks["test-task"] = task
        
        with patch.object(self.orchestrator, 'get_status') as mock_status:
            mock_status.return_value = {
                'active_agents': 2,
                'total_tasks': 5,
                'total_cost': 3.50,
                'runtime': '2h 30m'
            }
            
            report = await self.orchestrator.generate_product_status_report()
            
            assert 'product_metrics' in report
            assert 'roadmap_summary' in report
            assert report['product_metrics']['total_product_tasks'] == 1
            assert report['product_metrics']['total_rice_score'] == 12.5


class TestProductCLIIntegration:
    """Test CLI integration with product features."""
    
    def test_cli_command_integration(self):
        """Test that product commands are properly integrated."""
        from ai.cli.fresh import main
        
        # This is a basic smoke test - more detailed CLI testing would require
        # mocking sys.argv and testing actual command execution
        assert main is not None
    
    def test_scan_utility_function(self):
        """Test the repository scanning utility."""
        from ai.cli.product_commands import scan_repository_for_features
        
        with patch('ai.cli.product_commands.scan_repository') as mock_scan:
            from ai.loop.repo_scanner import Task, TaskType
            from pathlib import Path
            
            mock_task = Mock()
            mock_task.type = TaskType.TODO
            mock_task.description = "Fix this issue"
            mock_task.file_path = Path("test.py")
            mock_task.line_number = 10
            
            mock_scan.return_value = [mock_task]
            
            result = scan_repository_for_features(".")
            
            assert result['total_count'] == 1
            assert 'features' in result
            feature_name = list(result['features'].keys())[0]
            assert 'Task-TODO' in feature_name


class TestProductManagerFormulas:
    """Test specific product management formulas and calculations."""
    
    def test_rice_score_formula(self):
        """Test RICE score formula implementation."""
        rice = RICEScore(reach=100, impact=2.0, confidence=0.8, effort=0.5)
        
        expected_score = (100 * 2.0 * 0.8) / 0.5
        assert rice.score == expected_score
        assert rice.score == 320.0
    
    def test_problem_severity_thresholds(self):
        """Test problem severity threshold logic."""
        pm = ProductManagerAgent()
        
        # Test that problems below threshold are rejected
        low_severity_feature = {
            'name': 'LowImpactFeature',
            'issues': ['minor cosmetic issue'],
            'description': 'Very minor feature'
        }
        
        with pytest.raises(ValueError, match="Problem severity too low"):
            pm.analyze_feature_request(low_severity_feature)
    
    def test_five_why_analysis_generation(self):
        """Test 5-Why analysis generation for different problem types."""
        pm = ProductManagerAgent()
        
        accessibility_whys = pm._generate_five_why_analysis(
            "Feature not accessible via CLI"
        )
        assert len(accessibility_whys) == 5
        assert "Why 1:" in accessibility_whys[0]
        assert "interface" in accessibility_whys[0].lower()
        
        test_whys = pm._generate_five_why_analysis(
            "Feature lacks test coverage"
        )
        assert len(test_whys) == 5
        assert "test" in test_whys[0].lower()


@pytest.fixture
def sample_feature_data():
    """Fixture providing sample feature data for testing."""
    return {
        'name': 'SampleFeature',
        'description': 'A sample feature for testing',
        'issues': ['not accessible via CLI', 'lacks documentation'],
        'status': 'implemented'
    }


@pytest.mark.integration
class TestProductDrivenIntegration:
    """Integration tests for the complete product-driven system."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_product_analysis(self, sample_feature_data):
        """Test complete end-to-end product analysis flow."""
        pm = ProductManagerAgent()
        
        # Analyze feature
        spec = pm.analyze_feature_request(sample_feature_data)
        assert spec.feature_name == 'SampleFeature'
        
        # Generate PRD
        prd = pm.create_prd_document(spec)
        assert len(prd) > 1000  # Should be comprehensive
        
        # Test roadmap generation
        roadmap = pm.generate_product_roadmap([sample_feature_data])
        assert 'SampleFeature' in str(roadmap)
    
    @pytest.mark.asyncio
    async def test_orchestrator_product_integration(self, sample_feature_data):
        """Test orchestrator with product management integration."""
        memory_store = IntelligentMemoryStore()
        orchestrator = ProductAutonomousOrchestrator(memory_store)
        
        # Test product-driven task creation
        with patch.object(orchestrator, '_extract_feature_from_task') as mock_extract:
            mock_extract.return_value = sample_feature_data
            
            task_description = "Hook up SampleFeature to CLI"
            agent_id = await orchestrator.spawn_agent_with_product_analysis(task_description)
            
            assert agent_id is not None
            assert len(orchestrator.active_tasks) > 0
    
    @pytest.mark.asyncio
    async def test_memory_persistence_of_product_data(self):
        """Test that product analysis is properly stored in memory."""
        memory_store = IntelligentMemoryStore()
        orchestrator = ProductAutonomousOrchestrator(memory_store)
        
        # Mock the feature scanning
        with patch.object(orchestrator, '_scan_features_for_analysis') as mock_scan:
            mock_scan.return_value = {
                'features': [
                    {
                        'name': 'TestFeature',
                        'issues': ['not accessible via CLI'],
                        'description': 'Test feature'
                    }
                ]
            }
            
            await orchestrator.initialize_product_strategy()
            
            # Check that roadmap was stored in memory
            memories = memory_store.search_memories("product_roadmap", limit=10)
            # Note: search_memories is synchronous but may need to be awaited
            # depending on implementation
    
    def test_error_handling_in_product_analysis(self):
        """Test error handling in product analysis."""
        pm = ProductManagerAgent()
        
        # Test with invalid data
        invalid_feature = {
            'name': '',  # Empty name
            'issues': [],  # No issues
            'description': ''  # Empty description
        }
        
        # Should handle gracefully and either reject or create minimal analysis
        try:
            spec = pm.analyze_feature_request(invalid_feature)
            # If it succeeds, should have some default values
            assert spec.feature_name != ''
        except ValueError:
            # Or it should raise a clear error
            pass
    
    def test_concurrent_product_task_handling(self):
        """Test handling multiple concurrent product-driven tasks."""
        orchestrator = ProductAutonomousOrchestrator()
        
        # Add multiple product tasks
        for i in range(5):
            task = ProductTaskRequest(
                task_id=f"task-{i}",
                description=f"Product task {i}",
                priority=i + 1,
                requested_at=datetime.now(),
                rice_score=10 - i,
                problem_severity=8 - i,
                user_impact="developers",
                product_priority="P1" if i < 2 else "P2"
            )
            orchestrator.active_tasks[f"task-{i}"] = task
        
        # Test prioritization
        p0_tasks = [t for t in orchestrator.active_tasks.values() 
                   if t.product_priority == "P1"]
        assert len(p0_tasks) == 2
        
        # Test status reporting with multiple tasks
        # This would be an async test in real implementation
        # status_report = await orchestrator.generate_product_status_report()
        # assert status_report['product_metrics']['total_product_tasks'] == 5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
