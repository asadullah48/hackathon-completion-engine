"""Core /todo slash commands."""

import logging

import discord
from discord import app_commands
from discord.ext import commands

from bot.api_client import TodoAPIClient, APIError
from bot.embeds.todo_embed import (
    todo_detail_embed,
    todo_list_embed,
    success_embed,
    error_embed,
    constitutional_block_embed,
)
from bot.utils.pagination import paginate

logger = logging.getLogger(__name__)


class TodoCog(commands.Cog, name="Todo"):
    """Manage your todos directly from Discord."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api = TodoAPIClient()

    # ── /todo create ────────────────────────────────────────────

    @app_commands.command(name="todo-create", description="Create a new todo")
    @app_commands.describe(
        title="What do you need to do?",
        priority="Priority level",
        category="Todo category",
        deadline="Deadline (e.g. 2026-02-20T14:00:00)",
    )
    @app_commands.choices(
        priority=[
            app_commands.Choice(name="High", value="high"),
            app_commands.Choice(name="Medium", value="medium"),
            app_commands.Choice(name="Low", value="low"),
        ],
        category=[
            app_commands.Choice(name="Work", value="work"),
            app_commands.Choice(name="Personal", value="personal"),
            app_commands.Choice(name="Study", value="study"),
            app_commands.Choice(name="Health", value="health"),
            app_commands.Choice(name="Other", value="other"),
        ],
    )
    async def todo_create(
        self,
        interaction: discord.Interaction,
        title: str,
        priority: str = "medium",
        category: str = "other",
        deadline: str | None = None,
    ):
        await interaction.response.defer()
        try:
            todo = await self.api.create_todo(
                title, priority=priority, category=category, deadline=deadline
            )
            const_check = todo.get("constitutional_check", {})
            if const_check and not const_check.get("passed", True):
                decision = const_check.get("decision", "FLAG")
                reason = const_check.get("reason", "Flagged by safety system")
                if decision == "BLOCK":
                    await interaction.followup.send(
                        embed=constitutional_block_embed(reason)
                    )
                    return
            await interaction.followup.send(embed=todo_detail_embed(todo))
        except APIError as exc:
            if exc.status == 403:
                await interaction.followup.send(
                    embed=constitutional_block_embed(exc.detail)
                )
            else:
                await interaction.followup.send(embed=error_embed(exc.detail))

    # ── /todo list ──────────────────────────────────────────────

    @app_commands.command(name="todo-list", description="List your todos")
    @app_commands.describe(
        filter="Filter by status",
        page="Page number",
    )
    @app_commands.choices(
        filter=[
            app_commands.Choice(name="All", value="all"),
            app_commands.Choice(name="Active", value="active"),
            app_commands.Choice(name="Completed", value="completed"),
        ],
    )
    async def todo_list(
        self,
        interaction: discord.Interaction,
        filter: str = "all",
        page: int = 1,
    ):
        await interaction.response.defer()
        try:
            status_filter = None
            if filter == "active":
                status_filter = "pending"
            elif filter == "completed":
                status_filter = "completed"

            todos = await self.api.list_todos(status=status_filter)
            page_items, current_page, total_pages = paginate(todos, page)
            embed = todo_list_embed(
                page_items, page=current_page, total_pages=total_pages
            )
            await interaction.followup.send(embed=embed)
        except APIError as exc:
            await interaction.followup.send(embed=error_embed(exc.detail))

    # ── /todo show ──────────────────────────────────────────────

    @app_commands.command(name="todo-show", description="Show todo details")
    @app_commands.describe(todo_id="The todo ID (first 8 chars work)")
    async def todo_show(self, interaction: discord.Interaction, todo_id: str):
        await interaction.response.defer()
        try:
            todo = await self._resolve_todo(todo_id)
            await interaction.followup.send(embed=todo_detail_embed(todo))
        except APIError as exc:
            await interaction.followup.send(embed=error_embed(exc.detail))

    # ── /todo complete ──────────────────────────────────────────

    @app_commands.command(name="todo-complete", description="Mark a todo as completed")
    @app_commands.describe(todo_id="The todo ID (first 8 chars work)")
    async def todo_complete(self, interaction: discord.Interaction, todo_id: str):
        await interaction.response.defer()
        try:
            todo = await self._resolve_todo(todo_id)
            updated = await self.api.complete_todo(todo["id"])
            await interaction.followup.send(
                embed=success_embed(
                    f"Completed: **{updated.get('title', todo_id)}**"
                )
            )
        except APIError as exc:
            await interaction.followup.send(embed=error_embed(exc.detail))

    # ── /todo delete ────────────────────────────────────────────

    @app_commands.command(name="todo-delete", description="Delete a todo")
    @app_commands.describe(todo_id="The todo ID (first 8 chars work)")
    async def todo_delete(self, interaction: discord.Interaction, todo_id: str):
        await interaction.response.defer()
        try:
            todo = await self._resolve_todo(todo_id)
            await self.api.delete_todo(todo["id"])
            await interaction.followup.send(
                embed=success_embed(
                    f"Deleted: **{todo.get('title', todo_id)}**"
                )
            )
        except APIError as exc:
            await interaction.followup.send(embed=error_embed(exc.detail))

    # ── Helpers ─────────────────────────────────────────────────

    async def _resolve_todo(self, todo_id: str) -> dict:
        """Try direct lookup first; fall back to searching by prefix."""
        try:
            return await self.api.get_todo(todo_id)
        except APIError:
            todos = await self.api.list_todos()
            for t in todos:
                if t["id"].startswith(todo_id):
                    return t
            raise APIError(404, f"No todo found matching `{todo_id}`")


async def setup(bot: commands.Bot):
    await bot.add_cog(TodoCog(bot))
