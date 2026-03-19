"""Recurring Todo router for managing recurring patterns."""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from models import RecurringTodo, Todo
from services import RecurringService

router = APIRouter(prefix="/api/recurring", tags=["recurring"])


# Pydantic schemas
class RecurringCreateRequest(BaseModel):
    """Schema for creating a recurring todo pattern."""
    pattern: str = Field(..., description="Recurrence pattern: daily, weekly, monthly, custom")
    interval: int = Field(default=1, ge=1, description="Every N days/weeks/months")
    days_of_week: Optional[List[int]] = Field(None, description="Days of week [0=Mon, ..., 6=Sun]")
    day_of_month: Optional[int] = Field(None, ge=1, le=31, description="Day of month (1-31)")
    end_date: Optional[datetime] = None
    skip_holidays: bool = False
    template_todo_id: str = Field(..., description="ID of template todo to clone")


class RecurringUpdateRequest(BaseModel):
    """Schema for updating a recurring todo pattern."""
    pattern: Optional[str] = None
    interval: Optional[int] = Field(None, ge=1)
    days_of_week: Optional[List[int]] = None
    day_of_month: Optional[int] = Field(None, ge=1, le=31)
    end_date: Optional[datetime] = None
    skip_holidays: Optional[bool] = None
    is_active: Optional[bool] = None


class RecurringResponse(BaseModel):
    """Schema for recurring todo response."""
    id: str
    pattern: str
    interval: int
    days_of_week: Optional[List[int]]
    day_of_month: Optional[int]
    start_date: str
    end_date: Optional[str]
    next_occurrence: Optional[str]
    last_generated: Optional[str]
    skip_holidays: bool
    is_active: bool
    template_todo_id: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class TodoResponse(BaseModel):
    """Schema for todo response (simplified for generated todos)."""
    id: str
    title: str
    deadline: Optional[str]


@router.post("", response_model=RecurringResponse, status_code=201)
async def create_recurring(
    request: RecurringCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Create a recurring todo pattern.

    The pattern will automatically generate todos based on the schedule.
    """
    # Verify template todo exists
    template = db.query(Todo).filter(Todo.id == request.template_todo_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template todo not found")

    # Validate pattern
    valid_patterns = ["daily", "weekly", "monthly", "custom"]
    if request.pattern not in valid_patterns:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid pattern. Must be one of: {', '.join(valid_patterns)}"
        )

    # Create recurring todo
    recurring = RecurringTodo(
        pattern=request.pattern,
        interval=request.interval,
        days_of_week=request.days_of_week,
        day_of_month=request.day_of_month,
        end_date=request.end_date,
        skip_holidays=request.skip_holidays,
        template_todo_id=request.template_todo_id
    )

    # Calculate first occurrence
    recurring.next_occurrence = RecurringService.calculate_next_occurrence(recurring)

    db.add(recurring)
    db.commit()
    db.refresh(recurring)

    return _format_recurring_response(recurring)


@router.get("", response_model=List[RecurringResponse])
async def list_recurring(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    List all recurring todo patterns.

    Args:
        active_only: If True, only return active patterns
    """
    query = db.query(RecurringTodo)

    if active_only:
        query = query.filter(RecurringTodo.is_active == True)

    recurring_todos = query.order_by(RecurringTodo.created_at.desc()).all()
    return [_format_recurring_response(r) for r in recurring_todos]


@router.get("/{recurring_id}", response_model=RecurringResponse)
async def get_recurring(recurring_id: str, db: Session = Depends(get_db)):
    """Get a specific recurring pattern."""
    recurring = db.query(RecurringTodo).filter(RecurringTodo.id == recurring_id).first()
    if not recurring:
        raise HTTPException(status_code=404, detail="Recurring pattern not found")
    return _format_recurring_response(recurring)


@router.put("/{recurring_id}", response_model=RecurringResponse)
async def update_recurring(
    recurring_id: str,
    update_data: RecurringUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update a recurring pattern."""
    recurring = db.query(RecurringTodo).filter(RecurringTodo.id == recurring_id).first()
    if not recurring:
        raise HTTPException(status_code=404, detail="Recurring pattern not found")

    # Update fields
    if update_data.pattern is not None:
        recurring.pattern = update_data.pattern
    if update_data.interval is not None:
        recurring.interval = update_data.interval
    if update_data.days_of_week is not None:
        recurring.days_of_week = update_data.days_of_week
    if update_data.day_of_month is not None:
        recurring.day_of_month = update_data.day_of_month
    if update_data.end_date is not None:
        recurring.end_date = update_data.end_date
    if update_data.skip_holidays is not None:
        recurring.skip_holidays = update_data.skip_holidays
    if update_data.is_active is not None:
        recurring.is_active = update_data.is_active

    # Recalculate next occurrence
    recurring.next_occurrence = RecurringService.calculate_next_occurrence(recurring)

    recurring.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(recurring)

    return _format_recurring_response(recurring)


@router.delete("/{recurring_id}")
async def delete_recurring(recurring_id: str, db: Session = Depends(get_db)):
    """Delete a recurring pattern."""
    recurring = db.query(RecurringTodo).filter(RecurringTodo.id == recurring_id).first()
    if not recurring:
        raise HTTPException(status_code=404, detail="Recurring pattern not found")

    db.delete(recurring)
    db.commit()

    return {"deleted": True, "id": recurring_id}


@router.post("/{recurring_id}/generate", response_model=TodoResponse)
async def generate_occurrence(recurring_id: str, db: Session = Depends(get_db)):
    """
    Manually generate the next occurrence.

    This creates a new todo from the recurring pattern immediately.
    """
    recurring = db.query(RecurringTodo).filter(RecurringTodo.id == recurring_id).first()
    if not recurring:
        raise HTTPException(status_code=404, detail="Recurring pattern not found")

    if not recurring.is_active:
        raise HTTPException(status_code=400, detail="Recurring pattern is not active")

    todo = RecurringService.generate_occurrence(db, recurring)
    if not todo:
        raise HTTPException(
            status_code=400,
            detail="No more occurrences (end date reached or template not found)"
        )

    return {
        "id": todo.id,
        "title": todo.title,
        "deadline": todo.deadline.isoformat() if todo.deadline else None
    }


@router.post("/generate-all")
async def generate_all_due(db: Session = Depends(get_db)):
    """
    Generate all due recurring occurrences.

    This endpoint is intended for cron job scheduling.
    It generates todos for all recurring patterns that are due.
    """
    generated = RecurringService.generate_due_occurrences(db)
    return {
        "generated": len(generated),
        "todos": [
            {"id": t.id, "title": t.title, "deadline": t.deadline.isoformat() if t.deadline else None}
            for t in generated
        ]
    }


@router.get("/{recurring_id}/preview")
async def preview_occurrences(
    recurring_id: str,
    count: int = 5,
    db: Session = Depends(get_db)
):
    """
    Preview upcoming occurrences without generating todos.

    Args:
        count: Number of occurrences to preview (default 5, max 20)
    """
    recurring = db.query(RecurringTodo).filter(RecurringTodo.id == recurring_id).first()
    if not recurring:
        raise HTTPException(status_code=404, detail="Recurring pattern not found")

    count = min(count, 20)  # Limit to 20
    occurrences = RecurringService.preview_occurrences(recurring, count)

    return {
        "recurring_id": recurring_id,
        "pattern": recurring.pattern,
        "interval": recurring.interval,
        "upcoming_occurrences": [d.isoformat() for d in occurrences]
    }


def _format_recurring_response(recurring: RecurringTodo) -> dict:
    """Format a recurring todo for API response."""
    return {
        "id": recurring.id,
        "pattern": recurring.pattern,
        "interval": recurring.interval,
        "days_of_week": recurring.days_of_week,
        "day_of_month": recurring.day_of_month,
        "start_date": recurring.start_date.isoformat() if recurring.start_date else None,
        "end_date": recurring.end_date.isoformat() if recurring.end_date else None,
        "next_occurrence": recurring.next_occurrence.isoformat() if recurring.next_occurrence else None,
        "last_generated": recurring.last_generated.isoformat() if recurring.last_generated else None,
        "skip_holidays": recurring.skip_holidays,
        "is_active": recurring.is_active,
        "template_todo_id": recurring.template_todo_id,
        "created_at": recurring.created_at.isoformat(),
        "updated_at": recurring.updated_at.isoformat(),
    }
