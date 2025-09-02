from pathlib import Path
from types import SimpleNamespace
import subprocess
import sys

from ai.cli import fresh


def test_scaffold_python_package(tmp_path):
    dest = tmp_path / "proj"
    args = SimpleNamespace(name="MyLib", dest=str(dest), template="python-package", force=False, init_git=False)
    rc = fresh.main if False else None
    assert fresh._pkgname("MyLib") == "mylib"
    assert fresh._render_text("hello {{project}}", {"project": "MyLib"}) == "hello MyLib"

    # Run scaffold
    ret = fresh.cmd_scaffold_new(args)
    assert ret == 0
    # Files exist
    assert (dest / "README.md").exists()
    assert (dest / "pyproject.toml").exists()
    assert (dest / "setup.py").exists()
    assert (dest / "src" / "mylib" / "__init__.py").exists()
    assert (dest / "tests" / "test_sanity.py").exists()

    # Content rendered
    ini = (dest / "src" / "mylib" / "__init__.py").read_text()
    assert "hello from mylib" in ini

