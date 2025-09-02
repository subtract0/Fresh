from __future__ import annotations
import pytest
from unittest.mock import patch, MagicMock
from ai.monitor.status import get_status


@patch('ai.monitor.status.build_agency')
@patch('ai.monitor.activity.get_activity_detector')
@patch('ai.tools.next_steps.GenerateNextSteps')
@patch('ai.tools.release_notes.GenerateReleaseNotes')
@patch('ai.monitor.cost_tracker.get_cost_tracker')
def test_get_status_shape(
    mock_cost_tracker,
    mock_release_notes,
    mock_next_steps,
    mock_activity_detector,
    mock_build_agency
):
    """Test get_status returns correct structure without making external calls."""
    # Mock agency with expected agents
    mock_agent = MagicMock()
    mock_agent.name = "TestAgent"
    mock_agency = MagicMock()
    mock_agency.agents = [mock_agent] * 4  # At least 4 agents as expected
    mock_build_agency.return_value = mock_agency
    
    # Mock activity detector with flow events
    mock_event = MagicMock()
    mock_event.event_type = "flow_start"
    mock_event.details = "Agent1 -> Agent2"
    mock_detector = MagicMock()
    mock_detector.get_recent_events.return_value = [mock_event, mock_event]
    mock_activity_detector.return_value = mock_detector
    
    # Mock tools
    mock_next_steps_instance = MagicMock()
    mock_next_steps_instance.run.return_value = "- Step 1\n- Step 2\n- Step 3"
    mock_next_steps.return_value = mock_next_steps_instance
    
    mock_release_notes_instance = MagicMock()
    mock_release_notes_instance.run.return_value = "# Release Notes\nSome notes"
    mock_release_notes.return_value = mock_release_notes_instance
    
    # Mock cost tracker
    mock_tracker = MagicMock()
    mock_tracker.get_usage_summary.return_value = {"cost": 10.5, "tokens": 1000}
    mock_tracker.budget_alerts = [MagicMock(is_enabled=True)]
    mock_tracker.usage_records = [1, 2, 3]
    mock_cost_tracker.return_value = mock_tracker
    
    # Test the function
    out = get_status(limit=5)
    
    # Verify structure
    assert set(out.keys()) == {"agents", "flows", "memory_context", "next_steps", "release_notes", "cost_summary"}
    assert isinstance(out["agents"], list) and len(out["agents"]) >= 4
    assert isinstance(out["flows"], list) and all(len(p)==2 for p in out["flows"])
    
    # Verify no external calls were made to OpenAI
    mock_build_agency.assert_called_once()
