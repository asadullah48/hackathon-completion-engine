"""
Claude Reasoning Service for Personal AI Employee
Uses Anthropic Claude API as the vault reasoning engine.
Reads vault items, analyzes them, and makes triage/action decisions.
"""

import os
import json
import logging
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic SDK not installed. Run: pip install anthropic")

VAULT_REASONING_PROMPT = """You are the reasoning engine for a Personal AI Employee system.
You manage an Obsidian vault with this structure:
- Inbox/: New items to triage
- Needs_Action/: Items awaiting processing
- Pending_Approval/: Items needing human approval
- Approved/: Human-approved items ready for execution
- Done/: Completed items

Your job is to:
1. Analyze incoming items and determine priority (high/medium/low)
2. Categorize items (email, file, task, financial, communication)
3. Decide if items need human approval or can be auto-processed
4. Suggest specific actions for each item
5. Flag urgent items that need immediate attention

Rules from Company_Handbook.md:
- Financial transactions over $50 require human approval
- External communications require human approval
- Reading, categorizing, logging are auto-execute
- Always err on the side of requesting approval for sensitive actions
"""


class ClaudeService:
    """Claude-powered reasoning engine for vault item analysis and decision-making."""

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")
        self.vault_path = Path(os.getenv("VAULT_PATH", "../vault"))
        self._client: Optional[object] = None

    @property
    def client(self):
        if self._client is None:
            if not ANTHROPIC_AVAILABLE:
                raise RuntimeError("Anthropic SDK not installed")
            if not self.api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set")
            self._client = Anthropic(api_key=self.api_key)
        return self._client

    @property
    def is_configured(self) -> bool:
        return ANTHROPIC_AVAILABLE and bool(self.api_key)

    def reason_about_item(self, item_content: str, item_type: str = "unknown") -> Dict:
        """Analyze a vault item and return reasoning/decisions."""
        if not self.is_configured:
            return self._mock_reasoning(item_content, item_type)

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=VAULT_REASONING_PROMPT,
                messages=[{
                    "role": "user",
                    "content": f"Analyze this {item_type} item and provide your reasoning:\n\n{item_content}"
                }],
            )
            response_text = message.content[0].text
            return {
                "success": True,
                "reasoning": response_text,
                "model": self.model,
                "engine": "claude",
                "tokens_used": message.usage.input_tokens + message.usage.output_tokens,
            }
        except Exception as e:
            logger.error(f"Claude reasoning error: {e}")
            return {"success": False, "error": str(e), "engine": "claude"}

    def triage_vault(self) -> Dict:
        """Scan vault folders and provide triage recommendations."""
        results = {
            "timestamp": datetime.now().isoformat(),
            "engine": "claude",
            "inbox_items": [],
            "needs_action_items": [],
            "recommendations": [],
        }

        # Scan Inbox
        inbox = self.vault_path / "Inbox"
        if inbox.exists():
            for f in inbox.iterdir():
                if f.name != ".gitkeep" and f.is_file():
                    content = f.read_text(encoding="utf-8", errors="ignore")[:500]
                    results["inbox_items"].append({
                        "file": f.name,
                        "preview": content[:200],
                    })

        # Scan Needs_Action
        needs_action = self.vault_path / "Needs_Action"
        if needs_action.exists():
            for f in sorted(needs_action.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)[:10]:
                if f.name != ".gitkeep" and f.is_file():
                    content = f.read_text(encoding="utf-8", errors="ignore")[:500]
                    results["needs_action_items"].append({
                        "file": f.name,
                        "preview": content[:200],
                    })

        # Count items
        results["counts"] = {
            "inbox": len(results["inbox_items"]),
            "needs_action": len(results["needs_action_items"]),
            "pending_approval": len(list((self.vault_path / "Pending_Approval").glob("*"))) - 1
            if (self.vault_path / "Pending_Approval").exists() else 0,
        }

        return results

    def _mock_reasoning(self, item_content: str, item_type: str) -> Dict:
        """Provide mock reasoning when API key is not configured."""
        return {
            "success": True,
            "reasoning": (
                f"[Mock reasoning - configure ANTHROPIC_API_KEY for Claude analysis]\n\n"
                f"Item type: {item_type}\n"
                f"Suggested priority: medium\n"
                f"Suggested action: Review and categorize\n"
                f"Requires approval: No (read-only analysis)"
            ),
            "model": "mock",
            "engine": "claude",
            "mock": True,
        }


_service_instance: Optional[ClaudeService] = None


def get_claude_service() -> ClaudeService:
    global _service_instance
    if _service_instance is None:
        _service_instance = ClaudeService()
    return _service_instance
