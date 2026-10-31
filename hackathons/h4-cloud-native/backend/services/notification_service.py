"""Notification Service - Consumes Kafka events via Dapr pub/sub."""
from fastapi import FastAPI, Request
from datetime import datetime
import logging, json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("notification-service")
app = FastAPI(title="Todo Notification Service", version="1.0.0")

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "notification-service"}

@app.get("/dapr/subscribe")
async def subscribe():
    """Tell Dapr which Kafka topics to subscribe to."""
    return [
        {"pubsubname": "pubsub", "topic": "todo-events", "route": "/events/todo"},
        {"pubsubname": "pubsub", "topic": "todo-notifications", "route": "/events/notifications"},
    ]

@app.post("/events/todo")
async def handle_todo_event(request: Request):
    try:
        event = await request.json()
        event_data = event.get("data", event)
        event_type = event_data.get("type", "unknown")
        logger.info(f"TODO EVENT [{event_type}]: {json.dumps(event_data, indent=2, default=str)}")
        return {"success": True}
    except Exception as e:
        logger.error(f"Error processing todo event: {e}")
        return {"success": False, "error": str(e)}

@app.post("/events/notifications")
async def handle_notification(request: Request):
    event = await request.json()
    logger.info(f"NOTIFICATION: {json.dumps(event, indent=2, default=str)}")
    return {"success": True}
