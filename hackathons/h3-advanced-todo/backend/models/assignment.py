"""
TodoAssignment model for assigning todos to team members.
"""

from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
import uuid

from .todo import Base


class AssignmentStatus(str, PyEnum):
    """Status of a todo assignment."""
    ASSIGNED = "assigned"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DECLINED = "declined"


class TodoAssignment(Base):
    """Assignment of a todo to a user within a team."""

    __tablename__ = "todo_assignments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    todo_id = Column(String(36), ForeignKey('todos.id'), nullable=False)
    assignee_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    assigned_by = Column(String(36), ForeignKey('users.id'), nullable=False)
    team_id = Column(String(36), ForeignKey('teams.id'), nullable=True)
    status = Column(SQLEnum(AssignmentStatus), default=AssignmentStatus.ASSIGNED)
    due_date = Column(DateTime, nullable=True)
    notes = Column(String(500), nullable=True)
    assignment_metadata = Column(JSON, default=dict)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    todo = relationship("Todo", backref="assignments")
    assignee = relationship("User", foreign_keys=[assignee_id])
    assigner = relationship("User", foreign_keys=[assigned_by])
    team = relationship("Team")

    def to_dict(self, include_todo=False, include_assignee=False):
        """Convert assignment to dictionary."""
        result = {
            "id": self.id,
            "todo_id": self.todo_id,
            "assignee_id": self.assignee_id,
            "assigned_by": self.assigned_by,
            "team_id": self.team_id,
            "status": self.status.value if self.status else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "notes": self.notes,
            "metadata": self.assignment_metadata or {},
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        if include_todo and self.todo:
            result["todo"] = self.todo.to_dict()
        if include_assignee and self.assignee:
            result["assignee"] = self.assignee.to_dict()
        return result

    def __repr__(self):
        return f"<TodoAssignment {self.todo_id} -> {self.assignee_id}>"
