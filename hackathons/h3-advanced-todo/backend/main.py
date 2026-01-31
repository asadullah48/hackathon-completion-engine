"""
H3 Advanced Todo API
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
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db, get_db
from routers import (
    todos_router,
    stats_router,
    recurring_router,
    templates_router,
    users_router,
    teams_router,
    assignments_router,
)
from seeds import seed_templates


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and seed data on startup."""
    init_db()

    # Seed templates
    db = next(get_db())
    try:
        seed_templates(db)
    finally:
        db.close()

    yield


app = FastAPI(
    title="H3 Advanced Todo API",
    description="Zero-Backend-LLM Task Management with Constitutional Compliance, Recurring Todos, Templates, and Team Collaboration",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
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


@app.get("/")
async def root():
    """API info endpoint."""
    return {
        "name": "H3 Advanced Todo API",
        "version": "2.0.0",
        "description": "Zero-Backend-LLM Task Management with Constitutional Compliance and Team Collaboration",
        "endpoints": {
            "todos": "/api/todos",
            "stats": "/api/stats",
            "recurring": "/api/recurring",
            "templates": "/api/templates",
            "users": "/api/users",
            "teams": "/api/teams",
            "assignments": "/api/assignments",
            "health": "/health",
            "docs": "/docs",
        },
        "features": [
            "CRUD operations with SQLite persistence",
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
        ],
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "h3-advanced-todo-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
