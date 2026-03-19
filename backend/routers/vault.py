"""
Vault Router for Personal AI Employee API
Provides endpoints for vault triage, reasoning, and status using Claude AI.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
import os
from pathlib import Path

from services.claude_service import get_claude_service

logger = logging.getLogger(__name__)
router = APIRouter()

claude_service = get_claude_service()


class ReasonRequest(BaseModel):
    item_content: str
    item_type: str = "unknown"


@router.get("/vault/status")
async def vault_status():
    """Get current vault folder counts and system status."""
    vault_path = Path(os.getenv("VAULT_PATH", "../vault"))
    folders = ["Inbox", "Needs_Action", "Pending_Approval", "Approved", "Rejected", "Done", "Briefings"]
    counts = {}
    for folder in folders:
        folder_path = vault_path / folder
        if folder_path.exists():
            items = [f for f in folder_path.iterdir() if f.name != ".gitkeep" and f.is_file()]
            counts[folder] = len(items)
        else:
            counts[folder] = 0

    return {
        "status": "operational",
        "vault_path": str(vault_path),
        "counts": counts,
        "total_items": sum(counts.values()),
        "ai_engines": {
            "openai": {"configured": bool(os.getenv("OPENAI_API_KEY")), "purpose": "chat_companion"},
            "claude": {"configured": claude_service.is_configured, "purpose": "vault_reasoning"},
        },
    }


@router.get("/vault/triage")
async def vault_triage():
    """Scan vault and return triage recommendations."""
    return claude_service.triage_vault()


@router.post("/vault/reason")
async def vault_reason(request: ReasonRequest):
    """Use Claude to reason about a specific vault item."""
    result = claude_service.reason_about_item(request.item_content, request.item_type)
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Reasoning failed"))
    return result


@router.get("/vault/needs-action")
async def vault_needs_action():
    """List all items in Needs_Action with previews."""
    vault_path = Path(os.getenv("VAULT_PATH", "../vault"))
    needs_action = vault_path / "Needs_Action"
    items = []
    if needs_action.exists():
        for f in sorted(needs_action.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
            if f.name != ".gitkeep" and f.is_file():
                content = f.read_text(encoding="utf-8", errors="ignore")
                items.append({
                    "filename": f.name,
                    "preview": content[:300],
                    "size": f.stat().st_size,
                    "modified": f.stat().st_mtime,
                })
    return {"count": len(items), "items": items}
