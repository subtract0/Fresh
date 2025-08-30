from __future__ import annotations
from ai.tools.dod_checker import extract_adr_refs


def test_extract_adr_refs_finds_unique_refs():
    text = "fix: something (refs ADR-001) and docs (ADR-010); revisit ADR-001"
    refs = extract_adr_refs(text)
    assert refs == ["ADR-001", "ADR-010"]
