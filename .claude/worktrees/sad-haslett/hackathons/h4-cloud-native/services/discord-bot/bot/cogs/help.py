"""Help command for TodoMaster AI."""

import discord
from discord import app_commands
from discord.ext import commands

from bot.config import BOT_COLOR


class HelpCog(commands.Cog, name="Help"):
    """Display bot usage information."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Show all TodoMaster AI commands")
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="TodoMaster AI — Commands",
            description="The ONLY todo bot with Constitutional AI.",
            color=BOT_COLOR,
        )
        embed.add_field(
            name="\U0001f4dd Todo Management",
            value=(
                "`/todo-create` — Create a new todo\n"
                "`/todo-list` — List todos (all / active / completed)\n"
                "`/todo-show <id>` — Show todo details\n"
                "`/todo-complete <id>` — Mark todo as done\n"
                "`/todo-delete <id>` — Delete a todo"
            ),
            inline=False,
        )
        embed.add_field(
            name="\u2139\ufe0f General",
            value="`/help` — Show this message",
            inline=False,
        )
        embed.set_footer(text="Powered by AI  |  Constitutional AI Protected")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))
