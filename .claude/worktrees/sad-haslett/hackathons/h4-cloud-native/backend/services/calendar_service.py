"""Calendar Service for managing calendar integrations."""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import uuid

from models.calendar import (
    CalendarConnection, CalendarEvent,
    CalendarProvider, ConnectionStatus, SyncDirection
)
from models.todo import Todo


class CalendarService:
    """Service for managing calendar connections and events."""

    # Mock OAuth URLs (in production, these would be real OAuth endpoints)
    OAUTH_URLS = {
        CalendarProvider.GOOGLE: "https://accounts.google.com/o/oauth2/v2/auth",
        CalendarProvider.OUTLOOK: "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        CalendarProvider.APPLE: "https://appleid.apple.com/auth/authorize",
    }

    @staticmethod
    def initiate_connection(
        db: Session,
        user_id: str,
        provider: CalendarProvider
    ) -> Dict[str, Any]:
        """
        Initiate OAuth connection to a calendar provider.
        Returns mock OAuth URL for demo purposes.
        """
        # Check for existing connection
        existing = db.query(CalendarConnection).filter(
            CalendarConnection.user_id == user_id,
            CalendarConnection.provider == provider
        ).first()

        if existing and existing.status == ConnectionStatus.CONNECTED:
            return {
                "status": "already_connected",
                "connection_id": existing.id,
                "message": f"Already connected to {provider.value}"
            }

        # Create pending connection
        connection = CalendarConnection(
            user_id=user_id,
            provider=provider,
            status=ConnectionStatus.PENDING
        )
        db.add(connection)
        db.commit()
        db.refresh(connection)

        # Return mock OAuth URL
        oauth_url = CalendarService.OAUTH_URLS.get(provider, "")
        return {
            "status": "pending",
            "connection_id": connection.id,
            "oauth_url": f"{oauth_url}?state={connection.id}&redirect_uri=http://localhost:3000/calendar/callback",
            "message": f"Redirect user to OAuth URL to authorize {provider.value}"
        }

    @staticmethod
    def complete_connection(
        db: Session,
        connection_id: str,
        auth_code: Optional[str] = None
    ) -> Optional[CalendarConnection]:
        """
        Complete OAuth connection (mock implementation).
        In production, this would exchange auth_code for tokens.
        """
        connection = db.query(CalendarConnection).filter(
            CalendarConnection.id == connection_id
        ).first()

        if not connection:
            return None

        # Mock token exchange
        connection.access_token = f"mock_access_token_{uuid.uuid4().hex[:8]}"
        connection.refresh_token = f"mock_refresh_token_{uuid.uuid4().hex[:8]}"
        connection.token_expires_at = datetime.utcnow() + timedelta(hours=1)
        connection.status = ConnectionStatus.CONNECTED
        connection.calendar_name = f"Primary Calendar ({connection.provider.value})"
        connection.calendar_id = f"primary_{connection.user_id}"

        db.commit()
        db.refresh(connection)
        return connection

    @staticmethod
    def disconnect(db: Session, connection_id: str) -> bool:
        """Disconnect a calendar connection."""
        connection = db.query(CalendarConnection).filter(
            CalendarConnection.id == connection_id
        ).first()

        if not connection:
            return False

        connection.status = ConnectionStatus.DISCONNECTED
        connection.access_token = None
        connection.refresh_token = None
        connection.sync_enabled = False

        db.commit()
        return True

    @staticmethod
    def get_connections(
        db: Session,
        user_id: str,
        provider: Optional[CalendarProvider] = None
    ) -> List[CalendarConnection]:
        """Get user's calendar connections."""
        query = db.query(CalendarConnection).filter(
            CalendarConnection.user_id == user_id
        )

        if provider:
            query = query.filter(CalendarConnection.provider == provider)

        return query.all()

    @staticmethod
    def get_connection(db: Session, connection_id: str) -> Optional[CalendarConnection]:
        """Get a specific calendar connection."""
        return db.query(CalendarConnection).filter(
            CalendarConnection.id == connection_id
        ).first()

    @staticmethod
    def update_sync_settings(
        db: Session,
        connection_id: str,
        sync_enabled: Optional[bool] = None,
        sync_direction: Optional[SyncDirection] = None
    ) -> Optional[CalendarConnection]:
        """Update sync settings for a connection."""
        connection = db.query(CalendarConnection).filter(
            CalendarConnection.id == connection_id
        ).first()

        if not connection:
            return None

        if sync_enabled is not None:
            connection.sync_enabled = sync_enabled
        if sync_direction is not None:
            connection.sync_direction = sync_direction

        db.commit()
        db.refresh(connection)
        return connection

    @staticmethod
    def sync_todo_to_calendar(
        db: Session,
        todo: Todo,
        connection_id: str
    ) -> Optional[CalendarEvent]:
        """
        Sync a todo to the external calendar (mock implementation).
        Creates a calendar event for the todo.
        """
        connection = db.query(CalendarConnection).filter(
            CalendarConnection.id == connection_id,
            CalendarConnection.status == ConnectionStatus.CONNECTED
        ).first()

        if not connection:
            return None

        # Check if event already exists
        existing = db.query(CalendarEvent).filter(
            CalendarEvent.todo_id == todo.id,
            CalendarEvent.connection_id == connection_id
        ).first()

        if existing:
            # Update existing event
            existing.title = todo.title
            existing.description = todo.description
            if todo.deadline:
                existing.start_time = todo.deadline
                existing.end_time = todo.deadline + timedelta(hours=1)
            existing.is_synced = True
            existing.last_synced_at = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return existing

        # Create new event
        event = CalendarEvent(
            connection_id=connection_id,
            todo_id=todo.id,
            external_event_id=f"mock_event_{uuid.uuid4().hex[:8]}",
            title=todo.title,
            description=todo.description,
            start_time=todo.deadline or datetime.utcnow() + timedelta(days=1),
            end_time=(todo.deadline or datetime.utcnow() + timedelta(days=1)) + timedelta(hours=1),
            is_synced=True,
            last_synced_at=datetime.utcnow(),
            event_data={"todo_status": todo.status.value if todo.status else None}
        )

        db.add(event)
        db.commit()
        db.refresh(event)

        # Update connection last sync time
        connection.last_sync_at = datetime.utcnow()
        db.commit()

        return event

    @staticmethod
    def get_calendar_events(
        db: Session,
        connection_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[CalendarEvent]:
        """Get calendar events for a connection."""
        query = db.query(CalendarEvent).filter(
            CalendarEvent.connection_id == connection_id
        )

        if start_date:
            query = query.filter(CalendarEvent.start_time >= start_date)
        if end_date:
            query = query.filter(CalendarEvent.start_time <= end_date)

        return query.order_by(CalendarEvent.start_time).all()

    @staticmethod
    def create_event(
        db: Session,
        connection_id: str,
        title: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        description: Optional[str] = None,
        is_all_day: bool = False,
        location: Optional[str] = None,
        todo_id: Optional[str] = None
    ) -> Optional[CalendarEvent]:
        """Create a new calendar event."""
        connection = db.query(CalendarConnection).filter(
            CalendarConnection.id == connection_id,
            CalendarConnection.status == ConnectionStatus.CONNECTED
        ).first()

        if not connection:
            return None

        event = CalendarEvent(
            connection_id=connection_id,
            todo_id=todo_id,
            external_event_id=f"mock_event_{uuid.uuid4().hex[:8]}",
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time or (start_time + timedelta(hours=1)),
            is_all_day=is_all_day,
            location=location,
            is_synced=True,
            last_synced_at=datetime.utcnow()
        )

        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def delete_event(db: Session, event_id: str) -> bool:
        """Delete a calendar event."""
        event = db.query(CalendarEvent).filter(
            CalendarEvent.id == event_id
        ).first()

        if not event:
            return False

        db.delete(event)
        db.commit()
        return True

    @staticmethod
    def sync_all_todos(
        db: Session,
        user_id: str,
        connection_id: str
    ) -> Dict[str, Any]:
        """Sync all user's todos to calendar."""
        connection = db.query(CalendarConnection).filter(
            CalendarConnection.id == connection_id,
            CalendarConnection.user_id == user_id,
            CalendarConnection.status == ConnectionStatus.CONNECTED
        ).first()

        if not connection:
            return {"error": "Connection not found or not connected"}

        # Get todos with due dates
        todos = db.query(Todo).filter(
            Todo.owner_id == user_id,
            Todo.deadline != None
        ).all()

        synced = 0
        failed = 0

        for todo in todos:
            try:
                CalendarService.sync_todo_to_calendar(db, todo, connection_id)
                synced += 1
            except Exception:
                failed += 1

        connection.last_sync_at = datetime.utcnow()
        db.commit()

        return {
            "synced": synced,
            "failed": failed,
            "total": len(todos),
            "last_sync_at": connection.last_sync_at.isoformat()
        }


def get_calendar_service() -> CalendarService:
    """Factory function to get CalendarService instance."""
    return CalendarService()
