#!/usr/bin/env python
"""Fresh CLI - Command-line interface for autonomous development.

This module provides the main CLI commands for the Fresh autonomous
development system, including repository scanning, agent spawning,
and monitoring.

Usage:
    fresh scan              # Scan repository for issues
    fresh run --once        # Run one development cycle
    fresh run --watch       # Continuous monitoring mode
    fresh spawn "task"      # Spawn agent for specific task

Cross-references:
    - ADR-008: Autonomous Development Loop Architecture
    - Repository Scanner: ai/loop/repo_scanner.py
    - Mother Agent: ai/agents/mother.py
    - Development Loop: ai/loop/dev_loop.py
"""
from __future__ import annotations
import sys
import json
import argparse
import os
from pathlib import Path
from typing import List, Optional
import subprocess

from ai.loop.repo_scanner import scan_repository, Task, TaskType
from ai.agents.mother import MotherAgent
from ai.loop.dev_loop import DevLoop, run_development_cycle
import asyncio
import yaml
from datetime import datetime


# Helper functions exposed at module level (used by scaffold and tests)
def _slugify(name: str) -> str:
    return ''.join(c.lower() if c.isalnum() else '-' for c in name).strip('-')


def _pkgname(name: str) -> str:
    return ''.join(c.lower() if c.isalnum() else '_' for c in name).strip('_')


def _render_text(content: str, mapping: dict) -> str:
    out = content
    for k, v in mapping.items():
        out = out.replace(f"{{{{{k}}}}}", v)
    return out


def cmd_scan(args):
    """Scan repository for issues and print as JSON.
    
    Args:
        args: Parsed command-line arguments
    """
    tasks = scan_repository(args.path)
    
    if args.json:
        # Output as JSON for scripting
        output = {
            "total": len(tasks),
            "tasks": [t.to_dict() for t in tasks[:args.limit]]
        }
        print(json.dumps(output, indent=2))
    else:
        # Human-readable output
        print(f"\n📋 Found {len(tasks)} tasks:\n")
        
        if not tasks:
            print("  ✨ No issues found - repository is clean!")
        else:
            # Group by type
            by_type = {}
            for task in tasks:
                task_type = task.type.value
                if task_type not in by_type:
                    by_type[task_type] = []
                by_type[task_type].append(task)
            
            # Display by type
            for task_type, type_tasks in by_type.items():
                print(f"  {task_type} ({len(type_tasks)} items):")
                for task in type_tasks[:args.limit]:
                    print(f"    • {task.file_path}:{task.line_number}")
                    print(f"      {task.description[:80]}")
                if len(type_tasks) > args.limit:
                    print(f"      ... and {len(type_tasks) - args.limit} more")
                print()
    
    return 0 if not tasks else 1


def cmd_spawn(args):
    """Spawn an agent for a specific task.
    
    Args:
        args: Parsed command-line arguments
    """
    print(f"🤖 Spawning agent for task: {args.task}")
    
    mother = MotherAgent()
    result = mother.run(
        name=f"cli_spawn_{Path.cwd().name}",
        instructions=args.task,
        model=args.model,
        output_type=args.output
    )
    
    if result.success:
        print(f"✅ Agent {result.agent_type} completed successfully!")
        print(f"   Output: {result.output}")
        if result.artifacts:
            print(f"   Artifacts: {json.dumps(result.artifacts, indent=2)}")
    else:
        print(f"❌ Agent failed: {result.error}")
        return 1
    
    return 0


def cmd_run(args):
    """Run autonomous development loop.
    
    Args:
        args: Parsed command-line arguments
    """
    # Honor offline flag by setting env (downstream code checks FRESH_OFFLINE)
    if args.offline:
        os.environ["FRESH_OFFLINE"] = "1"

    if args.watch:
        print("👁️ Starting continuous monitoring mode...")
        print(f"   Scanning every {args.interval} seconds")
        print(f"   Max {args.max_tasks} tasks per cycle")
        if args.stop_after > 0:
            print(f"   Will stop after {args.stop_after} cycles")
        print("   Press Ctrl+C to stop\n")
        
        async def watch():
            from ai.loop.dev_loop import DevLoop
            loop = DevLoop(
                max_tasks=args.max_tasks,
                use_dashboard=args.dashboard,
                state_file=Path(".fresh/dev_loop_state.json")
            )
            
            cycles = 0
            while True:
                try:
                    results = await loop.run_cycle()
                    print(f"\n✅ Cycle completed: {len(results)} tasks processed")
                except Exception as e:
                    print(f"\n❌ Cycle failed: {e}")
                
                cycles += 1
                if args.stop_after and cycles >= args.stop_after:
                    print(f"\n⏹️ Reached stop-after limit ({args.stop_after} cycles)")
                    break

                print(f"Waiting {args.interval} seconds...")
                await asyncio.sleep(args.interval)
        
        try:
            asyncio.run(watch())
        except KeyboardInterrupt:
            print("\n⏹️ Stopped monitoring")
        return 0
    else:
        print("🚀 Running single development cycle...")
        
        loop = DevLoop(
            max_tasks=args.max_tasks,
            dry_run=args.dry_run,
            use_dashboard=args.dashboard
        )
        
        async def run_once():
            results = await loop.run_cycle()
            return results
        
        results = asyncio.run(run_once())
        
        print(f"\n✅ Processed {len(results)} tasks")
        for result in results:
            if result.success:
                print(f"   • {result.agent_type}: {result.output[:60]}...")
            else:
                print(f"   • Failed: {result.error}")
        
        return 0


def _read_version() -> str:
    """Read version string from VERSION file (repo root)."""
    try:
        root = Path(__file__).resolve().parents[2]
        version_file = root / "VERSION"
        if version_file.exists():
            return version_file.read_text(encoding="utf-8").strip()
    except Exception:
        pass
    return "unknown"


def _git_short_sha(default: str = "unknown") -> str:
    """Return short git sha for the current repo, if available."""
    try:
        # Use git rev-parse; fall back to default on error
        out = subprocess.run(
            ["git", "rev-parse", "--short=12", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False
        )
        sha = out.stdout.strip()
        return sha or default
    except Exception:
        return default


def cmd_health(args) -> int:
    """Print health information as JSON and return 0."""
    data = {
        "ok": True,
        "version": _read_version(),
        "commit": _git_short_sha(),
        "cwd": str(Path.cwd()),
    }
    print(json.dumps(data, indent=2))
    return 0


def cmd_version(args) -> int:
    """Print version and commit in a human-friendly format and return 0."""
    print(f"Fresh version: {_read_version()} ({_git_short_sha()})")
    return 0


def _docs_only_allowed(paths: list[str]) -> bool:
    """Return True if all paths are 'docs-only' (markdown/text or docs/.fresh trees)."""
    allowed_ext = ('.md', '.rst', '.txt')
    for p in paths:
        s = p.replace('\\', '/')
        if s.startswith('docs/') or s.startswith('.fresh/'):
            continue
        if s.endswith(allowed_ext):
            continue
        return False
    return True

# Assist helpers at module level for reuse and testing

def _load_policy(path: str) -> dict:
    root = Path(path).resolve()
    policy_path = root / ".fresh" / "assist.yaml"
    default = {
        'allow': None,
        'deny': ['.git', 'node_modules', 'venv', '.venv', '__pycache__']
    }
    try:
        if policy_path.exists():
            data = yaml.safe_load(policy_path.read_text(encoding='utf-8')) or {}
            allow = data.get('allow') or default['allow']
            deny = data.get('deny') or default['deny']
            return {'allow': allow, 'deny': deny}
    except Exception:
        pass
    return default


def _apply_filters(tasks, allow, deny):
    def allowed_task(t):
        p = str(t.file_path)
        if allow and not any(a in p for a in allow):
            return False
        if deny and any(d in p for d in deny):
            return False
        return True
    return [t for t in tasks if allowed_task(t)]


def cmd_assist_report(args) -> int:
    tasks = scan_repository(args.path)
    policy = _load_policy(args.path)
    allow = args.allow if args.allow is not None else policy['allow']
    deny = args.deny if args.deny is not None else policy['deny']
    tasks = _apply_filters(tasks, allow, deny)
    tasks.sort(key=lambda x: (str(x.file_path), x.line_number or 0, x.type.value))
    summary = {}
    for t in tasks:
        summary[t.type.value] = summary.get(t.type.value, 0) + 1
    # Build markdown
    lines = []
    lines.append(f"# Assist Report\n")
    lines.append(f"Scanned: {Path(args.path).resolve()}\n")
    lines.append("\n## Summary\n")
    total = len(tasks)
    lines.append(f"- Total findings: {total}")
    for k in sorted(summary.keys()):
        lines.append(f"- {k}: {summary[k]}")
    lines.append("\n## Items\n")
    for t in tasks[:args.limit]:
        desc = t.description.replace('\n', ' ')[:200]
        lines.append(f"- {t.type.value}: `{t.file_path}:{t.line_number}` — {desc}")
    content = "\n".join(lines) + "\n"
    out_path = Path(args.out)
    if out_path.exists() and not getattr(args, 'force', False):
        print(f"❌ Refusing to overwrite existing file: {out_path}")
        print("   Use --force to overwrite.")
        return 1
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding='utf-8')
    print(f"✅ Report written: {out_path}")
    return 0


def _git(args_list, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(args_list, cwd=str(cwd), capture_output=True, text=True, timeout=15)


def cmd_assist_plan_pr(args) -> int:
    root = Path(args.path).resolve()
    out = Path(args.out)
    # Ensure report exists; if not, generate it (still dry-run of code changes)
    if not out.exists():
        # Build a minimal args object for report generation
        class _Args:
            pass
        _args = _Args()
        _args.path = str(root)
        _args.out = str(out)
        _args.limit = args.limit
        _args.allow = args.allow
        _args.deny = args.deny
        _args.force = True
        cmd_assist_report(_args)
    # Git safety: ensure repo
    res = _git(["git", "rev-parse", "--is-inside-work-tree"], cwd=root)
    if res.returncode != 0 or res.stdout.strip() != "true":
        print("❌ Not a git repository:", root)
        return 1
    # If not force, ensure clean working tree
    if not getattr(args, 'force', False):
        st = _git(["git", "status", "--porcelain"], cwd=root)
        if st.returncode != 0:
            print("❌ git status failed:", st.stderr.strip())
            return 1
        lines = [line for line in st.stdout.splitlines() if line.strip()]
        if lines:
            rel_out = str(out.relative_to(root))
            # Extract file paths from porcelain lines (first two columns are status)
            dirty_files = [(ln[3:].strip() if len(ln) > 3 else ln.strip()) for ln in lines]
            non_report_dirty = [p for p in dirty_files if p != rel_out]
            if non_report_dirty:
                print("❌ Working tree not clean. Commit or stash changes, or pass --force.")
                return 1
    # Create branch name
    branch = args.branch or f"chore/assist-plan-{datetime.now().strftime('%Y%m%d-%H%M')}"
    # Create branch from current HEAD
    co = _git(["git", "checkout", "-b", branch], cwd=root)
    if co.returncode != 0:
        print("❌ Failed to create branch:", co.stderr.strip())
        return 1
    # Add only report file
    add = _git(["git", "add", str(out.relative_to(root))], cwd=root)
    if add.returncode != 0:
        print("❌ git add failed:", add.stderr.strip())
        return 1
    # Enforce docs-only staged changes
    staged = _git(["git", "diff", "--staged", "--name-only"], cwd=root)
    if staged.returncode != 0:
        print("❌ Failed to inspect staged changes:", staged.stderr.strip())
        return 1
    staged_paths = [line.strip() for line in staged.stdout.splitlines() if line.strip()]
    if not _docs_only_allowed(staged_paths):
        print("❌ Staged changes include non-docs files. Aborting to keep safe defaults.")
        print("   Staged:", ", ".join(staged_paths))
        print("   Allowed: docs/**, .fresh/**, *.md, *.rst, *.txt")
        return 1
    msg = f"docs(assist): add assist report\n\nGenerated safely by 'fresh assist report'"
    cm = _git(["git", "commit", "-m", msg], cwd=root)
    if cm.returncode != 0:
        print("❌ git commit failed:", cm.stderr.strip())
        return 1
    print(f"✅ Committed assist report on branch {branch}")
    pushed = False
    if getattr(args, 'push', False):
        ps = _git(["git", "push", "-u", "origin", branch], cwd=root)
        if ps.returncode != 0:
            print("⚠️ Push failed:", ps.stderr.strip())
            print("   You can push manually: git push -u origin", branch)
        else:
            pushed = True
            print(f"✅ Pushed branch to origin/{branch}")
    # Optional: create a draft PR using gh CLI when available
    if getattr(args, 'create_pr', False):
        if not pushed:
            print("❌ Cannot create PR because branch is not pushed. Re-run with --push or push manually.")
            return 1
        gh = _git(["gh", "--version"], cwd=root)
        pr_title = getattr(args, 'title', None) or f"Assist plan: {out.name}"
        if gh.returncode == 0:
            if getattr(args, 'body', None):
                body_arg = ["--body", args.body]
            else:
                body_arg = ["--body-file", str(out.relative_to(root))]
            pr = _git([
                "gh", "pr", "create",
                "--base", args.base,
                "--head", branch,
                "--title", pr_title,
                "--draft",
                "--label", "assist-plan",
                *body_arg
            ], cwd=root)
            if pr.returncode != 0:
                print("⚠️ gh pr create failed:", pr.stderr.strip())
                print("   You can open a PR manually on GitHub.")
            else:
                print("✅ Draft PR created via gh")
        else:
            print("⚠️ gh CLI not found. Skipping PR creation.")
            print("   Install GitHub CLI or open a PR manually using the pushed branch.")
    return 0


# Scaffold helper at module level so tests can import cmd_scaffold_new

def _copy_template(template_name: str, dest: Path, mapping: dict, force: bool = False) -> None:
    templates_root = Path(__file__).resolve().parents[2] / "scaffolding" / "templates" / template_name
    if not templates_root.exists():
        raise RuntimeError(f"Unknown template: {template_name}")
    # Safety: refuse to overwrite non-empty unless force
    if dest.exists() and not force:
        if any(dest.iterdir()):
            raise RuntimeError(f"Destination not empty: {dest}")
    dest.mkdir(parents=True, exist_ok=True)
    for root, dirs, files in os.walk(templates_root):
        rel = Path(root).relative_to(templates_root)
        # Render directory path parts (support {{package}} in folder names)
        if rel.parts:
            rendered_parts = [_render_text(part, mapping) for part in rel.parts]
            out_dir = dest.joinpath(*rendered_parts)
        else:
            out_dir = dest
        out_dir.mkdir(parents=True, exist_ok=True)
        for fname in files:
            src_file = Path(root) / fname
            # Render filename (supports {{package}})
            rendered_name = _render_text(fname, mapping)
            out_file = out_dir / rendered_name
            text = src_file.read_text(encoding='utf-8')
            rendered = _render_text(text, mapping)
            out_file.write_text(rendered, encoding='utf-8')


def cmd_scaffold_new(args) -> int:
    project = args.name
    template = args.template
    dest = Path(args.dest).resolve()
    mapping = {
        'project': project,
        'package': _pkgname(project),
    }
    try:
        _copy_template(template, dest, mapping, force=args.force)
    except Exception as e:
        print("❌ Scaffold failed:", str(e))
        return 1
    if getattr(args, 'init_git', False):
        subprocess.run(["git", "init"], cwd=str(dest), check=False)
    print(f"✅ Project scaffolded at {dest}")
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='fresh',
        description='Fresh - Autonomous Development System'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Scaffold command group
    scaffold_parser = subparsers.add_parser('scaffold', help='Generate a new project (deterministic, safe)')
    scaffold_sub = scaffold_parser.add_subparsers(dest='scaffold_cmd', help='Scaffold subcommands')

    scaffold_new = scaffold_sub.add_parser('new', help='Create a new project from a template')
    scaffold_new.add_argument('name', help='Project name (used for package and title)')
    scaffold_new.add_argument('dest', help='Destination directory (created if missing)')
    scaffold_new.add_argument('--template', default='python-package', help='Template name (default: python-package)')
    scaffold_new.add_argument('--force', action='store_true', help='Overwrite non-empty destination')
    scaffold_new.add_argument('--init-git', action='store_true', help='Initialize a git repository in the destination')
    scaffold_new.set_defaults(func=cmd_scaffold_new)
    
    # Assist command group
    assist_parser = subparsers.add_parser('assist', help='Assistant tooling (safe by default)')
    assist_sub = assist_parser.add_subparsers(dest='assist_cmd', help='Assist subcommands')

    def cmd_assist_scan(args) -> int:
        """Safe, dry-run scan for assist mode (JSON or human)."""
        tasks = scan_repository(args.path)
        # load policy and merge CLI filters
        policy = _load_policy(args.path)
        allow = args.allow if args.allow is not None else policy['allow']
        deny = args.deny if args.deny is not None else policy['deny']
        tasks = _apply_filters(tasks, allow, deny)
        # deterministic ordering
        tasks.sort(key=lambda x: (str(x.file_path), x.line_number or 0, x.type.value))
        summary = {
            'total': len(tasks),
            'by_type': {},
        }
        for t in tasks:
            k = t.type.value
            summary['by_type'][k] = summary['by_type'].get(k, 0) + 1
        if args.json:
            out = {
                'summary': summary,
                'items': [t.to_dict() for t in tasks[:args.limit]],
            }
            print(json.dumps(out, indent=2))
        else:
            print(f"Found {summary['total']} items")
            for k in sorted(summary['by_type'].keys()):
                print(f"  {k}: {summary['by_type'][k]}")
            print()
            for t in tasks[:args.limit]:
                print(f"• {t.type.value} {t.file_path}:{t.line_number} — {t.description[:80]}")
        return 0

    assist_scan = assist_sub.add_parser('scan', help='Scan repository safely (dry-run)')
    assist_scan.add_argument('path', nargs='?', default='.', help='Path to scan (default: .)')
    assist_scan.add_argument('--json', action='store_true', help='Output JSON')
    assist_scan.add_argument('--limit', type=int, default=200, help='Max items to emit')
    assist_scan.add_argument('--allow', nargs='*', help='Only include files containing any of these path fragments')
    assist_scan.add_argument('--deny', nargs='*', help='Exclude files containing any of these path fragments')
    assist_scan.set_defaults(func=cmd_assist_scan)


    assist_report = assist_sub.add_parser('report', help='Emit a Markdown report (dry-run)')
    assist_report.add_argument('path', nargs='?', default='.', help='Path to scan (default: .)')
    assist_report.add_argument('--out', default='assist_report.md', help='Output markdown file path')
    assist_report.add_argument('--limit', type=int, default=500, help='Max items to include')
    assist_report.add_argument('--allow', nargs='*', help='Only include files containing any of these path fragments')
    assist_report.add_argument('--deny', nargs='*', help='Exclude files containing any of these path fragments')
    assist_report.add_argument('--force', action='store_true', help='Overwrite if the output file exists')
    assist_report.set_defaults(func=cmd_assist_report)


    # Plan PR command
    assist_plan_pr = assist_sub.add_parser('plan-pr', help='Create a docs-only branch with the assist report (no code changes)')
    assist_plan_pr.add_argument('path', nargs='?', default='.', help='Path to repo (default: .)')
    assist_plan_pr.add_argument('--out', default='assist_report.md', help='Report file to include (will be generated if missing)')
    assist_plan_pr.add_argument('--limit', type=int, default=500, help='Max items in report if generated')
    assist_plan_pr.add_argument('--allow', nargs='*', help='Policy allow override')
    assist_plan_pr.add_argument('--deny', nargs='*', help='Policy deny override')
    assist_plan_pr.add_argument('--branch', help='Branch name (default chore/assist-plan-YYYYmmdd-HHMM)')
    assist_plan_pr.add_argument('--push', action='store_true', help='Push the branch to origin')
    assist_plan_pr.add_argument('--create-pr', action='store_true', help='Create a draft PR (requires gh or GITHUB_TOKEN)')
    assist_plan_pr.add_argument('--base', default='main', help='Base branch for PR (default: main)')
    assist_plan_pr.add_argument('--title', help='Custom PR title (default generated)')
    assist_plan_pr.add_argument('--body', help='Custom PR body (default: use report content)')
    assist_plan_pr.add_argument('--force', action='store_true', help='Proceed even if working tree not clean')
    assist_plan_pr.set_defaults(func=cmd_assist_plan_pr)

    # Health command
    health_parser = subparsers.add_parser('health', help='Show health status and version info (JSON)')
    health_parser.set_defaults(func=cmd_health)

    # Version command
    version_parser = subparsers.add_parser('version', help='Show version and commit')
    version_parser.set_defaults(func=cmd_version)

    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan repository for issues')
    scan_parser.add_argument('path', nargs='?', default='.', help='Repository path (default: current directory)')
    scan_parser.add_argument('--json', action='store_true', help='Output as JSON')
    scan_parser.add_argument('--limit', type=int, default=10, help='Max items per type to show')
    scan_parser.set_defaults(func=cmd_scan)
    
    # Spawn command
    spawn_parser = subparsers.add_parser('spawn', help='Spawn agent for specific task')
    spawn_parser.add_argument('task', help='Task description for agent')
    spawn_parser.add_argument('--model', default='gpt-4', help='AI model to use')
    spawn_parser.add_argument('--output', default='code', choices=['code', 'tests', 'docs', 'design', 'review'],
                             help='Expected output type')
    spawn_parser.set_defaults(func=cmd_spawn)
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run autonomous development loop')
    run_parser.add_argument('--once', action='store_true', help='Run single cycle')
    run_parser.add_argument('--watch', action='store_true', help='Continuous monitoring mode')
    run_parser.add_argument('--max-tasks', type=int, default=5, help='Max tasks per cycle')
    run_parser.add_argument('--interval', type=int, default=300, help='Seconds between cycles (watch mode)')
    run_parser.add_argument('--stop-after', type=int, default=0, help='Stop after N cycles (watch mode)')
    run_parser.add_argument('--dry-run', action='store_true', help='Scan but don\'t execute agents')
    run_parser.add_argument('--dashboard', action='store_true', help='Show real-time dashboard')
    run_parser.add_argument('--offline', action='store_true', help='Run in offline mode (skip network calls)')
    run_parser.set_defaults(func=cmd_run)
    
    # Monitor command (alias for run --watch --dashboard)
    monitor_parser = subparsers.add_parser('monitor', help='Monitor with live dashboard')
    monitor_parser.add_argument('--max-tasks', type=int, default=5, help='Max tasks per cycle')
    monitor_parser.add_argument('--interval', type=int, default=300, help='Seconds between cycles')
    monitor_parser.set_defaults(
        func=lambda args: cmd_run(argparse.Namespace(
            watch=True,
            dashboard=True,
            max_tasks=args.max_tasks,
            interval=args.interval,
            dry_run=False
        ))
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    if hasattr(args, 'func'):
        sys.exit(args.func(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
