"""Tests for template functionality."""
import pytest


class TestTemplateSeeding:
    """Tests for built-in template seeding."""

    def test_builtin_templates_seeded(self, client):
        """Test that built-in templates are seeded on startup."""
        response = client.get("/api/templates")
        assert response.status_code == 200
        data = response.json()

        # Should have 5 built-in templates
        assert len(data) >= 5

        # Check expected templates exist
        template_names = [t["name"] for t in data]
        assert "Project Kickoff" in template_names
        assert "Weekly Exercise Routine" in template_names
        assert "Exam Preparation" in template_names
        assert "Code Review Checklist" in template_names
        assert "Daily Morning Routine" in template_names

    def test_system_templates_not_deletable(self, client):
        """Test that system templates cannot be deleted."""
        # Get a system template
        response = client.get("/api/templates")
        system_template = next(
            t for t in response.json() if t["created_by"] == "system"
        )

        # Try to delete
        response = client.delete(f"/api/templates/{system_template['id']}")
        assert response.status_code == 403
        assert "system template" in response.json()["detail"].lower()


class TestTemplateCreate:
    """Tests for creating templates."""

    def test_create_template(self, client):
        """Test creating a new template."""
        response = client.post("/api/templates", json={
            "name": "Test Template",
            "description": "A test template",
            "category": "work",
            "todos": [
                {"title": "Task 1", "priority": "high"},
                {"title": "Task 2", "priority": "medium"}
            ],
            "tags": ["test", "work"]
        })

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Template"
        assert len(data["todos"]) == 2
        assert data["usage_count"] == 0
        assert data["created_by"] == "user"

    def test_create_template_with_relative_deadlines(self, client):
        """Test creating template with relative deadlines."""
        response = client.post("/api/templates", json={
            "name": "Project Template",
            "todos": [
                {"title": "Day 1 task", "relative_deadline_days": 1, "priority": "high"},
                {"title": "Day 3 task", "relative_deadline_days": 3, "priority": "medium"},
                {"title": "Week task", "relative_deadline_days": 7, "priority": "low"}
            ]
        })

        assert response.status_code == 201
        data = response.json()
        assert data["todos"][0]["relative_deadline_days"] == 1
        assert data["todos"][1]["relative_deadline_days"] == 3
        assert data["todos"][2]["relative_deadline_days"] == 7


class TestTemplateUse:
    """Tests for using templates to create todos."""

    def test_use_template_creates_todos(self, client):
        """Test that using a template creates todos."""
        # Create a template
        create_response = client.post("/api/templates", json={
            "name": "Test Template",
            "todos": [
                {"title": "Task 1", "category": "work", "priority": "high"},
                {"title": "Task 2", "category": "personal", "priority": "medium"}
            ]
        })
        template_id = create_response.json()["id"]

        # Use the template
        response = client.post(f"/api/templates/{template_id}/use")
        assert response.status_code == 200
        data = response.json()
        assert data["created"] == 2
        assert len(data["todos"]) == 2

    def test_use_template_with_deadlines(self, client):
        """Test that relative deadlines are calculated correctly."""
        # Create a template with deadlines
        create_response = client.post("/api/templates", json={
            "name": "Deadline Template",
            "todos": [
                {"title": "Task 1", "relative_deadline_days": 1, "priority": "high"},
                {"title": "Task 2", "relative_deadline_days": 3, "priority": "medium"}
            ]
        })
        template_id = create_response.json()["id"]

        # Use the template
        response = client.post(f"/api/templates/{template_id}/use")
        assert response.status_code == 200
        data = response.json()

        # Check deadlines are set
        for todo in data["todos"]:
            assert todo["deadline"] is not None

    def test_use_template_increases_usage_count(self, client):
        """Test that usage count increases when template is used."""
        # Create a template
        create_response = client.post("/api/templates", json={
            "name": "Usage Template",
            "todos": [{"title": "Task", "priority": "medium"}]
        })
        template_id = create_response.json()["id"]

        # Use the template twice
        client.post(f"/api/templates/{template_id}/use")
        client.post(f"/api/templates/{template_id}/use")

        # Check usage count
        response = client.get(f"/api/templates/{template_id}")
        assert response.json()["usage_count"] == 2

    def test_use_template_constitutional_check(self, client):
        """Test that constitutional check is applied to template todos."""
        # Create a template with a blocked todo
        create_response = client.post("/api/templates", json={
            "name": "Blocked Template",
            "todos": [
                {"title": "Normal task", "priority": "high"},
                {"title": "Do my homework for me", "priority": "high"}  # Should be blocked
            ]
        })
        template_id = create_response.json()["id"]

        # Use the template
        response = client.post(f"/api/templates/{template_id}/use")
        assert response.status_code == 200
        data = response.json()

        # Only 1 todo should be created, 1 should be blocked
        assert data["created"] == 1
        assert data["blocked"] == 1


class TestTemplatePreview:
    """Tests for template preview functionality."""

    def test_preview_template(self, client):
        """Test previewing template todos."""
        # Create a template
        create_response = client.post("/api/templates", json={
            "name": "Preview Template",
            "todos": [
                {"title": "Task 1", "relative_deadline_days": 1, "priority": "high"},
                {"title": "Task 2", "relative_deadline_days": 3, "priority": "medium"}
            ]
        })
        template_id = create_response.json()["id"]

        # Preview the template
        response = client.get(f"/api/templates/{template_id}/preview")
        assert response.status_code == 200
        data = response.json()

        assert data["template_name"] == "Preview Template"
        assert len(data["todos"]) == 2
        for todo in data["todos"]:
            assert "deadline" in todo
            assert "constitutional_decision" in todo


class TestTemplateSearch:
    """Tests for searching and filtering templates."""

    def test_search_templates_by_name(self, client):
        """Test searching templates by name."""
        # Create templates
        client.post("/api/templates", json={
            "name": "Unique Template Name",
            "todos": [{"title": "Task", "priority": "medium"}]
        })

        # Search
        response = client.get("/api/templates?search=Unique")
        assert response.status_code == 200
        data = response.json()

        found = [t for t in data if t["name"] == "Unique Template Name"]
        assert len(found) == 1

    def test_filter_templates_by_category(self, client):
        """Test filtering templates by category."""
        # Create template with category
        client.post("/api/templates", json={
            "name": "Health Template",
            "category": "health",
            "todos": [{"title": "Exercise", "priority": "medium"}]
        })

        # Filter
        response = client.get("/api/templates?category=health")
        assert response.status_code == 200
        data = response.json()

        # Should include our template and possibly the built-in health template
        health_templates = [t for t in data if t["category"] == "health"]
        assert len(health_templates) >= 1


class TestTemplateDelete:
    """Tests for deleting templates."""

    def test_delete_user_template(self, client):
        """Test deleting a user-created template."""
        # Create a template
        create_response = client.post("/api/templates", json={
            "name": "Deletable Template",
            "todos": [{"title": "Task", "priority": "medium"}]
        })
        template_id = create_response.json()["id"]

        # Delete
        response = client.delete(f"/api/templates/{template_id}")
        assert response.status_code == 200
        assert response.json()["deleted"] == True

        # Verify deleted
        response = client.get(f"/api/templates/{template_id}")
        assert response.status_code == 404
