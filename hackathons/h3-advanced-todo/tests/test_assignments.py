"""
Tests for Todo Assignment API endpoints.
H3 Session 2 - Team Collaboration
"""
import pytest
from fastapi.testclient import TestClient


def create_user(client: TestClient, email: str, display_name: str) -> dict:
    """Helper to create a user."""
    response = client.post(
        "/api/users",
        json={"email": email, "display_name": display_name}
    )
    return response.json()


def create_team(client: TestClient, name: str, owner_id: str) -> dict:
    """Helper to create a team."""
    response = client.post(
        "/api/teams",
        json={"name": name, "owner_id": owner_id}
    )
    return response.json()


def add_member(client: TestClient, team_id: str, user_id: str, role: str, added_by: str) -> dict:
    """Helper to add a member to a team."""
    response = client.post(
        f"/api/teams/{team_id}/members",
        params={"added_by": added_by},
        json={"user_id": user_id, "role": role}
    )
    return response.json()


class TestAssignments:
    """Test todo assignment functionality."""

    def test_assign_todo_to_user(self, client: TestClient):
        """Test assigning a todo to a team member."""
        # Create owner and assignee
        owner = create_user(client, "assign_owner@example.com", "Owner")
        assignee = create_user(client, "assignee@example.com", "Assignee")

        # Create team
        team = create_team(client, "Assignment Team", owner["id"])

        # Add assignee to team
        add_member(client, team["id"], assignee["id"], "editor", owner["id"])

        # Create todo
        todo = client.post("/api/todos", json={"title": "Todo to assign"}).json()

        # Assign todo to the assignee
        response = client.post(
            f"/api/todos/{todo['id']}/assign",
            params={"assigned_by": owner["id"]},
            json={
                "assignee_id": assignee["id"],
                "team_id": team["id"]
            }
        )
        assert response.status_code == 200
        assignment = response.json()
        assert assignment["todo_id"] == todo["id"]
        assert assignment["assignee_id"] == assignee["id"]
        assert assignment["assigned_by"] == owner["id"]
        assert assignment["status"] == "assigned"

    def test_get_todo_assignments(self, client: TestClient):
        """Test getting all assignments for a todo."""
        # Create owner and assignees
        owner = create_user(client, "list_owner@example.com", "Owner")
        assignee1 = create_user(client, "list_assignee1@example.com", "Assignee 1")
        assignee2 = create_user(client, "list_assignee2@example.com", "Assignee 2")

        # Create team and add assignees
        team = create_team(client, "List Assignments Team", owner["id"])
        add_member(client, team["id"], assignee1["id"], "editor", owner["id"])
        add_member(client, team["id"], assignee2["id"], "editor", owner["id"])

        # Create todo
        todo = client.post("/api/todos", json={"title": "Multi-assign todo"}).json()

        # Create assignments
        for assignee in [assignee1, assignee2]:
            client.post(
                f"/api/todos/{todo['id']}/assign",
                params={"assigned_by": owner["id"]},
                json={"assignee_id": assignee["id"], "team_id": team["id"]}
            )

        # Get assignments
        response = client.get(f"/api/todos/{todo['id']}/assignments")
        assert response.status_code == 200
        assignments = response.json()
        assert len(assignments) == 2

    def test_update_assignment_status(self, client: TestClient):
        """Test updating assignment status."""
        # Create users
        owner = create_user(client, "status_owner@example.com", "Owner")
        assignee = create_user(client, "status_assignee@example.com", "Assignee")

        # Create team and add member
        team = create_team(client, "Status Team", owner["id"])
        add_member(client, team["id"], assignee["id"], "editor", owner["id"])

        # Create todo
        todo = client.post("/api/todos", json={"title": "Status todo"}).json()

        # Create assignment
        assignment_response = client.post(
            f"/api/todos/{todo['id']}/assign",
            params={"assigned_by": owner["id"]},
            json={"assignee_id": assignee["id"], "team_id": team["id"]}
        )
        assignment = assignment_response.json()

        # Update status to accepted
        response = client.put(
            f"/api/assignments/{assignment['id']}",
            json={"status": "accepted"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "accepted"

        # Update status to in_progress
        response = client.put(
            f"/api/assignments/{assignment['id']}",
            json={"status": "in_progress"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "in_progress"

        # Update status to completed
        response = client.put(
            f"/api/assignments/{assignment['id']}",
            json={"status": "completed"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "completed"

    def test_decline_assignment(self, client: TestClient):
        """Test declining an assignment."""
        # Create users
        owner = create_user(client, "decline_owner@example.com", "Owner")
        assignee = create_user(client, "decline_assignee@example.com", "Assignee")

        # Create team and add member
        team = create_team(client, "Decline Team", owner["id"])
        add_member(client, team["id"], assignee["id"], "editor", owner["id"])

        # Create todo
        todo = client.post("/api/todos", json={"title": "Decline todo"}).json()

        # Create assignment
        assignment = client.post(
            f"/api/todos/{todo['id']}/assign",
            params={"assigned_by": owner["id"]},
            json={"assignee_id": assignee["id"], "team_id": team["id"]}
        ).json()

        # Decline assignment
        response = client.put(
            f"/api/assignments/{assignment['id']}",
            json={"status": "declined"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "declined"

    def test_remove_assignment(self, client: TestClient):
        """Test removing an assignment."""
        # Create users
        owner = create_user(client, "remove_owner@example.com", "Owner")
        assignee = create_user(client, "remove_assignee@example.com", "Assignee")

        # Create team and add member
        team = create_team(client, "Remove Team", owner["id"])
        add_member(client, team["id"], assignee["id"], "editor", owner["id"])

        # Create todo
        todo = client.post("/api/todos", json={"title": "Remove todo"}).json()

        # Create assignment
        assignment = client.post(
            f"/api/todos/{todo['id']}/assign",
            params={"assigned_by": owner["id"]},
            json={"assignee_id": assignee["id"], "team_id": team["id"]}
        ).json()

        # Remove assignment
        response = client.delete(f"/api/assignments/{assignment['id']}")
        assert response.status_code == 200

        # Verify removed
        assignments = client.get(f"/api/todos/{todo['id']}/assignments").json()
        assert len(assignments) == 0

    def test_get_user_assignments(self, client: TestClient):
        """Test getting all assignments for a user."""
        # Create users
        owner = create_user(client, "user_assign_owner@example.com", "Owner")
        assignee = create_user(client, "user_assign_target@example.com", "Target")

        # Create team and add member
        team = create_team(client, "User Assignments Team", owner["id"])
        add_member(client, team["id"], assignee["id"], "editor", owner["id"])

        # Create multiple todos
        todos = []
        for i in range(3):
            todo = client.post("/api/todos", json={"title": f"User Todo {i}"}).json()
            todos.append(todo)

        # Assign all todos to assignee
        for todo in todos:
            client.post(
                f"/api/todos/{todo['id']}/assign",
                params={"assigned_by": owner["id"]},
                json={"assignee_id": assignee["id"], "team_id": team["id"]}
            )

        # Get user's assignments
        response = client.get(f"/api/users/{assignee['id']}/assignments")
        assert response.status_code == 200
        assignments = response.json()
        assert len(assignments) == 3

    def test_cannot_assign_to_non_team_member(self, client: TestClient):
        """Test that non-team members cannot be assigned team todos."""
        # Create users
        owner = create_user(client, "non_member_owner@example.com", "Owner")
        non_member = create_user(client, "non_member@example.com", "Non Member")

        # Create team (non_member is NOT added)
        team = create_team(client, "Non Member Team", owner["id"])

        # Create todo
        todo = client.post("/api/todos", json={"title": "Non member todo"}).json()

        # Try to assign to non-member with team_id
        response = client.post(
            f"/api/todos/{todo['id']}/assign",
            params={"assigned_by": owner["id"]},
            json={"assignee_id": non_member["id"], "team_id": team["id"]}
        )
        # Should fail - non-member cannot be assigned with team_id
        assert response.status_code == 400
        assert "not a team member" in response.json()["detail"]

    def test_duplicate_assignment_fails(self, client: TestClient):
        """Test that duplicate assignments are not allowed."""
        # Create users
        owner = create_user(client, "dupe_owner@example.com", "Owner")
        assignee = create_user(client, "dupe_assignee@example.com", "Assignee")

        # Create team and add member
        team = create_team(client, "Dupe Team", owner["id"])
        add_member(client, team["id"], assignee["id"], "editor", owner["id"])

        # Create todo
        todo = client.post("/api/todos", json={"title": "Dupe todo"}).json()

        # First assignment
        response1 = client.post(
            f"/api/todos/{todo['id']}/assign",
            params={"assigned_by": owner["id"]},
            json={"assignee_id": assignee["id"], "team_id": team["id"]}
        )
        assert response1.status_code == 200

        # Try duplicate assignment
        response2 = client.post(
            f"/api/todos/{todo['id']}/assign",
            params={"assigned_by": owner["id"]},
            json={"assignee_id": assignee["id"], "team_id": team["id"]}
        )
        assert response2.status_code == 400
        assert "already assigned" in response2.json()["detail"]

    def test_assignment_without_team(self, client: TestClient):
        """Test assigning a todo without a team context."""
        # Create users
        owner = create_user(client, "no_team_owner@example.com", "Owner")
        assignee = create_user(client, "no_team_assignee@example.com", "Assignee")

        # Create todo
        todo = client.post("/api/todos", json={"title": "No team todo"}).json()

        # Assign without team_id
        response = client.post(
            f"/api/todos/{todo['id']}/assign",
            params={"assigned_by": owner["id"]},
            json={"assignee_id": assignee["id"]}
        )
        assert response.status_code == 200
        assignment = response.json()
        assert assignment["team_id"] is None

    def test_assignment_with_notes(self, client: TestClient):
        """Test assigning with notes."""
        # Create users
        owner = create_user(client, "notes_owner@example.com", "Owner")
        assignee = create_user(client, "notes_assignee@example.com", "Assignee")

        # Create todo
        todo = client.post("/api/todos", json={"title": "Notes todo"}).json()

        # Assign with notes
        response = client.post(
            f"/api/todos/{todo['id']}/assign",
            params={"assigned_by": owner["id"]},
            json={
                "assignee_id": assignee["id"],
                "notes": "Please complete by Friday"
            }
        )
        assert response.status_code == 200
        assignment = response.json()
        assert assignment["notes"] == "Please complete by Friday"

    def test_update_assignment_notes(self, client: TestClient):
        """Test updating assignment notes."""
        # Create users
        owner = create_user(client, "update_notes_owner@example.com", "Owner")
        assignee = create_user(client, "update_notes_assignee@example.com", "Assignee")

        # Create todo and assignment
        todo = client.post("/api/todos", json={"title": "Update notes todo"}).json()
        assignment = client.post(
            f"/api/todos/{todo['id']}/assign",
            params={"assigned_by": owner["id"]},
            json={"assignee_id": assignee["id"]}
        ).json()

        # Update notes
        response = client.put(
            f"/api/assignments/{assignment['id']}",
            json={"notes": "Updated instructions"}
        )
        assert response.status_code == 200
        assert response.json()["notes"] == "Updated instructions"
