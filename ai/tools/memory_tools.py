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


class WriteMemory(BaseTool):
    """Write a memory event to the shared store and return its id."""

    content: str = Field(..., description="Content to remember")
    tags: List[str] = Field(default_factory=list, description="Optional tags for filtering")

    def run(self) -> str:  # type: ignore[override]
        item = get_store().write(content=self.content, tags=self.tags)
        return item.id


class ReadMemoryContext(BaseTool):
    """Read recent memory items and render a compact prompt context string."""

    limit: int = Field(default=5, description="Max number of recent items to include")
    tags: Optional[List[str]] = Field(default=None, description="Optional tags filter")

    def run(self) -> str:  # type: ignore[override]
        from ai.memory.store import render_context
        return render_context(limit=self.limit, tags=self.tags)
