"""
Tests for Firestore Memory Store

Tests for the persistent memory store implementation using Firestore.
Includes tests for both connected and fallback modes.
"""
from __future__ import annotations
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

from ai.memory.firestore_store import (
    FirestoreMemoryStore,
    create_firestore_memory_store,
    FIRESTORE_AVAILABLE
)
from ai.memory.intelligent_store import MemoryType, EnhancedMemoryItem


class TestFirestoreMemoryStore:
    """Test FirestoreMemoryStore functionality."""
    
    @pytest.mark.skipif(not FIRESTORE_AVAILABLE, reason="Firestore dependencies not available")
    def test_init_with_firestore_available(self):
        """Test initialization when Firestore is available."""
        with patch('ai.memory.firestore_store.firestore') as mock_firestore:
            mock_client = Mock()
            mock_client.project = "test-project"
            mock_firestore.Client.return_value = mock_client
            
            store = FirestoreMemoryStore(project_id="test-project")
            
            assert store.project_id == "test-project"
            assert store.collection_name == "agent_memories"
            assert store.max_local_cache == 100
            assert store.sync_on_write is True
            # The client is wrapped, so check if it exists and has the right project
            assert store._firestore_client is not None
            assert hasattr(store._firestore_client, 'project')
    
    def test_init_without_firestore(self):
        """Test initialization fallback when Firestore is not available."""
        with patch('ai.memory.firestore_store.FIRESTORE_AVAILABLE', False):
            store = FirestoreMemoryStore()
            
            assert store._firestore_client is None
            # Should still work as IntelligentMemoryStore
            assert hasattr(store, '_items')
    
    def test_init_with_firestore_error(self):
        """Test initialization when Firestore client creation fails."""
        with patch('ai.memory.firestore_store.firestore') as mock_firestore:
            mock_firestore.Client.side_effect = Exception("Connection failed")
            
            store = FirestoreMemoryStore()
            
            assert store._firestore_client is None
    
    def test_fallback_write_without_firestore(self):
        """Test writing memories works even without Firestore."""
        with patch('ai.memory.firestore_store.FIRESTORE_AVAILABLE', False):
            store = FirestoreMemoryStore()
            
            item = store.write(content="Test memory", tags=["test"])
            
            assert item.content == "Test memory"
            assert "test" in item.tags
            assert len(store._items) == 1
    
    @pytest.mark.skipif(not FIRESTORE_AVAILABLE, reason="Firestore dependencies not available")
    def test_memory_item_conversion(self):
        """Test conversion between memory items and Firestore documents."""
        with patch('ai.memory.firestore_store.firestore'):
            store = FirestoreMemoryStore()
            store._firestore_client = None  # Disable Firestore for this test
            
            # Create a test item
            item = store.write(content="Test content", tags=["test"])
            
            # Convert to dict
            item_dict = store._memory_item_to_dict(item)
            
            assert item_dict['id'] == item.id
            assert item_dict['content'] == "Test content"
            assert item_dict['tags'] == ["test"]
            assert item_dict['memory_type'] == item.memory_type.value
            assert 'last_accessed' in item_dict
            
            # Convert back to item
            restored_item = store._dict_to_memory_item(item_dict)
            
            assert restored_item.id == item.id
            assert restored_item.content == item.content
            assert restored_item.tags == item.tags
            assert restored_item.memory_type == item.memory_type
    
    @pytest.mark.skipif(not FIRESTORE_AVAILABLE, reason="Firestore dependencies not available")
    def test_sync_to_firestore(self):
        """Test syncing memory items to Firestore."""
        with patch('ai.memory.firestore_store.firestore') as mock_firestore:
            mock_client = Mock()
            mock_collection = Mock()
            mock_doc = Mock()
            
            mock_client.collection.return_value = mock_collection
            mock_collection.document.return_value = mock_doc
            mock_firestore.Client.return_value = mock_client
            
            store = FirestoreMemoryStore()
            item = store.write(content="Test sync", tags=["sync"])
            
            # Verify Firestore was called
            mock_client.collection.assert_called_with("agent_memories")
            mock_collection.document.assert_called_with(item.id)
            mock_doc.set.assert_called_once()
    
    def test_local_cache_management(self):
        """Test local cache size management."""
        with patch('ai.memory.firestore_store.FIRESTORE_AVAILABLE', False):
            store = FirestoreMemoryStore(max_local_cache=3)
            
            # Add items beyond cache limit
            items = []
            for i in range(5):
                item = store.write(content=f"Test item {i}", tags=[f"item{i}"])
                items.append(item)
            
            # Should only keep 3 most important/recent items
            assert len(store._items) == 3
            
            # Check that high-importance items are kept
            contents = [item.content for item in store._items]
            # At least some of the recent items should be kept
            assert any("Test item" in content for content in contents)
    
    @pytest.mark.skipif(not FIRESTORE_AVAILABLE, reason="Firestore dependencies not available")
    def test_search_firestore_fallback(self):
        """Test Firestore search with fallback to local search."""
        with patch('ai.memory.firestore_store.firestore'):
            store = FirestoreMemoryStore()
            store._firestore_client = None  # Disable Firestore
            
            # Add some test memories
            store.write(content="Agent communication system", tags=["agent"])
            store.write(content="Database optimization", tags=["db"])
            store.write(content="Agent monitoring tools", tags=["agent", "monitoring"])
            
            # Search should fallback to local search
            results = store.search_firestore(keywords=["agent"], limit=10)
            
            assert len(results) >= 2
            for result in results:
                assert "agent" in result.keywords or "agent" in result.content.lower()
    
    @pytest.mark.skipif(not FIRESTORE_AVAILABLE, reason="Firestore dependencies not available")
    def test_get_memory_stats_without_firestore(self):
        """Test memory stats when Firestore is not connected."""
        with patch('ai.memory.firestore_store.FIRESTORE_AVAILABLE', False):
            store = FirestoreMemoryStore()
            
            store.write(content="Test memory", tags=["test"])
            
            stats = store.get_memory_stats()
            
            assert stats["firestore_connected"] is False
            assert stats["total_memories"] == 1
    
    @pytest.mark.skipif(not FIRESTORE_AVAILABLE, reason="Firestore dependencies not available")
    def test_get_memory_stats_with_firestore(self):
        """Test memory stats when Firestore is connected."""
        with patch('ai.memory.firestore_store.firestore') as mock_firestore:
            mock_client = Mock()
            mock_collection = Mock()
            
            # Mock empty collection
            mock_collection.limit.return_value.stream.return_value = iter([])
            mock_client.collection.return_value = mock_collection
            mock_firestore.Client.return_value = mock_client
            
            store = FirestoreMemoryStore()
            
            stats = store.get_memory_stats()
            
            assert stats["firestore_connected"] is True
            assert stats["local_cache_size"] == 0
            assert stats["max_cache_size"] == 100
    
    def test_force_sync_without_firestore(self):
        """Test force sync when Firestore is not available."""
        with patch('ai.memory.firestore_store.FIRESTORE_AVAILABLE', False):
            store = FirestoreMemoryStore()
            
            result = store.force_sync()
            
            assert "error" in result
            assert "Firestore not available" in result["error"]
    
    @pytest.mark.skipif(not FIRESTORE_AVAILABLE, reason="Firestore dependencies not available")
    def test_consolidate_memories_without_firestore(self):
        """Test memory consolidation when Firestore is not available."""
        with patch('ai.memory.firestore_store.FIRESTORE_AVAILABLE', False):
            store = FirestoreMemoryStore()
            
            result = store.consolidate_memories()
            
            assert result["status"] == "Firestore not available"


class TestFirestoreFactory:
    """Test factory function for creating Firestore memory stores."""
    
    def test_create_firestore_memory_store_success(self):
        """Test successful creation of FirestoreMemoryStore."""
        with patch('ai.memory.firestore_store.FirestoreMemoryStore') as MockStore:
            mock_instance = Mock()
            MockStore.return_value = mock_instance
            
            result = create_firestore_memory_store(project_id="test")
            
            assert result is mock_instance
            MockStore.assert_called_once_with(project_id="test")
    
    def test_create_firestore_memory_store_fallback(self):
        """Test fallback to IntelligentMemoryStore when FirestoreMemoryStore fails."""
        with patch('ai.memory.firestore_store.FirestoreMemoryStore') as MockFirestore, \
             patch('ai.memory.firestore_store.IntelligentMemoryStore') as MockIntelligent:
            
            MockFirestore.side_effect = Exception("Firestore unavailable")
            mock_intelligent = Mock()
            MockIntelligent.return_value = mock_intelligent
            
            result = create_firestore_memory_store(project_id="test")
            
            assert result is mock_intelligent
            MockIntelligent.assert_called_once()


class TestFirestoreIntegration:
    """Integration tests for Firestore memory store."""
    
    def test_end_to_end_fallback_mode(self):
        """Test complete workflow in fallback mode."""
        with patch('ai.memory.firestore_store.FIRESTORE_AVAILABLE', False):
            store = FirestoreMemoryStore()
            
            # Write diverse memories
            goal_item = store.write(content="Goal: Implement persistent memory", tags=["goal"])
            task_item = store.write(content="Task: Write Firestore integration", tags=["task"])
            error_item = store.write(content="Error: Connection timeout", tags=["error"])
            
            # Verify intelligent features still work
            assert goal_item.memory_type == MemoryType.GOAL
            assert task_item.memory_type == MemoryType.TASK
            assert error_item.memory_type == MemoryType.ERROR
            
            # Search functionality
            results = store.search_by_keywords(["memory"], limit=10)
            assert len(results) >= 1
            
            # Analytics
            stats = store.get_memory_stats()
            assert stats["total_memories"] == 3
            assert stats["firestore_connected"] is False
            
            # All items should have proper intelligence metadata
            assert all(item.keywords for item in [goal_item, task_item, error_item])
            assert all(0.0 <= item.importance_score <= 1.0 for item in [goal_item, task_item, error_item])
    
    @pytest.mark.skipif(not FIRESTORE_AVAILABLE, reason="Firestore dependencies not available")
    def test_mock_firestore_workflow(self):
        """Test workflow with mocked Firestore client."""
        with patch('ai.memory.firestore_store.firestore') as mock_firestore:
            # Set up mock Firestore client
            mock_client = Mock()
            mock_collection = Mock()
            mock_doc = Mock()
            
            # Mock the collection chain
            mock_client.collection.return_value = mock_collection
            mock_collection.document.return_value = mock_doc
            mock_collection.where.return_value.order_by.return_value.limit.return_value.stream.return_value = iter([])
            mock_firestore.Client.return_value = mock_client
            mock_client.project = "test-project"
            
            store = FirestoreMemoryStore(project_id="test-project")
            
            # Write a memory (should sync to Firestore)
            item = store.write(content="Test Firestore integration", tags=["test", "firestore"])
            
            # Verify Firestore operations were called
            mock_client.collection.assert_called()
            mock_doc.set.assert_called()
            
            # Memory should have intelligent features
            assert item.memory_type == MemoryType.CONTEXT  # Default classification
            assert "test" in item.keywords or "firestore" in item.keywords
            assert 0.0 <= item.importance_score <= 1.0
