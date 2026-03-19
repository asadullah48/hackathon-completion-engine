"""Tests for CRUD operations on todos."""
import pytest


class TestCreateTodo:
    """Tests for POST /api/todos endpoint."""

    def test_create_todo_success(self, client):
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

    def test_create_todo_constitutional_block(self, client):
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

    def test_create_todo_flagged(self, client):
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

    def test_create_todo_with_description(self, client):
        """Test creating a todo with description."""
        response = client.post(
            "/api/todos",
            json={
                "title": "Complete project",
                "description": "Work on the main project",
                "category": "work",
                "priority": "medium"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["description"] == "Work on the main project"


class TestReadTodos:
    """Tests for GET /api/todos endpoints."""

    def test_get_all_todos_empty(self, client):
        """Test getting todos when none exist."""
        response = client.get("/api/todos")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_all_todos_with_data(self, client):
        """Test getting todos after creating some."""
        client.post("/api/todos", json={"title": "Task 1", "category": "work"})
        client.post("/api/todos", json={"title": "Task 2", "category": "personal"})

        response = client.get("/api/todos")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_todo_by_id(self, client):
        """Test getting a single todo by ID."""
        create_response = client.post(
            "/api/todos",
            json={"title": "Test todo", "category": "work"}
        )
        todo_id = create_response.json()["id"]

        response = client.get(f"/api/todos/{todo_id}")
        assert response.status_code == 200
        assert response.json()["id"] == todo_id

    def test_get_todo_not_found(self, client):
        """Test getting non-existent todo."""
        response = client.get("/api/todos/non-existent-id")
        assert response.status_code == 404

    def test_filter_todos_by_category(self, client):
        """Test filtering todos by category."""
        client.post("/api/todos", json={"title": "Work task", "category": "work"})
        client.post("/api/todos", json={"title": "Personal task", "category": "personal"})

        response = client.get("/api/todos?category=work")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "work"

    def test_filter_todos_by_status(self, client):
        """Test filtering todos by status."""
        create_response = client.post(
            "/api/todos",
            json={"title": "Task 1", "category": "work"}
        )
        todo_id = create_response.json()["id"]
        client.put(f"/api/todos/{todo_id}", json={"status": "completed"})
        client.post("/api/todos", json={"title": "Task 2", "category": "work"})

        response = client.get("/api/todos?status=completed")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "completed"


class TestUpdateTodo:
    """Tests for PUT /api/todos/{id} endpoint."""

    def test_update_todo_title(self, client):
        """Test updating a todo's title."""
        create_response = client.post(
            "/api/todos",
            json={"title": "Original title", "category": "work"}
        )
        todo_id = create_response.json()["id"]

        response = client.put(
            f"/api/todos/{todo_id}",
            json={"title": "Updated title"}
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated title"

    def test_update_todo_status(self, client):
        """Test updating a todo's status."""
        create_response = client.post(
            "/api/todos",
            json={"title": "Test task", "category": "work"}
        )
        todo_id = create_response.json()["id"]

        response = client.put(
            f"/api/todos/{todo_id}",
            json={"status": "in_progress"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "in_progress"

    def test_update_todo_not_found(self, client):
        """Test updating non-existent todo."""
        response = client.put(
            "/api/todos/non-existent-id",
            json={"title": "New title"}
        )
        assert response.status_code == 404


class TestDeleteTodo:
    """Tests for DELETE /api/todos/{id} endpoint."""

    def test_delete_todo(self, client):
        """Test deleting a todo."""
        create_response = client.post(
            "/api/todos",
            json={"title": "Task to delete", "category": "work"}
        )
        todo_id = create_response.json()["id"]

        response = client.delete(f"/api/todos/{todo_id}")
        assert response.status_code == 200
        assert response.json()["deleted"] is True

        # Verify deleted
        get_response = client.get(f"/api/todos/{todo_id}")
        assert get_response.status_code == 404

    def test_delete_todo_not_found(self, client):
        """Test deleting non-existent todo."""
        response = client.delete("/api/todos/non-existent-id")
        assert response.status_code == 404


class TestStats:
    """Tests for GET /api/stats endpoint."""

    def test_get_stats_empty(self, client):
        """Test getting stats when no todos exist."""
        response = client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

    def test_get_stats_with_todos(self, client):
        """Test getting stats with some todos."""
        client.post("/api/todos", json={"title": "Task 1", "category": "work", "priority": "high"})
        client.post("/api/todos", json={"title": "Task 2", "category": "personal", "priority": "low"})

        response = client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert data["by_status"]["pending"] == 2
        assert data["by_category"]["work"] == 1
        assert data["by_category"]["personal"] == 1
