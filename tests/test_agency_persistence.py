from __future__ import annotations
import os
import pytest

# Only run if agency_swarm and a real OpenAI key are present
pytestmark = pytest.mark.skipif(
    os.getenv("OPENAI_API_KEY") in (None, "", "dummy"),
    reason="Requires real OPENAI_API_KEY for agency_swarm",
)


def test_context_function_available():
    # We avoid constructing the live Agency; just check the helper is importable
    from ai.agency import build_agency  # noqa: F401
    from ai.memory.store import InMemoryMemoryStore, set_memory_store
    from ai.memory.store import render_context

    set_memory_store(InMemoryMemoryStore())
    # After writing some events, render_context should include them
    from ai.memory.store import get_store

    s = get_store()
    s.write(content="hello world", tags=["greeting"])  # type: ignore[attr-defined]
    ctx = render_context(limit=3, tags=["greeting"])  # type: ignore[attr-defined]
    assert "hello world" in ctx

