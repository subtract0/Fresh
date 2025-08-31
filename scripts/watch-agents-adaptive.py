#!/usr/bin/env python3
"""
Adaptive agent monitoring with rich UI and dynamic refresh intervals.
Replaces the old static monitoring with activity-based refresh rates.
"""
from __future__ import annotations
import argparse
import signal
import sys
import time
from contextlib import contextmanager

from rich.console import Console
from rich.live import Live

from ai.monitor.status import get_status
from ai.monitor.adaptive_ui import AdaptiveMonitorUI, RefreshController


class AdaptiveWatcher:
    """Main class for adaptive agent monitoring."""
    
    def __init__(self, min_interval: float = 0.5, max_interval: float = 30.0):
        self.min_interval = min_interval
        self.max_interval = max_interval
        self.ui = AdaptiveMonitorUI()
        self.refresh_controller = RefreshController(min_interval=min_interval)
        self.running = True
        
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully."""
        self.running = False
        
    @contextmanager
    def _setup_signal_handler(self):
        """Context manager for signal handling."""
        old_handler = signal.signal(signal.SIGINT, self._signal_handler)
        try:
            yield
        finally:
            signal.signal(signal.SIGINT, old_handler)
            
    def run(self):
        """Main monitoring loop with adaptive refresh."""
        console = Console()
        
        try:
            with self._setup_signal_handler():
                with Live(console=console, auto_refresh=False, screen=True) as live:
                    self.ui.live = live
                    
                    while self.running:
                        # Get current status
                        status = get_status(limit=10)
                        
                        # Update display
                        self.ui.update_display(status)
                        live.refresh()
                        
                        # Get adaptive refresh interval
                        interval = self.refresh_controller.get_current_interval()
                        interval = max(min(interval, self.max_interval), self.min_interval)
                        
                        # Sleep with interrupt checking
                        start_time = time.time()
                        while time.time() - start_time < interval and self.running:
                            time.sleep(0.1)  # Check every 100ms for interrupts
                            
        except KeyboardInterrupt:
            pass  # Graceful shutdown
        finally:
            console.print("\n👋 Agent monitoring stopped.")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Adaptive Agent Monitoring")
    parser.add_argument(
        "--min-interval", 
        type=float, 
        default=0.5,
        help="Minimum refresh interval in seconds (default: 0.5)"
    )
    parser.add_argument(
        "--max-interval",
        type=float,
        default=30.0,
        help="Maximum refresh interval in seconds (default: 30.0)"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="Adaptive Agent Monitor v1.0 (ADR-005)"
    )
    
    args = parser.parse_args()
    
    watcher = AdaptiveWatcher(
        min_interval=args.min_interval,
        max_interval=args.max_interval
    )
    
    watcher.run()


if __name__ == "__main__":
    main()
