from __future__ import annotations
import re
import subprocess

try:
    from agency_swarm.tools import BaseTool
    from pydantic import Field
except Exception:  # pragma: no cover
    class BaseTool:  # type: ignore
        def run(self):
            raise NotImplementedError

    def Field(*args, **kwargs):  # type: ignore
        return None


_ADR_RE = re.compile(r"ADR-[0-9]+")


def extract_adr_refs(text: str) -> list[str]:
    return sorted(set(_ADR_RE.findall(text)))


def _run(cmd: list[str]) -> tuple[int, str]:
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        return 0, out.decode()
    except subprocess.CalledProcessError as e:  # pragma: no cover (invocation result)
        return e.returncode, e.output.decode()


class DoDCheck(BaseTool):
    """Definition-of-Done check: tests gate, test pass, ADR reference present.

    This tool runs local, non-interactive checks mirroring CI:
    - scripts/check-tests-changed.sh must pass
    - pytest must pass
    - HEAD commit message (or last 10) must include ADR-###
    Returns a markdown summary with pass/fail for each item.
    """

    lookback_commits: int = Field(default=10, description="How many commits to scan for ADR refs")

    def run(self) -> str:  # type: ignore[override]
        results: list[tuple[str, bool, str]] = []

        # tests changed gate
        code, out = _run(["bash", "scripts/check-tests-changed.sh"])
        results.append(("Tests-changed gate", code == 0, out.strip()))

        # run tests
        code, out = _run(["pytest", "-q"])
        results.append(("Pytest", code == 0, out.strip().splitlines()[-1] if out else ""))

        # ADR refs in recent commits
        code, out = _run(["git", "--no-pager", "log", f"-n{self.lookback_commits}", "--pretty=%s"])
        refs = extract_adr_refs(out)
        results.append(("ADR reference in recent commits", len(refs) > 0, ", ".join(refs) or "none"))

        # format markdown
        lines = ["# Definition of Done"]
        for name, ok, info in results:
            status = "PASS" if ok else "FAIL"
            lines.append(f"- [{status}] {name} - {info}")
        return "\n".join(lines) + "\n"
