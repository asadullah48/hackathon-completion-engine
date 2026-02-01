"""Tests for recurring todos functionality."""
import pytest
from datetime import datetime, timedelta


class TestCreateRecurring:
    """Tests for POST /api/recurring endpoint."""

    @pytest.fixture
    def template_todo(self, client):
        """Create a template todo for recurring patterns."""
        response = client.post(
            "/api/todos",
            json={
                "title": "Daily standup meeting",
                "category": "work",
                "priority": "high"
            }
        )
        return response.json()

    def test_create_daily_recurring(self, client, template_todo):
        """Test creating a daily recurring pattern."""
        response = client.post(
            "/api/recurring",
            json={
                "pattern": "daily",
                "interval": 1,
                "template_todo_id": template_todo["id"]
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["pattern"] == "daily"
        assert data["interval"] == 1
        assert data["is_active"] is True

    def test_create_weekly_recurring(self, client, template_todo):
        """Test creating a weekly recurring pattern."""
        response = client.post(
            "/api/recurring",
            json={
                "pattern": "weekly",
                "interval": 1,
                "days_of_week": [1, 3, 5],
                "template_todo_id": template_todo["id"]
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["pattern"] == "weekly"
        assert data["days_of_week"] == [1, 3, 5]

    def test_create_monthly_recurring(self, client, template_todo):
        """Test creating a monthly recurring pattern."""
        response = client.post(
            "/api/recurring",
            json={
                "pattern": "monthly",
                "interval": 1,
                "day_of_month": 15,
                "template_todo_id": template_todo["id"]
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["pattern"] == "monthly"
        assert data["day_of_month"] == 15

    def test_create_custom_recurring(self, client, template_todo):
        """Test creating a custom recurring pattern."""
        response = client.post(
            "/api/recurring",
            json={
                "pattern": "custom",
                "interval": 3,
                "template_todo_id": template_todo["id"]
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["pattern"] == "custom"
        assert data["interval"] == 3


class TestGetRecurring:
    """Tests for GET /api/recurring endpoints."""

    @pytest.fixture
    def template_todo(self, client):
        """Create a template todo."""
        response = client.post(
            "/api/todos",
            json={"title": "Recurring task", "category": "work"}
        )
        return response.json()

    @pytest.fixture
    def recurring_pattern(self, client, template_todo):
        """Create a recurring pattern."""
        response = client.post(
            "/api/recurring",
            json={
                "pattern": "daily",
                "interval": 1,
                "template_todo_id": template_todo["id"]
            }
        )
        return response.json()

    def test_get_all_recurring_empty(self, client):
        """Test getting recurring patterns when none exist."""
        response = client.get("/api/recurring")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_all_recurring(self, client, recurring_pattern):
        """Test getting all recurring patterns."""
        response = client.get("/api/recurring")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_get_recurring_by_id(self, client, recurring_pattern):
        """Test getting a recurring pattern by ID."""
        response = client.get(f"/api/recurring/{recurring_pattern['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == recurring_pattern["id"]

    def test_get_recurring_not_found(self, client):
        """Test getting non-existent recurring pattern."""
        response = client.get("/api/recurring/non-existent-id")
        assert response.status_code == 404


class TestGenerateOccurrence:
    """Tests for POST /api/recurring/{id}/generate endpoint."""

    @pytest.fixture
    def template_todo(self, client):
        """Create a template todo."""
        response = client.post(
            "/api/todos",
            json={"title": "Generate test", "category": "work"}
        )
        return response.json()

    @pytest.fixture
    def recurring_pattern(self, client, template_todo):
        """Create a recurring pattern."""
        response = client.post(
            "/api/recurring",
            json={
                "pattern": "daily",
                "interval": 1,
                "template_todo_id": template_todo["id"]
            }
        )
        return response.json()

    def test_generate_occurrence(self, client, recurring_pattern):
        """Test generating an occurrence from a pattern."""
        response = client.post(f"/api/recurring/{recurring_pattern['id']}/generate")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "title" in data

    def test_generate_occurrence_not_found(self, client):
        """Test generating occurrence for non-existent pattern."""
        response = client.post("/api/recurring/non-existent-id/generate")
        assert response.status_code == 404


class TestPreviewOccurrences:
    """Tests for GET /api/recurring/{id}/preview endpoint."""

    @pytest.fixture
    def template_todo(self, client):
        """Create a template todo."""
        response = client.post(
            "/api/todos",
            json={"title": "Preview test", "category": "work"}
        )
        return response.json()

    @pytest.fixture
    def recurring_pattern(self, client, template_todo):
        """Create a recurring pattern."""
        response = client.post(
            "/api/recurring",
            json={
                "pattern": "daily",
                "interval": 1,
                "template_todo_id": template_todo["id"]
            }
        )
        return response.json()

    def test_preview_occurrences(self, client, recurring_pattern):
        """Test previewing upcoming occurrences."""
        response = client.get(f"/api/recurring/{recurring_pattern['id']}/preview?count=5")
        assert response.status_code == 200
        data = response.json()
        assert "upcoming_occurrences" in data
        assert len(data["upcoming_occurrences"]) <= 5


class TestDeleteRecurring:
    """Tests for DELETE /api/recurring/{id} endpoint."""

    @pytest.fixture
    def template_todo(self, client):
        """Create a template todo."""
        response = client.post(
            "/api/todos",
            json={"title": "Delete test", "category": "work"}
        )
        return response.json()

    @pytest.fixture
    def recurring_pattern(self, client, template_todo):
        """Create a recurring pattern."""
        response = client.post(
            "/api/recurring",
            json={
                "pattern": "daily",
                "interval": 1,
                "template_todo_id": template_todo["id"]
            }
        )
        return response.json()

    def test_delete_recurring(self, client, recurring_pattern):
        """Test deleting a recurring pattern."""
        response = client.delete(f"/api/recurring/{recurring_pattern['id']}")
        assert response.status_code == 200
        assert response.json()["deleted"] is True

    def test_delete_recurring_not_found(self, client):
        """Test deleting non-existent recurring pattern."""
        response = client.delete("/api/recurring/non-existent-id")
        assert response.status_code == 404
