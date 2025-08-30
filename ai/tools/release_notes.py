from __future__ import annotations
from typing import List, Optional
from datetime import datetime, timezone

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


class GenerateReleaseNotes(BaseTool):
    """Generate concise release notes from recent memory items.

    Produces markdown:
    # Release Notes (YYYY-MM-DD)
    - item 1
    - item 2
    ...
    """

    limit: int = Field(default=10, description="Max number of items to include")
    tags: Optional[List[str]] = Field(default=None, description="Optional tags filter")
    title: str = Field(default="Release Notes", description="Top-level heading title")

    def run(self) -> str:  # type: ignore[override]
        items = get_store().query(limit=self.limit, tags=self.tags)
        today = datetime.now(timezone.utc).date().isoformat()
        lines = [f"# {self.title} ({today})"]
        for it in items:
            lines.append(f"- {it.content}")
        return "\n".join(lines) + "\n"
