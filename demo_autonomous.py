#!/usr/bin/env python
"""Demonstration of the Fresh Autonomous Development System.

This script showcases the complete autonomous development loop
with real-time monitoring and agent coordination.
"""
import asyncio
import sys
import tempfile
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import time

# Add ai module to path
sys.path.insert(0, str(Path(__file__).parent))

from ai.loop.dev_loop import DevLoop
from ai.loop.repo_scanner import TaskType
from ai.interface.console_dashboard import start_dashboard, stop_dashboard


console = Console()


def print_welcome():
    """Print welcome message."""
    welcome_text = Text()
    welcome_text.append("🎉 ", style="bold yellow")
    welcome_text.append("Fresh Autonomous Development System Demo", style="bold cyan")
    welcome_text.append("\n\n")
    welcome_text.append("This demonstration will show:\n", style="white")
    welcome_text.append("  • Repository scanning for issues\n", style="dim")
    welcome_text.append("  • Intelligent agent dispatching\n", style="dim")
    welcome_text.append("  • Real-time progress monitoring\n", style="dim")
    welcome_text.append("  • Automated task processing\n", style="dim")
    
    console.print(Panel(welcome_text, border_style="cyan", title="Welcome"))
    console.print()


def create_demo_repository(base_path: Path) -> Path:
    """Create a demo repository with various issues."""
    repo_path = base_path / "demo_repo"
    repo_path.mkdir(exist_ok=True)
    
    # Create Python file with TODOs
    app_file = repo_path / "app.py"
    app_file.write_text("""
# Main application file

def calculate_total(items):
    # TODO: Add input validation
    total = 0
    for item in items:
        total += item.price  # FIXME: Handle missing price attribute
    return total

def process_user_data(user_id):
    # TODO: Implement caching for better performance
    data = fetch_from_database(user_id)
    return data

def fetch_from_database(user_id):
    # TODO: Add proper error handling
    pass

# FIXME: Remove debug print statements before production
print("Debug: Application loaded")
""")
    
    # Create test file
    test_file = repo_path / "test_app.py"
    test_file.write_text("""
import pytest

def test_calculate_total():
    # TODO: Add more comprehensive test cases
    assert True  # Placeholder test
    
def test_process_user_data():
    # FIXME: Mock database calls properly
    pass
""")
    
    # Create documentation file
    readme = repo_path / "README.md"
    readme.write_text("""
# Demo Application

This is a demonstration application for the Fresh autonomous system.

## Features
- TODO: Document main features
- Calculate totals
- Process user data

## Installation
TODO: Add installation instructions

## Usage
FIXME: Update usage examples with current API
""")
    
    console.print(f"📁 Created demo repository at: {repo_path}")
    console.print(f"   • app.py (main code with TODOs and FIXMEs)")
    console.print(f"   • test_app.py (test file with issues)")
    console.print(f"   • README.md (documentation needing updates)")
    console.print()
    
    return repo_path


async def run_demo_with_dashboard(repo_path: Path):
    """Run the demo with dashboard visualization."""
    console.print("🚀 Starting autonomous development loop with dashboard...\n")
    
    # Initialize dev loop with dashboard
    loop = DevLoop(
        repo_path=str(repo_path),
        max_tasks=3,  # Process 3 tasks for demo
        dry_run=False,  # Actually process tasks
        use_dashboard=True,
        state_file=repo_path / ".fresh_state.json"
    )
    
    # Start dashboard
    start_dashboard()
    
    try:
        # Give dashboard time to initialize
        await asyncio.sleep(1)
        
        # Run development cycle
        results = await loop.run_cycle()
        
        # Keep dashboard visible for review
        console.print("\n" * 2)
        console.print("[bold cyan]Dashboard is running. Press Enter to continue...[/bold cyan]")
        input()
        
    finally:
        stop_dashboard()
    
    return results


async def run_demo_simple(repo_path: Path):
    """Run simple demo without dashboard."""
    console.print("🔍 Scanning repository for issues...\n")
    
    # Initialize dev loop
    loop = DevLoop(
        repo_path=str(repo_path),
        max_tasks=5,
        dry_run=True,  # Dry run for simple demo
        use_dashboard=False
    )
    
    # Scan and display tasks
    tasks = loop.scanner.scan()
    
    console.print(f"📋 Found {len(tasks)} issues:\n")
    
    # Group by type
    by_type = {}
    for task in tasks:
        task_type = task.type.value
        if task_type not in by_type:
            by_type[task_type] = []
        by_type[task_type].append(task)
    
    # Display tasks
    for task_type, type_tasks in by_type.items():
        console.print(f"[bold]{task_type}[/bold] ({len(type_tasks)} items):")
        for task in type_tasks[:3]:  # Show first 3 of each type
            console.print(f"  • {task.file_path}:{task.line_number}")
            console.print(f"    [dim]{task.description[:60]}[/dim]")
        if len(type_tasks) > 3:
            console.print(f"    [dim]... and {len(type_tasks) - 3} more[/dim]")
        console.print()
    
    # Simulate processing
    console.print("🤖 [bold]Simulating agent dispatch:[/bold]\n")
    
    for task in tasks[:3]:
        output_type = loop._determine_output_type(task)
        agent_type = loop._determine_agent_type_for_task(task)
        
        console.print(f"Task: [yellow]{task.description[:50]}...[/yellow]")
        console.print(f"  → Agent: [cyan]{agent_type}[/cyan]")
        console.print(f"  → Output: [green]{output_type}[/green]")
        console.print()
        
        # Simulate processing time
        time.sleep(0.5)
    
    console.print("[green]✅ Demo simulation complete![/green]")


async def main():
    """Main demo function."""
    print_welcome()
    
    # Ask user for demo mode
    console.print("[bold]Select demo mode:[/bold]")
    console.print("  1. Simple scan (dry run, no dashboard)")
    console.print("  2. Full demo with dashboard (requires Rich)")
    console.print("  3. Exit")
    console.print()
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "3":
        console.print("Goodbye! 👋")
        return
    
    # Create temporary demo repository
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = create_demo_repository(Path(temp_dir))
        
        if choice == "1":
            await run_demo_simple(repo_path)
        elif choice == "2":
            try:
                results = await run_demo_with_dashboard(repo_path)
                console.print(f"\n[green]✅ Processed {len(results)} tasks successfully![/green]")
            except ImportError:
                console.print("[red]Dashboard requires Rich library. Falling back to simple mode.[/red]")
                await run_demo_simple(repo_path)
        else:
            console.print("[red]Invalid choice[/red]")
    
    console.print("\n[bold cyan]Thank you for trying Fresh![/bold cyan]")
    console.print("Run './fresh scan' on your own repository to get started.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
        sys.exit(0)
