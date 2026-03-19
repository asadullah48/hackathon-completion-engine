"""Tests for teams API."""
import pytest


class TestCreateTeam:
    """Tests for POST /api/teams endpoint."""

    def test_create_team(self, client, test_user):
        """Test creating a new team."""
        response = client.post(
            "/api/teams",
            json={
                "name": "Test Team",
                "description": "A test team",
                "owner_id": test_user["id"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Team"
        assert data["owner_id"] == test_user["id"]

    def test_create_team_minimal(self, client, test_user):
        """Test creating team with minimal data."""
        response = client.post(
            "/api/teams",
            json={
                "name": "Minimal Team",
                "owner_id": test_user["id"]
            }
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Minimal Team"

    def test_create_team_owner_becomes_member(self, client, test_user):
        """Test that team owner is automatically added as member."""
        response = client.post(
            "/api/teams",
            json={
                "name": "Owner Member Team",
                "owner_id": test_user["id"]
            }
        )
        team_id = response.json()["id"]

        # Check members
        members_response = client.get(f"/api/teams/{team_id}/members")
        assert members_response.status_code == 200
        members = members_response.json()
        assert len(members) >= 1
        owner_member = next((m for m in members if m["user_id"] == test_user["id"]), None)
        assert owner_member is not None
        assert owner_member["role"] == "owner"


class TestGetTeams:
    """Tests for GET /api/teams endpoints."""

    @pytest.fixture
    def test_team(self, client, test_user):
        """Create a test team."""
        response = client.post(
            "/api/teams",
            json={
                "name": "Fixture Team",
                "owner_id": test_user["id"]
            }
        )
        return response.json()

    def test_get_user_teams(self, client, test_user, test_team):
        """Test getting user's teams."""
        response = client.get(f"/api/teams?user_id={test_user['id']}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_get_team_by_id(self, client, test_team):
        """Test getting a team by ID."""
        response = client.get(f"/api/teams/{test_team['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == test_team["id"]

    def test_get_team_not_found(self, client):
        """Test getting non-existent team."""
        response = client.get("/api/teams/non-existent-id")
        assert response.status_code == 404


class TestUpdateTeam:
    """Tests for PUT /api/teams/{id} endpoint."""

    @pytest.fixture
    def test_team(self, client, test_user):
        """Create a test team."""
        response = client.post(
            "/api/teams",
            json={
                "name": "Update Team",
                "owner_id": test_user["id"]
            }
        )
        return response.json()

    def test_update_team_name(self, client, test_team, test_user):
        """Test updating team name."""
        response = client.put(
            f"/api/teams/{test_team['id']}?user_id={test_user['id']}",
            json={"name": "Updated Team Name"}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Team Name"

    def test_update_team_description(self, client, test_team, test_user):
        """Test updating team description."""
        response = client.put(
            f"/api/teams/{test_team['id']}?user_id={test_user['id']}",
            json={"description": "New description"}
        )
        assert response.status_code == 200
        assert response.json()["description"] == "New description"

    def test_update_team_not_found(self, client, test_user):
        """Test updating non-existent team."""
        response = client.put(
            f"/api/teams/non-existent-id?user_id={test_user['id']}",
            json={"name": "New Name"}
        )
        assert response.status_code == 404


class TestDeleteTeam:
    """Tests for DELETE /api/teams/{id} endpoint."""

    @pytest.fixture
    def test_team(self, client, test_user):
        """Create a test team."""
        response = client.post(
            "/api/teams",
            json={
                "name": "Delete Team",
                "owner_id": test_user["id"]
            }
        )
        return response.json()

    def test_delete_team(self, client, test_team, test_user):
        """Test deleting a team."""
        response = client.delete(f"/api/teams/{test_team['id']}?user_id={test_user['id']}")
        assert response.status_code == 200

        # Verify deleted
        get_response = client.get(f"/api/teams/{test_team['id']}")
        assert get_response.status_code == 404

    def test_delete_team_not_found(self, client, test_user):
        """Test deleting non-existent team."""
        response = client.delete(f"/api/teams/non-existent-id?user_id={test_user['id']}")
        assert response.status_code == 404


class TestTeamMembers:
    """Tests for team member management."""

    @pytest.fixture
    def test_team(self, client, test_user):
        """Create a test team."""
        response = client.post(
            "/api/teams",
            json={
                "name": "Member Team",
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
                "email": "second@example.com",
                "display_name": "Second User"
            }
        )
        return response.json()

    def test_add_member(self, client, test_team, second_user, test_user):
        """Test adding a member to team."""
        response = client.post(
            f"/api/teams/{test_team['id']}/members?added_by={test_user['id']}",
            json={
                "user_id": second_user["id"],
                "role": "editor"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == second_user["id"]
        assert data["role"] == "editor"

    def test_add_member_as_viewer(self, client, test_team, second_user, test_user):
        """Test adding a member as viewer."""
        response = client.post(
            f"/api/teams/{test_team['id']}/members?added_by={test_user['id']}",
            json={
                "user_id": second_user["id"],
                "role": "viewer"
            }
        )
        assert response.status_code == 200
        assert response.json()["role"] == "viewer"

    def test_add_member_as_admin(self, client, test_team, second_user, test_user):
        """Test adding a member as admin."""
        response = client.post(
            f"/api/teams/{test_team['id']}/members?added_by={test_user['id']}",
            json={
                "user_id": second_user["id"],
                "role": "admin"
            }
        )
        assert response.status_code == 200
        assert response.json()["role"] == "admin"

    def test_get_team_members(self, client, test_team, test_user):
        """Test getting team members."""
        response = client.get(f"/api/teams/{test_team['id']}/members")
        assert response.status_code == 200
        members = response.json()
        assert len(members) >= 1

    def test_update_member_role(self, client, test_team, second_user, test_user):
        """Test updating member role."""
        # Add member first
        client.post(
            f"/api/teams/{test_team['id']}/members?added_by={test_user['id']}",
            json={"user_id": second_user["id"], "role": "viewer"}
        )

        # Update role
        response = client.put(
            f"/api/teams/{test_team['id']}/members/{second_user['id']}?updated_by={test_user['id']}",
            json={"role": "editor"}
        )
        assert response.status_code == 200
        assert response.json()["role"] == "editor"

    def test_remove_member(self, client, test_team, second_user, test_user):
        """Test removing a member from team."""
        # Add member first
        client.post(
            f"/api/teams/{test_team['id']}/members?added_by={test_user['id']}",
            json={"user_id": second_user["id"], "role": "viewer"}
        )

        # Remove member
        response = client.delete(
            f"/api/teams/{test_team['id']}/members/{second_user['id']}?removed_by={test_user['id']}"
        )
        assert response.status_code == 200

    def test_get_team_todos(self, client, test_team, test_user):
        """Test getting todos for a team."""
        response = client.get(f"/api/teams/{test_team['id']}/todos")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestTeamPermissions:
    """Tests for team permission checks."""

    @pytest.fixture
    def test_team(self, client, test_user):
        """Create a test team."""
        response = client.post(
            "/api/teams",
            json={
                "name": "Permission Team",
                "owner_id": test_user["id"]
            }
        )
        return response.json()

    @pytest.fixture
    def viewer_user(self, client, test_team, test_user):
        """Create a viewer user."""
        user_response = client.post(
            "/api/users",
            json={
                "email": "viewer@example.com",
                "display_name": "Viewer User"
            }
        )
        user = user_response.json()

        # Add as viewer
        client.post(
            f"/api/teams/{test_team['id']}/members?added_by={test_user['id']}",
            json={"user_id": user["id"], "role": "viewer"}
        )
        return user

    def test_owner_has_full_access(self, client, test_team, test_user):
        """Test that owner has full access."""
        # Owner can update team
        response = client.put(
            f"/api/teams/{test_team['id']}?user_id={test_user['id']}",
            json={"name": "Owner Updated"}
        )
        assert response.status_code == 200

    def test_get_member_role(self, client, test_team, viewer_user):
        """Test getting specific member's role."""
        response = client.get(f"/api/teams/{test_team['id']}/members")
        members = response.json()
        viewer = next((m for m in members if m["user_id"] == viewer_user["id"]), None)
        assert viewer is not None
        assert viewer["role"] == "viewer"
