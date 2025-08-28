from __future__ import annotations
from pathlib import Path
import os
import re
from datetime import date
from typing import Optional

try:
    from agency_swarm.tools import BaseTool
    from pydantic import Field
except Exception:  # pragma: no cover - imported only in runtime contexts
    class BaseTool:  # minimal shim for type checking if package missing
        def run(self):
            raise NotImplementedError
    def Field(*args, **kwargs):  # type: ignore
        return None


class CreateADR(BaseTool):
    """Create a new ADR under the ADR_DIR (or .cursor/rules by default).

    Fields (Pydantic model fields when running under Agency Swarm):
    - title: Decision title
    - status: One of Proposed|Accepted|Superseded|Deprecated (string, optional)
    """

    title: str = Field(..., description="Decision title for the ADR")
    status: str = Field(
        default="Proposed",
        description="Proposed|Accepted|Superseded|Deprecated",
    )

    def run(self) -> str:  # type: ignore[override]
        adr_dir_env = os.getenv("ADR_DIR")
        adr_dir = Path(adr_dir_env) if adr_dir_env else Path(".cursor/rules")
        adr_dir.mkdir(parents=True, exist_ok=True)

        # Determine next ADR number by scanning existing files
        pattern = re.compile(r"^ADR-(\d{3})\.md$")
        existing_nums = []
        for p in adr_dir.glob("ADR-*.md"):
            m = pattern.match(p.name)
            if m:
                existing_nums.append(int(m.group(1)))
        next_id = max(existing_nums, default=0) + 1
        fname = adr_dir / f"ADR-{next_id:03d}.md"

        content = (
            f"# ADR-{next_id:03d}: {self.title}\n"
            f"Status: {self.status}\n"
            f"Date: {date.today().isoformat()}\n\n"
            "## Context\n- \n\n"
            "## Decision\n- \n\n"
            "## Alternatives\n- \n\n"
            "## Consequences\n- Positive:\n- Negative:\n- Security/Privacy impact:\n- Migration plan:\n\n"
            "## Verification\n- Tests added/updated:\n- Metrics/alerts:\n"
        )
        fname.write_text(content, encoding="utf-8")
        return str(fname)

