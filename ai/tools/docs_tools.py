"""
Documentation Tools

Tools to check and maintain documentation alignment for Fresh.
"""
from __future__ import annotations
from typing import List

try:
    from agency_swarm.tools import BaseTool
    from pydantic import Field
    _PD_OK = True
except Exception:
    class BaseTool:  # type: ignore
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        def run(self):
            raise NotImplementedError
    def Field(default=None, **kwargs):  # type: ignore
        return default
    _PD_OK = False

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


class DocsAlignmentCheck(BaseTool):
    """Run documentation alignment checks and return a summary report.

    Executes scripts/check_docs_alignment.py. In strict mode, non-zero exit is returned as part of the report.
    """
    if _PD_OK:
        strict: bool = Field(default=True, description="Fail on issues if True")

    def __init__(self, strict: bool = True, **kwargs):
        if _PD_OK:
            super().__init__(**kwargs)
        else:
            super().__init__(strict=strict, **kwargs)

    def run(self) -> str:  # type: ignore[override]
        checker = REPO / "scripts/check_docs_alignment.py"
        if not checker.exists():
            return "Documentation checker script not found."
        cmd = [sys.executable, str(checker)]
        if self.strict:
            cmd.append("--strict")
        try:
            proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
            output = proc.stdout + ("\n" + proc.stderr if proc.stderr else "")
            status = "PASSED" if proc.returncode == 0 else f"FAILED (exit {proc.returncode})"
            return f"DOCS ALIGNMENT {status}\n\n{output.strip()}"
        except Exception as e:
            return f"Docs alignment check failed to run: {e}"

