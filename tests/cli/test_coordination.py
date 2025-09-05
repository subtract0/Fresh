"""Tests for coordination CLI commands.

Tests the coordination command group including:
- record-agent-activity
- record-flow-activity  
- recent-events
- activity-level
- refresh-interval
"""
import json
import sys
from unittest.mock import patch, MagicMock
import pytest

from ai.cli.fresh import main


def test_coordination_help():
    """Test that coordination --help displays correctly."""
    with patch.object(sys, 'argv', ['fresh', 'coordination', '--help']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0


def test_coordination_record_agent_activity_help():
    """Test that coordination record-agent-activity --help displays correctly."""
    with patch.object(sys, 'argv', ['fresh', 'coordination', 'record-agent-activity', '--help']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0


def test_coordination_record_flow_activity_help():
    """Test that coordination record-flow-activity --help displays correctly."""
    with patch.object(sys, 'argv', ['fresh', 'coordination', 'record-flow-activity', '--help']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0


def test_coordination_recent_events_help():
    """Test that coordination recent-events --help displays correctly."""
    with patch.object(sys, 'argv', ['fresh', 'coordination', 'recent-events', '--help']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0


def test_coordination_activity_level_help():
    """Test that coordination activity-level --help displays correctly."""
    with patch.object(sys, 'argv', ['fresh', 'coordination', 'activity-level', '--help']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0


def test_coordination_refresh_interval_help():
    """Test that coordination refresh-interval --help displays correctly."""
    with patch.object(sys, 'argv', ['fresh', 'coordination', 'refresh-interval', '--help']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0


@patch('ai.monitor.activity.record_agent_activity')
def test_record_agent_activity_success(mock_record):
    """Test successful agent activity recording."""
    mock_record.return_value = None
    
    with patch.object(sys, 'argv', ['fresh', 'coordination', 'record-agent-activity', 'start', 'test-agent']):
        with pytest.raises(SystemExit) as exc_info:
            main()
            
    assert exc_info.value.code == 0
    mock_record.assert_called_once_with('start', 'test-agent')


@patch('ai.monitor.activity.record_agent_activity')
def test_record_agent_activity_with_details(mock_record):
    """Test agent activity recording with details."""
    mock_record.return_value = None
    
    with patch.object(sys, 'argv', ['fresh', 'coordination', 'record-agent-activity', 'complete', 'test-agent', '--details', 'Task completed successfully']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        
    assert exc_info.value.code == 0
    mock_record.assert_called_once_with('complete', 'test-agent')


@patch('ai.monitor.activity.record_flow_activity')
def test_record_flow_activity_success(mock_record):
    """Test successful flow activity recording."""
    mock_record.return_value = None
    
    with patch.object(sys, 'argv', ['fresh', 'coordination', 'record-flow-activity', 'handoff', 'agent-a', 'agent-b']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        
    assert exc_info.value.code == 0
    mock_record.assert_called_once_with('handoff', 'agent-a', 'agent-b')


@patch('ai.monitor.activity.get_activity_detector')
def test_recent_events_success(mock_get_detector):
    """Test successful recent events retrieval."""
    mock_detector = MagicMock()
    mock_event = MagicMock()
    mock_event.timestamp = 1234567890.0
    mock_event.event_type = 'agent_start'
    mock_event.agent_name = 'test-agent'
    mock_event.details = 'Starting task'
    
    mock_detector.get_recent_events.return_value = [mock_event]
    mock_get_detector.return_value = mock_detector
    
    with patch.object(sys, 'argv', ['fresh', 'coordination', 'recent-events', '--limit', '5']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        
    assert exc_info.value.code == 0
    mock_detector.get_recent_events.assert_called_once_with(limit=5)


@patch('ai.monitor.activity.get_activity_detector')
def test_recent_events_json_output(mock_get_detector):
    """Test recent events with JSON output."""
    mock_detector = MagicMock()
    mock_event = MagicMock()
    mock_event.timestamp = 1234567890.0
    mock_event.event_type = 'agent_start'
    mock_event.agent_name = 'test-agent'
    mock_event.details = 'Starting task'
    
    mock_detector.get_recent_events.return_value = [mock_event]
    mock_get_detector.return_value = mock_detector
    
    with patch.object(sys, 'argv', ['fresh', 'coordination', 'recent-events', '--json']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        
    assert exc_info.value.code == 0
    mock_detector.get_recent_events.assert_called_once_with(limit=10)  # default


@patch('ai.monitor.activity.get_activity_detector')
def test_activity_level_success(mock_get_detector):
    """Test successful activity level retrieval."""
    from ai.monitor.activity import ActivityLevel
    
    mock_detector = MagicMock()
    mock_detector.compute_activity_level.return_value = ActivityLevel.MEDIUM
    mock_get_detector.return_value = mock_detector
    
    with patch.object(sys, 'argv', ['fresh', 'coordination', 'activity-level']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        
    assert exc_info.value.code == 0
    mock_detector.compute_activity_level.assert_called_once()


@patch('ai.monitor.activity.get_activity_detector')
def test_activity_level_json_output(mock_get_detector):
    """Test activity level with JSON output."""
    from ai.monitor.activity import ActivityLevel
    
    mock_detector = MagicMock()
    mock_detector.compute_activity_level.return_value = ActivityLevel.HIGH
    mock_get_detector.return_value = mock_detector
    
    with patch.object(sys, 'argv', ['fresh', 'coordination', 'activity-level', '--json']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        
    assert exc_info.value.code == 0
    mock_detector.compute_activity_level.assert_called_once()


@patch('ai.monitor.activity.get_activity_detector')
def test_refresh_interval_success(mock_get_detector):
    """Test successful refresh interval retrieval."""
    from ai.monitor.activity import ActivityLevel
    
    mock_detector = MagicMock()
    mock_detector.get_refresh_interval.return_value = 2.0
    mock_detector.compute_activity_level.return_value = ActivityLevel.MEDIUM
    mock_get_detector.return_value = mock_detector
    
    with patch.object(sys, 'argv', ['fresh', 'coordination', 'refresh-interval']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        
    assert exc_info.value.code == 0
    mock_detector.get_refresh_interval.assert_called_once()
    mock_detector.compute_activity_level.assert_called_once()


@patch('ai.monitor.activity.get_activity_detector')
def test_refresh_interval_json_output(mock_get_detector):
    """Test refresh interval with JSON output."""
    from ai.monitor.activity import ActivityLevel
    
    mock_detector = MagicMock()
    mock_detector.get_refresh_interval.return_value = 1.0
    mock_detector.compute_activity_level.return_value = ActivityLevel.HIGH
    mock_get_detector.return_value = mock_detector
    
    with patch.object(sys, 'argv', ['fresh', 'coordination', 'refresh-interval', '--json']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        
    assert exc_info.value.code == 0
    mock_detector.get_refresh_interval.assert_called_once()
    mock_detector.compute_activity_level.assert_called_once()


def test_coordination_invalid_subcommand():
    """Test coordination with invalid subcommand."""
    with patch.object(sys, 'argv', ['fresh', 'coordination', 'invalid-command']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        
    assert exc_info.value.code == 2  # argparse error code


@patch('ai.monitor.activity.record_agent_activity')
def test_record_agent_activity_import_error(mock_record):
    """Test agent activity recording with import error."""
    mock_record.side_effect = ImportError("Module not available")
    
    with patch.object(sys, 'argv', ['fresh', 'coordination', 'record-agent-activity', 'start', 'test-agent']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        
    assert exc_info.value.code == 1


@patch('ai.monitor.activity.get_activity_detector')
def test_recent_events_import_error(mock_get_detector):
    """Test recent events with import error."""
    mock_get_detector.side_effect = ImportError("Module not available")
    
    with patch.object(sys, 'argv', ['fresh', 'coordination', 'recent-events']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        
    assert exc_info.value.code == 1
