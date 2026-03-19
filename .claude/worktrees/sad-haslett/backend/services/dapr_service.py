"""
Dapr Service for Course Companion API
Handles Dapr integration for pub/sub, state management, and service invocation
"""

import asyncio
import logging
from typing import Any, Dict, Optional
from datetime import datetime

from dapr.clients import DaprClient
from dapr.clients.exceptions import DaprInternalError

logger = logging.getLogger(__name__)


class DaprService:
    """
    Service for interacting with Dapr runtime
    Provides pub/sub, state management, and service invocation capabilities
    """

    def __init__(self, dapr_client: Optional[DaprClient] = None):
        self._dapr_client = dapr_client
        self._initialized = False

    @property
    def client(self) -> DaprClient:
        """Lazy-load Dapr client"""
        if self._dapr_client is None:
            self._dapr_client = DaprClient()
        return self._dapr_client

    def initialize(self):
        """Initialize Dapr service"""
        try:
            # Test connection to Dapr
            with self.client as dapr:
                # This will establish connection to Dapr sidecar
                pass
            self._initialized = True
            logger.info("Dapr service initialized successfully")
        except Exception as e:
            logger.error(f"Dapr initialization failed: {str(e)}")
            raise

    async def publish_event(self, topic_name: str, data: Dict[str, Any], 
                           content_type: str = "application/json") -> bool:
        """
        Publish an event to a Dapr pub/sub topic

        Args:
            topic_name: Name of the pub/sub topic
            data: Event data to publish
            content_type: Content type of the data

        Returns:
            True if published successfully, False otherwise
        """
        try:
            # Add timestamp to the event
            event_data = {
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "course-companion-api"
            }

            with self.client as dapr:
                await dapr.publish_event(
                    pubsub_name="pubsub",  # This matches the pubsub component name
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
        """
        Save state to Dapr state store

        Args:
            store_name: Name of the state store
            key: State key
            value: State value
            etag: Optional etag for conditional updates

        Returns:
            True if saved successfully, False otherwise
        """
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
        """
        Get state from Dapr state store

        Args:
            store_name: Name of the state store
            key: State key

        Returns:
            State value if found, None otherwise
        """
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
        """
        Invoke another service via Dapr service invocation

        Args:
            app_id: Target service app ID
            method: Method to invoke
            data: Optional data to send

        Returns:
            Response from the target service
        """
        try:
            with self.client as dapr:
                response = await dapr.invoke_method(
                    app_id=app_id,
                    method=method,
                    data=data,
                    http_verb="POST",
                    http_querystring_params={}
                )
                
                # Decode response data
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