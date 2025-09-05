"""
@file store.py
@description Core memory store interfaces and base implementation for Fresh AI persistent memory system.

@connections
- imports: dataclasses for MemoryItem, typing for interfaces, ai.utils.clock for timestamps
- exports: MemoryStore abstract class, InMemoryMemoryStore implementation, MemoryItem data class
- implements: Abstract MemoryStore interface with write/query operations

@usage
# Get the current memory store (auto-creates InMemoryMemoryStore if none set)
store = get_store()

# Write memory with tags
memory = store.write(content="Goal: implement user auth", tags=["goal", "auth"])

# Query memories by tags and limit
recent_auth = store.query(tags=["auth"], limit=10)

@notes
- Global store pointer allows tools to access memory without explicit injection
- InMemoryMemoryStore is ephemeral (lost on restart) - use FirestoreMemoryStore for persistence
- MemoryItem uses timezone-aware timestamps for consistency across deployments
- Query results are ordered newest first for better context relevance

@see
- intelligent_store.py - Enhanced memory with auto-classification
- firestore_store.py - Persistent cross-session memory
- docs/MEMORY_SYSTEM.md#memory-stores - Architecture overview

@since v0.1.0
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional
import itertools

from ai.utils.clock import now as time_now

# Global store pointer for tools/integration
_current_store: "MemoryStore | None" = None


def set_memory_store(store: "MemoryStore") -> None:
    global _current_store
    _current_store = store


def get_store() -> "MemoryStore":
    if _current_store is None:
        # default to in-memory if not set
        set_memory_store(InMemoryMemoryStore())
    assert _current_store is not None
    return _current_store


def render_context(limit: int = 5, tags: Optional[List[str]] = None) -> str:
    items = get_store().query(limit=limit, tags=tags)
    lines = [f"- [{i.created_at.isoformat()}] {i.content}" for i in items]
    return "\n".join(lines)


@dataclass(frozen=False)
class MemoryItem:
    id: str
    content: str
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.fromtimestamp(time_now(), timezone.utc))


class MemoryStore:
    def write(self, *, content: str, tags: Optional[List[str]] = None) -> MemoryItem:  # pragma: no cover - interface
        raise NotImplementedError

    def query(self, *, limit: int = 5, tags: Optional[List[str]] = None) -> List[MemoryItem]:  # pragma: no cover - interface
        raise NotImplementedError


class InMemoryMemoryStore(MemoryStore):
    _id_counter = itertools.count(1)

    def __init__(self) -> None:
        self._items: List[MemoryItem] = []

    def write(self, *, content: str, tags: Optional[List[str]] = None) -> MemoryItem:
        mid = f"mem-{next(self._id_counter)}"
        item = MemoryItem(id=mid, content=content, tags=list(tags or []))
        self._items.append(item)
        return item

    def query(self, *, limit: int = 5, tags: Optional[List[str]] = None) -> List[MemoryItem]:
        items = self._items
        if tags:
            tagset = set(tags)
            items = [i for i in items if tagset.intersection(i.tags)]
        # newest first
        items = sorted(items, key=lambda i: i.created_at, reverse=True)
        return items[: max(0, limit)]
