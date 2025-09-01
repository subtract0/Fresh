"""
Tests for Intelligent Memory System

Comprehensive test suite for enhanced memory capabilities including
semantic search, auto-classification, and intelligent retrieval.
"""
from __future__ import annotations
from datetime import datetime, timezone
import pytest

from ai.memory.intelligent_store import (
    IntelligentMemoryStore, 
    MemoryType, 
    EnhancedMemoryItem
)
from ai.tools.enhanced_memory_tools import (
    SmartWriteMemory,
    SemanticSearchMemory, 
    GetMemoryByType,
    GetRelatedMemories,
    AnalyzeMemoryUsage,
    OptimizeMemoryStore
)


class TestIntelligentMemoryStore:
    """Test intelligent memory store functionality."""
    
    def test_auto_classification(self):
        """Test automatic content classification."""
        store = IntelligentMemoryStore()
        
        # Test goal classification
        goal_item = store.write(content="Goal: Implement real-time agent communication", tags=[])
        assert goal_item.memory_type == MemoryType.GOAL
        assert goal_item.importance_score > 0.7  # Goals are high importance
        
        # Test task classification
        task_item = store.write(content="Task: Fix bug in memory search algorithm", tags=["task"])
        assert task_item.memory_type == MemoryType.TASK
        
        # Test decision classification
        adr_item = store.write(content="ADR-008: Adopt intelligent memory system architecture", tags=[])
        assert adr_item.memory_type == MemoryType.DECISION
        assert adr_item.importance_score > 0.7  # Decisions are high importance
        
        # Test progress classification
        progress_item = store.write(content="Completed: Memory system integration tests", tags=["done"])
        assert progress_item.memory_type == MemoryType.PROGRESS
        
        # Test error classification
        error_item = store.write(content="Error: Agent communication timeout after 30s", tags=[])
        assert error_item.memory_type == MemoryType.ERROR
        assert error_item.importance_score >= 0.6  # Errors are important to remember
        
        # Test knowledge classification
        knowledge_item = store.write(content="Learned: Activity detection works best with 60s windows", tags=[])
        assert knowledge_item.memory_type == MemoryType.KNOWLEDGE
        
    def test_keyword_extraction(self):
        """Test keyword extraction from content."""
        store = IntelligentMemoryStore()
        
        item = store.write(content="Agent communication system needs real-time monitoring capabilities", tags=[])
        
        # Should extract meaningful keywords
        assert "agent" in item.keywords
        assert "communication" in item.keywords
        assert "system" in item.keywords
        assert "monitoring" in item.keywords
        
        # Should exclude stop words
        assert "needs" not in item.keywords
        assert "the" not in item.keywords
        
    def test_importance_scoring(self):
        """Test importance score calculation."""
        store = IntelligentMemoryStore()
        
        # Critical content should have high importance
        critical_item = store.write(content="Critical: System failure in production agent deployment", tags=[])
        assert critical_item.importance_score >= 0.8
        
        # Goals should have high importance
        goal_item = store.write(content="Goal: Launch agent monitoring system", tags=["goal"])
        assert goal_item.importance_score >= 0.8
        
        # Long detailed content should have higher importance
        detailed_item = store.write(
            content="This is a very detailed explanation of the agent communication protocol including specific implementation details, configuration parameters, error handling strategies, and performance optimization techniques that are essential for system operation.",
            tags=[]
        )
        assert detailed_item.importance_score > 0.5
        
        # Short context should have lower importance
        short_item = store.write(content="Quick note", tags=[])
        assert short_item.importance_score < 0.6
        
    def test_summary_generation(self):
        """Test automatic summary generation."""
        store = IntelligentMemoryStore()
        
        # Short content should not have summary
        short_item = store.write(content="Short message here.", tags=[])
        assert short_item.summary is None
        
        # Long content should have summary
        long_content = "This is a very long piece of content that describes the implementation details of the agent monitoring system. It includes information about activity detection, adaptive refresh rates, and real-time UI updates. The system uses Rich for terminal interface and psutil for performance monitoring."
        long_item = store.write(content=long_content, tags=[])
        assert long_item.summary is not None
        assert len(long_item.summary) < len(long_content)
        
    def test_related_memory_detection(self):
        """Test finding related memories based on keyword overlap."""
        store = IntelligentMemoryStore()
        
        # Create related memories
        item1 = store.write(content="Agent monitoring system architecture", tags=["system"])
        item2 = store.write(content="Monitoring performance optimization", tags=["performance"])  
        item3 = store.write(content="System architecture decisions", tags=["architecture"])
        item4 = store.write(content="Unrelated cooking recipe", tags=["food"])
        
        # Check bidirectional relationships
        # item1 is first so has no related items initially, but gets updated when related items are created
        # item2 and item3 should relate back to item1
        # item4 should not be related (no shared keywords)
        
        updated_item1 = store.get_by_id(item1.id)
        assert len(updated_item1.related_ids) >= 1  # Should find related memories after updates
        assert len(item2.related_ids) >= 1  # Should find item1 (shared "monitoring")
        assert len(item3.related_ids) >= 1  # Should find item1 (shared "system", "architecture")
        assert len(item4.related_ids) == 0  # Should not find unrelated memories
        
    def test_semantic_search(self):
        """Test keyword-based semantic search."""
        store = IntelligentMemoryStore()
        
        # Add diverse memories
        store.write(content="Agent communication protocol implementation", tags=["agent", "comm"])
        store.write(content="Real-time monitoring dashboard", tags=["monitoring", "ui"])
        store.write(content="Communication timeout errors", tags=["error", "comm"])
        store.write(content="Cooking pasta recipe", tags=["food"])
        
        # Search for communication-related memories
        results = store.search_by_keywords(["communication", "agent"], limit=10)
        
        # Should find relevant memories
        assert len(results) >= 2
        for result in results:
            content_lower = result.content.lower()
            assert "communication" in content_lower or "agent" in content_lower or "comm" in str(result.tags)
            
    def test_search_by_type(self):
        """Test searching memories by classification type."""
        store = IntelligentMemoryStore()
        
        # Add memories of different types
        store.write(content="Goal: Implement semantic search", tags=["goal"])
        store.write(content="Task: Write unit tests", tags=["task"])
        store.write(content="Goal: Launch beta version", tags=["goal"])
        store.write(content="Context: System uses Python 3.12", tags=[])
        
        # Search for goals
        goals = store.search_by_type(MemoryType.GOAL, limit=10)
        assert len(goals) == 2
        for goal in goals:
            assert goal.memory_type == MemoryType.GOAL
            
        # Search for tasks
        tasks = store.search_by_type(MemoryType.TASK, limit=10)
        assert len(tasks) == 1
        assert tasks[0].memory_type == MemoryType.TASK
        
    def test_memory_optimization(self):
        """Test memory store optimization."""
        store = IntelligentMemoryStore()
        
        # Add many memories with varying importance
        for i in range(50):
            importance_word = "critical" if i < 10 else ""  # First 10 are high importance
            content = f"{importance_word} Memory item {i} with some content"
            store.write(content=content, tags=[f"item{i}"])
            
        # Optimize to keep only 20 items
        removed = store.optimize_memory(max_items=20)
        
        assert removed == 30  # Should remove 30 items
        assert len(store._items) == 20  # Should keep 20 items
        
        # Should keep high-importance items
        remaining_content = [item.content for item in store._items]
        critical_remaining = sum(1 for content in remaining_content if "critical" in content)
        assert critical_remaining > 5  # Most critical items should be kept
        
    def test_memory_analytics(self):
        """Test memory usage analytics."""
        store = IntelligentMemoryStore()
        
        # Add diverse memories
        store.write(content="Goal: Launch system", tags=["goal"])
        store.write(content="Task: Write docs", tags=["task"])
        store.write(content="Error: Connection failed", tags=["error"])
        store.write(content="Agent monitoring system", tags=["agent"])
        
        analytics = store.get_memory_analytics()
        
        assert analytics["total_memories"] == 4
        assert "type_distribution" in analytics
        assert analytics["type_distribution"][MemoryType.GOAL] == 1
        assert analytics["type_distribution"][MemoryType.TASK] == 1
        assert analytics["type_distribution"][MemoryType.ERROR] == 1
        
        assert "average_importance" in analytics
        assert 0.0 <= analytics["average_importance"] <= 1.0
        
        assert "top_keywords" in analytics
        assert "agent" in analytics["top_keywords"]
        

class TestEnhancedMemoryTools:
    """Test enhanced memory tools."""
    
    def test_smart_write_memory(self):
        """Test SmartWriteMemory tool."""
        from ai.memory.store import set_memory_store
        
        # Use intelligent store
        store = IntelligentMemoryStore()
        set_memory_store(store)
        
        tool = SmartWriteMemory(
            content="Goal: Implement real-time agent communication system",
            tags=["goal", "communication"]
        )
        
        result = tool.run()
        
        # Should return JSON with intelligence metadata
        assert "mem-" in result
        assert "GOAL" in result or "goal" in result
        assert "importance" in result
        assert "keywords" in result
        
    def test_semantic_search_memory(self):
        """Test SemanticSearchMemory tool."""
        from ai.memory.store import set_memory_store
        
        store = IntelligentMemoryStore()
        set_memory_store(store)
        
        # Add searchable memories
        store.write(content="Agent communication protocol design", tags=["agent"])
        store.write(content="Real-time monitoring system", tags=["monitoring"])
        store.write(content="Communication error handling", tags=["error"])
        
        tool = SemanticSearchMemory(keywords=["communication", "agent"], limit=5)
        result = tool.run()
        
        assert "communication" in result.lower() or "agent" in result.lower()
        assert "Keywords:" in result  # Should show extracted keywords
        assert "Importance:" in result  # Should show importance scores
        
    def test_get_memory_by_type(self):
        """Test GetMemoryByType tool."""
        from ai.memory.store import set_memory_store
        
        store = IntelligentMemoryStore()
        set_memory_store(store)
        
        # Add typed memories
        store.write(content="Goal: Launch beta version", tags=["goal"])
        store.write(content="Task: Write documentation", tags=["task"])
        store.write(content="Another goal: Improve performance", tags=["goal"])
        
        tool = GetMemoryByType(memory_type="goal", limit=5)
        result = tool.run()
        
        assert "GOAL MEMORIES:" in result
        assert "beta version" in result
        assert "Improve performance" in result
        assert "Write documentation" not in result  # Should not include tasks
        
    def test_analyze_memory_usage(self):
        """Test AnalyzeMemoryUsage tool."""
        from ai.memory.store import set_memory_store
        
        store = IntelligentMemoryStore()
        set_memory_store(store)
        
        # Add memories for analysis
        store.write(content="Goal: Test analytics", tags=["goal"])
        store.write(content="Task: Implement features", tags=["task"])
        store.write(content="Agent system monitoring", tags=["agent"])
        
        tool = AnalyzeMemoryUsage()
        result = tool.run()
        
        assert "MEMORY USAGE ANALYTICS" in result
        assert "Total Memories: 3" in result
        assert "Memory Types:" in result
        assert "Top Keywords:" in result
        
    def test_optimize_memory_store(self):
        """Test OptimizeMemoryStore tool."""
        from ai.memory.store import set_memory_store
        
        store = IntelligentMemoryStore()
        set_memory_store(store)
        
        # Add many memories
        for i in range(15):
            store.write(content=f"Memory item {i}", tags=[f"item{i}"])
            
        tool = OptimizeMemoryStore(max_items=10)
        result = tool.run()
        
        assert "Memory optimized" in result
        assert "Removed 5" in result
        assert len(store._items) == 10
        
    def test_fallback_to_basic_store(self):
        """Test tools fallback gracefully to basic memory store."""
        from ai.memory.store import set_memory_store, InMemoryMemoryStore
        
        # Use basic store
        basic_store = InMemoryMemoryStore()
        set_memory_store(basic_store)
        
        # SmartWriteMemory should work but return simple ID
        smart_tool = SmartWriteMemory(content="Test content", tags=["test"])
        result = smart_tool.run()
        assert result.startswith("mem-")  # Should return basic ID
        
        # SemanticSearchMemory should fallback to basic search
        search_tool = SemanticSearchMemory(keywords=["test"], limit=5)
        result = search_tool.run()
        assert result is not None  # Should not crash
        
        # GetMemoryByType should fallback to tag filtering
        type_tool = GetMemoryByType(memory_type="goal", limit=5)
        result = type_tool.run()
        assert result is not None  # Should not crash


class TestMemoryIntegration:
    """Integration tests for intelligent memory system."""
    
    def test_full_workflow(self):
        """Test complete intelligent memory workflow."""
        from ai.memory.store import set_memory_store
        
        store = IntelligentMemoryStore()
        set_memory_store(store)
        
        # 1. Write diverse memories
        write_tool = SmartWriteMemory(content="Goal: Launch agent monitoring system", tags=["goal"])
        goal_result = write_tool.run()
        assert "goal" in goal_result.lower()
        
        write_tool = SmartWriteMemory(content="Task: Implement semantic search feature", tags=["task"])
        task_result = write_tool.run()
        
        write_tool = SmartWriteMemory(content="Error: Memory search timeout after 5 seconds", tags=["error"])
        error_result = write_tool.run()
        
        # 2. Search by keywords
        search_tool = SemanticSearchMemory(keywords=["search", "memory"], limit=5)
        search_result = search_tool.run()
        assert "semantic search" in search_result or "memory search" in search_result
        
        # 3. Get memories by type
        goal_tool = GetMemoryByType(memory_type="goal", limit=5)
        goal_memories = goal_tool.run()
        assert "GOAL MEMORIES:" in goal_memories
        assert "monitoring system" in goal_memories
        
        # 4. Analyze usage
        analytics_tool = AnalyzeMemoryUsage()
        analytics = analytics_tool.run()
        assert "Total Memories: 3" in analytics
        assert "GOAL: 1" in analytics
        assert "TASK: 1" in analytics
        assert "ERROR: 1" in analytics
        
        # 5. Verify intelligent features are working
        assert len(store._items) == 3
        assert all(isinstance(item, EnhancedMemoryItem) for item in store._items)
        assert all(item.keywords for item in store._items)  # All should have keywords
        assert all(0.0 <= item.importance_score <= 1.0 for item in store._items)  # Valid scores
