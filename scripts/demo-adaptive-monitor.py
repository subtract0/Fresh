#!/usr/bin/env python3
"""
Demo of the adaptive monitoring system with simulated agent activity.
Shows the Rich UI with activity-based refresh rates in action.
"""
from __future__ import annotations
import asyncio
import sys
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rich.console import Console
from rich.live import Live

from ai.monitor.activity import record_memory_operation, record_agent_activity, record_flow_activity
from ai.monitor.status import get_status
from ai.monitor.adaptive_ui import AdaptiveMonitorUI


def simulate_agent_activity():
    """Simulate realistic agent activity patterns."""
    console = Console()
    console.print("🤖 [bold]Simulating Agent Activity[/bold]")
    
    # Phase 1: Idle state
    console.print("📊 Phase 1: [dim]IDLE state[/dim] (10s intervals)")
    time.sleep(1)
    
    # Phase 2: Low activity
    console.print("📊 Phase 2: [yellow]LOW activity[/yellow] (5s intervals)")
    record_memory_operation('read', 'Father')
    record_agent_activity('start', 'Father')
    time.sleep(1)
    
    # Phase 3: Medium activity  
    console.print("📊 Phase 3: [blue]MEDIUM activity[/blue] (2s intervals)")
    record_memory_operation('read', 'Architect')
    record_memory_operation('write', 'Father')
    record_agent_activity('start', 'Architect')
    record_agent_activity('start', 'Developer')
    time.sleep(1)
    
    # Phase 4: High activity
    console.print("📊 Phase 4: [red]HIGH activity[/red] (1s intervals)")
    record_flow_activity('start', 'Father', 'Architect')
    record_memory_operation('write', 'Architect')
    record_memory_operation('write', 'Developer')
    record_agent_activity('complete', 'Father')
    time.sleep(1)
    
    console.print("✅ Activity simulation complete")


def demo_static_display():
    """Show a single snapshot of the monitoring display."""
    console = Console()
    console.print("\n🎯 [bold]Static Display Demo[/bold]")
    
    # Simulate some activity first
    record_memory_operation('write', 'Father')
    record_memory_operation('read', 'Architect') 
    record_agent_activity('start', 'Developer')
    
    # Get status and display
    ui = AdaptiveMonitorUI()
    status = get_status(limit=10)
    
    console.print("📊 Current Agent Status:")
    ui.update_display(status)
    
    return status


def demo_live_monitoring(duration: int = 15):
    """Demo the live monitoring with adaptive refresh."""
    console = Console()
    console.print(f"\n🔴 [bold]Live Monitoring Demo[/bold] ({duration}s)")
    console.print("Press Ctrl+C to stop early")
    
    ui = AdaptiveMonitorUI()
    
    try:
        with Live(console=console, auto_refresh=False, screen=False) as live:
            ui.live = live
            
            start_time = time.time()
            iteration = 0
            
            while time.time() - start_time < duration:
                iteration += 1
                
                # Simulate varying activity every few iterations
                if iteration % 3 == 0:
                    record_memory_operation('read', f'Agent{iteration % 5}')
                if iteration % 5 == 0:
                    record_agent_activity('start', f'Agent{iteration % 3}')
                if iteration % 10 == 0:
                    record_flow_activity('start', 'Father', 'Architect')
                
                # Get current status and update display
                status = get_status(limit=5)
                ui.update_display(status)
                live.refresh()
                
                # Use adaptive refresh interval
                interval = ui.refresh_controller.get_current_interval()
                time.sleep(min(interval, 2.0))  # Cap at 2s for demo
                
    except KeyboardInterrupt:
        console.print("\n👋 Demo stopped by user")
        
    console.print("\n✅ Live monitoring demo complete")


def main():
    """Main demo script."""
    console = Console()
    console.print("🎯 [bold cyan]Adaptive Agent Monitoring Demo[/bold cyan]")
    console.print("Demonstrates ADR-005 implementation\n")
    
    # Show static snapshot first
    status = demo_static_display()
    
    # Show activity simulation
    print()
    simulate_agent_activity() 
    
    # Ask user if they want live demo
    print()
    try:
        response = input("🔴 Run live monitoring demo? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            demo_live_monitoring(duration=20)
        else:
            console.print("👋 Demo complete")
    except KeyboardInterrupt:
        console.print("\n👋 Demo cancelled")


if __name__ == "__main__":
    main()
