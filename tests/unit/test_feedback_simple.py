"""
Simplified unit tests for the feedback loop component.
Tests core functionality that exists in the actual implementation.
"""

import pytest
from unittest.mock import Mock
from datetime import datetime

from ai.autonomous.feedback import FeedbackLoop, LearningPattern
from ai.memory.intelligent_store import IntelligentMemoryStore


class TestFeedbackLoopBasics:
    """Test basic feedback loop functionality."""
    
    @pytest.fixture
    def feedback_loop(self):
        """Create feedback loop instance with in-memory store."""
        return FeedbackLoop(memory_store=IntelligentMemoryStore())
    
    def test_initialization(self, feedback_loop):
        """Test feedback loop initializes correctly."""
        assert feedback_loop.memory_store is not None
        assert isinstance(feedback_loop.learned_patterns, list)
        assert isinstance(feedback_loop.execution_history, list)
        assert isinstance(feedback_loop.config, dict)
        assert "min_confidence_threshold" in feedback_loop.config
        assert "pattern_match_threshold" in feedback_loop.config
        assert "max_patterns" in feedback_loop.config
        assert "learning_rate" in feedback_loop.config
    
    def test_record_success(self, feedback_loop):
        """Test recording successful execution results."""
        success_result = {
            "success": True,
            "execution_type": "magic_fix",
            "description": "Fixed security vulnerability",
            "files_changed": ["src/auth.py", "tests/test_auth.py"],
            "opportunity": Mock(type="security", safety_score=0.8, estimated_effort="medium")
        }
        
        initial_pattern_count = len(feedback_loop.learned_patterns)
        
        # This should not raise an error
        feedback_loop.record_success(success_result)
        
        # Should store in memory
        memories = feedback_loop.memory_store.query(tags=["feedback_loop", "success"])
        assert len(memories) > 0
        
        # May have added patterns
        assert len(feedback_loop.learned_patterns) >= initial_pattern_count
    
    def test_record_failure(self, feedback_loop):
        """Test recording failed execution results."""
        failure_result = {
            "success": False,
            "execution_type": "magic_refactor",
            "error": "Refactoring caused syntax errors",
            "files_changed": [],
            "opportunity": Mock(type="quality", safety_score=0.7, estimated_effort="high")
        }
        
        initial_pattern_count = len(feedback_loop.learned_patterns)
        
        # This should not raise an error
        feedback_loop.record_failure(failure_result)
        
        # Should store in memory
        memories = feedback_loop.memory_store.query(tags=["feedback_loop", "failure"])
        assert len(memories) > 0
        
        # May have added patterns
        assert len(feedback_loop.learned_patterns) >= initial_pattern_count
    
    def test_analyze_results(self, feedback_loop):
        """Test analyzing execution results."""
        results = [
            {
                "success": True,
                "execution_type": "magic_fix",
                "opportunity_type": "security",
                "files_changed": ["src/auth.py"]
            },
            {
                "success": False,
                "execution_type": "magic_refactor",
                "opportunity_type": "quality",
                "error": "Syntax error"
            }
        ]
        
        initial_history_size = len(feedback_loop.execution_history)
        
        # This should add results to execution history
        feedback_loop.analyze_results(results)
        
        # Should have added to execution history
        assert len(feedback_loop.execution_history) == initial_history_size + len(results)
        
        # Each result should have a timestamp
        for result in feedback_loop.execution_history[-len(results):]:
            assert "timestamp" in result
    
    def test_adjust_strategies(self, feedback_loop):
        """Test strategy adjustment based on patterns."""
        # Add some mock patterns first
        success_pattern = LearningPattern(
            pattern_id="test_success_1",
            pattern_type="success",
            confidence=0.9,
            description="Successful security fixes",
            conditions={"opportunity_type": "security", "execution_type": "magic_fix"},
            actions={"approach": "cautious"},
            outcomes={"success_rate": 0.95},
            usage_count=10,
            success_rate=0.95
        )
        
        failure_pattern = LearningPattern(
            pattern_id="test_failure_1",
            pattern_type="failure",
            confidence=0.8,
            description="Failed performance refactoring",
            conditions={"opportunity_type": "performance", "execution_type": "magic_refactor"},
            actions={"approach": "aggressive"},
            outcomes={"success_rate": 0.3},
            usage_count=5,
            success_rate=0.3
        )
        
        feedback_loop.learned_patterns = [success_pattern, failure_pattern]
        
        adjustments = feedback_loop.adjust_strategies()
        
        assert isinstance(adjustments, dict)
        assert "type_preferences" in adjustments
        
        # Security should be preferred due to high success rate
        if "security" in adjustments["type_preferences"]:
            assert adjustments["type_preferences"]["security"] > 1.0
        
        # Performance should be de-emphasized due to failures
        if "performance" in adjustments["type_preferences"]:
            assert adjustments["type_preferences"]["performance"] < 1.0
    
    def test_get_recommendations(self, feedback_loop):
        """Test getting recommendations for a given context."""
        # Add a pattern that should match
        pattern = LearningPattern(
            pattern_id="test_rec_1",
            pattern_type="success",
            confidence=0.9,
            description="High-confidence security fixes",
            conditions={"opportunity_type": "security", "execution_type": "magic_fix"},
            actions={"validation": "extensive", "testing": "thorough"},
            outcomes={"success_rate": 0.95, "avg_duration": 30},
            usage_count=15,
            success_rate=0.95
        )
        
        feedback_loop.learned_patterns = [pattern]
        
        # Test security fix context that should match
        security_context = {
            "opportunity_type": "security",
            "execution_type": "magic_fix",
            "safety_score": 0.8
        }
        
        recommendations = feedback_loop.get_recommendations(security_context)
        
        # Should find matching recommendations
        assert len(recommendations) > 0
        
        # Test recommendations contain relevant fields
        for rec in recommendations:
            assert "confidence" in rec
            assert "description" in rec
            assert "recommended_actions" in rec
            assert "pattern_success_rate" in rec
            assert "expected_outcomes" in rec
            assert rec["confidence"] > 0.0
            assert rec["pattern_success_rate"] >= 0.0
    
    def test_update_patterns(self, feedback_loop):
        """Test updating patterns with recent performance."""
        # Add some execution history
        execution_results = [
            {
                "success": True,
                "execution_type": "magic_fix",
                "opportunity_type": "security",
                "timestamp": datetime.now().isoformat()
            },
            {
                "success": True,
                "execution_type": "magic_fix", 
                "opportunity_type": "security",
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        feedback_loop.execution_history = execution_results
        
        # Add a pattern that should be updated
        pattern = LearningPattern(
            pattern_id="test_update_1",
            pattern_type="success",
            confidence=0.7,
            description="Security fix pattern",
            conditions={"execution_type": "magic_fix", "opportunity_type": "security"},
            actions={"approach": "standard"},
            outcomes={"success_rate": 0.8},
            usage_count=5,
            success_rate=0.8
        )
        
        feedback_loop.learned_patterns = [pattern]
        
        initial_usage_count = pattern.usage_count
        
        # Update patterns based on recent history
        feedback_loop.update_patterns()
        
        # Pattern should have been updated
        assert pattern.usage_count >= initial_usage_count
    
    def test_pattern_matching(self, feedback_loop):
        """Test pattern matching against context."""
        pattern = LearningPattern(
            pattern_id="test_match_1", 
            pattern_type="success",
            confidence=0.8,
            description="Test pattern",
            conditions={"execution_type": "magic_fix", "opportunity_type": "security"},
            actions={"approach": "gradual"},
            outcomes={"success_rate": 0.9},
            usage_count=3,
            success_rate=0.9
        )
        
        # Test matching context
        matching_context = {
            "execution_type": "magic_fix",
            "opportunity_type": "security",
            "safety_score": 0.8
        }
        
        assert feedback_loop._pattern_matches_context(pattern, matching_context)
        
        # Test non-matching context
        non_matching_context = {
            "execution_type": "magic_refactor",
            "opportunity_type": "quality"
        }
        
        assert not feedback_loop._pattern_matches_context(pattern, non_matching_context)


class TestLearningPattern:
    """Test LearningPattern dataclass."""
    
    def test_learning_pattern_creation(self):
        """Test creating a LearningPattern."""
        pattern = LearningPattern(
            pattern_id="test_1",
            pattern_type="success",
            confidence=0.85,
            description="Test pattern",
            conditions={"test": True},
            actions={"action": "test"},
            outcomes={"outcome": "success"},
            usage_count=5,
            success_rate=0.9
        )
        
        assert pattern.pattern_id == "test_1"
        assert pattern.pattern_type == "success"
        assert pattern.confidence == 0.85
        assert pattern.usage_count == 5
        assert pattern.success_rate == 0.9
    
    def test_learning_pattern_to_dict(self):
        """Test converting LearningPattern to dictionary."""
        pattern = LearningPattern(
            pattern_id="test_2",
            pattern_type="failure", 
            confidence=0.6,
            description="Test failure pattern",
            conditions={"test": False},
            actions={"action": "avoid"},
            outcomes={"outcome": "failure"},
            usage_count=3,
            success_rate=0.2
        )
        
        pattern_dict = pattern.to_dict()
        
        assert isinstance(pattern_dict, dict)
        assert pattern_dict["pattern_id"] == "test_2"
        assert pattern_dict["pattern_type"] == "failure"
        assert pattern_dict["confidence"] == 0.6
        assert pattern_dict["usage_count"] == 3
        assert pattern_dict["success_rate"] == 0.2


class TestPatternIdentification:
    """Test pattern identification functionality."""
    
    @pytest.fixture
    def feedback_loop(self):
        """Create feedback loop instance."""
        return FeedbackLoop(memory_store=IntelligentMemoryStore())
    
    def test_identify_patterns_from_results(self, feedback_loop):
        """Test identifying patterns from execution results."""
        results = [
            {"success": True, "execution_type": "magic_fix"},
            {"success": True, "execution_type": "magic_fix"},
            {"success": False, "execution_type": "magic_refactor"},
            {"success": False, "execution_type": "magic_refactor"}
        ]
        
        patterns = feedback_loop._identify_patterns(results)
        
        # Should identify some patterns
        assert isinstance(patterns, list)
        
        for pattern in patterns:
            assert isinstance(pattern, LearningPattern)
            assert pattern.pattern_type in ["success", "failure"]
            assert 0.0 <= pattern.confidence <= 1.0
            assert pattern.usage_count >= 0
            assert 0.0 <= pattern.success_rate <= 1.0
    
    def test_find_common_patterns(self, feedback_loop):
        """Test finding common patterns in results."""
        # Test success patterns
        success_results = [
            {"success": True, "execution_type": "magic_fix"},
            {"success": True, "execution_type": "magic_fix"}
        ]
        
        success_patterns = feedback_loop._find_common_patterns(success_results, "success")
        
        assert len(success_patterns) > 0
        assert success_patterns[0].pattern_type == "success"
        
        # Test failure patterns
        failure_results = [
            {"success": False, "execution_type": "magic_refactor"},
            {"success": False, "execution_type": "magic_refactor"}
        ]
        
        failure_patterns = feedback_loop._find_common_patterns(failure_results, "failure")
        
        assert len(failure_patterns) > 0
        assert failure_patterns[0].pattern_type == "failure"


class TestMemoryIntegration:
    """Test integration with memory system."""
    
    @pytest.fixture
    def feedback_loop(self):
        """Create feedback loop with memory store."""
        return FeedbackLoop(memory_store=IntelligentMemoryStore())
    
    def test_memory_storage_on_success(self, feedback_loop):
        """Test that successes are stored in memory."""
        success_result = {
            "success": True,
            "execution_type": "magic_fix",
            "description": "Fixed security issue",
            "opportunity": Mock(type="security", safety_score=0.8)
        }
        
        feedback_loop.record_success(success_result)
        
        # Should store in memory
        memories = feedback_loop.memory_store.query(tags=["feedback_loop", "success"])
        assert len(memories) > 0
        
        # Memory should contain relevant information
        memory = memories[0]
        assert "magic_fix" in memory.content
    
    def test_memory_storage_on_failure(self, feedback_loop):
        """Test that failures are stored in memory."""
        failure_result = {
            "success": False,
            "execution_type": "magic_refactor",
            "error": "Refactoring failed",
            "opportunity": Mock(type="quality", safety_score=0.6)
        }
        
        feedback_loop.record_failure(failure_result)
        
        # Should store in memory
        memories = feedback_loop.memory_store.query(tags=["feedback_loop", "failure"])
        assert len(memories) > 0
        
        # Memory should contain error information
        memory = memories[0]
        assert "magic_refactor" in memory.content
        assert "Refactoring failed" in memory.content
    
    def test_pattern_saving(self, feedback_loop):
        """Test that learned patterns are saved to memory."""
        # Add some patterns
        pattern = LearningPattern(
            pattern_id="test_save_1",
            pattern_type="success",
            confidence=0.9,
            description="Test pattern",
            conditions={"test": "pattern"},
            actions={"approach": "test"},
            outcomes={"success_rate": 0.9},
            usage_count=3,
            success_rate=0.9
        )
        
        feedback_loop.learned_patterns.append(pattern)
        feedback_loop._save_patterns_to_memory()
        
        # Should be stored in memory
        memories = feedback_loop.memory_store.query(tags=["feedback_loop", "patterns"])
        assert len(memories) > 0
