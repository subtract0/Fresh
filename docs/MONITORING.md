# Monitoring & Observability

- Adaptive monitoring: ai/monitor/activity.py
- Execution monitor: ai/execution/monitor.py
- Status coordination: ai/coordination/status.py
- Documentation alignment: ai/system/docs_alignment.py (background service)

Usage:
- `poetry run python scripts/watch-agents-adaptive.py`
- `poetry run python scripts/demo-adaptive-monitor.py`

Documentation Alignment Service
- Purpose: Continuously checks documentation cross-references and stores issues/recoveries in memory
- Managed by: ai/system/coordinator.py as component "docs_alignment"
- Configuration:
  - Env: DOCS_CHECK_ENABLED=true|false (default: true)
  - Env: DOCS_CHECK_INTERVAL_SEC=600 (seconds)
  - File: launch_agent_system.py config section "documentation" with keys enabled, interval_sec

Manual Check
- Run `python scripts/check_docs_alignment.py --strict` (also available via Warp: `fresh::docs::check`)  

