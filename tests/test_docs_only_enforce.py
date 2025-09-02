from ai.cli.fresh import _docs_only_allowed


def test_docs_only_allowed_accepts_markdown_and_docs():
    assert _docs_only_allowed(["README.md"]) is True
    assert _docs_only_allowed(["docs/PLAN.md", ".fresh/assist.yaml"]) is True


def test_docs_only_allowed_rejects_code_paths():
    assert _docs_only_allowed(["ai/cli/fresh.py"]) is False
    assert _docs_only_allowed(["src/app.js"]) is False

