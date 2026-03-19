"""
Assignments router for todo assignments.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from database import get_db
from models import Todo, User, Team, TodoAssignment, AssignmentStatus, TeamMember, MemberRole

router = APIRouter(tags=["assignments"])


# Pydantic schemas
class AssignmentCreate(BaseModel):
    assignee_id: str
    team_id: Optional[str] = None
    due_date: Optional[str] = None
    notes: Optional[str] = None


class AssignmentUpdate(BaseModel):
    status: Optional[str] = None
    due_date: Optional[str] = None
    notes: Optional[str] = None


class AssignmentResponse(BaseModel):
    id: str
    todo_id: str
    assignee_id: str
    assigned_by: str
    team_id: Optional[str]
    status: str
    due_date: Optional[str]
    notes: Optional[str]
    assigned_at: str
    updated_at: Optional[str]
    todo: Optional[dict] = None
    assignee: Optional[dict] = None

    class Config:
        from_attributes = True


# Todo assignment endpoints
@router.post("/api/todos/{todo_id}/assign", response_model=AssignmentResponse)
async def assign_todo(
    todo_id: str,
    assignment_data: AssignmentCreate,
    assigned_by: str = Query(..., description="User making the assignment"),
    db: Session = Depends(get_db)
):
    """Assign a todo to a user."""
    # Verify todo exists
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    # Verify assigner exists
    assigner = db.query(User).filter(User.id == assigned_by).first()
    if not assigner:
        raise HTTPException(status_code=404, detail="Assigner user not found")

    # Verify assignee exists
    assignee = db.query(User).filter(User.id == assignment_data.assignee_id).first()
    if not assignee:
        raise HTTPException(status_code=404, detail="Assignee user not found")

    # If team_id provided, verify membership
    if assignment_data.team_id:
        team = db.query(Team).filter(Team.id == assignment_data.team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        # Check if assignee is a team member
        member = db.query(TeamMember).filter(
            TeamMember.team_id == assignment_data.team_id,
            TeamMember.user_id == assignment_data.assignee_id
        ).first()
        if not member:
            raise HTTPException(status_code=400, detail="Assignee is not a team member")

    # Parse due date if provided
    due_date = None
    if assignment_data.due_date:
        try:
            due_date = datetime.fromisoformat(assignment_data.due_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid due_date format")

    # Check for existing assignment
    existing = db.query(TodoAssignment).filter(
        TodoAssignment.todo_id == todo_id,
        TodoAssignment.assignee_id == assignment_data.assignee_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Todo already assigned to this user")

    # Create assignment
    assignment = TodoAssignment(
        todo_id=todo_id,
        assignee_id=assignment_data.assignee_id,
        assigned_by=assigned_by,
        team_id=assignment_data.team_id,
        due_date=due_date,
        notes=assignment_data.notes
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return assignment.to_dict(include_todo=True, include_assignee=True)


@router.get("/api/todos/{todo_id}/assignments", response_model=List[AssignmentResponse])
async def get_todo_assignments(todo_id: str, db: Session = Depends(get_db)):
    """Get all assignments for a todo."""
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    assignments = db.query(TodoAssignment).filter(
        TodoAssignment.todo_id == todo_id
    ).all()

    return [a.to_dict(include_assignee=True) for a in assignments]


@router.get("/api/users/{user_id}/assignments", response_model=List[AssignmentResponse])
async def get_user_assignments(
    user_id: str,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all assignments for a user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    query = db.query(TodoAssignment).filter(TodoAssignment.assignee_id == user_id)

    if status:
        try:
            status_enum = AssignmentStatus(status)
            query = query.filter(TodoAssignment.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")

    assignments = query.all()
    return [a.to_dict(include_todo=True) for a in assignments]


@router.put("/api/assignments/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: str,
    update_data: AssignmentUpdate,
    db: Session = Depends(get_db)
):
    """Update an assignment's status, due date, or notes."""
    assignment = db.query(TodoAssignment).filter(
        TodoAssignment.id == assignment_id
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    if update_data.status is not None:
        try:
            assignment.status = AssignmentStatus(update_data.status)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")

    if update_data.due_date is not None:
        try:
            assignment.due_date = datetime.fromisoformat(
                update_data.due_date.replace('Z', '+00:00')
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid due_date format")

    if update_data.notes is not None:
        assignment.notes = update_data.notes

    db.commit()
    db.refresh(assignment)

    return assignment.to_dict(include_todo=True, include_assignee=True)


@router.delete("/api/assignments/{assignment_id}")
async def delete_assignment(assignment_id: str, db: Session = Depends(get_db)):
    """Remove an assignment."""
    assignment = db.query(TodoAssignment).filter(
        TodoAssignment.id == assignment_id
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    db.delete(assignment)
    db.commit()

    return {"message": "Assignment removed", "assignment_id": assignment_id}
