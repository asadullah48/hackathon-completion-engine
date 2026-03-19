"""Stats router for todo statistics."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models import Todo, TodoCategory, TodoPriority, TodoStatus

router = APIRouter(prefix="/api/stats", tags=["stats"])


class StatsResponse(BaseModel):
    """Schema for statistics response."""
    total: int
    by_status: dict
    by_category: dict
    by_priority: dict
    completion_rate: float


@router.get("", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """
    Get todo statistics.

    Returns:
    - total: Total number of todos
    - by_status: Count per status (pending, in_progress, completed, flagged)
    - by_category: Count per category (work, personal, study, health, other)
    - by_priority: Count per priority (high, medium, low)
    - completion_rate: Ratio of completed todos to total (0.0 - 1.0)
    """
    # Total count
    total = db.query(func.count(Todo.id)).scalar() or 0

    # Count by status
    status_counts = db.query(
        Todo.status, func.count(Todo.id)
    ).group_by(Todo.status).all()

    by_status = {status.value: 0 for status in TodoStatus}
    for status, count in status_counts:
        by_status[status.value] = count

    # Count by category
    category_counts = db.query(
        Todo.category, func.count(Todo.id)
    ).group_by(Todo.category).all()

    by_category = {category.value: 0 for category in TodoCategory}
    for category, count in category_counts:
        by_category[category.value] = count

    # Count by priority
    priority_counts = db.query(
        Todo.priority, func.count(Todo.id)
    ).group_by(Todo.priority).all()

    by_priority = {priority.value: 0 for priority in TodoPriority}
    for priority, count in priority_counts:
        by_priority[priority.value] = count

    # Completion rate
    completed = by_status.get("completed", 0)
    completion_rate = completed / total if total > 0 else 0.0

    return {
        "total": total,
        "by_status": by_status,
        "by_category": by_category,
        "by_priority": by_priority,
        "completion_rate": round(completion_rate, 2),
    }
