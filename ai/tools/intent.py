from __future__ import annotations
from typing import List

try:
    from agency_swarm.tools import BaseTool
    from pydantic import Field
except Exception:  # pragma: no cover
    class BaseTool:  # type: ignore
        def run(self):
            raise NotImplementedError

    def Field(*args, **kwargs):  # type: ignore
        return None

_CANONICAL = {
    "feature": {"feature", "feat", "enhancement", "+feature"},
    "bug": {"bug", "fix", "hotfix", "defect", "bugfix"},
    "docs": {"docs", "documentation", "doc"},
    "refactor": {"refactor", "cleanup", "tidy"},
    "adr": {"adr", "decision"},
}


def normalize_tag(tag: str) -> str:
    t = tag.strip().lower().lstrip("+:")
    for canon, variants in _CANONICAL.items():
        if t in variants or t.startswith(canon):
            return canon
    return t  # pass through unknowns


class IntentNormalizer(BaseTool):
    """Normalize intent tags to canonical set: feature, bug, docs, refactor, adr."""

    tags: List[str] = Field(default_factory=list, description="Tags to normalize")

    def run(self) -> List[str]:  # type: ignore[override]
        out = []
        for t in self.tags:
            nt = normalize_tag(t)
            if nt not in out:
                out.append(nt)
        return out
