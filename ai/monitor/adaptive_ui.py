from __future__ import annotations
import psutil
from typing import Dict, List, Optional, Any

from ai.utils.clock import now as time_now

from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout

from ai.monitor.activity import ActivityDetection, ActivityLevel, ActivityEvent, get_activity_detector


class RefreshController:
    """Controls adaptive refresh intervals based on activity."""
    
    def __init__(self, min_interval: Optional[float] = None):
        self.min_interval = min_interval
        self.activity_detector = get_activity_detector()
        
    def get_current_interval(self) -> float:
        """Get current recommended refresh interval."""
        interval = self.activity_detector.get_refresh_interval()
        if self.min_interval is None:
            return interval
        return min(interval, self.min_interval) if self.min_interval < interval else interval


class AdaptiveMonitorUI:
    """Modern terminal UI for agent monitoring with adaptive refresh."""
    
    def __init__(self):
        self.console = Console()
        self.live: Optional[Live] = None
        self.refresh_controller = RefreshController()
        
    def _get_activity_color(self, level: ActivityLevel) -> str:
        """Get color for activity level."""
        colors = {
            ActivityLevel.IDLE: "dim",
            ActivityLevel.LOW: "yellow", 
            ActivityLevel.MEDIUM: "blue",
            ActivityLevel.HIGH: "red"
        }
        return colors[level]
        
    def _format_memory(self, bytes_val: int) -> str:
        """Format memory in human-readable units."""
        if bytes_val < 1024:
            return f"{bytes_val} B"
        elif bytes_val < 1024 * 1024:
            return f"{bytes_val / 1024:.1f} KB"
        elif bytes_val < 1024 * 1024 * 1024:
            return f"{bytes_val / (1024 * 1024):.1f} MB"
        else:
            return f"{bytes_val / (1024 * 1024 * 1024):.1f} GB"
            
    def _format_response_time(self, seconds: Optional[float]) -> str:
        """Format response time appropriately."""
        if seconds is None:
            return "-"
        elif seconds < 1.0:
            return f"{int(seconds * 1000)}ms"
        else:
            return f"{seconds:.2f}s"
            
    def _get_agent_health(self, agent_name: str, agent_events: List[ActivityEvent]) -> str:
        """Determine agent health status based on activity and system metrics."""
        try:
            process = psutil.Process()
            cpu_percent = process.cpu_percent()
            
            # Check for recent errors in events
            error_events = [e for e in agent_events if 'error' in e.event_type]
            
            # Health logic
            if error_events:
                return "[red]❌ Error[/red]"
            elif cpu_percent > 80:
                return "[yellow]⚠️ High CPU[/yellow]"
            elif len(agent_events) > 0:
                return "[green]✅ Healthy[/green]"
            else:
                return "[dim]💤 Idle[/dim]"
                
        except Exception:
            return "[dim]❓ Unknown[/dim]"
            
    def _generate_timeline_sparkline(self, events: List[ActivityEvent]) -> str:
        """Generate a simple timeline sparkline from events."""
        if not events:
            return "▁▁▁▁▁"  # Empty sparkline
            
        # Simple representation: more events = higher bars
        event_counts = {}
        now = time_now()
        
        # Group events into 5 time buckets for sparkline
        for event in events:
            bucket = int((now - event.timestamp) / 12)  # 12-second buckets for 1-minute window
            bucket = min(bucket, 4)  # Cap at 5 buckets
            event_counts[bucket] = event_counts.get(bucket, 0) + 1
            
        # Convert to sparkline characters
        chars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        sparkline = ""
        max_count = max(event_counts.values()) if event_counts else 1
        
        for i in range(5):
            count = event_counts.get(4-i, 0)  # Reverse order (recent first)
            if max_count > 0:
                char_idx = min(int((count / max_count) * (len(chars) - 1)), len(chars) - 1)
                sparkline += chars[char_idx]
            else:
                sparkline += chars[0]
                
        return sparkline
        
    def _generate_agent_table(self, status: Dict[str, Any]) -> Table:
        """Generate the main agent status table."""
        table = Table(title="🤖 Agent Swarm Status", title_style="bold magenta")
        
        # Define columns
        table.add_column("Agent", style="cyan", no_wrap=True)
        table.add_column("Status", style="green")
        table.add_column("Activity", justify="center")
        table.add_column("Health", justify="center")
        table.add_column("Memory", justify="right")
        table.add_column("Timeline", justify="center")
        
        detector = get_activity_detector()
        current_level = detector.compute_activity_level()
        
        # Get process info for memory metrics
        process = psutil.Process()
        
        for agent_name in status["agents"]:
            # Determine agent status
            is_in_flow = any(agent_name in flow for flow in status.get("flows", []))
            agent_status = "🔄 Active" if is_in_flow else "⏸️  Standby"
            
            # Get activity level for this agent
            agent_events = [e for e in detector.get_recent_events(20) if e.agent_name == agent_name]
            activity_text = f"{current_level.value.upper()}"
            activity_color = self._get_activity_color(current_level)
            
            # Health check
            health_status = self._get_agent_health(agent_name, agent_events)
            
            # Memory usage (approximate)
            memory_rss = process.memory_info().rss
            memory_text = self._format_memory(memory_rss)
            
            # Timeline sparkline
            timeline = self._generate_timeline_sparkline(agent_events)
            
            table.add_row(
                agent_name,
                agent_status,
                f"[{activity_color}]{activity_text}[/{activity_color}]",
                health_status,
                memory_text,
                timeline
            )
            
        return table
        
    def _generate_info_panel(self, status: Dict[str, Any]) -> Panel:
        """Generate info panel with flows and next steps."""
        detector = get_activity_detector()
        current_level = detector.compute_activity_level()
        refresh_interval = detector.get_refresh_interval()
        
        info_text = []
        info_text.append(f"📊 Activity Level: [{self._get_activity_color(current_level)}]{current_level.value.upper()}[/{self._get_activity_color(current_level)}]")
        info_text.append(f"⏱️  Refresh Interval: {refresh_interval}s")
        info_text.append(f"🔗 Active Flows: {len(status.get('flows', []))}")
        
        if status.get("next_steps"):
            info_text.append("\n📋 Next Steps:")
            for step in status["next_steps"][:3]:  # Show first 3
                info_text.append(f"  • {step}")
                
        content = "\n".join(info_text)
        return Panel(content, title="System Info", border_style="blue")
        
    def update_display(self, status: Dict[str, Any]) -> None:
        """Update the live display with current status."""
        layout = Layout()
        
        # Create main table and info panel
        agent_table = self._generate_agent_table(status)
        info_panel = self._generate_info_panel(status)
        
        # Layout: table on top, info on bottom
        layout.split_column(
            Layout(agent_table, name="agents", ratio=3),
            Layout(info_panel, name="info", ratio=1)
        )
        
        if self.live:
            self.live.update(layout)
        else:
            self.console.print(layout)
            
    def start_live_display(self) -> Live:
        """Start live updating display."""
        if self.live is None:
            self.live = Live(console=self.console, auto_refresh=False)
        return self.live
        
    def stop_live_display(self) -> None:
        """Stop live updating display."""
        if self.live:
            self.live.stop()
            self.live = None
