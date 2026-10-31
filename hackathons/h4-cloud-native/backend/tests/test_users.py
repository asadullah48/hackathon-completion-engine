"""Tests for users API."""
import pytest


class TestCreateUser:
    """Tests for POST /api/users endpoint."""

    def test_create_user(self, client):
        """Test creating a new user."""
        response = client.post(
            "/api/users",
            json={
                "email": "newuser@example.com",
                "display_name": "New User"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["display_name"] == "New User"
        assert data["is_active"] is True

    def test_create_user_with_avatar(self, client):
        """Test creating a user with avatar."""
        response = client.post(
            "/api/users",
            json={
                "email": "avatar@example.com",
                "display_name": "Avatar User",
                "avatar_url": "https://example.com/avatar.png"
            }
        )
        assert response.status_code == 200
        assert response.json()["avatar_url"] == "https://example.com/avatar.png"

    def test_create_duplicate_email(self, client, test_user):
        """Test creating user with duplicate email."""
        response = client.post(
            "/api/users",
            json={
                "email": test_user["email"],
                "display_name": "Duplicate"
            }
        )
        assert response.status_code == 400


class TestGetUsers:
    """Tests for GET /api/users endpoints."""

    def test_get_all_users(self, client, test_user):
        """Test getting all users."""
        response = client.get("/api/users")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_get_user_by_id(self, client, test_user):
        """Test getting a user by ID."""
        response = client.get(f"/api/users/{test_user['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == test_user["id"]

    def test_get_user_not_found(self, client):
        """Test getting non-existent user."""
        response = client.get("/api/users/non-existent-id")
        assert response.status_code == 404

    def test_search_users(self, client, test_user):
        """Test searching users by name or email."""
        response = client.get(f"/api/users?search={test_user['display_name'][:4]}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1


class TestUpdateUser:
    """Tests for PUT /api/users/{id} endpoint."""

    def test_update_user_name(self, client, test_user):
        """Test updating a user's display name."""
        response = client.put(
            f"/api/users/{test_user['id']}",
            json={"display_name": "Updated Name"}
        )
        assert response.status_code == 200
        assert response.json()["display_name"] == "Updated Name"

    def test_update_user_avatar(self, client, test_user):
        """Test updating a user's avatar."""
        response = client.put(
            f"/api/users/{test_user['id']}",
            json={"avatar_url": "https://new-avatar.com/pic.png"}
        )
        assert response.status_code == 200
        assert response.json()["avatar_url"] == "https://new-avatar.com/pic.png"

    def test_update_user_not_found(self, client):
        """Test updating non-existent user."""
        response = client.put(
            "/api/users/non-existent-id",
            json={"display_name": "New Name"}
        )
        assert response.status_code == 404
