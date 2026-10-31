
"""
Personal AI Employee - Main FastAPI Application
Dual AI engine: OpenAI for chat, Claude for vault reasoning.
Enforces constitutional rules for academic integrity.
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
from routers import vault

# Import middleware
from middleware.constitutional_filter import ConstitutionalFilter

# Import Dapr service
from services.dapr_service import get_dapr_service

# Initialize FastAPI app
app = FastAPI(
    title="Personal AI Employee API",
    description="Dual AI engine: OpenAI (chat) + Claude (vault reasoning). Constitutional rules enforced.",
    version="2.0.0"
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

# Initialize Dapr service
dapr_service = get_dapr_service()


@app.on_event('startup')
async def startup_event():
    """Initialize services on application startup"""
    # Ensure vault directories exist (needed for Render/cloud where filesystem starts empty)
    vault_path = os.getenv("VAULT_PATH", "../vault")
    for subdir in ["Inbox", "Needs_Action", "Pending_Approval", "Approved",
                    "Rejected", "Done", "Briefings", "Logs", "Conversation_Logs"]:
        os.makedirs(os.path.join(vault_path, subdir), exist_ok=True)
    logger.info(f"Vault directories ensured at: {vault_path}")

    try:
        dapr_service.initialize()
        logger.info("Dapr service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Dapr service: {str(e)}")
        # Continue without Dapr if initialization fails


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
        "service": "Personal AI Employee API",
        "version": "2.0.0",
        "ai_engines": {"openai": "chat", "claude": "vault_reasoning"},
        "constitutional_rules": "enforced",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "engines": {
            "openai": {"configured": bool(os.getenv("OPENAI_API_KEY")), "role": "chat_companion"},
            "claude": {"configured": bool(os.getenv("ANTHROPIC_API_KEY")), "role": "vault_reasoning"},
        },
    }


# Include routers with /api prefix
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(progress.router, prefix="/api", tags=["progress"])
app.include_router(vault.router, prefix="/api", tags=["vault"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
