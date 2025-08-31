from __future__ import annotations
from unittest.mock import patch
from ai.runner.mvp import run_mvp


@patch('subprocess.check_output')
def test_run_mvp_returns_summary_dict(mock_subprocess):
    # Mock subprocess calls to prevent recursive pytest
    mock_subprocess.return_value = b"All tests passed\n"
    out = run_mvp(goal="Test MVP flow", tags=["feature"], dry_run=True)
    assert isinstance(out, dict)
    assert out["goal"] == "Test MVP flow"
    assert isinstance(out["next_steps"], list) and len(out["next_steps"]) >= 2
    assert "Release Notes" in out["release_notes"]
    assert "Definition of Done" in out["dod_summary"]
