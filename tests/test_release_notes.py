from __future__ import annotations
from ai.memory.store import InMemoryMemoryStore, set_memory_store
from ai.tools.release_notes import GenerateReleaseNotes


def setup_function(_):
    set_memory_store(InMemoryMemoryStore())


def test_generate_release_notes_basic():
    store = InMemoryMemoryStore()
    set_memory_store(store)
    store.write(content="feat: add memory store", tags=["feature"])  # newest last written later
    store.write(content="fix: stabilize tests", tags=["bug"])  # more recent

    tool = GenerateReleaseNotes(limit=5)  # type: ignore
    md = tool.run()

    assert "Release Notes" in md
    # Recent-first order implies 'fix: stabilize tests' appears before 'feat: add memory store'
    assert md.find("fix: stabilize tests") < md.find("feat: add memory store")


def test_generate_release_notes_tag_filter():
    store = InMemoryMemoryStore()
    set_memory_store(store)
    store.write(content="feat: A", tags=["feature"])  # should appear
    store.write(content="bug: B", tags=["bug"])      # should be filtered out

    tool = GenerateReleaseNotes(limit=10, tags=["feature"])  # type: ignore
    md = tool.run()
    assert "feat: A" in md
    assert "bug: B" not in md
