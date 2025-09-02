from __future__ import annotations
import os
from typing import Optional

# Default timeouts for external calls (HTTP, OpenAI, git/gh subprocess, etc.)
# Can be overridden via env for debugging: FRESH_TIMEOUT_SECONDS=45
TIMEOUT_SECONDS: int = int(os.getenv("FRESH_TIMEOUT_SECONDS", "30") or 30)

_TRUE_SET = {"1", "true", "yes", "on"}


def is_offline() -> bool:
    """Return True when offline/safe mode is requested.

    Controlled via env FRESH_OFFLINE (1/true/yes/on). The CLI can also set this env
    when the --offline flag is provided.
    """
    val = os.getenv("FRESH_OFFLINE", "").strip().lower()
    return val in _TRUE_SET

