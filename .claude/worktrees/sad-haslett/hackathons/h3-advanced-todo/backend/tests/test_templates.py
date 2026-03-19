"""Tests for templates functionality."""
import pytest


class TestGetTemplates:
    """Tests for GET /api/templates endpoint."""

    def test_get_all_templates(self, client):
        """Test getting all templates including built-in ones."""
        response = client.get("/api/templates")
        assert response.status_code == 200
        data = response.json()
        # Should have built-in templates
        assert isinstance(data, list)

    def test_get_template_by_id(self, client):
        """Test getting a specific template."""
        # First get all templates
        response = client.get("/api/templates")
        templates = response.json()

        if len(templates) > 0:
            template_id = templates[0]["id"]
            response = client.get(f"/api/templates/{template_id}")
            assert response.status_code == 200
            assert response.json()["id"] == template_id

    def test_get_template_not_found(self, client):
        """Test getting non-existent template."""
        response = client.get("/api/templates/non-existent-id")
        assert response.status_code == 404

    def test_filter_templates_by_category(self, client):
        """Test filtering templates by category."""
        response = client.get("/api/templates?category=work")
        assert response.status_code == 200

    def test_search_templates(self, client):
        """Test searching templates."""
        response = client.get("/api/templates?search=project")
        assert response.status_code == 200


class TestCreateTemplate:
    """Tests for POST /api/templates endpoint."""

    def test_create_template(self, client):
        """Test creating a new template."""
        response = client.post(
            "/api/templates",
            json={
                "name": "My Custom Template",
                "description": "A custom template for testing",
                "category": "work",
                "todos": [
                    {"title": "Task 1", "priority": "high"},
                    {"title": "Task 2", "priority": "medium"},
                    {"title": "Task 3", "priority": "low"}
                ],
                "tags": ["custom", "test"]
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My Custom Template"
        assert len(data["todos"]) == 3
        assert data["usage_count"] == 0

    def test_create_template_minimal(self, client):
        """Test creating a template with minimal data."""
        response = client.post(
            "/api/templates",
            json={
                "name": "Minimal Template",
                "todos": [{"title": "Single task"}]
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Template"


class TestUseTemplate:
    """Tests for POST /api/templates/{id}/use endpoint."""

    def test_use_template(self, client):
        """Test using a template to create todos."""
        # Create a template first
        create_response = client.post(
            "/api/templates",
            json={
                "name": "Test Template",
                "todos": [
                    {"title": "Todo 1", "category": "work", "priority": "high"},
                    {"title": "Todo 2", "category": "work", "priority": "medium"}
                ]
            }
        )
        template_id = create_response.json()["id"]

        # Use the template
        response = client.post(f"/api/templates/{template_id}/use")
        assert response.status_code == 200
        data = response.json()
        assert data["created"] == 2
        assert len(data["todos"]) == 2

    def test_use_template_increments_usage(self, client):
        """Test that using a template increments its usage count."""
        # Create a template
        create_response = client.post(
            "/api/templates",
            json={
                "name": "Usage Count Template",
                "todos": [{"title": "Task"}]
            }
        )
        template_id = create_response.json()["id"]
        assert create_response.json()["usage_count"] == 0

        # Use the template
        client.post(f"/api/templates/{template_id}/use")

        # Check usage count
        get_response = client.get(f"/api/templates/{template_id}")
        assert get_response.json()["usage_count"] == 1

    def test_use_template_not_found(self, client):
        """Test using non-existent template."""
        response = client.post("/api/templates/non-existent-id/use")
        assert response.status_code == 404

    def test_use_template_with_blocked_content(self, client):
        """Test using a template that contains blocked content."""
        # Create a template with blocked content
        create_response = client.post(
            "/api/templates",
            json={
                "name": "Blocked Template",
                "todos": [
                    {"title": "Study for exam", "priority": "high"},
                    {"title": "Do my homework assignment", "priority": "low"}
                ]
            }
        )
        template_id = create_response.json()["id"]

        # Use the template - blocked todos should be skipped
        response = client.post(f"/api/templates/{template_id}/use")
        assert response.status_code == 200
        data = response.json()
        # One todo should be blocked
        assert data["blocked"] >= 1


class TestPreviewTemplate:
    """Tests for GET /api/templates/{id}/preview endpoint."""

    def test_preview_template(self, client):
        """Test previewing a template."""
        # Create a template
        create_response = client.post(
            "/api/templates",
            json={
                "name": "Preview Template",
                "todos": [
                    {"title": "Task 1", "relative_deadline_days": 1},
                    {"title": "Task 2", "relative_deadline_days": 3}
                ]
            }
        )
        template_id = create_response.json()["id"]

        response = client.get(f"/api/templates/{template_id}/preview")
        assert response.status_code == 200
        data = response.json()
        assert "template_name" in data
        assert "todos" in data
        assert len(data["todos"]) == 2


class TestDeleteTemplate:
    """Tests for DELETE /api/templates/{id} endpoint."""

    def test_delete_template(self, client):
        """Test deleting a template."""
        # Create a template
        create_response = client.post(
            "/api/templates",
            json={
                "name": "Delete Template",
                "todos": [{"title": "Task"}]
            }
        )
        template_id = create_response.json()["id"]

        response = client.delete(f"/api/templates/{template_id}")
        assert response.status_code == 200
        assert response.json()["deleted"] is True

        # Verify deleted
        get_response = client.get(f"/api/templates/{template_id}")
        assert get_response.status_code == 404

    def test_delete_template_not_found(self, client):
        """Test deleting non-existent template."""
        response = client.delete("/api/templates/non-existent-id")
        assert response.status_code == 404
