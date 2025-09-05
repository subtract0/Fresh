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
    args2 = SimpleNamespace(path=str(p), json=True, limit=200, allow=None, deny=None)
    fresh.cmd_scan(args2)
    out = capsys.readouterr().out
    data = json.loads(out)

    assert data["total"] >= 1
    # Ensure tasks include the python file
    tasks = data["tasks"]
    path_keys = ("file_path", "path", "file", "filename")

    def get_path(item):
        for k in path_keys:
            if k in item and item[k]:
                return item[k]
        return ""

    first_paths = [get_path(item) for item in tasks]
    assert any(pth.endswith("mod1.py") or "mod1.py" in pth for pth in first_paths)

    # Check that at least one of the expected comments is detected in the tasks for mod1.py
    comment_keys = ("description", "comment", "text", "message")

    def get_comment(item):
        for k in comment_keys:
            if k in item and item[k]:
                return item[k]
        return ""

    comments = [get_comment(item) for item in tasks if get_path(item).endswith("mod1.py") or "mod1.py" in get_path(item)]
    assert any(
        ("broken edge case" in comment) or ("refactor" in comment)
        for comment in comments
    )

    # Fix for the broken edge case: Ensure the specific comment is detected
    assert any("FIXME: broken edge case" in comment for comment in comments)