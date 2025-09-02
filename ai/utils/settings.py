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

    Additionally, default to offline-safe behavior when OPENAI_API_KEY is not set.
    This keeps tests and local development fast and deterministic by avoiding
    unintended network calls.
    """
    val = os.getenv("FRESH_OFFLINE", "").strip().lower()
    if val in _TRUE_SET:
        return True
    # If no OpenAI key is configured, stay offline by default
    if not os.getenv("OPENAI_API_KEY"):
        return True
    return False

