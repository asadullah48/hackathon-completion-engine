"""
Pytest configuration and fixtures for Course Companion tests
"""

import pytest
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(backend_path.parent))

# Set test environment
os.environ.setdefault("TESTING", "true")


@pytest.fixture(scope="session")
def test_vault():
    """Create and return test vault path"""
    vault_path = Path(__file__).parent.parent / "vault"
    vault_path.mkdir(parents=True, exist_ok=True)
    return vault_path


@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment before each test"""
    # Ensure we're in test mode
    os.environ["TESTING"] = "true"
    yield
    # Cleanup if needed
