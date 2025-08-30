from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional
import itertools

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


@dataclass(frozen=True)
class MemoryItem:
    id: str
    content: str
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


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
