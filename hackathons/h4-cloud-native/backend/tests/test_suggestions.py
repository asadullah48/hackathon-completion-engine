"""Tests for AI Suggestions API."""
import pytest


class TestGetSuggestions:
    """Tests for GET /api/suggestions endpoint."""

    def test_get_suggestions_empty(self, client, test_user):
        """Test getting suggestions when none exist."""
        response = client.get(f"/api/suggestions?user_id={test_user['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_get_suggestions_with_status_filter(self, client, test_user):
        """Test getting suggestions with status filter."""
        response = client.get(
            f"/api/suggestions?user_id={test_user['id']}&status=pending"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_suggestions_invalid_status(self, client, test_user):
        """Test getting suggestions with invalid status."""
        response = client.get(
            f"/api/suggestions?user_id={test_user['id']}&status=invalid"
        )
        assert response.status_code == 400


class TestGenerateSuggestions:
    """Tests for POST /api/suggestions/generate/{todo_id} endpoint."""

    @pytest.fixture
    def test_todo(self, client, test_user):
        """Create a test todo."""
        response = client.post(
            "/api/todos",
            json={
                "title": "Urgent: Complete this important task",
                "description": "This is an urgent deadline task",
                "category": "work",
                "priority": "low",
                "owner_id": test_user["id"]
            }
        )
        return response.json()

    def test_generate_suggestions_for_todo(self, client, test_user, test_todo):
        """Test generating suggestions for a todo."""
        response = client.post(
            f"/api/suggestions/generate/{test_todo['id']}?user_id={test_user['id']}"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "suggestion_type" in data[0]
            assert "title" in data[0]
            assert "confidence" in data[0]

    def test_generate_suggestions_todo_not_found(self, client, test_user):
        """Test generating suggestions for non-existent todo."""
        response = client.post(
            f"/api/suggestions/generate/non-existent-id?user_id={test_user['id']}"
        )
        assert response.status_code == 404


class TestGenerateInsights:
    """Tests for POST /api/suggestions/insights/{user_id} endpoint."""

    def test_generate_insights_no_todos(self, client, test_user):
        """Test generating insights when user has no todos."""
        response = client.post(f"/api/suggestions/insights/{test_user['id']}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_generate_insights_with_todos(self, client, test_user):
        """Test generating insights when user has todos."""
        client.post(
            "/api/todos",
            json={
                "title": "Test task for insights",
                "category": "work",
                "priority": "medium",
                "owner_id": test_user["id"]
            }
        )
        response = client.post(f"/api/suggestions/insights/{test_user['id']}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestUpdateSuggestion:
    """Tests for PUT /api/suggestions/{suggestion_id} endpoint."""

    @pytest.fixture
    def test_todo(self, client, test_user):
        """Create a test todo."""
        response = client.post(
            "/api/todos",
            json={
                "title": "Urgent: Complete this important task",
                "description": "This is an urgent deadline task",
                "category": "work",
                "priority": "low",
                "owner_id": test_user["id"]
            }
        )
        return response.json()

    def test_update_suggestion_status(self, client, test_user, test_todo):
        """Test updating a suggestion's status."""
        gen_response = client.post(
            f"/api/suggestions/generate/{test_todo['id']}?user_id={test_user['id']}"
        )
        suggestions = gen_response.json()

        if len(suggestions) > 0:
            suggestion_id = suggestions[0]["id"]
            response = client.put(
                f"/api/suggestions/{suggestion_id}",
                json={"status": "dismissed"}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "dismissed"

    def test_update_suggestion_not_found(self, client):
        """Test updating non-existent suggestion."""
        response = client.put(
            "/api/suggestions/non-existent-id",
            json={"status": "dismissed"}
        )
        assert response.status_code == 404

    def test_update_suggestion_invalid_status(self, client, test_user, test_todo):
        """Test updating suggestion with invalid status."""
        gen_response = client.post(
            f"/api/suggestions/generate/{test_todo['id']}?user_id={test_user['id']}"
        )
        suggestions = gen_response.json()

        if len(suggestions) > 0:
            suggestion_id = suggestions[0]["id"]
            response = client.put(
                f"/api/suggestions/{suggestion_id}",
                json={"status": "invalid_status"}
            )
            assert response.status_code == 400


class TestApplySuggestion:
    """Tests for POST /api/suggestions/{suggestion_id}/apply endpoint."""

    @pytest.fixture
    def test_todo(self, client, test_user):
        """Create a test todo."""
        response = client.post(
            "/api/todos",
            json={
                "title": "Urgent: Complete this important task",
                "description": "This is an urgent deadline task",
                "category": "work",
                "priority": "low",
                "owner_id": test_user["id"]
            }
        )
        return response.json()

    def test_apply_suggestion(self, client, test_user, test_todo):
        """Test applying a suggestion to a todo."""
        gen_response = client.post(
            f"/api/suggestions/generate/{test_todo['id']}?user_id={test_user['id']}"
        )
        suggestions = gen_response.json()
        actionable = [s for s in suggestions if s.get("is_actionable", False)]

        if len(actionable) > 0:
            suggestion_id = actionable[0]["id"]
            response = client.post(f"/api/suggestions/{suggestion_id}/apply")
            assert response.status_code == 200
            data = response.json()
            assert "suggestion_id" in data
            assert "applied_changes" in data

    def test_apply_suggestion_not_found(self, client):
        """Test applying non-existent suggestion."""
        response = client.post("/api/suggestions/non-existent-id/apply")
        assert response.status_code == 404


class TestDeleteSuggestion:
    """Tests for DELETE /api/suggestions/{suggestion_id} endpoint."""

    @pytest.fixture
    def test_todo(self, client, test_user):
        """Create a test todo."""
        response = client.post(
            "/api/todos",
            json={
                "title": "Urgent: Complete this important task",
                "description": "This is an urgent deadline task",
                "category": "work",
                "priority": "low",
                "owner_id": test_user["id"]
            }
        )
        return response.json()

    def test_delete_suggestion(self, client, test_user, test_todo):
        """Test deleting a suggestion."""
        gen_response = client.post(
            f"/api/suggestions/generate/{test_todo['id']}?user_id={test_user['id']}"
        )
        suggestions = gen_response.json()

        if len(suggestions) > 0:
            suggestion_id = suggestions[0]["id"]
            response = client.delete(f"/api/suggestions/{suggestion_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == suggestion_id

    def test_delete_suggestion_not_found(self, client):
        """Test deleting non-existent suggestion."""
        response = client.delete("/api/suggestions/non-existent-id")
        assert response.status_code == 404
