"""Templates router for managing todo templates."""
import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from models import Template, Todo, TodoCategory, TodoPriority, TodoStatus
from services import validate_todo, Decision

router = APIRouter(prefix="/api/templates", tags=["templates"])


# Pydantic schemas
class TemplateTodoItem(BaseModel):
    """Schema for a todo item within a template."""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    category: Optional[str] = "other"
    priority: Optional[str] = "medium"
    relative_deadline_days: Optional[int] = Field(None, description="Days from creation")


class TemplateCreateRequest(BaseModel):
    """Schema for creating a template."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    todos: List[TemplateTodoItem] = Field(..., min_length=1)
    tags: Optional[List[str]] = None


class TemplateUpdateRequest(BaseModel):
    """Schema for updating a template."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    todos: Optional[List[TemplateTodoItem]] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None


class TemplateResponse(BaseModel):
    """Schema for template response."""
    id: str
    name: str
    description: Optional[str]
    category: Optional[str]
    todos: List[dict]
    is_public: bool
    usage_count: int
    tags: Optional[List[str]]
    created_by: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class TodoCreatedResponse(BaseModel):
    """Schema for todo created from template."""
    id: str
    title: str
    category: str
    priority: str
    deadline: Optional[str]


@router.get("", response_model=List[TemplateResponse])
async def list_templates(
    category: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    List all public templates.

    Filters:
    - category: Filter by category
    - tag: Filter by tag
    - search: Search in name and description
    """
    query = db.query(Template).filter(Template.is_public == True)

    if category:
        query = query.filter(Template.category == category)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Template.name.ilike(search_pattern)) |
            (Template.description.ilike(search_pattern))
        )

    templates = query.order_by(Template.usage_count.desc()).all()

    # Filter by tag in Python (JSON field)
    if tag:
        templates = [t for t in templates if t.tags and tag in t.tags]

    return [_format_template_response(t) for t in templates]


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: str, db: Session = Depends(get_db)):
    """Get a specific template."""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return _format_template_response(template)


@router.post("", response_model=TemplateResponse, status_code=201)
async def create_template(
    request: TemplateCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new template.

    The template can contain multiple todo items with relative deadlines.
    """
    # Convert todos to dict format
    todos_data = [t.model_dump() for t in request.todos]

    template = Template(
        name=request.name,
        description=request.description,
        category=request.category,
        todos=todos_data,
        tags=request.tags,
        is_public=True,
        created_by="user"
    )

    db.add(template)
    db.commit()
    db.refresh(template)

    return _format_template_response(template)


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: str,
    update_data: TemplateUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update a template."""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Update fields
    if update_data.name is not None:
        template.name = update_data.name
    if update_data.description is not None:
        template.description = update_data.description
    if update_data.category is not None:
        template.category = update_data.category
    if update_data.todos is not None:
        template.todos = [t.model_dump() for t in update_data.todos]
    if update_data.tags is not None:
        template.tags = update_data.tags
    if update_data.is_public is not None:
        template.is_public = update_data.is_public

    template.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(template)

    return _format_template_response(template)


@router.delete("/{template_id}")
async def delete_template(template_id: str, db: Session = Depends(get_db)):
    """Delete a template."""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Don't allow deleting system templates
    if template.created_by == "system":
        raise HTTPException(status_code=403, detail="Cannot delete system templates")

    db.delete(template)
    db.commit()

    return {"deleted": True, "id": template_id}


@router.post("/{template_id}/use")
async def use_template(
    template_id: str,
    base_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    Create todos from a template.

    This instantiates all todos in the template with calculated deadlines.
    Constitutional validation is applied to each todo.

    Args:
        base_date: Base date for calculating relative deadlines (default: now)
    """
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    if base_date is None:
        base_date = datetime.utcnow()

    created_todos = []
    blocked_todos = []

    for todo_item in template.todos:
        # Constitutional check
        result = validate_todo(todo_item['title'], todo_item.get('description'))

        if result.decision == Decision.BLOCK:
            blocked_todos.append({
                "title": todo_item['title'],
                "reason": result.reason
            })
            continue

        # Calculate deadline
        deadline = None
        if todo_item.get('relative_deadline_days') is not None:
            deadline = base_date + timedelta(days=todo_item['relative_deadline_days'])

        # Map category string to enum
        category_str = todo_item.get('category', template.category or 'other')
        try:
            category = TodoCategory(category_str.lower())
        except ValueError:
            category = TodoCategory.OTHER

        # Map priority string to enum
        priority_str = todo_item.get('priority', 'medium')
        try:
            priority = TodoPriority(priority_str.lower())
        except ValueError:
            priority = TodoPriority.MEDIUM

        # Determine status based on constitutional check
        status = TodoStatus.FLAGGED if result.decision == Decision.FLAG else TodoStatus.PENDING

        # Create todo
        todo = Todo(
            id=str(uuid.uuid4()),
            title=todo_item['title'],
            description=todo_item.get('description'),
            category=category,
            priority=priority,
            status=status,
            deadline=deadline,
            constitutional_check=result.to_dict(),
            ai_metadata={
                "created_from": "template",
                "template_id": template.id,
                "template_name": template.name,
                "created_at": datetime.utcnow().isoformat()
            }
        )

        db.add(todo)
        created_todos.append(todo)

    # Update usage count
    template.usage_count += 1

    db.commit()

    return {
        "created": len(created_todos),
        "blocked": len(blocked_todos),
        "todos": [
            {
                "id": t.id,
                "title": t.title,
                "category": t.category.value,
                "priority": t.priority.value,
                "deadline": t.deadline.isoformat() if t.deadline else None
            }
            for t in created_todos
        ],
        "blocked_items": blocked_todos if blocked_todos else None
    }


@router.get("/{template_id}/preview")
async def preview_template(
    template_id: str,
    base_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    Preview what todos would be created from a template.

    This shows the calculated deadlines without actually creating todos.
    """
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    if base_date is None:
        base_date = datetime.utcnow()

    preview_todos = []

    for todo_item in template.todos:
        deadline = None
        if todo_item.get('relative_deadline_days') is not None:
            deadline = base_date + timedelta(days=todo_item['relative_deadline_days'])

        # Constitutional check
        result = validate_todo(todo_item['title'], todo_item.get('description'))

        preview_todos.append({
            "title": todo_item['title'],
            "description": todo_item.get('description'),
            "category": todo_item.get('category', template.category or 'other'),
            "priority": todo_item.get('priority', 'medium'),
            "deadline": deadline.isoformat() if deadline else None,
            "constitutional_decision": result.decision.value,
            "would_be_blocked": result.decision == Decision.BLOCK
        })

    return {
        "template_name": template.name,
        "base_date": base_date.isoformat(),
        "todos": preview_todos
    }


def _format_template_response(template: Template) -> dict:
    """Format a template for API response."""
    return {
        "id": template.id,
        "name": template.name,
        "description": template.description,
        "category": template.category,
        "todos": template.todos,
        "is_public": template.is_public,
        "usage_count": template.usage_count,
        "tags": template.tags,
        "created_by": template.created_by,
        "created_at": template.created_at.isoformat(),
        "updated_at": template.updated_at.isoformat(),
    }
