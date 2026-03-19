"""
Base Watcher - Abstract base class for all watchers
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict


class BaseWatcher(ABC):
    """Abstract base class for all watcher implementations."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize watcher with configuration.

        Args:
            config: Dictionary containing watcher configuration
        """
        self.config = config
        self.enabled = config.get('enabled', True)

    @abstractmethod
    def start(self):
        """Start the watcher service."""
        pass

    @abstractmethod
    def stop(self):
        """Stop the watcher service."""
        pass

    @abstractmethod
    def check_for_updates(self):
        """Check for new updates/events."""
        pass

    def update_dashboard(self, status: str, details: Dict[str, Any] = None):
        """
        Update the dashboard with current status.

        Args:
            status: Status indicator (e.g., 'running', 'stopped', 'error')
            details: Additional details about the status
        """
        # This would typically update the Dashboard.md file
        pass