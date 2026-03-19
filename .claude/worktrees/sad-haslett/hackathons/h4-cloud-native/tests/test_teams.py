"""Tests for teams API."""
import pytest
from fastapi.testclient import TestClient


def create_user(client: TestClient, email: str, display_name: str) -> dict:
    """Helper to create a user."""
    response = client.post(
        "/api/users",
        json={"email": email, "display_name": display_name}
    )
    return response.json()


class TestTeamCreate:
    """Test team creation."""

    def test_create_team(self, client: TestClient):
        """Test creating a team."""
        user = create_user(client, "team_owner@example.com", "Team Owner")

        response = client.post(
            "/api/teams",
            json={
                "name": "My Team",
                "description": "A test team",
                "owner_id": user["id"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "My Team"
        assert data["owner_id"] == user["id"]
        assert "id" in data

    def test_create_team_owner_becomes_member(self, client: TestClient):
        """Test that team owner automatically becomes a member."""
        user = create_user(client, "auto_member@example.com", "Auto Member")

        # Create team
        team_response = client.post(
            "/api/teams",
            json={"name": "Auto Member Team", "owner_id": user["id"]}
        )
        team = team_response.json()

        # Check members
        members_response = client.get(f"/api/teams/{team['id']}/members")
        members = members_response.json()

        assert len(members) == 1
        assert members[0]["user_id"] == user["id"]
        assert members[0]["role"] == "owner"

    def test_create_team_invalid_owner(self, client: TestClient):
        """Test creating team with invalid owner fails."""
        response = client.post(
            "/api/teams",
            json={"name": "Invalid Team", "owner_id": "nonexistent-user"}
        )
        assert response.status_code == 404


class TestTeamMembers:
    """Test team membership operations."""

    def test_add_member(self, client: TestClient):
        """Test adding a member to a team."""
        owner = create_user(client, "add_member_owner@example.com", "Owner")
        member = create_user(client, "new_member@example.com", "New Member")

        # Create team
        team_response = client.post(
            "/api/teams",
            json={"name": "Member Test Team", "owner_id": owner["id"]}
        )
        team = team_response.json()

        # Add member
        response = client.post(
            f"/api/teams/{team['id']}/members",
            params={"added_by": owner["id"]},
            json={"user_id": member["id"], "role": "editor"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == member["id"]
        assert data["role"] == "editor"

    def test_add_duplicate_member(self, client: TestClient):
        """Test adding duplicate member fails."""
        owner = create_user(client, "dupe_member_owner@example.com", "Owner")
        member = create_user(client, "dupe_member@example.com", "Member")

        # Create team
        team_response = client.post(
            "/api/teams",
            json={"name": "Dupe Member Team", "owner_id": owner["id"]}
        )
        team = team_response.json()

        # Add member first time
        client.post(
            f"/api/teams/{team['id']}/members",
            params={"added_by": owner["id"]},
            json={"user_id": member["id"], "role": "viewer"}
        )

        # Try to add again
        response = client.post(
            f"/api/teams/{team['id']}/members",
            params={"added_by": owner["id"]},
            json={"user_id": member["id"], "role": "editor"}
        )
        assert response.status_code == 400
        assert "already a member" in response.json()["detail"]

    def test_remove_member(self, client: TestClient):
        """Test removing a member from a team."""
        owner = create_user(client, "remove_member_owner@example.com", "Owner")
        member = create_user(client, "remove_me@example.com", "Remove Me")

        # Create team
        team_response = client.post(
            "/api/teams",
            json={"name": "Remove Member Team", "owner_id": owner["id"]}
        )
        team = team_response.json()

        # Add member
        client.post(
            f"/api/teams/{team['id']}/members",
            params={"added_by": owner["id"]},
            json={"user_id": member["id"], "role": "viewer"}
        )

        # Remove member
        response = client.delete(
            f"/api/teams/{team['id']}/members/{member['id']}",
            params={"removed_by": owner["id"]}
        )
        assert response.status_code == 200

        # Verify removed
        members_response = client.get(f"/api/teams/{team['id']}/members")
        members = members_response.json()
        assert not any(m["user_id"] == member["id"] for m in members)

    def test_cannot_remove_owner(self, client: TestClient):
        """Test that team owner cannot be removed."""
        owner = create_user(client, "no_remove_owner@example.com", "Owner")

        # Create team
        team_response = client.post(
            "/api/teams",
            json={"name": "No Remove Owner Team", "owner_id": owner["id"]}
        )
        team = team_response.json()

        # Try to remove owner
        response = client.delete(
            f"/api/teams/{team['id']}/members/{owner['id']}",
            params={"removed_by": owner["id"]}
        )
        assert response.status_code == 400
        assert "owner" in response.json()["detail"].lower()

    def test_update_member_role(self, client: TestClient):
        """Test updating a member's role."""
        owner = create_user(client, "update_role_owner@example.com", "Owner")
        member = create_user(client, "role_update@example.com", "Member")

        # Create team
        team_response = client.post(
            "/api/teams",
            json={"name": "Role Update Team", "owner_id": owner["id"]}
        )
        team = team_response.json()

        # Add member as viewer
        client.post(
            f"/api/teams/{team['id']}/members",
            params={"added_by": owner["id"]},
            json={"user_id": member["id"], "role": "viewer"}
        )

        # Update to editor
        response = client.put(
            f"/api/teams/{team['id']}/members/{member['id']}",
            params={"updated_by": owner["id"]},
            json={"role": "editor"}
        )
        assert response.status_code == 200
        assert response.json()["role"] == "editor"


class TestTeamPermissions:
    """Test team permission checks."""

    def test_non_admin_cannot_add_members(self, client: TestClient):
        """Test that non-admin members cannot add other members."""
        owner = create_user(client, "perm_owner@example.com", "Owner")
        editor = create_user(client, "perm_editor@example.com", "Editor")
        new_member = create_user(client, "perm_new@example.com", "New")

        # Create team
        team_response = client.post(
            "/api/teams",
            json={"name": "Permission Team", "owner_id": owner["id"]}
        )
        team = team_response.json()

        # Add editor
        client.post(
            f"/api/teams/{team['id']}/members",
            params={"added_by": owner["id"]},
            json={"user_id": editor["id"], "role": "editor"}
        )

        # Editor tries to add member
        response = client.post(
            f"/api/teams/{team['id']}/members",
            params={"added_by": editor["id"]},
            json={"user_id": new_member["id"], "role": "viewer"}
        )
        assert response.status_code == 403


class TestTeamDelete:
    """Test team deletion."""

    def test_owner_can_delete_team(self, client: TestClient):
        """Test that owner can delete team."""
        owner = create_user(client, "delete_team_owner@example.com", "Owner")

        # Create team
        team_response = client.post(
            "/api/teams",
            json={"name": "Delete Me Team", "owner_id": owner["id"]}
        )
        team = team_response.json()

        # Delete team
        response = client.delete(
            f"/api/teams/{team['id']}",
            params={"user_id": owner["id"]}
        )
        assert response.status_code == 200

        # Verify deleted
        get_response = client.get(f"/api/teams/{team['id']}")
        assert get_response.status_code == 404

    def test_non_owner_cannot_delete_team(self, client: TestClient):
        """Test that non-owner cannot delete team."""
        owner = create_user(client, "no_delete_owner@example.com", "Owner")
        member = create_user(client, "no_delete_member@example.com", "Member")

        # Create team
        team_response = client.post(
            "/api/teams",
            json={"name": "No Delete Team", "owner_id": owner["id"]}
        )
        team = team_response.json()

        # Add member as admin
        client.post(
            f"/api/teams/{team['id']}/members",
            params={"added_by": owner["id"]},
            json={"user_id": member["id"], "role": "admin"}
        )

        # Admin tries to delete team
        response = client.delete(
            f"/api/teams/{team['id']}",
            params={"user_id": member["id"]}
        )
        assert response.status_code == 403
