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
from pathlib import Path
from typing import List, Optional

from ai.loop.repo_scanner import scan_repository, Task
from ai.agents.mother import MotherAgent


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
    if args.watch:
        print("👁️ Starting continuous monitoring mode...")
        print("   (This feature will be implemented in dev_loop.py)")
        # TODO: Implement continuous monitoring
        return 0
    else:
        print("🚀 Running single development cycle...")
        print("   (This feature will be implemented in dev_loop.py)")
        # TODO: Implement single cycle
        return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='fresh',
        description='Fresh - Autonomous Development System'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
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
    run_parser.set_defaults(func=cmd_run)
    
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
