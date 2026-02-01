"""Calendar router for calendar integrations."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from models.calendar import CalendarProvider, ConnectionStatus, SyncDirection
from models.todo import Todo
from services.calendar_service import CalendarService

router = APIRouter(prefix="/api/calendar", tags=["calendar"])


# Pydantic models
class ConnectionResponse(BaseModel):
    id: str
    user_id: str
    provider: str
    status: str
    calendar_id: Optional[str]
    calendar_name: Optional[str]
    sync_direction: Optional[str]
    sync_enabled: bool
    last_sync_at: Optional[str]
    settings: dict
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        from_attributes = True


class InitiateConnectionRequest(BaseModel):
    provider: str


class InitiateConnectionResponse(BaseModel):
    status: str
    connection_id: str
    oauth_url: Optional[str] = None
    message: str


class CompleteConnectionRequest(BaseModel):
    auth_code: Optional[str] = None


class UpdateSyncSettingsRequest(BaseModel):
    sync_enabled: Optional[bool] = None
    sync_direction: Optional[str] = None


class EventResponse(BaseModel):
    id: str
    connection_id: str
    todo_id: Optional[str]
    external_event_id: Optional[str]
    title: str
    description: Optional[str]
    start_time: Optional[str]
    end_time: Optional[str]
    is_all_day: bool
    location: Optional[str]
    recurrence_rule: Optional[str]
    is_synced: bool
    last_synced_at: Optional[str]
    sync_error: Optional[str]
    metadata: dict
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        from_attributes = True


class CreateEventRequest(BaseModel):
    title: str
    start_time: str
    end_time: Optional[str] = None
    description: Optional[str] = None
    is_all_day: bool = False
    location: Optional[str] = None
    todo_id: Optional[str] = None


class SyncResponse(BaseModel):
    synced: int
    failed: int
    total: int
    last_sync_at: str


@router.post("/connections", response_model=InitiateConnectionResponse)
def initiate_connection(
    request: InitiateConnectionRequest,
    user_id: str = Query(...),
    db: Session = Depends(get_db)
):
    """Initiate OAuth connection to a calendar provider."""
    try:
        provider = CalendarProvider(request.provider)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid provider: {request.provider}. Supported: google, outlook, apple"
        )

    result = CalendarService.initiate_connection(
        db=db,
        user_id=user_id,
        provider=provider
    )

    return result


@router.post("/connections/{connection_id}/complete", response_model=ConnectionResponse)
def complete_connection(
    connection_id: str,
    request: CompleteConnectionRequest,
    db: Session = Depends(get_db)
):
    """Complete OAuth connection after user authorization."""
    connection = CalendarService.complete_connection(
        db=db,
        connection_id=connection_id,
        auth_code=request.auth_code
    )

    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    return connection.to_dict()


@router.get("/connections", response_model=List[ConnectionResponse])
def get_connections(
    user_id: str = Query(...),
    provider: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get user's calendar connections."""
    provider_enum = None
    if provider:
        try:
            provider_enum = CalendarProvider(provider)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}")

    connections = CalendarService.get_connections(
        db=db,
        user_id=user_id,
        provider=provider_enum
    )

    return [c.to_dict() for c in connections]


@router.get("/connections/{connection_id}", response_model=ConnectionResponse)
def get_connection(
    connection_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific calendar connection."""
    connection = CalendarService.get_connection(db=db, connection_id=connection_id)

    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    return connection.to_dict()


@router.put("/connections/{connection_id}", response_model=ConnectionResponse)
def update_sync_settings(
    connection_id: str,
    request: UpdateSyncSettingsRequest,
    db: Session = Depends(get_db)
):
    """Update sync settings for a calendar connection."""
    sync_direction = None
    if request.sync_direction:
        try:
            sync_direction = SyncDirection(request.sync_direction)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sync direction: {request.sync_direction}"
            )

    connection = CalendarService.update_sync_settings(
        db=db,
        connection_id=connection_id,
        sync_enabled=request.sync_enabled,
        sync_direction=sync_direction
    )

    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    return connection.to_dict()


@router.delete("/connections/{connection_id}")
def disconnect(
    connection_id: str,
    db: Session = Depends(get_db)
):
    """Disconnect a calendar connection."""
    success = CalendarService.disconnect(db=db, connection_id=connection_id)

    if not success:
        raise HTTPException(status_code=404, detail="Connection not found")

    return {"message": "Disconnected successfully", "id": connection_id}


@router.get("/connections/{connection_id}/events", response_model=List[EventResponse])
def get_events(
    connection_id: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get calendar events for a connection."""
    start = None
    end = None

    if start_date:
        try:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format")

    if end_date:
        try:
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format")

    events = CalendarService.get_calendar_events(
        db=db,
        connection_id=connection_id,
        start_date=start,
        end_date=end
    )

    return [e.to_dict() for e in events]


@router.post("/connections/{connection_id}/events", response_model=EventResponse)
def create_event(
    connection_id: str,
    request: CreateEventRequest,
    db: Session = Depends(get_db)
):
    """Create a new calendar event."""
    try:
        start_time = datetime.fromisoformat(request.start_time.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid start_time format")

    end_time = None
    if request.end_time:
        try:
            end_time = datetime.fromisoformat(request.end_time.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_time format")

    event = CalendarService.create_event(
        db=db,
        connection_id=connection_id,
        title=request.title,
        start_time=start_time,
        end_time=end_time,
        description=request.description,
        is_all_day=request.is_all_day,
        location=request.location,
        todo_id=request.todo_id
    )

    if not event:
        raise HTTPException(
            status_code=400,
            detail="Failed to create event. Connection may not be active."
        )

    return event.to_dict()


@router.delete("/events/{event_id}")
def delete_event(
    event_id: str,
    db: Session = Depends(get_db)
):
    """Delete a calendar event."""
    success = CalendarService.delete_event(db=db, event_id=event_id)

    if not success:
        raise HTTPException(status_code=404, detail="Event not found")

    return {"message": "Event deleted", "id": event_id}


@router.post("/connections/{connection_id}/sync", response_model=SyncResponse)
def sync_todos(
    connection_id: str,
    user_id: str = Query(...),
    db: Session = Depends(get_db)
):
    """Sync all user's todos to the calendar."""
    result = CalendarService.sync_all_todos(
        db=db,
        user_id=user_id,
        connection_id=connection_id
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.post("/todos/{todo_id}/sync", response_model=EventResponse)
def sync_single_todo(
    todo_id: str,
    connection_id: str = Query(...),
    db: Session = Depends(get_db)
):
    """Sync a single todo to the calendar."""
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    event = CalendarService.sync_todo_to_calendar(
        db=db,
        todo=todo,
        connection_id=connection_id
    )

    if not event:
        raise HTTPException(
            status_code=400,
            detail="Failed to sync todo. Connection may not be active."
        )

    return event.to_dict()
