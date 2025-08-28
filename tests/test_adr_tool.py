import os
from pathlib import Path
import re

import pytest


def test_create_adr_creates_numbered_file(tmp_path, monkeypatch):
    # Arrange: isolate ADR directory via env var
    monkeypatch.setenv("ADR_DIR", str(tmp_path))

    # Import deferred so it picks up ADR_DIR
    from ai.tools.adr_logger import CreateADR  # type: ignore

    tool = CreateADR(title="Adopt Agency Swarm", status="Proposed")

    # Act
    adr_path_str = tool.run()
    adr_path = Path(adr_path_str)

    # Assert
    assert adr_path.exists()
    text = adr_path.read_text(encoding="utf-8")
    assert re.search(r"^#\s*ADR-0*1:\s*Adopt Agency Swarm", text, re.M)
    assert "Status: Proposed" in text


def test_create_adr_increments_id(tmp_path, monkeypatch):
    monkeypatch.setenv("ADR_DIR", str(tmp_path))
    from ai.tools.adr_logger import CreateADR  # re-import after env set

    first = CreateADR(title="First", status="Proposed").run()
    second = CreateADR(title="Second", status="Proposed").run()

    assert first != second
    # Ensure second file has -002 in name
    assert Path(second).name.startswith("ADR-002")

