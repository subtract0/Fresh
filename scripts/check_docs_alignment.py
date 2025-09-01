#!/usr/bin/env python3
"""
Documentation alignment checker for Fresh.

Checks:
- Existence of core docs and code files referenced from README
- Markdown links in docs/INDEX.md resolve to existing files
- Warns for missing optional docs; can fail in --strict mode
"""
from __future__ import annotations
import argparse
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
README = REPO / "README.md"
DOCS = REPO / "docs"

CORE_DOCS = [
    DOCS / "MEMORY_SYSTEM.md",
    DOCS / "ENHANCED_AGENTS.md",
    DOCS / "API_REFERENCE.md",
    DOCS / "AGENT_DEVELOPMENT.md",
    DOCS / "DEPLOYMENT.md",
    DOCS / "INDEX.md",
    DOCS / "CAPABILITIES.md",
]

CORE_CODE_PATHS = [
    REPO / "ai/memory/store.py",
    REPO / "ai/memory/intelligent_store.py",
    REPO / "ai/memory/firestore_store.py",
    REPO / "ai/agents/enhanced_agents.py",
    REPO / "ai/tools/enhanced_memory_tools.py",
    REPO / "ai/tools/persistent_memory_tools.py",
    REPO / "tests/test_intelligent_memory.py",
    REPO / "tests/test_firestore_memory.py",
]

LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def check_exists(paths: list[Path]) -> list[str]:
    missing = []
    for p in paths:
        if not p.exists():
            missing.append(str(p.relative_to(REPO)))
    return missing


def extract_links(md_path: Path) -> list[str]:
    text = md_path.read_text(encoding="utf-8")
    return LINK_PATTERN.findall(text)


def resolve_link(target: str, base: Path) -> Path:
    # External links are ignored
    if target.startswith("http://") or target.startswith("https://"):
        return Path("/dev/null")
    # Strip anchor fragments (e.g., file.md#section)
    target_path = target.split('#', 1)[0]
    # Fragment-only links are ignored
    if target_path.strip() == "" or target_path == "#":
        return Path("/dev/null")
    return (base.parent / target_path).resolve()


def check_index_links() -> list[str]:
    idx = DOCS / "INDEX.md"
    if not idx.exists():
        return ["docs/INDEX.md (missing)"]
    broken = []
    for link in extract_links(idx):
        resolved = resolve_link(link, idx)
        if str(resolved) == "/dev/null":
            continue
        if not resolved.exists():
            try:
                broken.append(str(resolved.relative_to(REPO)))
            except Exception:
                broken.append(str(resolved))
    return broken


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if any issues found")
    args = parser.parse_args()

    missing_core_docs = check_exists(CORE_DOCS)
    missing_core_code = check_exists(CORE_CODE_PATHS)
    broken_index_links = check_index_links()

    issues = []
    if missing_core_docs:
        issues.append(("Missing core docs", missing_core_docs))
    if missing_core_code:
        issues.append(("Missing referenced code files", missing_core_code))
    if broken_index_links:
        issues.append(("Broken links in docs/INDEX.md", broken_index_links))

    if not issues:
        print("✅ Documentation alignment check passed.")
        return 0

    print("❌ Documentation alignment issues detected:\n")
    for title, items in issues:
        print(f"- {title}:")
        for it in items:
            print(f"  • {it}")
    print()

    return 1 if args.strict else 0


if __name__ == "__main__":
    sys.exit(main())

