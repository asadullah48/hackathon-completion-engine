"""Calendar integration models for external calendar sync."""
import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Boolean, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship
from .todo import Base


class CalendarProvider(str, enum.Enum):
    """Supported calendar providers."""
    GOOGLE = "google"
    OUTLOOK = "outlook"
    APPLE = "apple"


class ConnectionStatus(str, enum.Enum):
    """Status of calendar connection."""
    PENDING = "pending"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class SyncDirection(str, enum.Enum):
    """Direction of calendar sync."""
    TODO_TO_CALENDAR = "todo_to_calendar"
    CALENDAR_TO_TODO = "calendar_to_todo"
    BIDIRECTIONAL = "bidirectional"


class CalendarConnection(Base):
    """User's connection to an external calendar service."""
    __tablename__ = "calendar_connections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)

    provider = Column(Enum(CalendarProvider), nullable=False)
    status = Column(Enum(ConnectionStatus), default=ConnectionStatus.PENDING)

    # OAuth tokens (encrypted in production)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)

    # Calendar-specific settings
    calendar_id = Column(String(255), nullable=True)  # Selected calendar ID
    calendar_name = Column(String(200), nullable=True)

    # Sync settings
    sync_direction = Column(Enum(SyncDirection), default=SyncDirection.TODO_TO_CALENDAR)
    sync_enabled = Column(Boolean, default=True)
    last_sync_at = Column(DateTime, nullable=True)

    # Additional settings
    settings = Column(JSON, default={})

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])

    def to_dict(self):
        """Convert to dictionary (excludes sensitive tokens)."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "provider": self.provider.value if self.provider else None,
            "status": self.status.value if self.status else None,
            "calendar_id": self.calendar_id,
            "calendar_name": self.calendar_name,
            "sync_direction": self.sync_direction.value if self.sync_direction else None,
            "sync_enabled": self.sync_enabled,
            "last_sync_at": self.last_sync_at.isoformat() if self.last_sync_at else None,
            "settings": self.settings,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class CalendarEvent(Base):
    """Synced calendar event, may be linked to a todo."""
    __tablename__ = "calendar_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    connection_id = Column(String(36), ForeignKey("calendar_connections.id"), nullable=False)
    todo_id = Column(String(36), ForeignKey("todos.id"), nullable=True)

    # External calendar event ID
    external_event_id = Column(String(255), nullable=True)

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    is_all_day = Column(Boolean, default=False)

    # Location (optional)
    location = Column(String(500), nullable=True)

    # Recurrence rule (iCal format)
    recurrence_rule = Column(String(500), nullable=True)

    # Sync metadata
    is_synced = Column(Boolean, default=False)
    last_synced_at = Column(DateTime, nullable=True)
    sync_error = Column(Text, nullable=True)

    # Event extra data
    event_data = Column(JSON, default={})

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    connection = relationship("CalendarConnection", foreign_keys=[connection_id])
    todo = relationship("Todo", foreign_keys=[todo_id])

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "connection_id": self.connection_id,
            "todo_id": self.todo_id,
            "external_event_id": self.external_event_id,
            "title": self.title,
            "description": self.description,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "is_all_day": self.is_all_day,
            "location": self.location,
            "recurrence_rule": self.recurrence_rule,
            "is_synced": self.is_synced,
            "last_synced_at": self.last_synced_at.isoformat() if self.last_synced_at else None,
            "sync_error": self.sync_error,
            "metadata": self.event_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
