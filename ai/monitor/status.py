from __future__ import annotations
import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from ai.agency import build_agency
from ai.memory.store import set_memory_store, InMemoryMemoryStore, render_context
from ai.tools.next_steps import GenerateNextSteps
from ai.tools.release_notes import GenerateReleaseNotes
from ai.monitor.cost_tracker import get_cost_tracker


@dataclass
class MonitorStatus:
    agents: List[str]
    flows: List[List[str]]
    memory_context: str
    next_steps: List[str]
    release_notes: str
    cost_summary: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def get_status(limit: int = 10) -> Dict[str, Any]:
    # Use in-memory store for safe readout (does not mutate existing persistent store)
    set_memory_store(InMemoryMemoryStore())

    agency = build_agency()
    agents = [a.name for a in agency.agents]
    # Extract active flows from recent activity events
    flows: List[List[str]] = []
    from ai.monitor.activity import get_activity_detector
    detector = get_activity_detector()
    recent_events = detector.get_recent_events(20)
    
    # Find recent flow events and extract flow pairs
    flow_events = [e for e in recent_events if "flow" in e.event_type and e.details]
    for event in flow_events[-5:]:  # Show last 5 active flows
        if "->" in str(event.details):
            try:
                from_agent, to_agent = event.details.split("->", 1)
                flows.append([from_agent.strip(), to_agent.strip()])
            except ValueError:
                pass  # Skip malformed flow details

    context = render_context(limit=limit)

    steps_md = GenerateNextSteps(limit=3).run()  # type: ignore
    steps = [l[2:] for l in steps_md.splitlines() if l.startswith("- ")]

    notes_md = GenerateReleaseNotes(limit=limit).run()  # type: ignore

    # Get cost monitoring summary
    try:
        cost_tracker = get_cost_tracker()
        cost_summary = {
            "daily": cost_tracker.get_usage_summary(days=1),
            "weekly": cost_tracker.get_usage_summary(days=7),
            "monthly": cost_tracker.get_usage_summary(days=30),
            "budget_alerts_count": len([a for a in cost_tracker.budget_alerts if a.is_enabled]),
            "total_records": len(cost_tracker.usage_records)
        }
    except Exception as e:
        # Fallback if cost tracking fails
        cost_summary = {"error": str(e), "enabled": False}

    status = MonitorStatus(
        agents=agents,
        flows=flows,
        memory_context=context,
        next_steps=steps,
        release_notes=notes_md,
        cost_summary=cost_summary,
    )
    return status.to_dict()


if __name__ == "__main__":
    print(json.dumps(get_status(), indent=2))
