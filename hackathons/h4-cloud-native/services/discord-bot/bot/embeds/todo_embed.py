"""Rich Discord embed builders for todo display."""

from datetime import datetime
from typing import Optional

import discord

from bot.config import BOT_COLOR

PRIORITY_EMOJI = {"high": "\U0001f534", "medium": "\U0001f7e1", "low": "\U0001f7e2"}
CATEGORY_EMOJI = {
    "work": "\U0001f4bc",
    "personal": "\U0001f3e0",
    "study": "\U0001f4da",
    "health": "\U0001f3cb\ufe0f",
    "other": "\U0001f4cc",
}
STATUS_EMOJI = {
    "pending": "\u2b1c",
    "in_progress": "\U0001f7e6",
    "completed": "\u2705",
    "flagged": "\u26a0\ufe0f",
}


def _format_deadline(deadline: Optional[str]) -> str:
    if not deadline:
        return "None"
    try:
        dt = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y %I:%M %p")
    except (ValueError, AttributeError):
        return str(deadline)


def _relative_time(iso_str: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        diff = datetime.now(dt.tzinfo) - dt if dt.tzinfo else datetime.now() - dt
        seconds = int(diff.total_seconds())
        if seconds < 60:
            return "just now"
        if seconds < 3600:
            return f"{seconds // 60}m ago"
        if seconds < 86400:
            return f"{seconds // 3600}h ago"
        return f"{seconds // 86400}d ago"
    except (ValueError, AttributeError):
        return iso_str


def todo_detail_embed(todo: dict) -> discord.Embed:
    """Build a rich embed for a single todo."""
    status = todo.get("status", "pending")
    priority = todo.get("priority", "medium")
    category = todo.get("category", "other")

    emoji = STATUS_EMOJI.get(status, "")
    title = f"{emoji} Todo #{todo['id'][:8]}"

    embed = discord.Embed(title=title, color=BOT_COLOR)
    embed.add_field(
        name="\U0001f4dd Title", value=todo.get("title", "Untitled"), inline=False
    )
    if todo.get("description"):
        embed.add_field(
            name="\U0001f4c4 Description", value=todo["description"], inline=False
        )
    embed.add_field(
        name="\U0001f4c5 Deadline", value=_format_deadline(todo.get("deadline"))
    )
    embed.add_field(
        name=f"{PRIORITY_EMOJI.get(priority, '')} Priority",
        value=priority.capitalize(),
    )
    embed.add_field(
        name=f"{CATEGORY_EMOJI.get(category, '')} Category",
        value=category.capitalize(),
    )
    embed.add_field(name="Status", value=status.replace("_", " ").capitalize())

    const_check = todo.get("constitutional_check", {})
    if const_check and not const_check.get("passed", True):
        embed.add_field(
            name="\u26a0\ufe0f Constitutional AI",
            value=const_check.get("reason", "Flagged by safety system"),
            inline=False,
        )

    created = todo.get("created_at", "")
    if created:
        embed.set_footer(text=f"Created {_relative_time(created)}")

    return embed


def todo_list_embed(
    todos: list[dict], *, page: int = 1, total_pages: int = 1
) -> discord.Embed:
    """Build an embed for a paginated list of todos."""
    active = [t for t in todos if t.get("status") != "completed"]
    completed = [t for t in todos if t.get("status") == "completed"]

    embed = discord.Embed(
        title=f"\U0001f4cb Your Todos ({len(active)} active)",
        color=BOT_COLOR,
    )

    if not todos:
        embed.description = "No todos found. Create one with `/todo create`!"
        return embed

    lines: list[str] = []
    for todo in todos:
        s_emoji = STATUS_EMOJI.get(todo.get("status", "pending"), "")
        p_emoji = PRIORITY_EMOJI.get(todo.get("priority", "medium"), "")
        short_id = todo["id"][:8]
        lines.append(f"{s_emoji} `{short_id}` {todo['title']}  {p_emoji}")

    embed.description = "\n".join(lines)

    if total_pages > 1:
        embed.set_footer(text=f"Page {page}/{total_pages}")

    return embed


def success_embed(message: str) -> discord.Embed:
    return discord.Embed(
        title="\u2705 Success",
        description=message,
        color=0x57F287,  # Discord green
    )


def error_embed(message: str) -> discord.Embed:
    return discord.Embed(
        title="\u274c Error",
        description=message,
        color=0xED4245,  # Discord red
    )


def constitutional_block_embed(reason: str) -> discord.Embed:
    embed = discord.Embed(
        title="\u26a0\ufe0f Constitutional AI — Blocked",
        description=reason,
        color=0xFEE75C,  # Discord yellow
    )
    embed.add_field(
        name="\U0001f4a1 Tip",
        value="TodoMaster AI helps you manage YOUR tasks. Try rephrasing!",
        inline=False,
    )
    return embed
