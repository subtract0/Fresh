from __future__ import annotations
import os
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from ai.utils.clock import now as time_now
try:
    from ai.monitor.event_bus import get_bus
except Exception:
    # Fallback if event bus is unavailable for any reason
    def get_bus():  # type: ignore
        class _Nop:
            def append(self, *_args, **_kwargs):
                pass
            def read_recent(self, *_args, **_kwargs):
                return []
        return _Nop()


class ActivityLevel(Enum):
    """Agent activity levels for adaptive monitoring refresh rates."""
    IDLE = "idle"       # No flows, no memory writes: 10s intervals
    LOW = "low"         # Occasional memory reads, single agent: 5s intervals
    MEDIUM = "medium"   # Multiple agents active, memory writes: 2s intervals
    HIGH = "high"       # Active flows, rapid operations: 1s intervals


@dataclass
class ActivityEvent:
    """Single activity event with timestamp and type."""
    timestamp: float
    event_type: str  # memory_read, memory_write, agent_start, agent_complete, flow_start, flow_end
    agent_name: Optional[str] = None
    details: Optional[str] = None


@dataclass
class AgentMetrics:
    """Performance metrics for a single agent."""
    name: str
    memory_rss: int  # bytes
    last_response_time: float  # seconds
    activity_count: int  # events in current window
    last_activity: Optional[float] = None  # timestamp


class ActivityDetection:
    """Detects agent activity levels for adaptive monitoring."""
    
    def __init__(self, window_seconds: int = 60):
        self.window_seconds = window_seconds
        self.events: deque[ActivityEvent] = deque()
        self.agent_metrics: Dict[str, AgentMetrics] = {}
        self._persist_write = os.getenv("MONITOR_PERSIST_EVENTS", "0") in ("1", "true", "True")
        self._persist_read_default = True  # default to read if bus file exists
        
    def record_event(self, event_type: str, agent_name: Optional[str] = None, details: Optional[str] = None) -> None:
        """Record an activity event (and optionally persist)."""
        event = ActivityEvent(
            timestamp=time_now(),
            event_type=event_type,
            agent_name=agent_name,
            details=details
        )
        self.events.append(event)
        self._cleanup_old_events()
        
        # Optional persistence for cross-process visibility
        try:
            if self._persist_write:
                get_bus().append({
                    "timestamp": event.timestamp,
                    "event_type": event.event_type,
                    "agent_name": event.agent_name,
                    "details": event.details,
                })
        except Exception:
            pass
        
    def _cleanup_old_events(self) -> None:
        """Remove events older than the window."""
        cutoff = time_now() - self.window_seconds
        while self.events and self.events[0].timestamp < cutoff:
            self.events.popleft()
            
    def compute_activity_level(self) -> ActivityLevel:
        """Compute current activity level based on recent events.
        If a persistent bus exists and MONITOR_READ_PERSIST is enabled (or default),
        incorporate recent persisted events for computation.
        """
        self._cleanup_old_events()
        
        try:
            use_persist = os.getenv("MONITOR_READ_PERSIST")
            if use_persist is None:
                use_persist = "1" if self._persist_read_default else "0"
            if use_persist in ("1", "true", "True"):
                # Merge recent persisted events into in-memory window for computation
                persisted = get_bus().read_recent(limit=50)
                for ev in persisted:
                    self.events.append(ActivityEvent(
                        timestamp=float(ev.get("timestamp", time_now())),
                        event_type=str(ev.get("event_type", "")),
                        agent_name=ev.get("agent_name"),
                        details=ev.get("details"),
                    ))
                self._cleanup_old_events()
        except Exception:
            pass
        
        if not self.events:
            return ActivityLevel.IDLE
            
        # Count different event types
        memory_writes = sum(1 for e in self.events if e.event_type == "memory_write")
        memory_reads = sum(1 for e in self.events if e.event_type == "memory_read")
        flow_events = sum(1 for e in self.events if "flow" in e.event_type)
        agent_events = sum(1 for e in self.events if "agent" in e.event_type)
        
        # Activity level thresholds (per minute)
        events_per_minute = len(self.events) * (60.0 / self.window_seconds)
        
        # High: Active flows OR >30 events/min OR >5 memory writes/min
        if flow_events > 0 or events_per_minute > 30 or memory_writes * (60.0 / self.window_seconds) > 5:
            return ActivityLevel.HIGH
            
        # Medium: Multiple agents OR >15 events/min OR >2 memory writes/min
        active_agents = len(set(e.agent_name for e in self.events if e.agent_name))
        if active_agents > 1 or events_per_minute > 15 or memory_writes * (60.0 / self.window_seconds) > 2:
            return ActivityLevel.MEDIUM
            
        # Low: Any recent activity
        if len(self.events) > 0:
            return ActivityLevel.LOW
            
        return ActivityLevel.IDLE
    
    def get_refresh_interval(self) -> float:
        """Get recommended refresh interval in seconds."""
        level = self.compute_activity_level()
        intervals = {
            ActivityLevel.IDLE: 10.0,
            ActivityLevel.LOW: 5.0,
            ActivityLevel.MEDIUM: 2.0,
            ActivityLevel.HIGH: 1.0,
        }
        return intervals[level]
    
    def get_recent_events(self, limit: int = 10) -> List[ActivityEvent]:
        """Get recent events for timeline display. If a persistent bus exists, prefer it."""
        try:
            use_persist = os.getenv("MONITOR_READ_PERSIST")
            if use_persist is None:
                use_persist = "1" if self._persist_read_default else "0"
            if use_persist in ("1", "true", "True"):
                persisted = get_bus().read_recent(limit=limit)
                if persisted:
                    return [
                        ActivityEvent(
                            timestamp=float(ev.get("timestamp", time_now())),
                            event_type=str(ev.get("event_type", "")),
                            agent_name=ev.get("agent_name"),
                            details=ev.get("details"),
                        ) for ev in persisted
                    ]
        except Exception:
            pass
        
        self._cleanup_old_events()
        return list(self.events)[-limit:] if self.events else []


# Global activity detector instance
_activity_detector: Optional[ActivityDetection] = None


def get_activity_detector() -> ActivityDetection:
    """Get or create the global activity detector."""
    global _activity_detector
    if _activity_detector is None:
        _activity_detector = ActivityDetection()
    return _activity_detector


def record_memory_operation(operation_type: str, agent_name: Optional[str] = None) -> None:
    """Hook function for memory operations."""
    detector = get_activity_detector()
    detector.record_event(f"memory_{operation_type}", agent_name)


def record_agent_activity(activity_type: str, agent_name: str) -> None:
    """Hook function for agent lifecycle events."""
    detector = get_activity_detector()
    detector.record_event(f"agent_{activity_type}", agent_name)


def record_flow_activity(flow_type: str, from_agent: str, to_agent: str) -> None:
    """Hook function for flow events."""
    detector = get_activity_detector()
    detector.record_event(f"flow_{flow_type}", details=f"{from_agent}->{to_agent}")
