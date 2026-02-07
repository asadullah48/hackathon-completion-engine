"""
H4 Cloud-Native Todo API
Zero-Backend-LLM Task Management with Constitutional Compliance

This FastAPI backend provides:
- CRUD operations for todos
- Constitutional validation on content
- Statistics endpoint
- HITL approval workflow for flagged items
- Recurring todo patterns
- Todo templates
- Team collaboration
- Todo assignments

All AI logic runs in the frontend (Zero-Backend-LLM architecture).
"""
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db, get_db
from services.dapr_service import get_dapr_service
from routers import (
    todos_router,
    stats_router,
    recurring_router,
    templates_router,
    users_router,
    teams_router,
    assignments_router,
    suggestions_router,
    calendar_router,
)
from seeds import seed_templates


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database, Dapr, and seed data on startup."""
    init_db()

    # Seed templates
    db = next(get_db())
    try:
        seed_templates(db)
    finally:
        db.close()

    # Initialize Dapr sidecar connection (retry for sidecar startup race)
    import time as _time
    dapr = get_dapr_service()
    for attempt in range(10):
        if dapr.check_health():
            logger.info("Dapr sidecar connected successfully")
            break
        logger.info(f"Waiting for Dapr sidecar (attempt {attempt + 1}/10)...")
        _time.sleep(2)
    else:
        logger.warning("Dapr sidecar not available at startup - will retry on first publish")

    yield


app = FastAPI(
    title="H4 Cloud-Native Todo API",
    description="Zero-Backend-LLM Task Management with Constitutional Compliance, Recurring Todos, Templates, and Team Collaboration - Kubernetes Deployment",
    version="4.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend
# Allow origins from environment or default to localhost
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
allowed_origins = [origin.strip() for origin in cors_origins.split(",")]
# Support wildcard for development
if cors_origins == "*":
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(todos_router)
app.include_router(stats_router)
app.include_router(recurring_router)
app.include_router(templates_router)
app.include_router(users_router)
app.include_router(teams_router)
app.include_router(assignments_router)
app.include_router(suggestions_router)
app.include_router(calendar_router)


@app.get("/")
async def root():
    """API info endpoint."""
    return {
        "name": "H4 Cloud-Native Todo API",
        "version": "4.0.0",
        "description": "Zero-Backend-LLM Task Management with Constitutional Compliance and Team Collaboration - Kubernetes Deployment",
        "endpoints": {
            "todos": "/api/todos",
            "stats": "/api/stats",
            "recurring": "/api/recurring",
            "templates": "/api/templates",
            "users": "/api/users",
            "teams": "/api/teams",
            "assignments": "/api/assignments",
            "suggestions": "/api/suggestions",
            "calendar": "/api/calendar",
            "health": "/health",
            "docs": "/docs",
        },
        "features": [
            "CRUD operations with PostgreSQL/SQLite persistence",
            "Constitutional validation (blocks academic dishonesty, illegal activities, harmful content)",
            "HITL approval workflow for flagged todos",
            "Search and filter capabilities",
            "Statistics dashboard data",
            "Recurring todo patterns (daily, weekly, monthly, custom)",
            "Todo templates with 5 built-in templates",
            "Automatic todo generation from recurring patterns",
            "Team collaboration",
            "User management",
            "Todo assignments with status tracking",
            "Role-based permissions (owner, admin, editor, viewer)",
            "AI-powered task suggestions",
            "Productivity insights",
            "Calendar integration (Google, Outlook, Apple)",
            "Todo-to-calendar sync",
        ],
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "h4-cloud-native-todo-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
