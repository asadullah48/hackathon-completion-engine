"""
Dapr Service for Course Companion API
Handles Dapr integration for pub/sub, state management, and service invocation.
Gracefully degrades when Dapr is not available (e.g., on Render, local dev without Dapr).
"""

import asyncio
import logging
from typing import Any, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import Dapr - gracefully handle when not installed
try:
    from dapr.clients import DaprClient
    from dapr.clients.exceptions import DaprInternalError
    DAPR_AVAILABLE = True
except ImportError:
    DAPR_AVAILABLE = False
    DaprClient = None
    DaprInternalError = Exception
    logger.info("Dapr package not installed. Running without Dapr integration.")


class DaprService:
    """
    Service for interacting with Dapr runtime.
    Provides pub/sub, state management, and service invocation capabilities.
    All methods gracefully no-op when Dapr is not available.
    """

    def __init__(self, dapr_client=None):
        self._dapr_client = dapr_client
        self._initialized = False

    @property
    def client(self):
        """Lazy-load Dapr client"""
        if not DAPR_AVAILABLE:
            return None
        if self._dapr_client is None:
            self._dapr_client = DaprClient()
        return self._dapr_client

    def initialize(self):
        """Initialize Dapr service"""
        if not DAPR_AVAILABLE:
            logger.info("Dapr not available. Skipping initialization.")
            return

        try:
            with self.client as dapr:
                pass
            self._initialized = True
            logger.info("Dapr service initialized successfully")
        except Exception as e:
            logger.error(f"Dapr initialization failed: {str(e)}")
            raise

    async def publish_event(self, topic_name: str, data: Dict[str, Any],
                           content_type: str = "application/json") -> bool:
        """Publish an event to a Dapr pub/sub topic."""
        if not DAPR_AVAILABLE or self.client is None:
            logger.debug(f"Dapr not available. Skipping publish to '{topic_name}'")
            return False

        try:
            event_data = {
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "course-companion-api"
            }

            with self.client as dapr:
                await dapr.publish_event(
                    pubsub_name="pubsub",
                    topic_name=topic_name,
                    data=event_data,
                    data_content_type=content_type
                )

            logger.info(f"Event published to topic '{topic_name}': {event_data}")
            return True

        except DaprInternalError as e:
            logger.error(f"Dapr internal error publishing event to '{topic_name}': {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error publishing event to '{topic_name}': {str(e)}")
            return False

    async def save_state(self, store_name: str, key: str, value: Any,
                         etag: Optional[str] = None) -> bool:
        """Save state to Dapr state store."""
        if not DAPR_AVAILABLE or self.client is None:
            logger.debug(f"Dapr not available. Skipping save_state to '{store_name}'")
            return False

        try:
            with self.client as dapr:
                await dapr.save_state(
                    store_name=store_name,
                    key=key,
                    value=value,
                    etag=etag
                )

            logger.info(f"State saved to store '{store_name}' with key '{key}'")
            return True

        except DaprInternalError as e:
            logger.error(f"Dapr internal error saving state to '{store_name}': {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error saving state to '{store_name}': {str(e)}")
            return False

    async def get_state(self, store_name: str, key: str) -> Optional[Any]:
        """Get state from Dapr state store."""
        if not DAPR_AVAILABLE or self.client is None:
            return None

        try:
            with self.client as dapr:
                response = await dapr.get_state(store_name=store_name, key=key)
                value = response.data

            logger.info(f"Retrieved state from store '{store_name}' with key '{key}'")
            return value

        except DaprInternalError as e:
            logger.error(f"Dapr internal error getting state from '{store_name}': {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error getting state from '{store_name}': {str(e)}")
            return None

    async def invoke_service(self, app_id: str, method: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """Invoke another service via Dapr service invocation."""
        if not DAPR_AVAILABLE or self.client is None:
            return None

        try:
            with self.client as dapr:
                response = await dapr.invoke_method(
                    app_id=app_id,
                    method=method,
                    data=data,
                    http_verb="POST",
                    http_querystring_params={}
                )
                response_data = response.json()

            logger.info(f"Service invocation to '{app_id}/{method}' successful")
            return response_data

        except DaprInternalError as e:
            logger.error(f"Dapr internal error invoking service '{app_id}/{method}': {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error invoking service '{app_id}/{method}': {str(e)}")
            return None


# Global Dapr service instance
_dapr_service: Optional[DaprService] = None


def get_dapr_service() -> DaprService:
    """Get or create singleton Dapr service instance"""
    global _dapr_service
    if _dapr_service is None:
        _dapr_service = DaprService()
    return _dapr_service
