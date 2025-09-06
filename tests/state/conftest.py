"""
Configuration for Firestore state management tests.

Provides shared fixtures and configuration for testing the unified agent
architecture state management system.

Cross-references:
    - ADR-003: Unified Enhanced Architecture Migration
    - ai/state/: Firestore state management implementation
"""
import pytest
import asyncio
import os
from unittest.mock import patch, Mock

# Configure async event loop for all tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def mock_firebase_environment():
    """Mock Firebase environment variables for all tests."""
    test_env = {
        'FIREBASE_PROJECT_ID': 'test-firestore-project',
        'FIREBASE_CLIENT_EMAIL': 'test@test-project.iam.gserviceaccount.com',
        'FIREBASE_PRIVATE_KEY': 'test-private-key-content',
        'PYTHONPATH': os.environ.get('PYTHONPATH', '')
    }
    
    with patch.dict(os.environ, test_env):
        yield


# Removed autouse Firebase mocking - handled in individual tests


@pytest.fixture
def clean_memory_stores():
    """Ensure memory stores are clean between tests."""
    # This fixture can be expanded to clean up any global memory state
    # that might persist between tests
    yield
    # Cleanup code can go here if needed


# Test markers for organizing test runs
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", 
        "integration: marks tests as integration tests (may take longer to run)"
    )
    config.addinivalue_line(
        "markers",
        "firestore: marks tests that specifically test Firestore functionality"
    )
    config.addinivalue_line(
        "markers",
        "migration: marks tests that test state migration functionality"
    )
    config.addinivalue_line(
        "markers", 
        "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )


# Configure asyncio mode for pytest-asyncio
pytest_plugins = ['pytest_asyncio']
