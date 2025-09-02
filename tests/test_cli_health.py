import json
from types import SimpleNamespace

from ai.cli import fresh


def test_health_outputs_ok_and_version(monkeypatch, capsys):
    # Ensure deterministic commit display during test by stubbing git call if needed
    def fake_git_short_sha(default: str = "unknown") -> str:
        return "deadbeefcafe"

    monkeypatch.setattr(fresh, "_git_short_sha", fake_git_short_sha)

    # Create dummy args namespace and invoke
    args = SimpleNamespace()
    rc = fresh.cmd_health(args)

    assert rc == 0
    captured = capsys.readouterr().out
    data = json.loads(captured)

    assert data["ok"] is True
    # Version should be a non-empty string
    assert isinstance(data["version"], str)
    assert len(data["version"]) > 0
    # Commit should be our stub value
    assert data["commit"] == "deadbeefcafe"

