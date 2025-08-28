from __future__ import annotations
from pathlib import Path
from ai.loop.devcycle import run_devcycle_slugify_sandbox


def test_devcycle_slugify(tmp_path):
    result = run_devcycle_slugify_sandbox(tmp_path)
    assert result["iterations"] == 2
    assert result["first_fail"] is True
    assert result["final_pass"] is True
    # basic sanity on output
    assert "---" in result["output"]

