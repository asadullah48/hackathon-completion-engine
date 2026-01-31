"""Pytest configuration and fixtures."""
import sys
import os

# Add backend to path for all tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import get_db
from models import Base


# Create test database engine (in-memory SQLite)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Override database dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Apply override globally
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Setup fresh database for each test."""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)

    # Seed templates
    from seeds import seed_templates
    db = TestingSessionLocal()
    try:
        seed_templates(db)
    finally:
        db.close()

    yield

    # Cleanup after test
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    """Get test client."""
    return TestClient(app)
