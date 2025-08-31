from __future__ import annotations
import time
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


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
        
    def record_event(self, event_type: str, agent_name: Optional[str] = None, details: Optional[str] = None) -> None:
        """Record an activity event."""
        event = ActivityEvent(
            timestamp=time.time(),
            event_type=event_type,
            agent_name=agent_name,
            details=details
        )
        self.events.append(event)
        self._cleanup_old_events()
        
    def _cleanup_old_events(self) -> None:
        """Remove events older than the window."""
        cutoff = time.time() - self.window_seconds
        while self.events and self.events[0].timestamp < cutoff:
            self.events.popleft()
            
    def compute_activity_level(self) -> ActivityLevel:
        """Compute current activity level based on recent events."""
        self._cleanup_old_events()
        
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
        """Get recent events for timeline display."""
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
