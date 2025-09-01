"""
Cost Monitoring Dashboard

Interactive dashboard for monitoring API costs, usage patterns, and budget management.
Built using Rich for terminal UI with real-time updates.

Features:
- Real-time cost and usage display
- Service breakdown (Firestore, OpenAI, Google APIs)
- Budget management and alerts
- Historical usage charts
- Cost optimization recommendations
- Export capabilities
"""
from __future__ import annotations
import os
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.tree import Tree
from rich import box
from rich.markdown import Markdown

from ai.monitor.cost_tracker import get_cost_tracker, ServiceType, BudgetAlert

logger = logging.getLogger(__name__)


class CostDashboard:
    """Interactive cost monitoring dashboard."""
    
    def __init__(self):
        self.console = Console()
        self.cost_tracker = get_cost_tracker()
        self._running = False
        self._refresh_interval = 5.0  # seconds
        
    def create_layout(self) -> Layout:
        """Create the dashboard layout."""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        layout["left"].split_column(
            Layout(name="current_usage", ratio=2),
            Layout(name="service_breakdown", ratio=2),
            Layout(name="budget_status", ratio=1)
        )
        
        layout["right"].split_column(
            Layout(name="recent_activity", ratio=2),
            Layout(name="optimization", ratio=1),
            Layout(name="controls", ratio=1)
        )
        
        return layout
        
    def create_header(self) -> Panel:
        """Create dashboard header."""
        title = Text("💰 Fresh AI Cost Monitoring Dashboard", style="bold blue")
        timestamp = Text(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", style="dim")
        
        header_text = Text.assemble(title, "\\n", timestamp)
        return Panel(header_text, box=box.ROUNDED)
        
    def create_current_usage_panel(self) -> Panel:
        """Create current usage summary panel."""
        # Get current month usage
        now = datetime.now()
        monthly_usage = self.cost_tracker.get_monthly_usage(now.year, now.month)
        weekly_usage = self.cost_tracker.get_usage_summary(days=7)
        daily_usage = self.cost_tracker.get_usage_summary(days=1)
        
        table = Table(title="Current Usage", box=box.MINIMAL_DOUBLE_HEAD)
        table.add_column("Period", style="cyan", no_wrap=True)
        table.add_column("Operations", justify="right", style="green")
        table.add_column("Cost (USD)", justify="right", style="yellow")
        
        table.add_row(
            "Today",
            str(daily_usage["total_operations"]),
            f"${daily_usage['total_cost_usd']:.4f}"
        )
        table.add_row(
            "This Week", 
            str(weekly_usage["total_operations"]),
            f"${weekly_usage['total_cost_usd']:.4f}"
        )
        table.add_row(
            "This Month",
            str(monthly_usage["total_operations"]),
            f"${monthly_usage['total_cost_usd']:.4f}"
        )
        
        return Panel(table, title="📊 Usage Summary", border_style="blue")
        
    def create_service_breakdown_panel(self) -> Panel:
        """Create service breakdown panel."""
        usage_summary = self.cost_tracker.get_usage_summary(days=30)
        
        table = Table(title="Service Breakdown (30 days)", box=box.MINIMAL_DOUBLE_HEAD)
        table.add_column("Service", style="cyan", no_wrap=True)
        table.add_column("Operations", justify="right", style="green")
        table.add_column("Quantity", justify="right", style="blue")
        table.add_column("Cost (USD)", justify="right", style="yellow")
        table.add_column("Percentage", justify="right", style="magenta")
        
        total_cost = usage_summary["total_cost_usd"]
        
        for service_name, service_data in usage_summary["service_breakdown"].items():
            percentage = (service_data["cost"] / max(total_cost, 0.0001)) * 100
            
            # Format service name
            service_display = {
                "firestore": "🔥 Firestore",
                "openai": "🤖 OpenAI",
                "google_api": "🌐 Google APIs"
            }.get(service_name, service_name.title())
            
            table.add_row(
                service_display,
                str(service_data["operations"]),
                str(service_data["quantity"]),
                f"${service_data['cost']:.4f}",
                f"{percentage:.1f}%"
            )
        
        return Panel(table, title="🔧 Service Breakdown", border_style="green")
        
    def create_budget_status_panel(self) -> Panel:
        """Create budget status panel."""
        current_month = datetime.now()
        monthly_usage = self.cost_tracker.get_monthly_usage(current_month.year, current_month.month)
        current_usage = monthly_usage["total_cost_usd"]
        
        if not self.cost_tracker.budget_alerts:
            content = Text("No budget alerts configured", style="dim")
            return Panel(content, title="💸 Budget Status", border_style="yellow")
        
        table = Table(box=box.MINIMAL)
        table.add_column("Budget", style="cyan")
        table.add_column("Used", style="yellow")
        table.add_column("Remaining", style="green")
        table.add_column("Status", style="bold")
        
        for alert in self.cost_tracker.budget_alerts:
            if not alert.is_enabled:
                continue
                
            # Calculate usage for this alert
            if alert.service:
                alert_usage = sum(
                    r.estimated_cost_usd for r in self.cost_tracker.usage_records
                    if (r.service == alert.service and
                        r.timestamp.year == current_month.year and
                        r.timestamp.month == current_month.month)
                )
            else:
                alert_usage = current_usage
                
            remaining = max(alert.monthly_limit_usd - alert_usage, 0)
            usage_percentage = (alert_usage / alert.monthly_limit_usd) * 100
            
            # Status styling
            if usage_percentage >= alert.threshold_percentage * 100:
                status = "🚨 ALERT"
                status_style = "red"
            elif usage_percentage >= 70:
                status = "⚠️ WARNING" 
                status_style = "yellow"
            else:
                status = "✅ OK"
                status_style = "green"
                
            service_name = alert.service.value if alert.service else "Total"
            
            table.add_row(
                f"{service_name}: ${alert.monthly_limit_usd:.2f}",
                f"${alert_usage:.2f} ({usage_percentage:.1f}%)",
                f"${remaining:.2f}",
                Text(status, style=status_style)
            )
        
        return Panel(table, title="💸 Budget Status", border_style="yellow")
        
    def create_recent_activity_panel(self) -> Panel:
        """Create recent activity panel."""
        recent_records = self.cost_tracker.usage_records[-10:] if self.cost_tracker.usage_records else []
        
        if not recent_records:
            content = Text("No recent activity", style="dim")
            return Panel(content, title="🕐 Recent Activity", border_style="cyan")
        
        table = Table(box=box.MINIMAL)
        table.add_column("Time", style="dim", max_width=8)
        table.add_column("Service", style="cyan", max_width=10)
        table.add_column("Operation", style="green", max_width=12)
        table.add_column("Quantity", justify="right", style="blue", max_width=8)
        table.add_column("Cost", justify="right", style="yellow", max_width=10)
        
        for record in reversed(recent_records):
            service_icon = {
                ServiceType.FIRESTORE: "🔥",
                ServiceType.OPENAI: "🤖", 
                ServiceType.GOOGLE_API: "🌐"
            }.get(record.service, "📡")
            
            table.add_row(
                record.timestamp.strftime("%H:%M:%S"),
                f"{service_icon} {record.service.value}",
                record.operation.value,
                str(record.quantity),
                f"${record.estimated_cost_usd:.4f}"
            )
        
        return Panel(table, title="🕐 Recent Activity", border_style="cyan")
        
    def create_optimization_panel(self) -> Panel:
        """Create cost optimization recommendations panel."""
        suggestions = self.cost_tracker.get_optimization_suggestions()
        
        if not suggestions:
            content = Text("✅ No optimization suggestions at this time", style="green")
            return Panel(content, title="🚀 Optimization", border_style="green")
        
        content_lines = []
        for i, suggestion in enumerate(suggestions[:3], 1):  # Show top 3
            content_lines.append(f"{i}. {suggestion}")
        
        content = Text("\\n".join(content_lines), style="yellow")
        return Panel(content, title="🚀 Cost Optimization", border_style="yellow")
        
    def create_controls_panel(self) -> Panel:
        """Create controls panel."""
        controls = [
            "Press 'q' to quit",
            "Press 'r' to refresh",
            "Press 'b' to manage budgets",
            "Press 'e' to export report",
            "Press 'h' for help"
        ]
        
        content = Text("\\n".join(controls), style="dim")
        return Panel(content, title="🎮 Controls", border_style="white")
        
    def create_footer(self) -> Panel:
        """Create dashboard footer."""
        total_records = len(self.cost_tracker.usage_records)
        data_dir = self.cost_tracker.data_dir
        
        footer_text = Text.assemble(
            ("Fresh AI Cost Monitor", "bold"),
            " • ",
            (f"{total_records} records", "cyan"),
            " • ",
            (f"Data: {data_dir}", "dim"),
            " • ",
            ("Auto-refresh: ON", "green")
        )
        
        return Panel(footer_text, box=box.ROUNDED)
        
    async def update_layout(self, layout: Layout):
        """Update all dashboard panels."""
        try:
            layout["header"].update(self.create_header())
            layout["current_usage"].update(self.create_current_usage_panel())
            layout["service_breakdown"].update(self.create_service_breakdown_panel())
            layout["budget_status"].update(self.create_budget_status_panel())
            layout["recent_activity"].update(self.create_recent_activity_panel())
            layout["optimization"].update(self.create_optimization_panel())
            layout["controls"].update(self.create_controls_panel())
            layout["footer"].update(self.create_footer())
        except Exception as e:
            logger.error(f"Failed to update dashboard layout: {e}")
            
    async def run_dashboard(self):
        """Run the interactive dashboard."""
        layout = self.create_layout()
        
        self.console.print("[bold blue]Starting Fresh AI Cost Monitoring Dashboard...[/]")
        await asyncio.sleep(1)
        
        try:
            with Live(layout, refresh_per_second=1, console=self.console) as live:
                self._running = True
                
                while self._running:
                    await self.update_layout(layout)
                    await asyncio.sleep(self._refresh_interval)
                    
        except KeyboardInterrupt:
            self.console.print("\\n[yellow]Dashboard stopped by user[/]")
            self._running = False
        except Exception as e:
            self.console.print(f"\\n[red]Dashboard error: {e}[/]")
            logger.error(f"Dashboard error: {e}")
            
    def stop_dashboard(self):
        """Stop the dashboard."""
        self._running = False
        
    def show_budget_management(self):
        """Show budget management interface."""
        self.console.print("\\n[bold blue]Budget Management[/]")
        self.console.print("=" * 50)
        
        # Show current budgets
        if self.cost_tracker.budget_alerts:
            table = Table(title="Current Budget Alerts", box=box.ROUNDED)
            table.add_column("Service", style="cyan")
            table.add_column("Monthly Limit", justify="right", style="yellow")
            table.add_column("Threshold", justify="right", style="blue")
            table.add_column("Status", style="green")
            
            for i, alert in enumerate(self.cost_tracker.budget_alerts):
                service_name = alert.service.value if alert.service else "Total"
                status = "Enabled" if alert.is_enabled else "Disabled"
                
                table.add_row(
                    service_name,
                    f"${alert.monthly_limit_usd:.2f}",
                    f"{alert.threshold_percentage * 100:.0f}%",
                    status
                )
                
            self.console.print(table)
        else:
            self.console.print("[dim]No budget alerts configured[/]")
            
        self.console.print("\\n[dim]Tip: Use the cost tracker API to add budget alerts programmatically[/]")
        
    def export_report(self, filepath: Optional[str] = None) -> str:
        """Export cost report."""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"cost_report_{timestamp}.json"
            
        self.cost_tracker.export_usage_report(filepath)
        
        self.console.print(f"\\n[green]✅ Report exported to: {filepath}[/]")
        return filepath
        
    def show_detailed_usage(self, days: int = 30):
        """Show detailed usage breakdown."""
        usage = self.cost_tracker.get_usage_summary(days=days)
        
        self.console.print(f"\\n[bold blue]Detailed Usage Report ({days} days)[/]")
        self.console.print("=" * 60)
        
        # Top expensive operations
        self.console.print("\\n[bold yellow]Top Expensive Operations:[/]")
        for i, (op_name, op_data) in enumerate(usage["top_expensive_operations"][:5], 1):
            self.console.print(f"  {i}. {op_name}: ${op_data['cost']:.4f} ({op_data['operations']} ops)")
            
        # Service breakdown
        self.console.print("\\n[bold yellow]Service Breakdown:[/]")
        for service, data in usage["service_breakdown"].items():
            percentage = (data["cost"] / max(usage["total_cost_usd"], 0.0001)) * 100
            self.console.print(f"  {service}: ${data['cost']:.4f} ({percentage:.1f}%)")
            
        return usage


def run_cost_dashboard():
    """Run the cost monitoring dashboard."""
    dashboard = CostDashboard()
    
    try:
        asyncio.run(dashboard.run_dashboard())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Dashboard failed: {e}")


def quick_cost_summary():
    """Show a quick cost summary without full dashboard."""
    console = Console()
    cost_tracker = get_cost_tracker()
    
    console.print("[bold blue]💰 Quick Cost Summary[/]")
    console.print("=" * 40)
    
    # Current usage
    daily = cost_tracker.get_usage_summary(days=1)
    weekly = cost_tracker.get_usage_summary(days=7)
    monthly = cost_tracker.get_usage_summary(days=30)
    
    table = Table(box=box.ROUNDED)
    table.add_column("Period", style="cyan")
    table.add_column("Operations", justify="right", style="green")
    table.add_column("Cost (USD)", justify="right", style="yellow")
    
    table.add_row("Today", str(daily["total_operations"]), f"${daily['total_cost_usd']:.4f}")
    table.add_row("This Week", str(weekly["total_operations"]), f"${weekly['total_cost_usd']:.4f}")
    table.add_row("This Month", str(monthly["total_operations"]), f"${monthly['total_cost_usd']:.4f}")
    
    console.print(table)
    
    # Optimization suggestions
    suggestions = cost_tracker.get_optimization_suggestions()
    if suggestions:
        console.print("\\n[bold yellow]💡 Optimization Suggestions:[/]")
        for i, suggestion in enumerate(suggestions[:3], 1):
            console.print(f"  {i}. {suggestion}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        quick_cost_summary()
    else:
        run_cost_dashboard()
