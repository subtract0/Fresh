"""Real-time console dashboard for monitoring agent activity.

This module provides a rich terminal interface for visualizing
the autonomous development loop in real-time.

Cross-references:
    - Development Loop: ai/loop/dev_loop.py
    - Mother Agent: ai/agents/mother.py
    - ADR-008: Autonomous Development Loop Architecture
"""
from __future__ import annotations
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.text import Text
from rich.align import Align

from ai.loop.repo_scanner import Task, TaskType
from ai.agents.mother import AgentResult


@dataclass
class DashboardState:
    """Current state of the dashboard."""
    current_task: Optional[Task] = None
    active_agent: Optional[str] = None
    tasks_found: int = 0
    tasks_processed: int = 0
    tasks_failed: int = 0
    recent_results: List[AgentResult] = field(default_factory=list)
    scan_in_progress: bool = False
    start_time: datetime = field(default_factory=datetime.now)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.tasks_processed == 0:
            return 0.0
        return (self.tasks_processed - self.tasks_failed) / self.tasks_processed * 100


class ConsoleDashboard:
    """Rich console dashboard for agent monitoring."""
    
    def __init__(self):
        """Initialize dashboard."""
        self.console = Console()
        self.state = DashboardState()
        self.live = None
        
    def start(self) -> None:
        """Start the live dashboard."""
        self.live = Live(
            self._generate_layout(),
            console=self.console,
            refresh_per_second=2,
            screen=True
        )
        self.live.start()
        
    def stop(self) -> None:
        """Stop the live dashboard."""
        if self.live:
            self.live.stop()
            
    def update_scan_status(self, scanning: bool, tasks_found: int = 0) -> None:
        """Update scan status."""
        self.state.scan_in_progress = scanning
        if tasks_found > 0:
            self.state.tasks_found = tasks_found
        if self.live:
            self.live.update(self._generate_layout())
            
    def update_task_progress(self, task: Optional[Task], agent: Optional[str] = None) -> None:
        """Update current task being processed."""
        self.state.current_task = task
        self.state.active_agent = agent
        if self.live:
            self.live.update(self._generate_layout())
            
    def add_result(self, result: AgentResult) -> None:
        """Add a completed result."""
        self.state.recent_results.insert(0, result)
        # Keep only last 10 results
        self.state.recent_results = self.state.recent_results[:10]
        
        self.state.tasks_processed += 1
        if not result.success:
            self.state.tasks_failed += 1
            
        if self.live:
            self.live.update(self._generate_layout())
    
    def _generate_layout(self) -> Layout:
        """Generate the dashboard layout."""
        layout = Layout()
        
        # Create main sections
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        # Split body into columns
        layout["body"].split_row(
            Layout(name="status", ratio=1),
            Layout(name="results", ratio=2)
        )
        
        # Populate sections
        layout["header"].update(self._make_header())
        layout["status"].update(self._make_status_panel())
        layout["results"].update(self._make_results_panel())
        layout["footer"].update(self._make_footer())
        
        return layout
    
    def _make_header(self) -> Panel:
        """Create header panel."""
        elapsed = datetime.now() - self.state.start_time
        elapsed_str = str(elapsed).split('.')[0]
        
        header_text = Text()
        header_text.append("🤖 ", style="bold cyan")
        header_text.append("Fresh Autonomous Development Loop", style="bold white")
        header_text.append(f"  |  Runtime: {elapsed_str}", style="dim")
        
        return Panel(
            Align.center(header_text),
            style="bold blue",
            border_style="blue"
        )
    
    def _make_status_panel(self) -> Panel:
        """Create status panel."""
        table = Table(show_header=False, expand=True, box=None)
        table.add_column("Label", style="cyan")
        table.add_column("Value", style="white")
        
        # Add status rows
        if self.state.scan_in_progress:
            table.add_row("🔍 Status:", "[yellow]Scanning...[/yellow]")
        elif self.state.current_task:
            table.add_row("⚡ Status:", "[green]Processing[/green]")
        else:
            table.add_row("💤 Status:", "[dim]Idle[/dim]")
            
        table.add_row("📊 Found:", str(self.state.tasks_found))
        table.add_row("✅ Processed:", str(self.state.tasks_processed))
        table.add_row("❌ Failed:", str(self.state.tasks_failed))
        table.add_row(
            "📈 Success Rate:", 
            f"{self.state.success_rate:.1f}%"
        )
        
        if self.state.current_task:
            table.add_row("", "")  # Spacer
            table.add_row("📋 Current Task:", "")
            task_desc = self.state.current_task.description[:40]
            if len(self.state.current_task.description) > 40:
                task_desc += "..."
            table.add_row("", f"[yellow]{task_desc}[/yellow]")
            table.add_row(
                "🤖 Agent:", 
                f"[cyan]{self.state.active_agent or 'Dispatching...'}[/cyan]"
            )
        
        return Panel(
            table,
            title="📊 Status",
            border_style="green"
        )
    
    def _make_results_panel(self) -> Panel:
        """Create results panel."""
        table = Table(expand=True)
        table.add_column("Time", style="dim", width=8)
        table.add_column("Agent", style="cyan", width=12)
        table.add_column("Task", style="white")
        table.add_column("Status", justify="center", width=10)
        
        for result in self.state.recent_results:
            time_str = result.timestamp.strftime("%H:%M:%S")
            task_desc = result.instructions[:50]
            if len(result.instructions) > 50:
                task_desc += "..."
                
            status = "✅ Done" if result.success else "❌ Failed"
            status_style = "green" if result.success else "red"
            
            table.add_row(
                time_str,
                result.agent_type,
                task_desc,
                f"[{status_style}]{status}[/{status_style}]"
            )
        
        if not self.state.recent_results:
            table.add_row("", "", "[dim]No results yet[/dim]", "")
        
        return Panel(
            table,
            title="📜 Recent Activity",
            border_style="blue"
        )
    
    def _make_footer(self) -> Panel:
        """Create footer panel."""
        footer_text = Text()
        footer_text.append("Commands: ", style="dim")
        footer_text.append("Ctrl+C", style="bold yellow")
        footer_text.append(" to stop  |  ", style="dim")
        footer_text.append("fresh run --watch", style="bold cyan")
        footer_text.append(" for continuous mode", style="dim")
        
        return Panel(
            Align.center(footer_text),
            style="dim",
            border_style="dim"
        )


# Global dashboard instance
_dashboard: Optional[ConsoleDashboard] = None


def get_dashboard() -> ConsoleDashboard:
    """Get or create the global dashboard instance."""
    global _dashboard
    if _dashboard is None:
        _dashboard = ConsoleDashboard()
    return _dashboard


def start_dashboard() -> None:
    """Start the dashboard."""
    dashboard = get_dashboard()
    dashboard.start()


def stop_dashboard() -> None:
    """Stop the dashboard."""
    dashboard = get_dashboard()
    dashboard.stop()


def update_scan_status(scanning: bool, tasks_found: int = 0) -> None:
    """Update scan status on dashboard."""
    dashboard = get_dashboard()
    dashboard.update_scan_status(scanning, tasks_found)


def update_task_progress(task: Optional[Task], agent: Optional[str] = None) -> None:
    """Update task progress on dashboard."""
    dashboard = get_dashboard()
    dashboard.update_task_progress(task, agent)


def add_result(result: AgentResult) -> None:
    """Add result to dashboard."""
    dashboard = get_dashboard()
    dashboard.add_result(result)
