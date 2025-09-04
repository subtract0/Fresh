"""
Enhanced Firestore Memory Store

Production-ready Firestore backend with intelligent memory support, backup/restore
capabilities, and enhanced analytics. Extends the intelligent memory system to work
with persistent cloud storage.

Features:
- Full intelligent memory support (classification, keywords, importance)  
- Backup and restore operations
- Production-grade error handling and retry logic
- Memory analytics and metrics
- Batch operations for performance
- Data migration utilities
"""
from __future__ import annotations
import os
import json
import time
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import asdict, fields

from ai.memory.store import MemoryStore, MemoryItem
from ai.memory.intelligent_store import (
    IntelligentMemoryStore, 
    EnhancedMemoryItem,
    MemoryType
)
from ai.monitor.firestore_tracker import wrap_firestore_client


class EnhancedFirestoreMemoryStore(IntelligentMemoryStore):
    """
    Enhanced Firestore memory store with intelligent features and production capabilities.
    
    Combines intelligent memory processing with persistent Firestore storage,
    including backup/restore, analytics, and production-grade reliability.
    """
    
    def __init__(self, collection_name: str = "intelligent_memory"):
        """
        Initialize enhanced Firestore store.
        
        Args:
            collection_name: Firestore collection name for memory storage
        """
        self.collection_name = collection_name
        self._setup_firestore()
        
        # Initialize intelligent memory capabilities
        super().__init__()
        
        # Load existing memories from Firestore
        self._load_from_firestore()
        
    def _setup_firestore(self) -> None:
        """Setup Firestore client with proper error handling."""
        try:
            from google.cloud import firestore
            from google.api_core import exceptions as gcp_exceptions
        except Exception as e:
            raise RuntimeError("google-cloud-firestore not installed") from e
        
        # Store the exceptions module for retry logic
        self._gcp_exceptions = gcp_exceptions
        
        project_id = os.getenv("FIREBASE_PROJECT_ID")
        client_email = os.getenv("FIREBASE_CLIENT_EMAIL") 
        private_key = os.getenv("FIREBASE_PRIVATE_KEY")
        
        if not (project_id and client_email and private_key):
            raise RuntimeError("FIREBASE_* env vars are required for Enhanced Firestore")
        
        raw_client = firestore.Client(project=project_id)
        self._db = wrap_firestore_client(raw_client)  # Add cost tracking
        self._collection = self._db.collection(self.collection_name)
        
        print(f"🔥 Enhanced Firestore: Connected to {project_id}/{self.collection_name}")
        
    def _retry_operation(self, operation, max_retries: int = 3, delay: float = 1.0):
        """Retry Firestore operations with exponential backoff."""
        for attempt in range(max_retries):
            try:
                return operation()
            except (self._gcp_exceptions.ServiceUnavailable, 
                    self._gcp_exceptions.DeadlineExceeded,
                    self._gcp_exceptions.InternalServerError) as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(delay * (2 ** attempt))
            except Exception as e:
                # Non-retryable errors, fail immediately  
                raise e
                
    def _enhanced_item_to_dict(self, item: EnhancedMemoryItem) -> Dict[str, Any]:
        """Convert enhanced memory item to Firestore-compatible dict."""
        data = {
            "id": item.id,
            "content": item.content,
            "tags": item.tags,
            "created_at": item.created_at.isoformat(),
            "memory_type": item.memory_type.value,
            "keywords": item.keywords,
            "related_ids": item.related_ids,
            "importance_score": item.importance_score,
            "summary": item.summary,
            # Metadata for production tracking
            "schema_version": "1.0",
            "store_type": "enhanced_firestore"
        }
        return data
        
    def _dict_to_enhanced_item(self, data: Dict[str, Any]) -> EnhancedMemoryItem:
        """Convert Firestore dict back to enhanced memory item."""
        # Handle legacy items without enhanced fields
        memory_type = MemoryType(data.get("memory_type", "context"))
        keywords = data.get("keywords", [])
        related_ids = data.get("related_ids", [])
        importance_score = data.get("importance_score", 0.5)
        summary = data.get("summary")
        
        # Parse created_at
        created_at_str = data.get("created_at")
        if isinstance(created_at_str, str):
            created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
        else:
            created_at = datetime.now(timezone.utc)
            
        return EnhancedMemoryItem(
            id=data["id"],
            content=data["content"], 
            tags=data.get("tags", []),
            created_at=created_at,
            memory_type=memory_type,
            keywords=keywords,
            related_ids=related_ids,
            importance_score=importance_score,
            summary=summary
        )
        
    def _load_from_firestore(self) -> None:
        """Load existing memories from Firestore into local cache."""
        try:
            def load_operation():
                docs = list(self._collection.stream())
                return docs
                
            docs = self._retry_operation(load_operation)
            
            for doc in docs:
                try:
                    data = doc.to_dict()
                    if data:
                        enhanced_item = self._dict_to_enhanced_item(data)
                        self._items.append(enhanced_item)
                        self._update_indexes(enhanced_item)
                except Exception as e:
                    print(f"⚠️  Failed to load memory {doc.id}: {e}")
                    
            print(f"📥 Loaded {len(self._items)} memories from Firestore")
            
        except Exception as e:
            print(f"⚠️  Failed to load from Firestore: {e}")
            print("   Continuing with empty memory store...")
        
    def write(self, *, content: str, tags: Optional[List[str]] = None) -> MemoryItem:
        """Write enhanced memory item with Firestore persistence."""
        # First create the intelligent memory item locally
        local_item = super().write(content=content, tags=tags)
        
        # Then persist to Firestore
        try:
            def write_operation():
                doc_data = self._enhanced_item_to_dict(local_item)
                doc_ref = self._collection.document(local_item.id)
                doc_ref.set(doc_data)
                return doc_ref
                
            self._retry_operation(write_operation)
            
        except Exception as e:
            print(f"⚠️  Failed to persist memory {local_item.id} to Firestore: {e}")
            # Continue with local storage even if Firestore write fails
            
        return local_item
        
    def backup_memories(self, backup_path: str) -> Dict[str, Any]:
        """
        Backup all memories to a JSON file.
        
        Args:
            backup_path: Path to save backup file
            
        Returns:
            Backup metadata including count and timestamp
        """
        try:
            backup_data = {
                "metadata": {
                    "backup_timestamp": datetime.now(timezone.utc).isoformat(),
                    "total_memories": len(self._items),
                    "collection_name": self.collection_name,
                    "schema_version": "1.0"
                },
                "memories": []
            }
            
            # Export all memories
            for item in self._items:
                backup_data["memories"].append(self._enhanced_item_to_dict(item))
                
            # Write to file
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
                
            print(f"💾 Backed up {len(self._items)} memories to {backup_path}")
            return backup_data["metadata"]
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            raise e
            
    def restore_memories(self, backup_path: str, clear_existing: bool = False) -> Dict[str, Any]:
        """
        Restore memories from a backup file.
        
        Args:
            backup_path: Path to backup file
            clear_existing: Whether to clear existing memories first
            
        Returns:
            Restore metadata including counts and status
        """
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
                
            if clear_existing:
                self._clear_all_memories()
                
            restored_count = 0
            failed_count = 0
            
            for memory_data in backup_data.get("memories", []):
                try:
                    # Restore to local storage
                    enhanced_item = self._dict_to_enhanced_item(memory_data)
                    self._items.append(enhanced_item)
                    self._update_indexes(enhanced_item)
                    
                    # Restore to Firestore
                    def restore_operation():
                        doc_ref = self._collection.document(enhanced_item.id)
                        doc_ref.set(memory_data)
                        
                    self._retry_operation(restore_operation)
                    restored_count += 1
                    
                except Exception as e:
                    print(f"⚠️  Failed to restore memory: {e}")
                    failed_count += 1
                    
            restore_metadata = {
                "restore_timestamp": datetime.now(timezone.utc).isoformat(),
                "backup_file": backup_path,
                "restored_count": restored_count,
                "failed_count": failed_count,
                "total_memories": len(self._items)
            }
            
            print(f"📥 Restored {restored_count} memories (failed: {failed_count})")
            return restore_metadata
            
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            raise e
            
    def _clear_all_memories(self) -> None:
        """Clear all memories from both local storage and Firestore."""
        # Clear local storage
        self._items.clear()
        self._keyword_index.clear()
        self._type_index.clear()
        
        # Clear Firestore (batch delete)
        try:
            def delete_operation():
                docs = list(self._collection.stream())
                batch = self._db.batch()
                for doc in docs:
                    batch.delete(doc.reference)
                batch.commit()
                
            self._retry_operation(delete_operation)
            
        except Exception as e:
            print(f"⚠️  Failed to clear Firestore collection: {e}")
            
    def get_production_analytics(self) -> Dict[str, Any]:
        """Get enhanced analytics including Firestore metrics."""
        base_analytics = self.get_memory_analytics()
        
        # Add production-specific metrics
        try:
            def get_firestore_stats():
                docs = list(self._collection.stream())
                return len(docs)
                
            firestore_count = self._retry_operation(get_firestore_stats)
            
            production_metrics = {
                "firestore_memory_count": firestore_count,
                "local_memory_count": len(self._items),
                "sync_status": "synced" if firestore_count == len(self._items) else "out_of_sync",
                "collection_name": self.collection_name,
                "last_check": datetime.now(timezone.utc).isoformat()
            }
            
            base_analytics["production_metrics"] = production_metrics
            
        except Exception as e:
            print(f"⚠️  Failed to get Firestore analytics: {e}")
            base_analytics["production_metrics"] = {"error": str(e)}
            
        return base_analytics
        
    def sync_with_firestore(self) -> Dict[str, int]:
        """
        Synchronize local memory with Firestore.
        
        Returns:
            Sync statistics
        """
        try:
            def get_firestore_memories():
                docs = list(self._collection.stream())
                return {doc.id: doc.to_dict() for doc in docs}
                
            firestore_memories = self._retry_operation(get_firestore_memories)
            local_memory_ids = {item.id for item in self._items}
            firestore_ids = set(firestore_memories.keys())
            
            # Find differences
            missing_in_local = firestore_ids - local_memory_ids
            missing_in_firestore = local_memory_ids - firestore_ids
            
            sync_stats = {
                "local_count": len(self._items),
                "firestore_count": len(firestore_memories),
                "missing_in_local": len(missing_in_local),
                "missing_in_firestore": len(missing_in_firestore),
                "synced": 0,
                "failed": 0
            }
            
            # Sync missing memories from Firestore to local
            for memory_id in missing_in_local:
                try:
                    data = firestore_memories[memory_id]
                    enhanced_item = self._dict_to_enhanced_item(data)
                    self._items.append(enhanced_item)
                    self._update_indexes(enhanced_item)
                    sync_stats["synced"] += 1
                except Exception as e:
                    print(f"⚠️  Failed to sync memory {memory_id} from Firestore: {e}")
                    sync_stats["failed"] += 1
                    
            # Sync missing memories from local to Firestore
            for item in self._items:
                if item.id in missing_in_firestore:
                    try:
                        def sync_to_firestore():
                            doc_data = self._enhanced_item_to_dict(item)
                            doc_ref = self._collection.document(item.id)
                            doc_ref.set(doc_data)
                            
                        self._retry_operation(sync_to_firestore)
                        sync_stats["synced"] += 1
                    except Exception as e:
                        print(f"⚠️  Failed to sync memory {item.id} to Firestore: {e}")
                        sync_stats["failed"] += 1
                        
            print(f"🔄 Sync complete: {sync_stats}")
            return sync_stats
            
        except Exception as e:
            print(f"❌ Sync failed: {e}")
            return {"error": str(e)}
            
    def optimize_firestore_memory(self, max_items: int = 1000) -> Dict[str, int]:
        """
        Optimize memory by removing low-importance items from both local and Firestore.
        
        Args:
            max_items: Maximum number of items to keep
            
        Returns:
            Optimization statistics
        """
        if len(self._items) <= max_items:
            return {"removed": 0, "kept": len(self._items)}
            
        # Sort by importance and age (keep important and recent)
        self._items.sort(key=lambda i: (i.importance_score, i.created_at.timestamp()), reverse=True)
        
        # Items to remove
        items_to_remove = self._items[max_items:]
        removed_ids = [item.id for item in items_to_remove]
        
        # Keep only the top items locally
        self._items = self._items[:max_items]
        
        # Rebuild indexes
        self._keyword_index.clear()
        self._type_index.clear()
        for item in self._items:
            self._update_indexes(item)
            
        # Remove from Firestore
        removed_count = 0
        failed_count = 0
        
        for item_id in removed_ids:
            try:
                def delete_operation():
                    doc_ref = self._collection.document(item_id)
                    doc_ref.delete()
                    
                self._retry_operation(delete_operation)
                removed_count += 1
            except Exception as e:
                print(f"⚠️  Failed to delete memory {item_id} from Firestore: {e}")
                failed_count += 1
                
        optimization_stats = {
            "removed": removed_count,
            "failed": failed_count,
            "kept": len(self._items),
            "total_processed": len(removed_ids)
        }
        
        print(f"🧹 Firestore optimization: {optimization_stats}")
        return optimization_stats
