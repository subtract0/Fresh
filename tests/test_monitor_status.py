from __future__ import annotations
from ai.monitor.status import get_status


def test_get_status_shape():
    out = get_status(limit=5)
    assert set(out.keys()) == {"agents", "flows", "memory_context", "next_steps", "release_notes"}
    assert isinstance(out["agents"], list) and len(out["agents"]) >= 4
    assert isinstance(out["flows"], list) and all(len(p)==2 for p in out["flows"])
