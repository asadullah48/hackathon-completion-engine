"""
H1 Course Companion FTE - Main FastAPI Application
Enforces constitutional rules for academic integrity
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import routers
from routers import chat, progress

# Import middleware
from middleware.constitutional_filter import ConstitutionalFilter

# Initialize FastAPI app
app = FastAPI(
    title="Course Companion API",
    description="AI-powered learning assistant with constitutional rules",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constitutional filter middleware
constitutional_filter = ConstitutionalFilter()


@app.middleware("http")
async def constitutional_middleware(request: Request, call_next):
    """
    Constitutional filtering middleware
    Logs all requests and applies filtering to chat endpoints
    """
    start_time = time.time()

    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")

    # Process request
    response = await call_next(request)

    # Log response time
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"Response: {response.status_code} in {process_time:.3f}s")

    return response


# Health check endpoint
@app.get("/")
async def root():
    return {
        "status": "operational",
        "service": "Course Companion API",
        "version": "1.0.0",
        "constitutional_rules": "enforced"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "api_key_configured": bool(os.getenv("OPENAI_API_KEY"))
    }


# Include routers with /api prefix
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(progress.router, prefix="/api", tags=["progress"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
