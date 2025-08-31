from __future__ import annotations
import time
from unittest.mock import patch

import pytest

from ai.monitor.activity import ActivityDetection, ActivityLevel, ActivityEvent


class TestActivityDetection:
    
    def test_idle_state_with_no_events(self):
        """Should return IDLE when no events recorded."""
        detector = ActivityDetection(window_seconds=60)
        assert detector.compute_activity_level() == ActivityLevel.IDLE
        assert detector.get_refresh_interval() == 10.0
        
    def test_low_activity_single_agent(self):
        """Should return LOW for occasional single agent activity."""
        detector = ActivityDetection(window_seconds=60)
        detector.record_event("memory_read", "Father")
        detector.record_event("agent_start", "Father")
        
        assert detector.compute_activity_level() == ActivityLevel.LOW
        assert detector.get_refresh_interval() == 5.0
        
    def test_medium_activity_multiple_agents(self):
        """Should return MEDIUM for multiple agents or memory writes."""
        detector = ActivityDetection(window_seconds=60)
        
        # Multiple agents
        detector.record_event("memory_read", "Father")
        detector.record_event("memory_read", "Architect")
        detector.record_event("agent_start", "Developer")
        
        assert detector.compute_activity_level() == ActivityLevel.MEDIUM
        assert detector.get_refresh_interval() == 2.0
        
    def test_medium_activity_memory_writes(self):
        """Should return MEDIUM for frequent memory writes."""
        detector = ActivityDetection(window_seconds=60)
        
        # Simulate 3 memory writes (>2 per minute threshold)
        for i in range(3):
            detector.record_event("memory_write", "Father")
            
        assert detector.compute_activity_level() == ActivityLevel.MEDIUM
        assert detector.get_refresh_interval() == 2.0
        
    def test_high_activity_with_flows(self):
        """Should return HIGH when flows are active."""
        detector = ActivityDetection(window_seconds=60)
        detector.record_event("flow_start", details="Father->Architect")
        detector.record_event("memory_read", "Architect")
        
        assert detector.compute_activity_level() == ActivityLevel.HIGH
        assert detector.get_refresh_interval() == 1.0
        
    def test_high_activity_many_events(self):
        """Should return HIGH for very frequent events (>30/min)."""
        detector = ActivityDetection(window_seconds=60)
        
        # Add 35 events to exceed 30/min threshold
        for i in range(35):
            detector.record_event("memory_read", f"Agent{i % 3}")
            
        assert detector.compute_activity_level() == ActivityLevel.HIGH
        assert detector.get_refresh_interval() == 1.0
        
    def test_high_activity_frequent_memory_writes(self):
        """Should return HIGH for frequent memory writes (>5/min)."""
        detector = ActivityDetection(window_seconds=60)
        
        # Add 6 memory writes to exceed 5/min threshold
        for i in range(6):
            detector.record_event("memory_write", "Father")
            
        assert detector.compute_activity_level() == ActivityLevel.HIGH
        assert detector.get_refresh_interval() == 1.0
        
    def test_event_window_cleanup(self, mock_clock, fast_forward):
        """Should clean up old events outside the window."""
        detector = ActivityDetection(window_seconds=5)  # Short window for testing
        
        # Add an event
        detector.record_event("memory_read", "Father")
        assert len(detector.events) == 1
        
        # Fast-forward time and add another event (old one should be cleaned up)
        fast_forward(6)  # Advance longer than window
        detector.record_event("memory_read", "Architect")
        
        # Should only have recent event after cleanup
        recent_events = detector.get_recent_events()
        assert len(recent_events) == 1
        assert recent_events[0].agent_name == "Architect"
        
    def test_activity_level_transitions(self):
        """Should transition between activity levels correctly."""
        detector = ActivityDetection(window_seconds=60)
        
        # Start idle
        assert detector.compute_activity_level() == ActivityLevel.IDLE
        
        # Add single event -> LOW
        detector.record_event("memory_read", "Father")
        assert detector.compute_activity_level() == ActivityLevel.LOW
        
        # Add multiple agents -> MEDIUM
        detector.record_event("memory_read", "Architect")
        assert detector.compute_activity_level() == ActivityLevel.MEDIUM
        
        # Add flow -> HIGH
        detector.record_event("flow_start", details="Father->Architect")
        assert detector.compute_activity_level() == ActivityLevel.HIGH
        
    def test_recent_events_limit(self):
        """Should return limited number of recent events."""
        detector = ActivityDetection(window_seconds=60)
        
        # Add 15 events
        for i in range(15):
            detector.record_event("memory_read", f"Agent{i}")
            
        # Should return only last 10
        recent = detector.get_recent_events(limit=10)
        assert len(recent) == 10
        assert recent[-1].agent_name == "Agent14"  # Most recent
        assert recent[0].agent_name == "Agent5"   # 10th from end
