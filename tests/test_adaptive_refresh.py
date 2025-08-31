from __future__ import annotations
import time
from unittest.mock import patch, MagicMock

import pytest

from ai.monitor.activity import get_activity_detector, record_memory_operation, ActivityLevel, ActivityEvent
from ai.monitor.adaptive_ui import AdaptiveMonitorUI, RefreshController


class TestRefreshController:
    
    def test_initial_state_is_idle(self):
        """Should start with idle refresh interval."""
        controller = RefreshController()
        assert controller.get_current_interval() == 10.0
        
    def test_interval_mapping_correct(self):
        """Should map activity levels to correct intervals."""
        controller = RefreshController()
        
        # Test all mappings
        with patch.object(controller.activity_detector, 'compute_activity_level') as mock_level:
            mock_level.return_value = ActivityLevel.IDLE
            assert controller.get_current_interval() == 10.0
            
            mock_level.return_value = ActivityLevel.LOW
            assert controller.get_current_interval() == 5.0
            
            mock_level.return_value = ActivityLevel.MEDIUM
            assert controller.get_current_interval() == 2.0
            
            mock_level.return_value = ActivityLevel.HIGH
            assert controller.get_current_interval() == 1.0
            
    def test_custom_min_interval_override(self):
        """Should respect custom minimum interval."""
        controller = RefreshController(min_interval=0.5)
        
        with patch.object(controller.activity_detector, 'compute_activity_level') as mock_level:
            mock_level.return_value = ActivityLevel.HIGH
            assert controller.get_current_interval() == 0.5
            
    def test_interval_changes_with_activity(self):
        """Should adapt interval as activity changes."""
        controller = RefreshController()
        detector = controller.activity_detector
        
        # Start idle
        assert controller.get_current_interval() == 10.0
        
        # Add activity -> should become LOW
        detector.record_event("memory_read", "Father")
        assert controller.get_current_interval() == 5.0
        
        # Add flow -> should become HIGH
        detector.record_event("flow_start", details="Father->Architect")
        assert controller.get_current_interval() == 1.0


class TestAdaptiveMonitorUI:
    
    def test_ui_initializes_with_console(self):
        """Should initialize with rich console and live display."""
        ui = AdaptiveMonitorUI()
        assert ui.console is not None
        assert ui.live is None  # Live starts as None until start_live_display() is called
        
        # Test that live display can be started
        live = ui.start_live_display()
        assert live is not None
        assert ui.live is not None
        
    def test_generate_agent_table_structure(self):
        """Should generate table with correct columns."""
        ui = AdaptiveMonitorUI()
        
        mock_status = {
            "agents": ["Father", "Architect"],
            "flows": [["Father", "Architect"]],
            "memory_context": "test context",
            "next_steps": ["step 1", "step 2"],
            "release_notes": "# Notes"
        }
        
        table = ui._generate_agent_table(mock_status)
        
        # Should have expected columns
        expected_columns = ["Agent", "Status", "Activity", "Memory", "Last Response", "Timeline"]
        assert len(table.columns) == len(expected_columns)
        
    def test_color_coding_by_activity_level(self):
        """Should apply correct colors based on activity level."""
        ui = AdaptiveMonitorUI()
        
        # Test color mapping
        assert ui._get_activity_color(ActivityLevel.IDLE) == "dim"
        assert ui._get_activity_color(ActivityLevel.LOW) == "yellow"
        assert ui._get_activity_color(ActivityLevel.MEDIUM) == "blue"
        assert ui._get_activity_color(ActivityLevel.HIGH) == "red"
        
    def test_format_memory_rss(self):
        """Should format memory in human-readable units."""
        ui = AdaptiveMonitorUI()
        
        assert ui._format_memory(1024) == "1.0 KB"
        assert ui._format_memory(1024 * 1024) == "1.0 MB"
        assert ui._format_memory(1536 * 1024) == "1.5 MB"
        
    def test_format_response_time(self):
        """Should format response times appropriately."""
        ui = AdaptiveMonitorUI()
        
        assert ui._format_response_time(0.123) == "123ms"
        assert ui._format_response_time(1.567) == "1.57s"
        assert ui._format_response_time(None) == "-"
        
    def test_generate_timeline_sparkline(self):
        """Should generate sparkline from recent events."""
        ui = AdaptiveMonitorUI()
        
        # Mock recent events
        events = [
            ActivityEvent(time.time() - 10, "memory_read", "Father"),
            ActivityEvent(time.time() - 5, "memory_write", "Father"),
            ActivityEvent(time.time() - 1, "agent_start", "Father"),
        ]
        
        sparkline = ui._generate_timeline_sparkline(events)
        assert len(sparkline) > 0  # Should generate some representation
        
    def test_update_display_integration(self):
        """Should update live display without errors."""
        ui = AdaptiveMonitorUI()
        
        mock_status = {
            "agents": ["Father"],
            "flows": [],
            "memory_context": "",
            "next_steps": [],
            "release_notes": ""
        }
        
        # Should not raise exception
        ui.update_display(mock_status)


class TestMonitorIntegration:
    
    def test_monitor_uses_adaptive_intervals(self):
        """Should use activity detector for refresh intervals."""
        # This will be implemented when we create the adaptive monitor script
        pass
        
    def test_activity_hooks_record_events(self):
        """Should record events when memory operations occur."""
        detector = get_activity_detector()
        initial_count = len(detector.events)
        
        # Record operation
        record_memory_operation("read", "Father")
        
        # Should have new event
        assert len(detector.events) == initial_count + 1
        assert detector.events[-1].event_type == "memory_read"
        assert detector.events[-1].agent_name == "Father"
