from __future__ import annotations
from pathlib import Path
import textwrap
import re
import unicodedata
from ai.tools.test_runner import run_pytest


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_devcycle_slugify_sandbox(base: Path) -> dict:
    """Demonstrate an iterative TDD dev cycle in a sandbox.

    Steps:
      1) Write failing tests for slugify in sandbox/tests/
      2) Run pytest (expect failure)
      3) Implement minimal slugify in sandbox/src/utils/slugify.py
      4) Run pytest (expect success)
    Returns a result dict with fields: iterations, first_fail, final_pass, output.
    """
    tests_dir = base / "tests"
    src_dir = base / "src" / "utils"

    test_code = textwrap.dedent(
        """
        from src.utils.slugify import slugify

        def test_basic_slugify():
            assert slugify("Hello, World!") == "hello-world"

        def test_multiple_spaces():
            assert slugify("  Multiple   spaces  ") == "multiple-spaces"

        def test_accents_and_symbols():
            assert slugify("Café Déjà Vu!!!") == "cafe-deja-vu"

        def test_existing_dashes_and_underscores():
            assert slugify("__Already--slug__") == "already-slug"
        """
    )
    _write(tests_dir / "test_slugify.py", test_code)

    # 1) RED
    # run pytest from sandbox root so `src` is importable
    (base / "src").mkdir(parents=True, exist_ok=True)
    _write(base / "src" / "__init__.py", "")
    _write(src_dir / "__init__.py", "")
    # Ensure sandbox root is on sys.path during pytest collection
    _write(base / "conftest.py", "import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))\n")

    code, out1 = run_pytest(base)

    # 2) GREEN - implement minimal slugify
    impl = textwrap.dedent(
        """
        import re
        import unicodedata

        def _strip_accents(s: str) -> str:
            return (
                unicodedata.normalize("NFKD", s)
                .encode("ascii", "ignore")
                .decode("ascii")
            )

        def slugify(text: str) -> str:
            s = _strip_accents(text.lower())
            # Replace non-alphanumeric with dashes
            s = re.sub(r"[^a-z0-9]+", "-", s)
            # Collapse multiple dashes
            s = re.sub(r"-+", "-", s)
            # Trim leading/trailing dashes
            return s.strip("-")
        """
    )
    _write(src_dir / "slugify.py", impl)

    code2, out2 = run_pytest(base)

    return {
        "iterations": 2,
        "first_fail": code != 0,
        "final_pass": code2 == 0,
        "output": out1 + "\n---\n" + out2,
        "sandbox": str(base),
    }

