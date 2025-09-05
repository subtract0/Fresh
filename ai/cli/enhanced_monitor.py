#!/usr/bin/env python
"""Enhanced Interactive CLI Monitor for Agent Control

This module provides an advanced command-line interface for monitoring
and controlling different types of AI agents with real-time updates,
interactive controls, and visual feedback.

Features:
- Real-time agent status display
- Interactive controls for different agent types
- Live performance metrics
- Safety alerts and opportunity feed
- Professional terminal UI with Rich library

Usage:
    python -m ai.cli.fresh monitor-enhanced
    
Controls:
    [1] - Autonomous Loop    [2] - Single Scan
    [3] - Product Manager    [4] - Documentation Agent  
    [5] - Custom Spawn       [S] - Stop Current
    [E] - Emergency Stop     [Q] - Quit
"""
from __future__ import annotations

import asyncio
import json
import signal
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List
import subprocess

try:
    from rich.console import Console
    from rich.live import Live
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.columns import Columns
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.align import Align
    from rich.box import ROUNDED
except ImportError:
    print("⚠️ Rich library required: pip install rich")
    sys.exit(1)

from ai.autonomous import AutonomousLoop
from ai.memory.intelligent_store import IntelligentMemoryStore


class AgentStatus:
    """Track status of different agent types"""
    def __init__(self):
        self.agents: Dict[str, Dict[str, Any]] = {
            'autonomous': {'status': 'idle', 'last_cycle': None, 'total_cycles': 0},
            'scanner': {'status': 'idle', 'last_scan': None, 'issues_found': 0},
            'product_manager': {'status': 'idle', 'last_run': None, 'plans_created': 0},
            'documentation': {'status': 'idle', 'last_run': None, 'docs_updated': 0},
            'custom': {'status': 'idle', 'last_spawn': None, 'tasks_completed': 0}
        }
        self.current_operation: Optional[str] = None
        self.emergency_stop = False
        
    def update_agent(self, agent_type: str, status: str, **kwargs):
        """Update agent status"""
        if agent_type in self.agents:
            self.agents[agent_type]['status'] = status
            self.agents[agent_type].update(kwargs)
            
    def get_status_emoji(self, agent_type: str) -> str:
        """Get emoji for agent status"""
        status = self.agents[agent_type]['status']
        return {
            'idle': '😴',
            'running': '🚀', 
            'working': '⚙️',
            'completed': '✅',
            'error': '❌',
            'stopped': '⏹️'
        }.get(status, '❓')


class EnhancedMonitor:
    """Enhanced CLI monitor with interactive controls"""
    
    def __init__(self):
        self.console = Console()
        self.agent_status = AgentStatus()
        self.autonomous_loop: Optional[AutonomousLoop] = None
        self.running = True
        self.last_opportunities = 0
        self.recent_activities: List[str] = []
        self.performance_metrics = {
            'avg_cycle_time': 0,
            'success_rate': 0,
            'opportunities_per_minute': 0,
            'total_improvements': 0
        }
        
    def create_layout(self) -> Layout:
        """Create the main dashboard layout"""
        layout = Layout()
        
        layout.split(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="controls", size=8)
        )
        
        layout["main"].split_row(
            Layout(name="agents", ratio=1),
            Layout(name="activity", ratio=1)
        )
        
        return layout
        
    def create_header(self) -> Panel:
        """Create header with title and current time"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        title = Text("🤖 Fresh Agent Control Dashboard", style="bold blue")
        subtitle = Text(f"Live Monitor • {current_time}", style="dim")
        
        return Panel(
            Align.center(title + "\n" + subtitle),
            border_style="blue",
            box=ROUNDED
        )
        
    def create_agent_panel(self) -> Panel:
        """Create agent status panel"""
        table = Table(show_header=True, header_style="bold magenta", box=ROUNDED)
        table.add_column("Agent Type", style="cyan", width=15)
        table.add_column("Status", width=10)
        table.add_column("Last Activity", style="dim", width=20)
        table.add_column("Metrics", style="green", width=15)
        
        for agent_type, data in self.agent_status.agents.items():
            emoji = self.agent_status.get_status_emoji(agent_type)
            status = f"{emoji} {data['status']}"
            
            # Format last activity
            last_key = next((k for k in data.keys() if k.startswith('last_')), None)
            last_activity = data.get(last_key, 'Never') if last_key else 'Never'
            if last_activity and last_activity != 'Never':
                try:
                    if isinstance(last_activity, str):
                        last_activity = datetime.fromisoformat(last_activity).strftime('%H:%M:%S')
                except:
                    pass
                    
            # Format metrics
            metric_key = next((k for k in data.keys() if k.startswith('total_') or k.endswith('_found') or k.endswith('_created') or k.endswith('_updated') or k.endswith('_completed')), None)
            metrics = str(data.get(metric_key, 0)) if metric_key else "0"
            
            table.add_row(
                agent_type.replace('_', ' ').title(),
                status,
                str(last_activity),
                metrics
            )
            
        return Panel(table, title="🤖 Agent Status", border_style="green")
        
    def create_activity_panel(self) -> Panel:
        """Create activity feed panel"""
        # Performance metrics
        perf_table = Table(show_header=False, box=None, padding=(0, 1))
        perf_table.add_column("Metric", style="cyan")
        perf_table.add_column("Value", style="bold green")
        
        perf_table.add_row("Avg Cycle Time", f"{self.performance_metrics['avg_cycle_time']:.1f}s")
        perf_table.add_row("Success Rate", f"{self.performance_metrics['success_rate']:.1f}%")
        perf_table.add_row("Opportunities", str(self.last_opportunities))
        perf_table.add_row("Total Improvements", str(self.performance_metrics['total_improvements']))
        
        # Recent activities
        activities_text = "\n".join(self.recent_activities[-8:]) if self.recent_activities else "No recent activity"
        
        content = Columns([
            Panel(perf_table, title="📊 Metrics", border_style="blue"),
            Panel(activities_text, title="📝 Recent Activity", border_style="yellow")
        ])
        
        return Panel(content, title="⚡ Live Activity", border_style="magenta")
        
    def create_controls_panel(self) -> Panel:
        """Create controls panel"""
        controls_text = Text()
        controls_text.append("🎮 Agent Controls\n\n", style="bold cyan")
        controls_text.append("[1] Autonomous Loop  ", style="green")
        controls_text.append("[2] Single Scan      ", style="blue")
        controls_text.append("[3] Product Manager\n", style="yellow")
        controls_text.append("[4] Documentation    ", style="magenta")
        controls_text.append("[5] Custom Spawn     ", style="white")
        controls_text.append("[S] Stop Current\n", style="red")
        controls_text.append("[E] Emergency Stop   ", style="bold red")
        controls_text.append("[R] Refresh Status   ", style="cyan")
        controls_text.append("[Q] Quit", style="dim")
        
        current_op = self.agent_status.current_operation
        status_text = f"\n\n🎯 Current: {current_op or 'None'}"
        if self.agent_status.emergency_stop:
            status_text += "\n🚨 EMERGENCY STOP ACTIVE"
            
        controls_text.append(status_text, style="bold")
        
        return Panel(controls_text, title="🎛️ Controls", border_style="cyan")
        
    def add_activity(self, message: str):
        """Add activity to recent activities"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.recent_activities.append(f"[{timestamp}] {message}")
        if len(self.recent_activities) > 20:
            self.recent_activities = self.recent_activities[-20:]
            
    async def start_autonomous_loop(self):
        """Start autonomous improvement loop"""
        try:
            self.agent_status.update_agent('autonomous', 'running')
            self.agent_status.current_operation = 'Autonomous Loop'
            self.add_activity("🚀 Starting autonomous improvement loop")
            
            # Create autonomous loop
            self.autonomous_loop = AutonomousLoop(
                working_directory=".",
                config={
                    'max_improvements_per_cycle': 3,
                    'safety_level': 'high',
                    'scan_interval': 300
                }
            )
            
            # Start continuous loop in background
            def run_loop():
                try:
                    self.autonomous_loop.start_continuous_loop()
                except Exception as e:
                    self.add_activity(f"❌ Autonomous loop error: {str(e)}")
                    self.agent_status.update_agent('autonomous', 'error')
                    
            loop_thread = threading.Thread(target=run_loop, daemon=True)
            loop_thread.start()
            
            self.add_activity("✅ Autonomous loop started successfully")
            
        except Exception as e:
            self.add_activity(f"❌ Failed to start autonomous loop: {str(e)}")
            self.agent_status.update_agent('autonomous', 'error')
            
    async def run_single_scan(self):
        """Run single repository scan"""
        try:
            self.agent_status.update_agent('scanner', 'running')
            self.agent_status.current_operation = 'Repository Scan'
            self.add_activity("🔍 Running repository scan")
            
            # Run scan command
            process = await asyncio.create_subprocess_exec(
                'poetry', 'run', 'python', '-m', 'ai.cli.fresh', 'scan', '.', '--json',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                try:
                    result = json.loads(stdout.decode())
                    total_issues = result.get('total', 0)
                    self.agent_status.update_agent('scanner', 'completed', 
                                                 issues_found=total_issues,
                                                 last_scan=datetime.now().isoformat())
                    self.add_activity(f"✅ Scan completed: {total_issues} issues found")
                except json.JSONDecodeError:
                    self.add_activity("✅ Scan completed (parsing error)")
            else:
                self.add_activity(f"❌ Scan failed: {stderr.decode()}")
                self.agent_status.update_agent('scanner', 'error')
                
            self.agent_status.current_operation = None
            
        except Exception as e:
            self.add_activity(f"❌ Scan error: {str(e)}")
            self.agent_status.update_agent('scanner', 'error')
            self.agent_status.current_operation = None
            
    async def spawn_custom_agent(self):
        """Spawn custom agent"""
        try:
            self.agent_status.update_agent('custom', 'running') 
            self.agent_status.current_operation = 'Custom Agent'
            self.add_activity("🛠️ Spawning custom agent")
            
            # For demo, run a simple task
            process = await asyncio.create_subprocess_exec(
                'poetry', 'run', 'python', '-m', 'ai.cli.fresh', 'spawn', 
                'Analyze code quality and suggest improvements',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                self.agent_status.update_agent('custom', 'completed',
                                             tasks_completed=self.agent_status.agents['custom']['tasks_completed'] + 1,
                                             last_spawn=datetime.now().isoformat())
                self.add_activity("✅ Custom agent completed task")
            else:
                self.add_activity(f"❌ Custom agent failed: {stderr.decode()}")
                self.agent_status.update_agent('custom', 'error')
                
            self.agent_status.current_operation = None
            
        except Exception as e:
            self.add_activity(f"❌ Custom agent error: {str(e)}")
            self.agent_status.update_agent('custom', 'error')
            self.agent_status.current_operation = None
            
    async def stop_current_operation(self):
        """Stop current operation"""
        if self.autonomous_loop and self.autonomous_loop.running:
            self.autonomous_loop.stop_continuous_loop()
            self.add_activity("⏹️ Stopped autonomous loop")
            self.agent_status.update_agent('autonomous', 'stopped')
            
        self.agent_status.current_operation = None
        self.add_activity("⏹️ Stopped current operation")
        
    async def emergency_stop(self):
        """Activate emergency stop"""
        self.agent_status.emergency_stop = True
        self.add_activity("🚨 EMERGENCY STOP ACTIVATED")
        
        if self.autonomous_loop:
            try:
                self.autonomous_loop.safety_controller.emergency_stop("User requested emergency stop")
                self.autonomous_loop.stop_continuous_loop()
            except:
                pass
                
        # Stop all agents
        for agent_type in self.agent_status.agents:
            self.agent_status.update_agent(agent_type, 'stopped')
            
        self.agent_status.current_operation = None
        
    def get_keyboard_input(self) -> Optional[str]:
        """Get non-blocking keyboard input"""
        import select
        import termios
        import tty
        
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.cbreak(sys.stdin.fileno())
            
            if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                return sys.stdin.read(1)
            return None
        except:
            return None
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            
    async def handle_input(self, key: str):
        """Handle keyboard input"""
        key = key.lower()
        
        if key == '1':
            await self.start_autonomous_loop()
        elif key == '2':
            await self.run_single_scan()
        elif key == '3':
            self.agent_status.update_agent('product_manager', 'running')
            self.agent_status.current_operation = 'Product Manager'
            self.add_activity("📋 Product Manager mode activated")
            # Placeholder for product manager logic
            await asyncio.sleep(2)
            self.agent_status.update_agent('product_manager', 'completed')
            self.agent_status.current_operation = None
        elif key == '4':
            self.agent_status.update_agent('documentation', 'running')
            self.agent_status.current_operation = 'Documentation Agent'
            self.add_activity("📚 Documentation agent activated")
            # Placeholder for documentation logic
            await asyncio.sleep(2)
            self.agent_status.update_agent('documentation', 'completed')
            self.agent_status.current_operation = None
        elif key == '5':
            await self.spawn_custom_agent()
        elif key == 's':
            await self.stop_current_operation()
        elif key == 'e':
            await self.emergency_stop()
        elif key == 'r':
            self.add_activity("🔄 Refreshing status")
        elif key == 'q':
            self.running = False
            self.add_activity("👋 Shutting down monitor")
            
    async def run_monitor(self):
        """Run the enhanced monitor"""
        layout = self.create_layout()
        
        self.add_activity("🚀 Enhanced monitor started")
        
        with Live(layout, console=self.console, refresh_per_second=4, screen=True) as live:
            while self.running:
                # Update layout
                layout["header"].update(self.create_header())
                layout["agents"].update(self.create_agent_panel())
                layout["activity"].update(self.create_activity_panel())
                layout["controls"].update(self.create_controls_panel())
                
                # Handle keyboard input (non-blocking)
                try:
                    key = self.get_keyboard_input()
                    if key:
                        await self.handle_input(key)
                except:
                    pass
                    
                # Update metrics periodically
                if hasattr(self, 'autonomous_loop') and self.autonomous_loop:
                    try:
                        status = self.autonomous_loop.get_status()
                        self.performance_metrics['total_improvements'] = status.get('total_cycles', 0)
                        if status.get('recent_cycles'):
                            # Calculate average cycle time from recent cycles
                            recent = status['recent_cycles'][-5:]  # Last 5 cycles
                            if recent:
                                avg_time = sum(c.get('duration_seconds', 0) for c in recent) / len(recent)
                                self.performance_metrics['avg_cycle_time'] = avg_time
                    except:
                        pass
                
                await asyncio.sleep(0.25)  # 4 FPS update rate
                
        # Cleanup
        if self.autonomous_loop and self.autonomous_loop.running:
            self.autonomous_loop.stop_continuous_loop()


async def run_enhanced_monitor():
    """Main entry point for enhanced monitor"""
    monitor = EnhancedMonitor()
    
    # Setup signal handlers
    def signal_handler(signum, frame):
        monitor.running = False
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await monitor.run_monitor()
    except KeyboardInterrupt:
        pass
    finally:
        print("\n👋 Enhanced monitor stopped")


if __name__ == "__main__":
    asyncio.run(run_enhanced_monitor())
