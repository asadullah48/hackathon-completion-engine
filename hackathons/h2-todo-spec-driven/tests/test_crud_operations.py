"""Tests for CRUD operations on todos."""
import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import get_db
from models import Base, TodoCategory, TodoPriority, TodoStatus


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Apply override
app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Set up fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestCreateTodo:
    """Tests for POST /api/todos endpoint."""

    def test_create_todo_success(self):
        """Test creating a valid todo."""
        response = client.post(
            "/api/todos",
            json={
                "title": "Study for exam tomorrow",
                "category": "study",
                "priority": "high"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Study for exam tomorrow"
        assert data["category"] == "study"
        assert data["priority"] == "high"
        assert data["status"] == "pending"
        assert data["constitutional_check"]["passed"] is True
        assert data["constitutional_check"]["decision"] == "allow"

    def test_create_todo_constitutional_block(self):
        """Test that constitutional violation returns 403."""
        response = client.post(
            "/api/todos",
            json={
                "title": "Do my homework assignment",
                "category": "study"
            }
        )
        assert response.status_code == 403
        data = response.json()
        assert data["detail"]["error"] == "constitutional_violation"
        assert data["detail"]["decision"] == "block"

    def test_create_todo_flagged(self):
        """Test that flagged todo is created with flagged status."""
        response = client.post(
            "/api/todos",
            json={
                "title": "Urgent need to finish assignment before midnight",
                "category": "study"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "flagged"
        assert data["constitutional_check"]["decision"] == "flag"

    def test_create_todo_with_defaults(self):
        """Test that defaults are applied correctly."""
        response = client.post(
            "/api/todos",
            json={"title": "Buy groceries"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["category"] == "other"
        assert data["priority"] == "medium"
        assert data["status"] == "pending"

    def test_create_todo_with_description(self):
        """Test creating todo with description."""
        response = client.post(
            "/api/todos",
            json={
                "title": "Complete project",
                "description": "Finish the frontend implementation"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["description"] == "Finish the frontend implementation"


class TestListTodos:
    """Tests for GET /api/todos endpoint."""

    def test_list_todos_empty(self):
        """Test listing when no todos exist."""
        response = client.get("/api/todos")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_todos_with_data(self):
        """Test listing todos."""
        # Create some todos
        client.post("/api/todos", json={"title": "Todo 1", "category": "work"})
        client.post("/api/todos", json={"title": "Todo 2", "category": "personal"})

        response = client.get("/api/todos")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_filter_by_category(self):
        """Test filtering by category."""
        client.post("/api/todos", json={"title": "Work task", "category": "work"})
        client.post("/api/todos", json={"title": "Personal task", "category": "personal"})

        response = client.get("/api/todos?category=work")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "work"

    def test_filter_by_status(self):
        """Test filtering by status."""
        # Create a todo and update its status
        create_response = client.post("/api/todos", json={"title": "Task 1"})
        todo_id = create_response.json()["id"]
        client.put(f"/api/todos/{todo_id}", json={"status": "completed"})

        client.post("/api/todos", json={"title": "Task 2"})

        response = client.get("/api/todos?status=completed")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "completed"

    def test_filter_by_priority(self):
        """Test filtering by priority."""
        client.post("/api/todos", json={"title": "High priority", "priority": "high"})
        client.post("/api/todos", json={"title": "Low priority", "priority": "low"})

        response = client.get("/api/todos?priority=high")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["priority"] == "high"

    def test_search_todos(self):
        """Test searching todos."""
        client.post("/api/todos", json={"title": "Buy milk from store"})
        client.post("/api/todos", json={"title": "Study for exam"})

        response = client.get("/api/todos?search=milk")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "milk" in data[0]["title"].lower()


class TestGetTodo:
    """Tests for GET /api/todos/{id} endpoint."""

    def test_get_todo_success(self):
        """Test getting a single todo."""
        create_response = client.post(
            "/api/todos",
            json={"title": "Test todo"}
        )
        todo_id = create_response.json()["id"]

        response = client.get(f"/api/todos/{todo_id}")
        assert response.status_code == 200
        assert response.json()["id"] == todo_id

    def test_get_todo_not_found(self):
        """Test getting non-existent todo."""
        response = client.get("/api/todos/non-existent-id")
        assert response.status_code == 404


class TestUpdateTodo:
    """Tests for PUT /api/todos/{id} endpoint."""

    def test_update_todo(self):
        """Test updating a todo."""
        create_response = client.post(
            "/api/todos",
            json={"title": "Original title", "priority": "low"}
        )
        todo_id = create_response.json()["id"]

        response = client.put(
            f"/api/todos/{todo_id}",
            json={"title": "Updated title", "priority": "high"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated title"
        assert data["priority"] == "high"

    def test_update_todo_status(self):
        """Test updating todo status."""
        create_response = client.post(
            "/api/todos",
            json={"title": "Task to complete"}
        )
        todo_id = create_response.json()["id"]

        response = client.put(
            f"/api/todos/{todo_id}",
            json={"status": "completed"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "completed"

    def test_update_todo_constitutional_recheck(self):
        """Test that updating title triggers constitutional recheck."""
        create_response = client.post(
            "/api/todos",
            json={"title": "Valid task"}
        )
        todo_id = create_response.json()["id"]

        # Try to update with blocked content
        response = client.put(
            f"/api/todos/{todo_id}",
            json={"title": "Do my homework assignment"}
        )
        assert response.status_code == 403

    def test_update_todo_not_found(self):
        """Test updating non-existent todo."""
        response = client.put(
            "/api/todos/non-existent-id",
            json={"title": "New title"}
        )
        assert response.status_code == 404


class TestDeleteTodo:
    """Tests for DELETE /api/todos/{id} endpoint."""

    def test_delete_todo(self):
        """Test deleting a todo."""
        create_response = client.post(
            "/api/todos",
            json={"title": "Todo to delete"}
        )
        todo_id = create_response.json()["id"]

        response = client.delete(f"/api/todos/{todo_id}")
        assert response.status_code == 200
        assert response.json()["deleted"] is True
        assert response.json()["id"] == todo_id

        # Verify it's gone
        get_response = client.get(f"/api/todos/{todo_id}")
        assert get_response.status_code == 404

    def test_delete_todo_not_found(self):
        """Test deleting non-existent todo."""
        response = client.delete("/api/todos/non-existent-id")
        assert response.status_code == 404


class TestStats:
    """Tests for GET /api/stats endpoint."""

    def test_stats_empty(self):
        """Test stats with no todos."""
        response = client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["completion_rate"] == 0.0

    def test_stats_with_data(self):
        """Test stats with todos."""
        # Create various todos
        client.post("/api/todos", json={"title": "Work 1", "category": "work"})
        client.post("/api/todos", json={"title": "Work 2", "category": "work"})
        client.post("/api/todos", json={"title": "Personal 1", "category": "personal"})

        # Complete one
        create_response = client.post("/api/todos", json={"title": "Completed task"})
        todo_id = create_response.json()["id"]
        client.put(f"/api/todos/{todo_id}", json={"status": "completed"})

        response = client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 4
        assert data["by_category"]["work"] == 2
        assert data["by_category"]["personal"] == 1
        assert data["by_status"]["completed"] == 1
        assert data["completion_rate"] == 0.25


class TestHealthCheck:
    """Tests for health and root endpoints."""

    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "H2 Todo API"
        assert "endpoints" in data
