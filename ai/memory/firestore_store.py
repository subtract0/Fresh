"""
Firestore Memory Store

Persistent memory store implementation using Google Cloud Firestore for
long-term agent memory across sessions and deployments.

Features:
- Persistent storage across agent sessions
- Automatic memory consolidation and cleanup
- Activity-based memory scoring and relevance
- Graceful fallback to in-memory store if Firestore unavailable

Cross-references:
    - ADR-004: Persistent Agent Memory
    - ai/memory/store.py: Base memory store interface
    - ai/memory/intelligent_store.py: Enhanced memory features
"""
from __future__ import annotations
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import asdict

from ai.memory.intelligent_store import IntelligentMemoryStore, EnhancedMemoryItem, MemoryType
from ai.utils.clock import now as time_now
from ai.monitor.firestore_tracker import wrap_firestore_client

# Try to import Firestore with graceful fallback
try:
    from google.cloud import firestore
    from google.cloud.exceptions import NotFound, GoogleCloudError
    FIRESTORE_AVAILABLE = True
except ImportError:
    FIRESTORE_AVAILABLE = False
    firestore = None

logger = logging.getLogger(__name__)


class FirestoreMemoryStore(IntelligentMemoryStore):
    """
    Firestore-backed intelligent memory store for persistent agent memory.
    
    Extends IntelligentMemoryStore with:
    - Persistent storage in Google Cloud Firestore
    - Automatic memory consolidation and cleanup
    - Cross-session memory persistence
    - Activity-based memory relevance scoring
    """
    
    def __init__(self, 
                 project_id: Optional[str] = None,
                 collection_name: str = "agent_memories",
                 max_local_cache: int = 100,
                 sync_on_write: bool = True):
        """
        Initialize Firestore memory store.
        
        Args:
            project_id: Google Cloud project ID. If None, will use default.
            collection_name: Firestore collection name for memories
            max_local_cache: Maximum items to keep in local cache
            sync_on_write: Whether to sync to Firestore on every write
        """
        super().__init__()
        
        self.project_id = project_id
        self.collection_name = collection_name
        self.max_local_cache = max_local_cache
        self.sync_on_write = sync_on_write
        self._firestore_client = None
        self._last_sync = 0.0
        
        # Initialize Firestore connection
        self._init_firestore()
        
        # Load existing memories from Firestore
        if self._firestore_client:
            self._load_from_firestore()
    
    def _init_firestore(self) -> None:
        """Initialize Firestore client with error handling."""
        if not FIRESTORE_AVAILABLE:
            logger.warning("Firestore not available - falling back to in-memory storage")
            return
            
        try:
            if self.project_id:
                raw_client = firestore.Client(project=self.project_id)
            else:
                raw_client = firestore.Client()
            self._firestore_client = wrap_firestore_client(raw_client)  # Add cost tracking
            logger.info(f"Connected to Firestore project: {self._firestore_client.project}")
        except Exception as e:
            logger.error(f"Failed to initialize Firestore client: {e}")
            logger.warning("Falling back to in-memory storage")
            self._firestore_client = None
    
    def _load_from_firestore(self) -> None:
        """Load existing memories from Firestore into local cache."""
        if not self._firestore_client:
            return
            
        try:
            collection_ref = self._firestore_client.collection(self.collection_name)
            
            # Load recent memories first (last 30 days)
            cutoff_time = datetime.fromtimestamp(time_now() - 30 * 24 * 3600, timezone.utc)
            
            query = collection_ref.where('created_at', '>=', cutoff_time).order_by('created_at', direction=firestore.Query.DESCENDING).limit(self.max_local_cache)
            
            memories = []
            for doc in query.stream():
                try:
                    data = doc.to_dict()
                    memory_item = self._dict_to_memory_item(data)
                    memories.append(memory_item)
                except Exception as e:
                    logger.warning(f"Failed to deserialize memory {doc.id}: {e}")
                    
            # Load in chronological order
            self._items = list(reversed(memories))
            
            # Rebuild indexes
            self._keyword_index.clear()
            self._type_index.clear()
            for item in self._items:
                self._update_indexes(item)
                
            logger.info(f"Loaded {len(self._items)} memories from Firestore")
            self._last_sync = time_now()
            
        except Exception as e:
            logger.error(f"Failed to load memories from Firestore: {e}")
    
    def _dict_to_memory_item(self, data: Dict[str, Any]) -> EnhancedMemoryItem:
        """Convert Firestore document data to EnhancedMemoryItem."""
        # Handle datetime conversion
        if 'created_at' in data and hasattr(data['created_at'], 'timestamp'):
            created_at = datetime.fromtimestamp(data['created_at'].timestamp(), timezone.utc)
        else:
            created_at = datetime.fromtimestamp(time_now(), timezone.utc)
        
        # Convert memory type
        memory_type = MemoryType.CONTEXT
        if 'memory_type' in data:
            try:
                memory_type = MemoryType(data['memory_type'])
            except ValueError:
                pass
                
        return EnhancedMemoryItem(
            id=data.get('id', ''),
            content=data.get('content', ''),
            tags=data.get('tags', []),
            created_at=created_at,
            memory_type=memory_type,
            keywords=data.get('keywords', []),
            related_ids=data.get('related_ids', []),
            importance_score=data.get('importance_score', 0.5),
            summary=data.get('summary')
        )
    
    def _memory_item_to_dict(self, item: EnhancedMemoryItem) -> Dict[str, Any]:
        """Convert EnhancedMemoryItem to Firestore document data."""
        data = {
            'id': item.id,
            'content': item.content,
            'tags': item.tags,
            'created_at': item.created_at,
            'memory_type': item.memory_type.value,
            'keywords': item.keywords,
            'related_ids': item.related_ids,
            'importance_score': item.importance_score,
            'summary': item.summary,
            'last_accessed': datetime.fromtimestamp(time_now(), timezone.utc)
        }
        return data
    
    def _sync_to_firestore(self, item: EnhancedMemoryItem) -> None:
        """Sync a single memory item to Firestore."""
        if not self._firestore_client:
            return
            
        try:
            collection_ref = self._firestore_client.collection(self.collection_name)
            doc_ref = collection_ref.document(item.id)
            data = self._memory_item_to_dict(item)
            doc_ref.set(data)
            logger.debug(f"Synced memory {item.id} to Firestore")
        except Exception as e:
            logger.error(f"Failed to sync memory {item.id} to Firestore: {e}")
    
    def write(self, *, content: str, tags: Optional[List[str]] = None) -> EnhancedMemoryItem:
        """Write enhanced memory item with Firestore persistence."""
        # Use parent implementation for intelligent processing
        item = super().write(content=content, tags=tags)
        
        # Sync to Firestore if enabled
        if self.sync_on_write:
            self._sync_to_firestore(item)
        
        # Manage local cache size
        self._manage_local_cache()
        
        return item
    
    def _manage_local_cache(self) -> None:
        """Manage local cache size by removing least important old items."""
        if len(self._items) <= self.max_local_cache:
            return
            
        # Sort by importance and recency, keep the most valuable
        self._items.sort(key=lambda i: (i.importance_score, i.created_at.timestamp()), reverse=True)
        
        # Keep only the top items in local cache
        removed_items = self._items[self.max_local_cache:]
        self._items = self._items[:self.max_local_cache]
        
        # Rebuild indexes for remaining items
        self._keyword_index.clear()
        self._type_index.clear()
        for item in self._items:
            self._update_indexes(item)
            
        logger.debug(f"Trimmed local cache, removed {len(removed_items)} items")
    
    def consolidate_memories(self, days_back: int = 7, min_importance: float = 0.6) -> Dict[str, int]:
        """
        Consolidate and clean up old memories in Firestore.
        
        Args:
            days_back: How many days back to consider for consolidation
            min_importance: Minimum importance score to keep memories
            
        Returns:
            Stats about consolidation process
        """
        if not self._firestore_client:
            return {"status": "Firestore not available"}
            
        try:
            collection_ref = self._firestore_client.collection(self.collection_name)
            
            # Find old, low-importance memories
            cutoff_time = datetime.fromtimestamp(time_now() - days_back * 24 * 3600, timezone.utc)
            
            query = collection_ref.where('created_at', '<', cutoff_time).where('importance_score', '<', min_importance)
            
            deleted_count = 0
            batch = self._firestore_client.batch()
            batch_size = 0
            
            for doc in query.stream():
                batch.delete(doc.reference)
                batch_size += 1
                
                # Commit in batches of 500 (Firestore limit)
                if batch_size >= 500:
                    batch.commit()
                    deleted_count += batch_size
                    batch = self._firestore_client.batch()
                    batch_size = 0
            
            # Commit remaining deletions
            if batch_size > 0:
                batch.commit()
                deleted_count += batch_size
            
            # Update access times for remaining memories
            updated_count = self._update_access_times()
            
            logger.info(f"Memory consolidation complete: deleted {deleted_count}, updated {updated_count}")
            
            return {
                "deleted_count": deleted_count,
                "updated_count": updated_count,
                "days_back": days_back,
                "min_importance": min_importance
            }
            
        except Exception as e:
            logger.error(f"Memory consolidation failed: {e}")
            return {"error": str(e)}
    
    def _update_access_times(self) -> int:
        """Update last_accessed times for frequently used memories."""
        if not self._firestore_client:
            return 0
            
        try:
            collection_ref = self._firestore_client.collection(self.collection_name)
            
            # Update access times for high-importance memories
            query = collection_ref.where('importance_score', '>=', 0.7).limit(1000)
            
            updated_count = 0
            batch = self._firestore_client.batch()
            batch_size = 0
            
            current_time = datetime.fromtimestamp(time_now(), timezone.utc)
            
            for doc in query.stream():
                batch.update(doc.reference, {'last_accessed': current_time})
                batch_size += 1
                
                if batch_size >= 500:
                    batch.commit()
                    updated_count += batch_size
                    batch = self._firestore_client.batch()
                    batch_size = 0
            
            if batch_size > 0:
                batch.commit()
                updated_count += batch_size
                
            return updated_count
            
        except Exception as e:
            logger.error(f"Failed to update access times: {e}")
            return 0
    
    def search_firestore(self, keywords: List[str], limit: int = 10, 
                        memory_type: Optional[MemoryType] = None) -> List[EnhancedMemoryItem]:
        """
        Search Firestore directly for memories (beyond local cache).
        
        Args:
            keywords: Keywords to search for
            limit: Maximum results to return
            memory_type: Filter by memory type
            
        Returns:
            List of matching memory items
        """
        if not self._firestore_client:
            # Fall back to local search
            return self.search_by_keywords(keywords, limit)
            
        try:
            collection_ref = self._firestore_client.collection(self.collection_name)
            
            # Build query
            query = collection_ref.order_by('importance_score', direction=firestore.Query.DESCENDING)
            
            if memory_type:
                query = query.where('memory_type', '==', memory_type.value)
                
            # Note: Firestore doesn't support full-text search natively
            # We'll fetch more results and filter locally
            query = query.limit(limit * 3)
            
            results = []
            for doc in query.stream():
                try:
                    data = doc.to_dict()
                    item = self._dict_to_memory_item(data)
                    
                    # Check keyword match
                    item_keywords = set(item.keywords)
                    keyword_set = set(k.lower() for k in keywords)
                    
                    if keyword_set & item_keywords:
                        results.append(item)
                        if len(results) >= limit:
                            break
                            
                except Exception as e:
                    logger.warning(f"Failed to process search result: {e}")
                    
            return results
            
        except Exception as e:
            logger.error(f"Firestore search failed: {e}")
            return self.search_by_keywords(keywords, limit)  # Fallback to local
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics including Firestore metrics."""
        stats = self.get_memory_analytics()
        
        if self._firestore_client:
            try:
                collection_ref = self._firestore_client.collection(self.collection_name)
                
                # Count total documents
                # Note: This is expensive - in production, maintain a counter document
                total_docs = 0
                for _ in collection_ref.limit(1).stream():
                    total_docs = 1  # At least one exists
                    break
                
                stats.update({
                    "firestore_connected": True,
                    "local_cache_size": len(self._items),
                    "max_cache_size": self.max_local_cache,
                    "last_sync": self._last_sync,
                    "sync_on_write": self.sync_on_write
                })
                
            except Exception as e:
                logger.error(f"Failed to get Firestore stats: {e}")
                stats["firestore_error"] = str(e)
        else:
            stats["firestore_connected"] = False
            
        return stats
    
    def force_sync(self) -> Dict[str, int]:
        """Force sync all local memories to Firestore."""
        if not self._firestore_client:
            return {"error": "Firestore not available"}
            
        try:
            synced_count = 0
            failed_count = 0
            
            for item in self._items:
                try:
                    self._sync_to_firestore(item)
                    synced_count += 1
                except Exception:
                    failed_count += 1
                    
            self._last_sync = time_now()
            
            return {
                "synced_count": synced_count,
                "failed_count": failed_count,
                "total_items": len(self._items)
            }
            
        except Exception as e:
            logger.error(f"Force sync failed: {e}")
            return {"error": str(e)}


def create_firestore_memory_store(project_id: Optional[str] = None, 
                                 **kwargs) -> FirestoreMemoryStore:
    """
    Factory function to create FirestoreMemoryStore with error handling.
    
    Args:
        project_id: Google Cloud project ID
        **kwargs: Additional arguments for FirestoreMemoryStore
        
    Returns:
        FirestoreMemoryStore instance (may fallback to in-memory if Firestore unavailable)
    """
    try:
        return FirestoreMemoryStore(project_id=project_id, **kwargs)
    except Exception as e:
        logger.error(f"Failed to create FirestoreMemoryStore: {e}")
        logger.warning("Falling back to IntelligentMemoryStore")
        return IntelligentMemoryStore()
