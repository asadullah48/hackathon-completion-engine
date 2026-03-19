"""Tests for recurring todo functionality."""
import pytest


@pytest.fixture
def template_todo(client):
    """Create a template todo for recurring patterns."""
    response = client.post("/api/todos", json={
        "title": "Daily standup meeting",
        "description": "Morning team sync",
        "category": "work",
        "priority": "medium"
    })
    assert response.status_code == 201
    return response.json()


class TestRecurringCreate:
    """Tests for creating recurring patterns."""

    def test_create_daily_recurring(self, client, template_todo):
        """Test creating a daily recurring pattern."""
        response = client.post("/api/recurring", json={
            "pattern": "daily",
            "interval": 1,
            "template_todo_id": template_todo["id"]
        })

        assert response.status_code == 201
        data = response.json()
        assert data["pattern"] == "daily"
        assert data["interval"] == 1
        assert data["is_active"] == True
        assert data["next_occurrence"] is not None

    def test_create_weekly_recurring(self, client, template_todo):
        """Test creating a weekly recurring pattern with specific days."""
        response = client.post("/api/recurring", json={
            "pattern": "weekly",
            "interval": 1,
            "days_of_week": [0, 2, 4],  # Mon, Wed, Fri
            "template_todo_id": template_todo["id"]
        })

        assert response.status_code == 201
        data = response.json()
        assert data["pattern"] == "weekly"
        assert data["days_of_week"] == [0, 2, 4]

    def test_create_monthly_recurring(self, client, template_todo):
        """Test creating a monthly recurring pattern."""
        response = client.post("/api/recurring", json={
            "pattern": "monthly",
            "interval": 1,
            "day_of_month": 15,
            "template_todo_id": template_todo["id"]
        })

        assert response.status_code == 201
        data = response.json()
        assert data["pattern"] == "monthly"
        assert data["day_of_month"] == 15

    def test_create_recurring_invalid_template(self, client):
        """Test creating recurring with non-existent template."""
        response = client.post("/api/recurring", json={
            "pattern": "daily",
            "interval": 1,
            "template_todo_id": "invalid-id"
        })

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_create_recurring_invalid_pattern(self, client, template_todo):
        """Test creating recurring with invalid pattern."""
        response = client.post("/api/recurring", json={
            "pattern": "invalid",
            "interval": 1,
            "template_todo_id": template_todo["id"]
        })

        assert response.status_code == 400


class TestRecurringList:
    """Tests for listing recurring patterns."""

    def test_list_recurring_empty(self, client):
        """Test listing when no recurring patterns exist."""
        response = client.get("/api/recurring")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_recurring(self, client, template_todo):
        """Test listing recurring patterns."""
        # Create some patterns
        client.post("/api/recurring", json={
            "pattern": "daily",
            "interval": 1,
            "template_todo_id": template_todo["id"]
        })
        client.post("/api/recurring", json={
            "pattern": "weekly",
            "interval": 1,
            "template_todo_id": template_todo["id"]
        })

        response = client.get("/api/recurring")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


class TestRecurringGenerate:
    """Tests for generating occurrences."""

    def test_generate_occurrence(self, client, template_todo):
        """Test manually generating an occurrence."""
        # Create recurring pattern
        create_response = client.post("/api/recurring", json={
            "pattern": "daily",
            "interval": 1,
            "template_todo_id": template_todo["id"]
        })
        recurring_id = create_response.json()["id"]

        # Generate occurrence
        response = client.post(f"/api/recurring/{recurring_id}/generate")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["title"] == template_todo["title"]

    def test_preview_occurrences(self, client, template_todo):
        """Test previewing upcoming occurrences."""
        # Create recurring pattern
        create_response = client.post("/api/recurring", json={
            "pattern": "daily",
            "interval": 1,
            "template_todo_id": template_todo["id"]
        })
        recurring_id = create_response.json()["id"]

        # Preview occurrences
        response = client.get(f"/api/recurring/{recurring_id}/preview?count=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["upcoming_occurrences"]) == 5


class TestRecurringDelete:
    """Tests for deleting recurring patterns."""

    def test_delete_recurring(self, client, template_todo):
        """Test deleting a recurring pattern."""
        # Create pattern
        create_response = client.post("/api/recurring", json={
            "pattern": "daily",
            "interval": 1,
            "template_todo_id": template_todo["id"]
        })
        recurring_id = create_response.json()["id"]

        # Delete pattern
        response = client.delete(f"/api/recurring/{recurring_id}")
        assert response.status_code == 200
        assert response.json()["deleted"] == True

        # Verify deleted
        response = client.get(f"/api/recurring/{recurring_id}")
        assert response.status_code == 404
