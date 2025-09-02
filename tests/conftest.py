import pytest

INTEGRATION_FILES = {
    "test_mcp_integration.py",
    "test_telegram_integration.py",
    "test_agency_bootstrap.py",
    "test_agency_persistence.py",
}


def pytest_collection_modifyitems(config, items):
    for item in items:
        # Mark known integration test modules as integration
        nodeid = item.nodeid
        for fname in INTEGRATION_FILES:
            if nodeid.endswith("::" + fname) or fname in nodeid:
                item.add_marker(pytest.mark.integration)
                break

import sys
from pathlib import Path
import pytest
from unittest.mock import patch

# Ensure project root is importable during tests
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

# Load .env so integration tests like agency_swarm see OPENAI_API_KEY
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=root / ".env")
except Exception:
    pass

from ai.utils.clock import MockClock, set_clock, reset_to_system_clock


@pytest.fixture(autouse=True)
def reset_global_state():
    """Reset all global state between tests."""
    import os
    
    # Disable event persistence during tests to avoid cross-test contamination
    original_persist_write = os.environ.get("MONITOR_PERSIST_EVENTS")
    original_persist_read = os.environ.get("MONITOR_READ_PERSIST")
    os.environ["MONITOR_PERSIST_EVENTS"] = "0"
    os.environ["MONITOR_READ_PERSIST"] = "0"
    
    # Reset clock to system default
    reset_to_system_clock()
    
    # Reset global activity detector
    import ai.monitor.activity
    ai.monitor.activity._activity_detector = None
    
    yield
    
    # Cleanup after test
    reset_to_system_clock()
    ai.monitor.activity._activity_detector = None
    
    # Restore original environment variables
    if original_persist_write is not None:
        os.environ["MONITOR_PERSIST_EVENTS"] = original_persist_write
    else:
        os.environ.pop("MONITOR_PERSIST_EVENTS", None)
        
    if original_persist_read is not None:
        os.environ["MONITOR_READ_PERSIST"] = original_persist_read
    else:
        os.environ.pop("MONITOR_READ_PERSIST", None)


@pytest.fixture
def mock_clock():
    """Provide a mock clock for deterministic time testing."""
    clock = MockClock(start_time=1000.0)  # Start at epoch + 1000 for easy testing
    set_clock(clock)
    return clock


@pytest.fixture 
def fast_forward(mock_clock):
    """Helper to advance mock time without real delays."""
    def _fast_forward(seconds: float):
        mock_clock.advance(seconds)
    return _fast_forward


@pytest.fixture
def no_rich_live():
    """Disable Rich Live displays during tests to prevent hanging."""
    with patch('rich.live.Live') as mock_live:
        # Create a mock that doesn't actually start a live display
        mock_instance = mock_live.return_value
        mock_instance.__enter__ = lambda self: self
        mock_instance.__exit__ = lambda self, *args: None
        mock_instance.update = lambda self, content: None
        mock_instance.refresh = lambda self: None
        mock_instance.start = lambda self: None  
        mock_instance.stop = lambda self: None
        yield mock_live

