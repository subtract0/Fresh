from __future__ import annotations
from ai.memory.store import InMemoryMemoryStore, set_memory_store
from ai.tools.next_steps import GenerateNextSteps


def setup_function(_):
    set_memory_store(InMemoryMemoryStore())


def test_next_steps_for_bug_focuses_on_tests_and_fix():
    store = InMemoryMemoryStore()
    set_memory_store(store)
    store.write(content="bug: intermittent failure in tests", tags=["bug"])  # most recent
    tool = GenerateNextSteps(limit=5)  # type: ignore
    out = tool.run()
    assert "Add/extend failing test" in out
    assert "Minimal fix" in out


def test_next_steps_for_feature_focuses_on_tests_then_impl():
    store = InMemoryMemoryStore()
    set_memory_store(store)
    store.write(content="feat: add search filters", tags=["feature"])  # most recent
    tool = GenerateNextSteps(limit=5)  # type: ignore
    out = tool.run()
    assert "Write failing tests" in out
    assert "Implement minimal" in out
