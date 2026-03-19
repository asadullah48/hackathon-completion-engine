"""TodoMaster AI — Discord bot entry point."""

import asyncio
import logging
import os

import discord
from discord.ext import commands

from bot.config import DISCORD_TOKEN, BOT_STATUS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s  %(message)s",
)
logger = logging.getLogger("todomaster")

EXTENSIONS = [
    "bot.cogs.todo",
    "bot.cogs.help",
]


class TodoMasterBot(commands.Bot):
    """Custom bot subclass for TodoMaster AI."""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        for ext in EXTENSIONS:
            await self.load_extension(ext)
            logger.info("Loaded extension: %s", ext)
        await self.tree.sync()
        logger.info("Slash commands synced globally")

    async def on_ready(self):
        assert self.user is not None
        logger.info("Logged in as %s (ID: %s)", self.user, self.user.id)
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, name=BOT_STATUS
            )
        )


def main():
    if not DISCORD_TOKEN:
        logger.error("DISCORD_BOT_TOKEN is not set — exiting")
        raise SystemExit(1)

    bot = TodoMasterBot()
    bot.run(DISCORD_TOKEN, log_handler=None)


if __name__ == "__main__":
    main()
