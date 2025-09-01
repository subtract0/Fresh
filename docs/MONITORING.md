# Monitoring & Observability

- Adaptive monitoring: ai/monitor/activity.py
- Execution monitor: ai/execution/monitor.py
- Status coordination: ai/coordination/status.py
- Documentation alignment: ai/system/docs_alignment.py (background service)

Usage:
- `poetry run python scripts/watch-agents-adaptive.py`
- `poetry run python scripts/demo-adaptive-monitor.py`

Persistent Event Bus (cross-process visibility)
- New: ai/monitor/event_bus.py provides a lightweight JSONL event bus at .monitor/events.jsonl
- Writing: set MONITOR_PERSIST_EVENTS=1 in any process that emits activity (e.g., demos, agents)
- Reading: watcher defaults to MONITOR_READ_PERSIST=1 so it sees events from other processes
- This prevents “IDLE” displays when activity happens in a different terminal/session

Documentation Alignment Service
- Purpose: Continuously checks documentation cross-references and stores issues/recoveries in memory
- Managed by: ai/system/coordinator.py as component "docs_alignment"
- Configuration:
  - Env: DOCS_CHECK_ENABLED=true|false (default: true)
  - Env: DOCS_CHECK_INTERVAL_SEC=600 (seconds)
  - File: launch_agent_system.py config section "documentation" with keys enabled, interval_sec

Manual Check
- Run `python scripts/check_docs_alignment.py --strict` (also available via Warp: `fresh::docs::check`)  

