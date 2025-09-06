"""Root-level pytest configuration.

This file configures pytest plugins and settings for the entire test suite.
"""
import pytest

# Configure pytest-asyncio plugin at root level
pytest_plugins = ['pytest_asyncio']


def pytest_configure(config):
    """Configure custom pytest markers."""
    # Add custom markers if not already defined
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
    config.addinivalue_line(
        "markers",
        "docker: marks tests requiring Docker (deselect with '-m \"not docker\"')"
    )
