"""Pagination utilities for Discord embed lists."""

import math
from typing import Any

from bot.config import ITEMS_PER_PAGE


def paginate(items: list[Any], page: int = 1) -> tuple[list[Any], int, int]:
    """Return (page_items, current_page, total_pages)."""
    total_pages = max(1, math.ceil(len(items) / ITEMS_PER_PAGE))
    page = max(1, min(page, total_pages))
    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    return items[start:end], page, total_pages
