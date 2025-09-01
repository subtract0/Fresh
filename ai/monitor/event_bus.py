from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_REL_PATH = ".monitor/events.jsonl"


def _find_project_root(start: Optional[Path] = None) -> Path:
    """Best-effort project root detection by walking up for .git or pyproject.toml."""
    cur = (start or Path(__file__).resolve()).parent
    for p in [cur] + list(cur.parents):
        if (p / ".git").exists() or (p / "pyproject.toml").exists():
            return p
    return cur


def _bus_path() -> Path:
    env_path = os.getenv("MONITOR_EVENT_BUS_PATH")
    if env_path:
        return Path(env_path).expanduser().resolve()
    root = _find_project_root()
    return (root / DEFAULT_REL_PATH).resolve()


class PersistentEventBus:
    """Simple JSONL-backed event bus for cross-process monitoring visibility.

    Each line is a JSON object with keys: timestamp, event_type, agent_name, details.
    """

    def __init__(self, path: Optional[Path] = None, max_lines: int = 5000) -> None:
        self.path = path or _bus_path()
        self.max_lines = max_lines
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: Dict) -> None:
        try:
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(event) + "\n")
        except Exception:
            # Non-fatal: monitoring should never break core workflows
            pass
        # Occasional compaction (best-effort)
        try:
            if self.path.stat().st_size > 2_000_000:  # ~2MB
                self._compact()
        except Exception:
            pass

    def _compact(self) -> None:
        try:
            lines = self.path.read_text(encoding="utf-8").splitlines()
            if len(lines) > self.max_lines:
                lines = lines[-self.max_lines :]
                self.path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        except Exception:
            pass

    def read_recent(self, limit: int = 20) -> List[Dict]:
        try:
            if not self.path.exists():
                return []
            # Simple tail read
            with self.path.open("r", encoding="utf-8") as f:
                lines = f.readlines()
            if not lines:
                return []
            return [json.loads(line) for line in lines[-limit:]]
        except Exception:
            return []


_bus: Optional[PersistentEventBus] = None


def get_bus() -> PersistentEventBus:
    global _bus
    if _bus is None:
        _bus = PersistentEventBus()
    return _bus
