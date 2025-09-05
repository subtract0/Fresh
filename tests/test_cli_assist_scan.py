from pathlib import Path
import json
from types import SimpleNamespace

from ai.cli import fresh


def test_assist_scan_json(tmp_path, monkeypatch, capsys):
    # Create a tiny repo fixture
    p = tmp_path / "pkg"
    p.mkdir()
    f1 = p / "mod1.py"
    f1.write_text("""
# TODO: refactor
# FIXME: broken edge case  # Test data for scanner
"""
    )
    f2 = p / "readme.md"
    f2.write_text("ok\n")

    args = SimpleNamespace(path=str(tmp_path), json=True, limit=100, allow=None, deny=None)
    rc = fresh.main if False else None  # silence linter; we're calling internal cmd

    # call the internal function wired via parser in the CLI module
    # For simplicity, directly call the nested function by reconstructing it here is complex;
    # Instead, invoke the CLI through argparse would be overkill in-unit.
    # We'll import scan_repository directly to emulate the same path and compare counts.
    # To keep scope tight, call the internal helper by constructing a minimal Namespace and using cmd_scan.
    args2 = SimpleNamespace(path=str(tmp_path), json=True, limit=200)
    fresh.cmd_scan(args2)
    out = capsys.readouterr().out
    data = json.loads(out)

    assert data["total"] >= 1
    # Ensure tasks include the python file
    first_paths = [item["file_path"] for item in data["tasks"]]
    assert any("mod1.py" in p for p in first_paths)

