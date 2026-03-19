"""Tests for Calendar Integration API."""
import pytest
from datetime import datetime, timedelta


@pytest.fixture
def calendar_user(client):
    """Create a test user for calendar tests."""
    response = client.post(
        "/api/users",
        json={
            "email": "calendar@example.com",
            "display_name": "Calendar User"
        }
    )
    return response.json()


@pytest.fixture
def test_connection(client, calendar_user):
    """Create a test calendar connection."""
    init_response = client.post(
        f"/api/calendar/connections?user_id={calendar_user['id']}",
        json={"provider": "google"}
    )
    connection_id = init_response.json()["connection_id"]
    complete_response = client.post(
        f"/api/calendar/connections/{connection_id}/complete",
        json={}
    )
    return complete_response.json()


@pytest.fixture
def calendar_todo(client, calendar_user):
    """Create a test todo with a deadline."""
    tomorrow = (datetime.utcnow() + timedelta(days=1)).isoformat()
    response = client.post(
        "/api/todos",
        json={
            "title": "Meeting with team",
            "description": "Weekly sync meeting",
            "category": "work",
            "priority": "high",
            "deadline": tomorrow,
            "owner_id": calendar_user["id"]
        }
    )
    return response.json()


class TestInitiateConnection:
    """Tests for POST /api/calendar/connections endpoint."""

    def test_initiate_google_connection(self, client, calendar_user):
        """Test initiating a Google Calendar connection."""
        response = client.post(
            f"/api/calendar/connections?user_id={calendar_user['id']}",
            json={"provider": "google"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"
        assert "connection_id" in data
        assert "oauth_url" in data

    def test_initiate_outlook_connection(self, client, calendar_user):
        """Test initiating an Outlook Calendar connection."""
        response = client.post(
            f"/api/calendar/connections?user_id={calendar_user['id']}",
            json={"provider": "outlook"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"

    def test_initiate_invalid_provider(self, client, calendar_user):
        """Test initiating connection with invalid provider."""
        response = client.post(
            f"/api/calendar/connections?user_id={calendar_user['id']}",
            json={"provider": "invalid_provider"}
        )
        assert response.status_code == 400


class TestCompleteConnection:
    """Tests for POST /api/calendar/connections/{id}/complete endpoint."""

    def test_complete_connection(self, client, calendar_user):
        """Test completing a calendar connection."""
        init_response = client.post(
            f"/api/calendar/connections?user_id={calendar_user['id']}",
            json={"provider": "google"}
        )
        connection_id = init_response.json()["connection_id"]
        response = client.post(
            f"/api/calendar/connections/{connection_id}/complete",
            json={"auth_code": "mock_auth_code"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "connected"
        assert data["calendar_name"] is not None

    def test_complete_nonexistent_connection(self, client):
        """Test completing a non-existent connection."""
        response = client.post(
            "/api/calendar/connections/non-existent-id/complete",
            json={}
        )
        assert response.status_code == 404


class TestGetConnections:
    """Tests for GET /api/calendar/connections endpoint."""

    def test_get_connections_empty(self, client, calendar_user):
        """Test getting connections when none exist."""
        response = client.get(
            f"/api/calendar/connections?user_id={calendar_user['id']}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_get_connections_with_connection(self, client, calendar_user, test_connection):
        """Test getting connections when one exists."""
        response = client.get(
            f"/api/calendar/connections?user_id={calendar_user['id']}"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "connected"

    def test_get_connections_filter_by_provider(self, client, calendar_user, test_connection):
        """Test filtering connections by provider."""
        response = client.get(
            f"/api/calendar/connections?user_id={calendar_user['id']}&provider=google"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        response2 = client.get(
            f"/api/calendar/connections?user_id={calendar_user['id']}&provider=outlook"
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2) == 0


class TestGetConnection:
    """Tests for GET /api/calendar/connections/{id} endpoint."""

    def test_get_connection(self, client, test_connection):
        """Test getting a specific connection."""
        response = client.get(
            f"/api/calendar/connections/{test_connection['id']}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_connection["id"]

    def test_get_nonexistent_connection(self, client):
        """Test getting non-existent connection."""
        response = client.get("/api/calendar/connections/non-existent-id")
        assert response.status_code == 404


class TestUpdateSyncSettings:
    """Tests for PUT /api/calendar/connections/{id} endpoint."""

    def test_update_sync_enabled(self, client, test_connection):
        """Test updating sync enabled setting."""
        response = client.put(
            f"/api/calendar/connections/{test_connection['id']}",
            json={"sync_enabled": False}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["sync_enabled"] is False

    def test_update_sync_direction(self, client, test_connection):
        """Test updating sync direction."""
        response = client.put(
            f"/api/calendar/connections/{test_connection['id']}",
            json={"sync_direction": "bidirectional"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["sync_direction"] == "bidirectional"

    def test_update_nonexistent_connection(self, client):
        """Test updating non-existent connection."""
        response = client.put(
            "/api/calendar/connections/non-existent-id",
            json={"sync_enabled": False}
        )
        assert response.status_code == 404


class TestDisconnect:
    """Tests for DELETE /api/calendar/connections/{id} endpoint."""

    def test_disconnect(self, client, test_connection):
        """Test disconnecting a calendar."""
        response = client.delete(
            f"/api/calendar/connections/{test_connection['id']}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_connection["id"]

    def test_disconnect_nonexistent(self, client):
        """Test disconnecting non-existent connection."""
        response = client.delete("/api/calendar/connections/non-existent-id")
        assert response.status_code == 404


class TestCalendarEvents:
    """Tests for calendar event endpoints."""

    def test_get_events_empty(self, client, test_connection):
        """Test getting events when none exist."""
        response = client.get(
            f"/api/calendar/connections/{test_connection['id']}/events"
        )
        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_create_event(self, client, test_connection):
        """Test creating a calendar event."""
        start_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        end_time = (datetime.utcnow() + timedelta(hours=2)).isoformat()
        response = client.post(
            f"/api/calendar/connections/{test_connection['id']}/events",
            json={
                "title": "Test Event",
                "start_time": start_time,
                "end_time": end_time,
                "description": "A test event"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Event"
        assert data["is_synced"] is True

    def test_create_event_minimal(self, client, test_connection):
        """Test creating an event with minimal data."""
        start_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        response = client.post(
            f"/api/calendar/connections/{test_connection['id']}/events",
            json={
                "title": "Minimal Event",
                "start_time": start_time
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Minimal Event"

    def test_delete_event(self, client, test_connection):
        """Test deleting a calendar event."""
        start_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        create_response = client.post(
            f"/api/calendar/connections/{test_connection['id']}/events",
            json={
                "title": "Event to Delete",
                "start_time": start_time
            }
        )
        event_id = create_response.json()["id"]
        response = client.delete(f"/api/calendar/events/{event_id}")
        assert response.status_code == 200
        assert response.json()["id"] == event_id

    def test_delete_nonexistent_event(self, client):
        """Test deleting non-existent event."""
        response = client.delete("/api/calendar/events/non-existent-id")
        assert response.status_code == 404


class TestSyncTodos:
    """Tests for syncing todos to calendar."""

    def test_sync_all_todos(self, client, calendar_user, test_connection, calendar_todo):
        """Test syncing all todos to calendar."""
        response = client.post(
            f"/api/calendar/connections/{test_connection['id']}/sync?user_id={calendar_user['id']}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "synced" in data
        assert "failed" in data
        assert "total" in data
        assert "last_sync_at" in data

    def test_sync_single_todo(self, client, test_connection, calendar_todo):
        """Test syncing a single todo to calendar."""
        response = client.post(
            f"/api/calendar/todos/{calendar_todo['id']}/sync?connection_id={test_connection['id']}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["todo_id"] == calendar_todo["id"]
        assert data["title"] == calendar_todo["title"]

    def test_sync_nonexistent_todo(self, client, test_connection):
        """Test syncing non-existent todo."""
        response = client.post(
            f"/api/calendar/todos/non-existent-id/sync?connection_id={test_connection['id']}"
        )
        assert response.status_code == 404
