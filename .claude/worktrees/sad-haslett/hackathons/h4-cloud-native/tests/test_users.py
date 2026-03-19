"""Tests for users API."""
import pytest
from fastapi.testclient import TestClient


class TestUserCreate:
    """Test user creation."""

    def test_create_user(self, client: TestClient):
        """Test creating a new user."""
        response = client.post(
            "/api/users",
            json={
                "email": "test@example.com",
                "display_name": "Test User"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["display_name"] == "Test User"
        assert "id" in data
        assert data["is_active"] is True

    def test_create_user_with_avatar(self, client: TestClient):
        """Test creating user with avatar URL."""
        response = client.post(
            "/api/users",
            json={
                "email": "avatar@example.com",
                "display_name": "Avatar User",
                "avatar_url": "https://example.com/avatar.jpg"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["avatar_url"] == "https://example.com/avatar.jpg"

    def test_create_duplicate_email(self, client: TestClient):
        """Test creating user with duplicate email fails."""
        # Create first user
        client.post(
            "/api/users",
            json={"email": "dupe@example.com", "display_name": "First"}
        )

        # Try to create second user with same email
        response = client.post(
            "/api/users",
            json={"email": "dupe@example.com", "display_name": "Second"}
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]


class TestUserGet:
    """Test user retrieval."""

    def test_get_user_by_id(self, client: TestClient):
        """Test getting user by ID."""
        # Create user
        create_response = client.post(
            "/api/users",
            json={"email": "getme@example.com", "display_name": "Get Me"}
        )
        user_id = create_response.json()["id"]

        # Get user
        response = client.get(f"/api/users/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["email"] == "getme@example.com"

    def test_get_user_not_found(self, client: TestClient):
        """Test getting non-existent user."""
        response = client.get("/api/users/nonexistent-id")
        assert response.status_code == 404


class TestUserUpdate:
    """Test user updates."""

    def test_update_user_display_name(self, client: TestClient):
        """Test updating user display name."""
        # Create user
        create_response = client.post(
            "/api/users",
            json={"email": "update@example.com", "display_name": "Original"}
        )
        user_id = create_response.json()["id"]

        # Update
        response = client.put(
            f"/api/users/{user_id}",
            json={"display_name": "Updated Name"}
        )
        assert response.status_code == 200
        assert response.json()["display_name"] == "Updated Name"

    def test_update_user_avatar(self, client: TestClient):
        """Test updating user avatar."""
        # Create user
        create_response = client.post(
            "/api/users",
            json={"email": "avatar_update@example.com", "display_name": "User"}
        )
        user_id = create_response.json()["id"]

        # Update avatar
        response = client.put(
            f"/api/users/{user_id}",
            json={"avatar_url": "https://example.com/new.jpg"}
        )
        assert response.status_code == 200
        assert response.json()["avatar_url"] == "https://example.com/new.jpg"


class TestUserList:
    """Test user listing."""

    def test_list_users(self, client: TestClient):
        """Test listing users."""
        # Create some users
        client.post(
            "/api/users",
            json={"email": "list1@example.com", "display_name": "List User 1"}
        )
        client.post(
            "/api/users",
            json={"email": "list2@example.com", "display_name": "List User 2"}
        )

        # List
        response = client.get("/api/users")
        assert response.status_code == 200
        users = response.json()
        assert len(users) >= 2

    def test_search_users(self, client: TestClient):
        """Test searching users."""
        # Create user
        client.post(
            "/api/users",
            json={"email": "search@example.com", "display_name": "Searchable User"}
        )

        # Search
        response = client.get("/api/users", params={"search": "Searchable"})
        assert response.status_code == 200
        users = response.json()
        assert len(users) >= 1
        assert any("Searchable" in u["display_name"] for u in users)
