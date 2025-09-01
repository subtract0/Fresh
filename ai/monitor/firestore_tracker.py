"""
Firestore Usage Tracker

Wrapper around Firestore operations to automatically track usage and costs.
Integrates with the cost monitoring system to provide accurate billing estimates.

Features:
- Transparent wrapper around existing Firestore operations
- Automatic cost tracking for reads, writes, deletes
- Batch operation support
- Collection and document level tracking
- Real-time cost estimation
"""
from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional, Union, Iterator
from datetime import datetime, timezone
from contextlib import contextmanager

from ai.monitor.cost_tracker import get_cost_tracker, ServiceType, OperationType

logger = logging.getLogger(__name__)


class FirestoreUsageTracker:
    """Tracks Firestore operations and costs."""
    
    def __init__(self):
        self.cost_tracker = get_cost_tracker()
        
    def track_read(self, count: int = 1, collection: str = "", metadata: Optional[Dict] = None):
        """Track document read operations."""
        self.cost_tracker.record_usage(
            service=ServiceType.FIRESTORE,
            operation=OperationType.READ,
            quantity=count,
            metadata={
                "collection": collection,
                **(metadata or {})
            }
        )
        logger.debug(f"📖 Tracked {count} Firestore reads from {collection}")
        
    def track_write(self, count: int = 1, collection: str = "", metadata: Optional[Dict] = None):
        """Track document write operations.""" 
        self.cost_tracker.record_usage(
            service=ServiceType.FIRESTORE,
            operation=OperationType.WRITE,
            quantity=count,
            metadata={
                "collection": collection,
                **(metadata or {})
            }
        )
        logger.debug(f"✍️ Tracked {count} Firestore writes to {collection}")
        
    def track_delete(self, count: int = 1, collection: str = "", metadata: Optional[Dict] = None):
        """Track document delete operations."""
        self.cost_tracker.record_usage(
            service=ServiceType.FIRESTORE,
            operation=OperationType.DELETE,
            quantity=count,
            metadata={
                "collection": collection,
                **(metadata or {})
            }
        )
        logger.debug(f"🗑️ Tracked {count} Firestore deletes from {collection}")


class TrackedFirestoreClient:
    """Firestore client wrapper with automatic usage tracking."""
    
    def __init__(self, client):
        """Initialize with existing Firestore client."""
        self._client = client
        self._tracker = FirestoreUsageTracker()
        
    def collection(self, collection_path: str) -> 'TrackedCollectionReference':
        """Get a tracked collection reference."""
        return TrackedCollectionReference(
            self._client.collection(collection_path),
            self._tracker,
            collection_path
        )
        
    def document(self, document_path: str) -> 'TrackedDocumentReference':
        """Get a tracked document reference."""
        collection_path = document_path.split('/')[0]
        return TrackedDocumentReference(
            self._client.document(document_path),
            self._tracker,
            collection_path
        )
        
    @contextmanager
    def batch(self):
        """Create a tracked batch write context."""
        batch = self._client.batch()
        tracked_batch = TrackedWriteBatch(batch, self._tracker)
        yield tracked_batch
        
    def __getattr__(self, name):
        """Delegate unknown attributes to the wrapped client."""
        return getattr(self._client, name)


class TrackedCollectionReference:
    """Collection reference wrapper with usage tracking."""
    
    def __init__(self, collection_ref, tracker: FirestoreUsageTracker, collection_path: str):
        self._ref = collection_ref
        self._tracker = tracker
        self._collection_path = collection_path
        
    def get(self, **kwargs) -> 'TrackedQuerySnapshot':
        """Get all documents with tracking."""
        snapshot = self._ref.get(**kwargs)
        # Track reads for all documents retrieved
        doc_count = len(list(snapshot))
        self._tracker.track_read(doc_count, self._collection_path)
        
        return TrackedQuerySnapshot(snapshot, self._tracker, self._collection_path)
        
    def stream(self, **kwargs) -> Iterator['TrackedDocumentSnapshot']:
        """Stream documents with tracking."""
        doc_count = 0
        for doc_snapshot in self._ref.stream(**kwargs):
            doc_count += 1
            yield TrackedDocumentSnapshot(doc_snapshot, self._tracker, self._collection_path)
            
        # Track total reads after streaming
        if doc_count > 0:
            self._tracker.track_read(doc_count, self._collection_path, {"operation": "stream"})
            
    def add(self, document_data: dict, **kwargs) -> 'TrackedDocumentReference':
        """Add document with tracking."""
        doc_ref = self._ref.add(document_data, **kwargs)
        self._tracker.track_write(1, self._collection_path, {"operation": "add"})
        
        return TrackedDocumentReference(doc_ref, self._tracker, self._collection_path)
        
    def document(self, document_id: str = None) -> 'TrackedDocumentReference':
        """Get tracked document reference."""
        doc_ref = self._ref.document(document_id)
        return TrackedDocumentReference(doc_ref, self._tracker, self._collection_path)
        
    def where(self, field_path: str, op_string: str, value: Any) -> 'TrackedQuery':
        """Create tracked query."""
        query = self._ref.where(field_path, op_string, value)
        return TrackedQuery(query, self._tracker, self._collection_path)
        
    def order_by(self, field_path: str, **kwargs) -> 'TrackedQuery':
        """Create tracked ordered query."""
        query = self._ref.order_by(field_path, **kwargs)
        return TrackedQuery(query, self._tracker, self._collection_path)
        
    def limit(self, count: int) -> 'TrackedQuery':
        """Create tracked limited query."""
        query = self._ref.limit(count)
        return TrackedQuery(query, self._tracker, self._collection_path)
        
    def __getattr__(self, name):
        """Delegate unknown attributes to the wrapped collection reference."""
        return getattr(self._ref, name)


class TrackedDocumentReference:
    """Document reference wrapper with usage tracking."""
    
    def __init__(self, doc_ref, tracker: FirestoreUsageTracker, collection_path: str):
        self._ref = doc_ref
        self._tracker = tracker
        self._collection_path = collection_path
        
    def get(self, **kwargs) -> 'TrackedDocumentSnapshot':
        """Get document with tracking."""
        doc_snapshot = self._ref.get(**kwargs)
        self._tracker.track_read(1, self._collection_path, {"document_id": self._ref.id})
        
        return TrackedDocumentSnapshot(doc_snapshot, self._tracker, self._collection_path)
        
    def set(self, document_data: dict, **kwargs):
        """Set document with tracking."""
        result = self._ref.set(document_data, **kwargs)
        self._tracker.track_write(1, self._collection_path, {
            "document_id": self._ref.id,
            "operation": "set"
        })
        return result
        
    def update(self, field_updates: dict, **kwargs):
        """Update document with tracking.""" 
        result = self._ref.update(field_updates, **kwargs)
        self._tracker.track_write(1, self._collection_path, {
            "document_id": self._ref.id,
            "operation": "update"
        })
        return result
        
    def delete(self, **kwargs):
        """Delete document with tracking."""
        result = self._ref.delete(**kwargs)
        self._tracker.track_delete(1, self._collection_path, {"document_id": self._ref.id})
        return result
        
    def collection(self, collection_id: str) -> TrackedCollectionReference:
        """Get subcollection with tracking."""
        subcoll_ref = self._ref.collection(collection_id)
        subcoll_path = f"{self._collection_path}/{collection_id}"
        return TrackedCollectionReference(subcoll_ref, self._tracker, subcoll_path)
        
    def __getattr__(self, name):
        """Delegate unknown attributes to the wrapped document reference.""" 
        return getattr(self._ref, name)


class TrackedQuery:
    """Query wrapper with usage tracking."""
    
    def __init__(self, query, tracker: FirestoreUsageTracker, collection_path: str):
        self._query = query
        self._tracker = tracker
        self._collection_path = collection_path
        
    def get(self, **kwargs) -> 'TrackedQuerySnapshot':
        """Execute query with tracking."""
        snapshot = self._query.get(**kwargs)
        doc_count = len(list(snapshot))
        self._tracker.track_read(doc_count, self._collection_path, {"operation": "query"})
        
        return TrackedQuerySnapshot(snapshot, self._tracker, self._collection_path)
        
    def stream(self, **kwargs) -> Iterator['TrackedDocumentSnapshot']:
        """Stream query results with tracking."""
        doc_count = 0
        for doc_snapshot in self._query.stream(**kwargs):
            doc_count += 1
            yield TrackedDocumentSnapshot(doc_snapshot, self._tracker, self._collection_path)
            
        if doc_count > 0:
            self._tracker.track_read(doc_count, self._collection_path, {"operation": "query_stream"})
            
    def where(self, field_path: str, op_string: str, value: Any) -> 'TrackedQuery':
        """Chain where clause."""
        query = self._query.where(field_path, op_string, value)
        return TrackedQuery(query, self._tracker, self._collection_path)
        
    def order_by(self, field_path: str, **kwargs) -> 'TrackedQuery':
        """Chain order by clause."""
        query = self._query.order_by(field_path, **kwargs)
        return TrackedQuery(query, self._tracker, self._collection_path)
        
    def limit(self, count: int) -> 'TrackedQuery':
        """Chain limit clause."""
        query = self._query.limit(count)
        return TrackedQuery(query, self._tracker, self._collection_path)
        
    def __getattr__(self, name):
        """Delegate unknown attributes to the wrapped query."""
        return getattr(self._query, name)


class TrackedQuerySnapshot:
    """Query snapshot wrapper with usage tracking."""
    
    def __init__(self, snapshot, tracker: FirestoreUsageTracker, collection_path: str):
        self._snapshot = snapshot
        self._tracker = tracker
        self._collection_path = collection_path
        
    def __iter__(self) -> Iterator['TrackedDocumentSnapshot']:
        """Iterate over documents."""
        for doc_snapshot in self._snapshot:
            yield TrackedDocumentSnapshot(doc_snapshot, self._tracker, self._collection_path)
            
    def __len__(self) -> int:
        """Get document count."""
        return len(self._snapshot)
        
    def __getattr__(self, name):
        """Delegate unknown attributes to the wrapped snapshot."""
        return getattr(self._snapshot, name)


class TrackedDocumentSnapshot:
    """Document snapshot wrapper with usage tracking."""
    
    def __init__(self, snapshot, tracker: FirestoreUsageTracker, collection_path: str):
        self._snapshot = snapshot
        self._tracker = tracker
        self._collection_path = collection_path
        
    def to_dict(self) -> dict:
        """Get document data."""
        return self._snapshot.to_dict()
        
    def get(self, field_path: str):
        """Get field value."""
        return self._snapshot.get(field_path)
        
    @property
    def reference(self) -> TrackedDocumentReference:
        """Get tracked document reference."""
        return TrackedDocumentReference(
            self._snapshot.reference, 
            self._tracker, 
            self._collection_path
        )
        
    def __getattr__(self, name):
        """Delegate unknown attributes to the wrapped snapshot."""
        return getattr(self._snapshot, name)


class TrackedWriteBatch:
    """Write batch wrapper with usage tracking."""
    
    def __init__(self, batch, tracker: FirestoreUsageTracker):
        self._batch = batch
        self._tracker = tracker
        self._operations = {
            "writes": 0,
            "deletes": 0,
            "collections": set()
        }
        
    def set(self, reference, document_data: dict, **kwargs):
        """Set document in batch."""
        result = self._batch.set(reference, document_data, **kwargs)
        self._operations["writes"] += 1
        self._operations["collections"].add(self._extract_collection_path(reference))
        return result
        
    def update(self, reference, field_updates: dict, **kwargs):
        """Update document in batch."""
        result = self._batch.update(reference, field_updates, **kwargs)
        self._operations["writes"] += 1
        self._operations["collections"].add(self._extract_collection_path(reference))
        return result
        
    def delete(self, reference, **kwargs):
        """Delete document in batch."""
        result = self._batch.delete(reference, **kwargs)
        self._operations["deletes"] += 1
        self._operations["collections"].add(self._extract_collection_path(reference))
        return result
        
    def commit(self, **kwargs):
        """Commit batch and track usage."""
        result = self._batch.commit(**kwargs)
        
        # Track all operations
        for collection in self._operations["collections"]:
            if self._operations["writes"] > 0:
                self._tracker.track_write(
                    self._operations["writes"], 
                    collection, 
                    {"operation": "batch_write"}
                )
            if self._operations["deletes"] > 0:
                self._tracker.track_delete(
                    self._operations["deletes"], 
                    collection, 
                    {"operation": "batch_delete"}
                )
                
        logger.info(f"📦 Batch committed: {self._operations['writes']} writes, {self._operations['deletes']} deletes")
        return result
        
    def _extract_collection_path(self, reference) -> str:
        """Extract collection path from document reference."""
        try:
            if hasattr(reference, 'path'):
                return reference.path.split('/')[0]
            elif hasattr(reference, '_path'):
                return reference._path[0]
            else:
                return "unknown"
        except Exception:
            return "unknown"
            
    def __getattr__(self, name):
        """Delegate unknown attributes to the wrapped batch."""
        return getattr(self._batch, name)


def create_tracked_firestore_client(client) -> TrackedFirestoreClient:
    """Create a tracked Firestore client from an existing client."""
    return TrackedFirestoreClient(client)


# Convenience function for easy integration
def wrap_firestore_client(client):
    """
    Wrap an existing Firestore client with cost tracking.
    
    Usage:
        from google.cloud import firestore
        from ai.monitor.firestore_tracker import wrap_firestore_client
        
        # Original client
        db = firestore.Client()
        
        # Wrapped client with cost tracking
        db = wrap_firestore_client(db)
        
        # Use normally - all operations are automatically tracked
        doc_ref = db.collection('users').document('user123')
        doc_ref.set({'name': 'John', 'email': 'john@example.com'})
    """
    return create_tracked_firestore_client(client)
