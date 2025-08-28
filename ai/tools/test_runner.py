from __future__ import annotations
import subprocess
import shlex
from pathlib import Path


def run_pytest(path: str | Path) -> tuple[int, str]:
    """Run pytest in the given path, returning (exit_code, output)."""
    p = Path(path)
    cmd = f"pytest -q {shlex.quote(str(p))}"
    try:
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return 0, out.decode()
    except subprocess.CalledProcessError as e:
        return e.returncode, e.output.decode()

