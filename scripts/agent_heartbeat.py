#!/usr/bin/env python3
"""
Agent Heartbeat

Emits low-rate monitoring events periodically so the adaptive monitor reflects
that the system is alive, even when no long-running agents are executing.

- Cross-process visible via persistent event bus when MONITOR_PERSIST_EVENTS=1
- Safe and non-interactive; default interval 30s

Usage:
  MONITOR_PERSIST_EVENTS=1 poetry run python scripts/agent_heartbeat.py --agent Father --interval 20
"""
from __future__ import annotations
import argparse
import time

from ai.monitor.activity import record_agent_activity, record_memory_operation


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit periodic monitoring heartbeats")
    parser.add_argument("--agent", default="Heartbeat", help="Agent name to attribute events to")
    parser.add_argument("--interval", type=float, default=30.0, help="Seconds between heartbeats")
    args = parser.parse_args()

    while True:
        # Emit a small set of events
        record_agent_activity("start", args.agent)
        record_memory_operation("read", args.agent)
        record_agent_activity("complete", args.agent)
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
