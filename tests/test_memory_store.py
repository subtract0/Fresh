from __future__ import annotations
import time
from typing import List
import pytest


# We will rely on the in-memory store by default
from ai.memory.store import InMemoryMemoryStore, MemoryItem


def test_inmemory_store_write_and_query_ordering(mock_clock, fast_forward):
    store = InMemoryMemoryStore()
    ids: List[str] = []
    ids.append(store.write(content="first", tags=["init"]).id)
    fast_forward(0.01)
    ids.append(store.write(content="second", tags=["work"]).id)
    fast_forward(0.01)
    ids.append(store.write(content="third", tags=["work", "init"]).id)

    # Default query: newest first
    items = store.query(limit=2)
    assert [it.content for it in items] == ["third", "second"]

    # Filter by tag
    work = store.query(limit=10, tags=["work"])
    assert [it.content for it in work] == ["third", "second"]


def test_inmemory_store_returns_stable_ids():
    store = InMemoryMemoryStore()
    a = store.write(content="alpha").id
    b = store.write(content="beta").id
    assert a != b

