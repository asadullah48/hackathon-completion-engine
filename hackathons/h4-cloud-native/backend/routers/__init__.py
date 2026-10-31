"""Routers package."""
from .todos import router as todos_router
from .stats import router as stats_router
from .recurring import router as recurring_router
from .templates import router as templates_router
from .users import router as users_router
from .teams import router as teams_router
from .assignments import router as assignments_router
from .suggestions import router as suggestions_router
from .calendar import router as calendar_router

__all__ = [
    "todos_router",
    "stats_router",
    "recurring_router",
    "templates_router",
    "users_router",
    "teams_router",
    "assignments_router",
    "suggestions_router",
    "calendar_router",
]
