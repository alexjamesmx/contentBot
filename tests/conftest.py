"""Pytest configuration file for ContentBot tests."""

import sys
import os
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import MagicMock

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# Register custom markers
def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )


# ======================== FIXTURES FOR MULTI-PART STORIES (TDD) ========================

@pytest.fixture
def sample_series_metadata():
    """Standard series metadata for multi-part story tests."""
    return {
        "genre": "terror",
        "total_parts": 3,
        "theme": "haunted investigation"
    }


@pytest.fixture
def sample_story_part():
    """Standard story part for multi-part story tests."""
    return {
        "story_text": "I entered the house and heard strange noises.",
        "duration": 75,
        "hook": "The door slammed shut behind me."
    }


@pytest.fixture
def temp_series_cache():
    """Temporary directory for story series cache with cleanup."""
    with tempfile.TemporaryDirectory(prefix="story_series_test_") as temp_dir:
        yield temp_dir
    # Cleanup handled by context manager


@pytest.fixture
def client():
    """Flask test client for API testing."""
    from app import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_groq_service():
    """Mock Groq AI service for testing."""
    mock = MagicMock()
    mock.generate.return_value = {
        "story": "Test story text.",
        "duration": 70
    }
    return mock
