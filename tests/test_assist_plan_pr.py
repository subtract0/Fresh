import os
import subprocess
from types import SimpleNamespace
from pathlib import Path

import ai.cli.fresh as fresh


def _run(cmd, cwd):
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, check=False)


def _init_repo(tmp):
    repo = tmp / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    # init
    assert _run(["git", "init"], repo).returncode == 0
    # configure identity
    assert _run(["git", "config", "user.email", "test@example.com"], repo).returncode == 0
    assert _run(["git", "config", "user.name", "Test User"], repo).returncode == 0
    # initial commit
    (repo / "README.md").write_text("# Repo\n", encoding="utf-8")
    assert _run(["git", "add", "README.md"], repo).returncode == 0
    assert _run(["git", "commit", "-m", "init"], repo).returncode == 0
    return repo


def test_assist_plan_pr_commits_docs_only(tmp_path):
    repo = _init_repo(tmp_path)

    out = repo / "assist_report.md"
    # Prepare args for success path (no pre-staged non-doc files)
    args = SimpleNamespace(
        path=str(repo),
        out=str(out),
        limit=5,
        allow=None,
        deny=None,
        branch=None,
        push=False,
        create_pr=False,
        base="main",
        title=None,
        body=None,
        force=False,
    )

    # Run the plan-pr command
    ret = fresh.cmd_assist_plan_pr(args)
    assert ret == 0

    # Verify we are on a new branch and a commit exists including only the report
    # Get current branch name
    b = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo)
    assert b.returncode == 0
    branch_name = b.stdout.strip()
    assert branch_name.startswith("chore/assist-plan-")

    # Verify last commit files
    show = _run(["git", "--no-pager", "show", "--name-only", "--pretty=format:%n"], repo)
    assert show.returncode == 0
    changed = [p.strip() for p in show.stdout.splitlines() if p.strip()]
    # Only assist_report.md should be listed
    assert changed == ["assist_report.md"]


def test_assist_plan_pr_enforces_docs_only(tmp_path):
    repo = _init_repo(tmp_path)

    # Pre-stage a non-doc file
    (repo / "code.py").write_text("print('hi')\n", encoding="utf-8")
    assert _run(["git", "add", "code.py"], repo).returncode == 0

    out = repo / "assist_report.md"
    args = SimpleNamespace(
        path=str(repo),
        out=str(out),
        limit=5,
        allow=None,
        deny=None,
        branch="chore/assist-plan-test",
        push=False,
        create_pr=False,
        base="main",
        title=None,
        body=None,
        force=True,  # bypass dirty working tree check
    )

    ret = fresh.cmd_assist_plan_pr(args)
    assert ret == 1, "Should abort because staged changes include non-doc files"

    # Ensure no new commit was made on the new branch
    # Switch to the branch to match behavior (it is created even on failure)
    co = _run(["git", "checkout", "chore/assist-plan-test"], repo)
    assert co.returncode == 0

    # Count commits should still be 1 (the init commit)
    log = _run(["git", "--no-pager", "log", "--oneline"], repo)
    assert log.returncode == 0
    commits = [line for line in log.stdout.splitlines() if line.strip()]
    assert len(commits) == 1, f"Unexpected commits: {commits}"
