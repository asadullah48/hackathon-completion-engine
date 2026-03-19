"""
H2 Todo Spec-Driven API
Zero-Backend-LLM Task Management with Constitutional Compliance

This FastAPI backend provides:
- CRUD operations for todos
- Constitutional validation on content
- Statistics endpoint
- HITL approval workflow for flagged items

All AI logic runs in the frontend (Zero-Backend-LLM architecture).
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routers import todos_router, stats_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    init_db()
    yield


app = FastAPI(
    title="H2 Todo API",
    description="Zero-Backend-LLM Task Management with Constitutional Compliance",
    version="1.0.0",
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


@app.get("/")
async def root():
    """API info endpoint."""
    return {
        "name": "H2 Todo API",
        "version": "1.0.0",
        "description": "Zero-Backend-LLM Task Management with Constitutional Compliance",
        "endpoints": {
            "todos": "/api/todos",
            "stats": "/api/stats",
            "health": "/health",
            "docs": "/docs",
        },
        "features": [
            "CRUD operations with SQLite persistence",
            "Constitutional validation (blocks academic dishonesty, illegal activities, harmful content)",
            "HITL approval workflow for flagged todos",
            "Search and filter capabilities",
            "Statistics dashboard data",
        ],
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "h2-todo-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
