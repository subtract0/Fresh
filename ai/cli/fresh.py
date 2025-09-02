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
from pathlib import Path


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


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='fresh',
        description='Fresh - Autonomous Development System'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Assist command group
    assist_parser = subparsers.add_parser('assist', help='Assistant tooling (safe by default)')
    assist_sub = assist_parser.add_subparsers(dest='assist_cmd', help='Assist subcommands')

    def cmd_assist_scan(args) -> int:
        """Safe, dry-run scan for assist mode (JSON or human)."""
        tasks = scan_repository(args.path)
        # apply allow/deny filters
        def allowed(t):
            p = str(t.file_path)
            if args.allow and not any(a in p for a in args.allow):
                return False
            if args.deny and any(d in p for d in args.deny):
                return False
            return True
        tasks = [t for t in tasks if allowed(t)]
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
