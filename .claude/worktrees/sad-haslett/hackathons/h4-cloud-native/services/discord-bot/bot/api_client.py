"""Async HTTP client for the FastAPI backend."""

import logging
from typing import Any, Optional

import aiohttp

from bot.config import BACKEND_URL, API_TIMEOUT

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Raised when the backend returns a non-success status."""

    def __init__(self, status: int, detail: str):
        self.status = status
        self.detail = detail
        super().__init__(f"API error {status}: {detail}")


class TodoAPIClient:
    """Thin async wrapper around the existing FastAPI backend."""

    def __init__(self, base_url: str = BACKEND_URL):
        self.base_url = base_url.rstrip("/")

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> Any:
        url = f"{self.base_url}{path}"
        timeout = aiohttp.ClientTimeout(total=API_TIMEOUT)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.request(
                    method, url, json=json, params=params
                ) as resp:
                    body = await resp.json()
                    if resp.status >= 400:
                        detail = body.get("detail", str(body))
                        raise APIError(resp.status, detail)
                    return body
        except aiohttp.ClientError as exc:
            logger.error("Backend unreachable: %s", exc)
            raise APIError(503, "Backend service is currently unavailable") from exc

    # ── Todo CRUD ────────────────────────────────────────────────

    async def create_todo(
        self,
        title: str,
        *,
        description: Optional[str] = None,
        category: str = "other",
        priority: str = "medium",
        deadline: Optional[str] = None,
    ) -> dict:
        payload: dict[str, Any] = {
            "title": title,
            "category": category,
            "priority": priority,
        }
        if description:
            payload["description"] = description
        if deadline:
            payload["deadline"] = deadline
        return await self._request("POST", "/api/todos", json=payload)

    async def list_todos(
        self,
        *,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
    ) -> list[dict]:
        params: dict[str, str] = {}
        if status:
            params["status"] = status
        if priority:
            params["priority"] = priority
        if category:
            params["category"] = category
        if search:
            params["search"] = search
        return await self._request("GET", "/api/todos", params=params or None)

    async def get_todo(self, todo_id: str) -> dict:
        return await self._request("GET", f"/api/todos/{todo_id}")

    async def update_todo(self, todo_id: str, **fields: Any) -> dict:
        return await self._request("PUT", f"/api/todos/{todo_id}", json=fields)

    async def delete_todo(self, todo_id: str) -> dict:
        return await self._request("DELETE", f"/api/todos/{todo_id}")

    async def complete_todo(self, todo_id: str) -> dict:
        return await self.update_todo(todo_id, status="completed")

    # ── Health ───────────────────────────────────────────────────

    async def health(self) -> dict:
        return await self._request("GET", "/health")
