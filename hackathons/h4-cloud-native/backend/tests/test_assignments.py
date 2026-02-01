"""Tests for todo assignments API."""
import pytest


class TestAssignTodo:
    """Tests for POST /api/todos/{todo_id}/assign endpoint."""

    @pytest.fixture
    def test_team(self, client, test_user):
        """Create a test team."""
        response = client.post(
            "/api/teams",
            json={
                "name": "Assignment Team",
                "owner_id": test_user["id"]
            }
        )
        return response.json()

    @pytest.fixture
    def second_user(self, client):
        """Create a second user."""
        response = client.post(
            "/api/users",
            json={
                "email": "assignee@example.com",
                "display_name": "Assignee User"
            }
        )
        return response.json()

    @pytest.fixture
    def test_todo(self, client, test_user):
        """Create a test todo."""
        response = client.post(
            "/api/todos",
            json={
                "title": "Assignment test todo",
                "category": "work",
                "owner_id": test_user["id"]
            }
        )
        return response.json()

    def test_assign_todo(self, client, test_todo, test_user, second_user, test_team):
        """Test assigning a todo to a user."""
        # Add second user to team first
        client.post(
            f"/api/teams/{test_team['id']}/members?added_by={test_user['id']}",
            json={"user_id": second_user["id"], "role": "editor"}
        )

        response = client.post(
            f"/api/todos/{test_todo['id']}/assign?assigned_by={test_user['id']}",
            json={
                "assignee_id": second_user["id"],
                "team_id": test_team["id"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["todo_id"] == test_todo["id"]
        assert data["assignee_id"] == second_user["id"]
        assert data["status"] == "assigned"

    def test_assign_todo_with_due_date(self, client, test_todo, test_user, second_user, test_team):
        """Test assigning todo with due date."""
        client.post(
            f"/api/teams/{test_team['id']}/members?added_by={test_user['id']}",
            json={"user_id": second_user["id"], "role": "editor"}
        )

        response = client.post(
            f"/api/todos/{test_todo['id']}/assign?assigned_by={test_user['id']}",
            json={
                "assignee_id": second_user["id"],
                "team_id": test_team["id"],
                "due_date": "2024-12-31T23:59:59"
            }
        )
        assert response.status_code == 200
        assert "due_date" in response.json()

    def test_assign_todo_with_notes(self, client, test_todo, test_user, second_user, test_team):
        """Test assigning todo with notes."""
        client.post(
            f"/api/teams/{test_team['id']}/members?added_by={test_user['id']}",
            json={"user_id": second_user["id"], "role": "editor"}
        )

        response = client.post(
            f"/api/todos/{test_todo['id']}/assign?assigned_by={test_user['id']}",
            json={
                "assignee_id": second_user["id"],
                "team_id": test_team["id"],
                "notes": "Please complete by end of week"
            }
        )
        assert response.status_code == 200
        assert response.json()["notes"] == "Please complete by end of week"

    def test_assign_todo_not_found(self, client, test_user, second_user):
        """Test assigning non-existent todo."""
        response = client.post(
            f"/api/todos/non-existent-id/assign?assigned_by={test_user['id']}",
            json={
                "assignee_id": second_user["id"]
            }
        )
        assert response.status_code == 404


class TestGetAssignments:
    """Tests for GET /api/todos/{todo_id}/assignments endpoint."""

    @pytest.fixture
    def test_team(self, client, test_user):
        """Create a test team."""
        response = client.post(
            "/api/teams",
            json={
                "name": "Get Assignment Team",
                "owner_id": test_user["id"]
            }
        )
        return response.json()

    @pytest.fixture
    def second_user(self, client):
        """Create a second user."""
        response = client.post(
            "/api/users",
            json={
                "email": "getassignee@example.com",
                "display_name": "Get Assignee"
            }
        )
        return response.json()

    @pytest.fixture
    def test_todo(self, client, test_user):
        """Create a test todo."""
        response = client.post(
            "/api/todos",
            json={
                "title": "Get assignments todo",
                "category": "work",
                "owner_id": test_user["id"]
            }
        )
        return response.json()

    def test_get_assignments_empty(self, client, test_todo):
        """Test getting assignments when none exist."""
        response = client.get(f"/api/todos/{test_todo['id']}/assignments")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_assignments_with_data(self, client, test_todo, test_user, second_user, test_team):
        """Test getting assignments for a todo."""
        # Add member and create assignment
        client.post(
            f"/api/teams/{test_team['id']}/members?added_by={test_user['id']}",
            json={"user_id": second_user["id"], "role": "editor"}
        )

        client.post(
            f"/api/todos/{test_todo['id']}/assign?assigned_by={test_user['id']}",
            json={
                "assignee_id": second_user["id"],
                "team_id": test_team["id"]
            }
        )

        response = client.get(f"/api/todos/{test_todo['id']}/assignments")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1


class TestUpdateAssignment:
    """Tests for PUT /api/assignments/{assignment_id} endpoint."""

    @pytest.fixture
    def test_team(self, client, test_user):
        """Create a test team."""
        response = client.post(
            "/api/teams",
            json={
                "name": "Update Assignment Team",
                "owner_id": test_user["id"]
            }
        )
        return response.json()

    @pytest.fixture
    def second_user(self, client):
        """Create a second user."""
        response = client.post(
            "/api/users",
            json={
                "email": "updateassignee@example.com",
                "display_name": "Update Assignee"
            }
        )
        return response.json()

    @pytest.fixture
    def test_todo(self, client, test_user):
        """Create a test todo."""
        response = client.post(
            "/api/todos",
            json={
                "title": "Update assignment todo",
                "category": "work",
                "owner_id": test_user["id"]
            }
        )
        return response.json()

    @pytest.fixture
    def test_assignment(self, client, test_todo, test_user, second_user, test_team):
        """Create a test assignment."""
        client.post(
            f"/api/teams/{test_team['id']}/members?added_by={test_user['id']}",
            json={"user_id": second_user["id"], "role": "editor"}
        )

        response = client.post(
            f"/api/todos/{test_todo['id']}/assign?assigned_by={test_user['id']}",
            json={
                "assignee_id": second_user["id"],
                "team_id": test_team["id"]
            }
        )
        return response.json()

    def test_update_assignment_status_accepted(self, client, test_assignment):
        """Test updating assignment status to accepted."""
        response = client.put(
            f"/api/assignments/{test_assignment['id']}",
            json={"status": "accepted"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "accepted"

    def test_update_assignment_status_in_progress(self, client, test_assignment):
        """Test updating assignment status to in_progress."""
        response = client.put(
            f"/api/assignments/{test_assignment['id']}",
            json={"status": "in_progress"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "in_progress"

    def test_update_assignment_status_completed(self, client, test_assignment):
        """Test updating assignment status to completed."""
        response = client.put(
            f"/api/assignments/{test_assignment['id']}",
            json={"status": "completed"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "completed"

    def test_update_assignment_status_declined(self, client, test_assignment):
        """Test updating assignment status to declined."""
        response = client.put(
            f"/api/assignments/{test_assignment['id']}",
            json={"status": "declined"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "declined"

    def test_update_assignment_not_found(self, client):
        """Test updating non-existent assignment."""
        response = client.put(
            "/api/assignments/non-existent-id",
            json={"status": "accepted"}
        )
        assert response.status_code == 404

    def test_update_assignment_invalid_status(self, client, test_assignment):
        """Test updating assignment with invalid status."""
        response = client.put(
            f"/api/assignments/{test_assignment['id']}",
            json={"status": "invalid_status"}
        )
        assert response.status_code == 400


class TestDeleteAssignment:
    """Tests for DELETE /api/assignments/{assignment_id} endpoint."""

    @pytest.fixture
    def test_team(self, client, test_user):
        """Create a test team."""
        response = client.post(
            "/api/teams",
            json={
                "name": "Delete Assignment Team",
                "owner_id": test_user["id"]
            }
        )
        return response.json()

    @pytest.fixture
    def second_user(self, client):
        """Create a second user."""
        response = client.post(
            "/api/users",
            json={
                "email": "deleteassignee@example.com",
                "display_name": "Delete Assignee"
            }
        )
        return response.json()

    @pytest.fixture
    def test_todo(self, client, test_user):
        """Create a test todo."""
        response = client.post(
            "/api/todos",
            json={
                "title": "Delete assignment todo",
                "category": "work",
                "owner_id": test_user["id"]
            }
        )
        return response.json()

    @pytest.fixture
    def test_assignment(self, client, test_todo, test_user, second_user, test_team):
        """Create a test assignment."""
        client.post(
            f"/api/teams/{test_team['id']}/members?added_by={test_user['id']}",
            json={"user_id": second_user["id"], "role": "editor"}
        )

        response = client.post(
            f"/api/todos/{test_todo['id']}/assign?assigned_by={test_user['id']}",
            json={
                "assignee_id": second_user["id"],
                "team_id": test_team["id"]
            }
        )
        return response.json()

    def test_delete_assignment(self, client, test_assignment):
        """Test deleting an assignment."""
        response = client.delete(f"/api/assignments/{test_assignment['id']}")
        assert response.status_code == 200

    def test_delete_assignment_not_found(self, client):
        """Test deleting non-existent assignment."""
        response = client.delete("/api/assignments/non-existent-id")
        assert response.status_code == 404


class TestUserAssignments:
    """Tests for GET /api/users/{user_id}/assignments endpoint."""

    @pytest.fixture
    def test_team(self, client, test_user):
        """Create a test team."""
        response = client.post(
            "/api/teams",
            json={
                "name": "User Assignments Team",
                "owner_id": test_user["id"]
            }
        )
        return response.json()

    @pytest.fixture
    def second_user(self, client):
        """Create a second user."""
        response = client.post(
            "/api/users",
            json={
                "email": "userassignments@example.com",
                "display_name": "User Assignments"
            }
        )
        return response.json()

    def test_get_user_assignments_empty(self, client, second_user):
        """Test getting user assignments when none exist."""
        response = client.get(f"/api/users/{second_user['id']}/assignments")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_user_assignments_with_data(self, client, test_user, second_user, test_team):
        """Test getting user's assignments."""
        # Add member to team
        client.post(
            f"/api/teams/{test_team['id']}/members?added_by={test_user['id']}",
            json={"user_id": second_user["id"], "role": "editor"}
        )

        # Create todo and assign
        todo_response = client.post(
            "/api/todos",
            json={
                "title": "User assignment todo",
                "category": "work",
                "owner_id": test_user["id"]
            }
        )
        todo = todo_response.json()

        client.post(
            f"/api/todos/{todo['id']}/assign?assigned_by={test_user['id']}",
            json={
                "assignee_id": second_user["id"],
                "team_id": test_team["id"]
            }
        )

        response = client.get(f"/api/users/{second_user['id']}/assignments")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_get_user_assignments_with_status_filter(self, client, test_user, second_user, test_team):
        """Test filtering user assignments by status."""
        response = client.get(
            f"/api/users/{second_user['id']}/assignments?status=assigned"
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
