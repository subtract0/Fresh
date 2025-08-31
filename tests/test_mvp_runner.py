from __future__ import annotations
from ai.runner.mvp import run_mvp


def test_run_mvp_returns_summary_dict():
    out = run_mvp(goal="Test MVP flow", tags=["feature"], dry_run=True)
    assert isinstance(out, dict)
    assert out["goal"] == "Test MVP flow"
    assert isinstance(out["next_steps"], list) and len(out["next_steps"]) >= 2
    assert "Release Notes" in out["release_notes"]
    assert "Definition of Done" in out["dod_summary"]
