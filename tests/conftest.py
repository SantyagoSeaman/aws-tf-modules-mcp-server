"""
Pytest configuration and fixtures for test suite.

This module initializes NLTK data before any tests run.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tfmod_search_lib import initialize_nltk


def pytest_configure(config):
    """
    Initialize NLTK data before running tests.

    This runs once at the start of the test session, before any tests.
    """
    initialize_nltk()
