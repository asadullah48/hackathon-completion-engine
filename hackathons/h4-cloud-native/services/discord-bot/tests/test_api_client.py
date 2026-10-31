"""Tests for the backend API client."""

import pytest
from aioresponses import aioresponses

from bot.api_client import TodoAPIClient, APIError

BASE = "http://test-backend:8000"


@pytest.fixture
def client():
    return TodoAPIClient(base_url=BASE)


@pytest.fixture
def mock_api():
    with aioresponses() as m:
        yield m


# ── create_todo ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_todo_success(client, mock_api):
    expected = {
        "id": "abc-123",
        "title": "Buy milk",
        "priority": "medium",
        "category": "personal",
        "status": "pending",
        "constitutional_check": {"passed": True, "decision": "ALLOW", "reason": None},
        "created_at": "2026-02-12T10:00:00",
        "updated_at": "2026-02-12T10:00:00",
    }
    mock_api.post(f"{BASE}/api/todos", payload=expected, status=201)

    result = await client.create_todo("Buy milk", category="personal")
    assert result["id"] == "abc-123"
    assert result["title"] == "Buy milk"


@pytest.mark.asyncio
async def test_create_todo_with_all_params(client, mock_api):
    expected = {"id": "xyz", "title": "Test", "priority": "high", "category": "work",
                "status": "pending", "deadline": "2026-03-01T09:00:00",
                "constitutional_check": {"passed": True, "decision": "ALLOW", "reason": None},
                "created_at": "2026-02-12T10:00:00", "updated_at": "2026-02-12T10:00:00"}
    mock_api.post(f"{BASE}/api/todos", payload=expected, status=201)

    result = await client.create_todo(
        "Test", priority="high", category="work", deadline="2026-03-01T09:00:00"
    )
    assert result["priority"] == "high"
    assert result["deadline"] == "2026-03-01T09:00:00"


@pytest.mark.asyncio
async def test_create_todo_blocked(client, mock_api):
    mock_api.post(
        f"{BASE}/api/todos",
        payload={"detail": "Blocked by Constitutional AI"},
        status=403,
    )

    with pytest.raises(APIError) as exc_info:
        await client.create_todo("do my homework")
    assert exc_info.value.status == 403
    assert "Constitutional" in exc_info.value.detail


# ── list_todos ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_todos_empty(client, mock_api):
    mock_api.get(f"{BASE}/api/todos", payload=[])

    result = await client.list_todos()
    assert result == []


@pytest.mark.asyncio
async def test_list_todos_with_items(client, mock_api):
    todos = [
        {"id": "1", "title": "First", "status": "pending", "priority": "high",
         "category": "work", "constitutional_check": {"passed": True},
         "created_at": "2026-02-12T10:00:00", "updated_at": "2026-02-12T10:00:00"},
        {"id": "2", "title": "Second", "status": "completed", "priority": "low",
         "category": "personal", "constitutional_check": {"passed": True},
         "created_at": "2026-02-12T11:00:00", "updated_at": "2026-02-12T11:00:00"},
    ]
    mock_api.get(f"{BASE}/api/todos", payload=todos)

    result = await client.list_todos()
    assert len(result) == 2


@pytest.mark.asyncio
async def test_list_todos_with_filter(client, mock_api):
    mock_api.get(f"{BASE}/api/todos?status=pending", payload=[])

    result = await client.list_todos(status="pending")
    assert result == []


# ── get_todo ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_todo_success(client, mock_api):
    todo = {"id": "abc-123", "title": "Test", "status": "pending", "priority": "medium",
            "category": "other", "constitutional_check": {"passed": True},
            "created_at": "2026-02-12T10:00:00", "updated_at": "2026-02-12T10:00:00"}
    mock_api.get(f"{BASE}/api/todos/abc-123", payload=todo)

    result = await client.get_todo("abc-123")
    assert result["id"] == "abc-123"


@pytest.mark.asyncio
async def test_get_todo_not_found(client, mock_api):
    mock_api.get(
        f"{BASE}/api/todos/nonexistent",
        payload={"detail": "Todo not found"},
        status=404,
    )

    with pytest.raises(APIError) as exc_info:
        await client.get_todo("nonexistent")
    assert exc_info.value.status == 404


# ── update_todo / complete_todo ──────────────────────────────────

@pytest.mark.asyncio
async def test_complete_todo(client, mock_api):
    updated = {"id": "abc-123", "title": "Test", "status": "completed",
               "priority": "medium", "category": "other",
               "constitutional_check": {"passed": True},
               "created_at": "2026-02-12T10:00:00", "updated_at": "2026-02-12T12:00:00"}
    mock_api.put(f"{BASE}/api/todos/abc-123", payload=updated)

    result = await client.complete_todo("abc-123")
    assert result["status"] == "completed"


@pytest.mark.asyncio
async def test_update_todo_priority(client, mock_api):
    updated = {"id": "abc-123", "title": "Test", "status": "pending",
               "priority": "high", "category": "other",
               "constitutional_check": {"passed": True},
               "created_at": "2026-02-12T10:00:00", "updated_at": "2026-02-12T12:00:00"}
    mock_api.put(f"{BASE}/api/todos/abc-123", payload=updated)

    result = await client.update_todo("abc-123", priority="high")
    assert result["priority"] == "high"


# ── delete_todo ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_delete_todo(client, mock_api):
    mock_api.delete(
        f"{BASE}/api/todos/abc-123",
        payload={"deleted": True, "id": "abc-123"},
    )

    result = await client.delete_todo("abc-123")
    assert result["deleted"] is True


# ── health ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_check(client, mock_api):
    mock_api.get(
        f"{BASE}/health",
        payload={"status": "healthy", "service": "h4-cloud-native-todo-api"},
    )

    result = await client.health()
    assert result["status"] == "healthy"


# ── error handling ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_backend_unreachable(client, mock_api):
    import aiohttp
    mock_api.get(f"{BASE}/health", exception=aiohttp.ClientConnectionError("refused"))

    with pytest.raises(APIError) as exc_info:
        await client.health()
    assert exc_info.value.status == 503
    assert "unavailable" in exc_info.value.detail


@pytest.mark.asyncio
async def test_server_error(client, mock_api):
    mock_api.get(
        f"{BASE}/api/todos",
        payload={"detail": "Internal server error"},
        status=500,
    )

    with pytest.raises(APIError) as exc_info:
        await client.list_todos()
    assert exc_info.value.status == 500
