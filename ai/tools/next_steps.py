from __future__ import annotations
from typing import List, Optional

try:
    from agency_swarm.tools import BaseTool
    from pydantic import Field
except Exception:  # pragma: no cover - allow running tests without agency_swarm
    class BaseTool:  # type: ignore
        def run(self):
            raise NotImplementedError

    def Field(*args, **kwargs):  # type: ignore
        return None

from ai.memory.store import get_store


class GenerateNextSteps(BaseTool):
    """Suggest the next 2–3 smallest steps based on recent memory.

    Heuristics:
    - If recent items include a 'bug' tag => prioritize failing test reproduction and minimal fix.
    - Else if include 'feature' => write failing tests, implement minimal, then review.
    - Fallback => read context, identify missing tests, propose one crisp step.
    """

    limit: int = Field(default=5, description="How many recent items to consider")
    tags: Optional[List[str]] = Field(default=None, description="Optional filter of recent items")

    def run(self) -> str:  # type: ignore[override]
        items = get_store().query(limit=self.limit, tags=self.tags)
        has_bug = any("bug" in (t.lower() for t in it.tags) or it.content.lower().startswith("bug:") for it in items)
        has_feature = any("feature" in (t.lower() for t in it.tags) or it.content.lower().startswith("feat:") for it in items)

        steps: List[str] = []
        if has_bug:
            steps = [
                "Add/extend failing test to reproduce the bug",
                "Minimal fix to make tests green",
                "Refactor if needed; write a short memory of the root cause",
            ]
        elif has_feature:
            steps = [
                "Write failing tests that capture the desired behavior",
                "Implement minimal change to pass the tests",
                "Request/perform review and tag ADR reference if architecture changes",
            ]
        else:
            steps = [
                "Read recent context (top-k) and identify missing tests",
                "Write one failing test for the most critical gap",
                "Implement minimal fix and verify",
            ]
        return "\n".join(f"- {s}" for s in steps) + "\n"
