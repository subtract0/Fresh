from __future__ import annotations
import pytest

from ai.memory.store import InMemoryMemoryStore, set_memory_store
from ai.tools.memory_tools import WriteMemory, ReadMemoryContext


def setup_function(_):
    # fresh in-memory store per test
    set_memory_store(InMemoryMemoryStore())


def test_write_and_read_tools_roundtrip():
    w = WriteMemory(content="noted item", tags=["note"])  # type: ignore
    mem_id = w.run()
    assert isinstance(mem_id, str)

    r = ReadMemoryContext(limit=5, tags=["note"])  # type: ignore
    context = r.run()
    assert "noted item" in context

