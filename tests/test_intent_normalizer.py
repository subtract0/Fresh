from __future__ import annotations
from ai.tools.intent import IntentNormalizer, normalize_tag


def test_normalize_tag_variants():
    assert normalize_tag("feat") == "feature"
    assert normalize_tag("Feature") == "feature"
    assert normalize_tag(":bug") == "bug"
    assert normalize_tag("cleanup") == "refactor"
    assert normalize_tag("decision") == "adr"


def test_intent_normalizer_deduplicates_and_orders():
    out = IntentNormalizer(tags=["feat", "feature", "docs", "DOCS"]).run()  # type: ignore
    assert out == ["feature", "docs"]
