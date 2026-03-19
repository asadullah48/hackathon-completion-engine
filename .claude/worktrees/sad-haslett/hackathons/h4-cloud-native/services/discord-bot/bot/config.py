"""Bot configuration loaded from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()

# Discord
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
BOT_STATUS = os.getenv("BOT_STATUS", "Managing todos")

# Backend API
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "10"))

# Bot behaviour
ITEMS_PER_PAGE = int(os.getenv("ITEMS_PER_PAGE", "5"))
BOT_COLOR = 0x5865F2  # Discord Blurple
