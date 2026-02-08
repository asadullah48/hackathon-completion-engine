"""Dapr integration service for pub/sub events and state management."""
import json
import logging
import time
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

logger = logging.getLogger(__name__)

DAPR_HTTP_PORT = 3500
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"
PUBSUB_NAME = "pubsub"
STATE_STORE = "statestore"


class DaprService:
    """Lightweight Dapr client using the HTTP API."""

    def __init__(self):
        self._healthy = False

    def check_health(self) -> bool:
        """Check if the Dapr sidecar is available."""
        try:
            req = Request(f"{DAPR_BASE_URL}/v1.0/healthz")
            urlopen(req, timeout=2)
            if not self._healthy:
                logger.info("Dapr sidecar connected")
            self._healthy = True
            return True
        except Exception as e:
            self._healthy = False
            logger.warning(f"Dapr health check failed: {e}")
            return False

    def publish_event(self, topic: str, data: dict) -> bool:
        """Publish an event to a Dapr pub/sub topic. Retries health check if needed."""
        if not self._healthy:
            self.check_health()

        try:
            payload = json.dumps(data).encode()
            req = Request(
                f"{DAPR_BASE_URL}/v1.0/publish/{PUBSUB_NAME}/{topic}",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            urlopen(req, timeout=5)
            self._healthy = True
            logger.info(f"Published event to {topic}: {data.get('type', 'unknown')}")
            return True
        except Exception as e:
            self._healthy = False
            logger.warning(f"Failed to publish to {topic}: {e}")
            return False

    def save_state(self, key: str, value: dict) -> bool:
        """Save state to the Dapr state store."""
        if not self._ensure_healthy():
            return False

        try:
            payload = json.dumps([{"key": key, "value": value}]).encode()
            req = Request(
                f"{DAPR_BASE_URL}/v1.0/state/{STATE_STORE}",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            urlopen(req, timeout=5)
            return True
        except (URLError, HTTPError) as e:
            logger.warning(f"Failed to save state {key}: {e}")
            return False

    def get_state(self, key: str) -> dict | None:
        """Get state from the Dapr state store."""
        if not self._ensure_healthy():
            return None

        try:
            req = Request(f"{DAPR_BASE_URL}/v1.0/state/{STATE_STORE}/{key}")
            resp = urlopen(req, timeout=5)
            data = resp.read().decode()
            return json.loads(data) if data else None
        except (URLError, HTTPError) as e:
            logger.warning(f"Failed to get state {key}: {e}")
            return None


# Singleton
_dapr_service = DaprService()


def get_dapr_service() -> DaprService:
    return _dapr_service


def publish_todo_event(event_type: str, todo_id: str, **kwargs) -> bool:
    """Convenience function to publish a todo-related event."""
    from metrics.prometheus_metrics import TODO_EVENTS
    data = {
        "type": event_type,
        "todo_id": todo_id,
        "timestamp": time.time(),
        **kwargs,
    }
    result = _dapr_service.publish_event("todo-events", data)
    if result:
        TODO_EVENTS.labels(event_type=event_type).inc()
    return result
