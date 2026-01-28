"""Todo CRUD router with constitutional enforcement."""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from models import Todo, TodoCategory, TodoPriority, TodoStatus
from services import validate_todo, log_decision, create_approval_request, Decision

router = APIRouter(prefix="/api/todos", tags=["todos"])


# Pydantic schemas for request/response
class TodoCreate(BaseModel):
    """Schema for creating a todo."""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    category: Optional[TodoCategory] = TodoCategory.OTHER
    priority: Optional[TodoPriority] = TodoPriority.MEDIUM
    deadline: Optional[datetime] = None
    ai_metadata: Optional[dict] = None


class TodoUpdate(BaseModel):
    """Schema for updating a todo."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    category: Optional[TodoCategory] = None
    priority: Optional[TodoPriority] = None
    status: Optional[TodoStatus] = None
    deadline: Optional[datetime] = None
    ai_metadata: Optional[dict] = None


class TodoResponse(BaseModel):
    """Schema for todo response."""
    id: str
    title: str
    description: Optional[str]
    category: str
    priority: str
    status: str
    deadline: Optional[str]
    created_at: str
    updated_at: str
    constitutional_check: dict
    ai_metadata: Optional[dict]

    class Config:
        from_attributes = True


class ConstitutionalBlockedError(BaseModel):
    """Error response for blocked todos."""
    error: str = "constitutional_violation"
    message: str
    decision: str


@router.post("", response_model=TodoResponse, status_code=201)
async def create_todo(todo_data: TodoCreate, db: Session = Depends(get_db)):
    """
    Create a new todo with constitutional validation.

    The todo content is checked against constitutional rules:
    - Academic dishonesty patterns are BLOCKED
    - Illegal activity patterns are BLOCKED
    - Harmful action patterns are BLOCKED
    - Suspicious patterns are FLAGGED for human review
    """
    # Constitutional check
    result = validate_todo(todo_data.title, todo_data.description)

    # Block if constitutional violation detected
    if result.decision == Decision.BLOCK:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "constitutional_violation",
                "message": result.reason,
                "decision": result.decision.value,
            }
        )

    # Determine status based on constitutional check
    status = TodoStatus.FLAGGED if result.decision == Decision.FLAG else TodoStatus.PENDING

    # Create todo
    todo = Todo(
        title=todo_data.title,
        description=todo_data.description,
        category=todo_data.category or TodoCategory.OTHER,
        priority=todo_data.priority or TodoPriority.MEDIUM,
        status=status,
        deadline=todo_data.deadline,
        constitutional_check=result.to_dict(),
        ai_metadata=todo_data.ai_metadata,
    )

    db.add(todo)
    db.commit()
    db.refresh(todo)

    # Log the decision
    log_decision(todo.id, todo.title, result)

    # Create approval request if flagged
    if result.decision == Decision.FLAG:
        create_approval_request(todo.id, todo.title, todo.description, result)

    return _format_todo_response(todo)


@router.get("", response_model=List[TodoResponse])
async def list_todos(
    category: Optional[TodoCategory] = Query(None),
    status: Optional[TodoStatus] = Query(None),
    priority: Optional[TodoPriority] = Query(None),
    search: Optional[str] = Query(None, min_length=1),
    db: Session = Depends(get_db)
):
    """
    List todos with optional filtering.

    Filters:
    - category: Filter by category (work, personal, study, health, other)
    - status: Filter by status (pending, in_progress, completed, flagged)
    - priority: Filter by priority (high, medium, low)
    - search: Search in title and description
    """
    query = db.query(Todo)

    if category:
        query = query.filter(Todo.category == category)
    if status:
        query = query.filter(Todo.status == status)
    if priority:
        query = query.filter(Todo.priority == priority)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Todo.title.ilike(search_pattern)) |
            (Todo.description.ilike(search_pattern))
        )

    todos = query.order_by(Todo.created_at.desc()).all()
    return [_format_todo_response(todo) for todo in todos]


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: str, db: Session = Depends(get_db)):
    """Get a single todo by ID."""
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return _format_todo_response(todo)


@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(todo_id: str, update_data: TodoUpdate, db: Session = Depends(get_db)):
    """
    Update a todo.

    If title or description is changed, constitutional validation is re-run.
    """
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    # Check if content is being updated (requires constitutional re-check)
    content_changed = False
    new_title = update_data.title if update_data.title else todo.title
    new_description = update_data.description if update_data.description is not None else todo.description

    if update_data.title and update_data.title != todo.title:
        content_changed = True
    if update_data.description is not None and update_data.description != todo.description:
        content_changed = True

    # Re-validate if content changed
    if content_changed:
        result = validate_todo(new_title, new_description)

        if result.decision == Decision.BLOCK:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "constitutional_violation",
                    "message": result.reason,
                    "decision": result.decision.value,
                }
            )

        todo.constitutional_check = result.to_dict()

        # Update status if newly flagged
        if result.decision == Decision.FLAG and todo.status != TodoStatus.FLAGGED:
            todo.status = TodoStatus.FLAGGED
            create_approval_request(todo.id, new_title, new_description, result)

    # Update fields
    if update_data.title is not None:
        todo.title = update_data.title
    if update_data.description is not None:
        todo.description = update_data.description
    if update_data.category is not None:
        todo.category = update_data.category
    if update_data.priority is not None:
        todo.priority = update_data.priority
    if update_data.status is not None:
        todo.status = update_data.status
    if update_data.deadline is not None:
        todo.deadline = update_data.deadline
    if update_data.ai_metadata is not None:
        todo.ai_metadata = update_data.ai_metadata

    todo.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(todo)

    return _format_todo_response(todo)


@router.delete("/{todo_id}")
async def delete_todo(todo_id: str, db: Session = Depends(get_db)):
    """Delete a todo by ID."""
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(todo)
    db.commit()

    return {"deleted": True, "id": todo_id}


def _format_todo_response(todo: Todo) -> dict:
    """Format a todo for API response."""
    return {
        "id": todo.id,
        "title": todo.title,
        "description": todo.description,
        "category": todo.category.value,
        "priority": todo.priority.value,
        "status": todo.status.value,
        "deadline": todo.deadline.isoformat() if todo.deadline else None,
        "created_at": todo.created_at.isoformat(),
        "updated_at": todo.updated_at.isoformat(),
        "constitutional_check": todo.constitutional_check,
        "ai_metadata": todo.ai_metadata,
    }
