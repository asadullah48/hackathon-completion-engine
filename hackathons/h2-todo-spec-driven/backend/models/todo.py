"""Todo model with SQLAlchemy ORM."""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import Column, String, DateTime, Enum, JSON, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TodoCategory(str, PyEnum):
    """Categories for todos."""
    WORK = "work"
    PERSONAL = "personal"
    STUDY = "study"
    HEALTH = "health"
    OTHER = "other"


class TodoPriority(str, PyEnum):
    """Priority levels for todos."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TodoStatus(str, PyEnum):
    """Status states for todos."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FLAGGED = "flagged"


class ConstitutionalDecision(str, PyEnum):
    """Constitutional check decisions."""
    ALLOW = "allow"
    BLOCK = "block"
    FLAG = "flag"


class Todo(Base):
    """Todo model with constitutional compliance tracking."""

    __tablename__ = "todos"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)

    category = Column(
        Enum(TodoCategory),
        default=TodoCategory.OTHER,
        nullable=False
    )
    priority = Column(
        Enum(TodoPriority),
        default=TodoPriority.MEDIUM,
        nullable=False
    )
    status = Column(
        Enum(TodoStatus),
        default=TodoStatus.PENDING,
        nullable=False
    )

    deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Constitutional compliance tracking
    constitutional_check = Column(
        JSON,
        default=lambda: {"passed": True, "decision": "allow", "reason": None},
        nullable=False
    )

    # AI metadata for parsed todos
    ai_metadata = Column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<Todo(id={self.id}, title='{self.title[:30]}...', status={self.status.value})>"

    def to_dict(self) -> dict:
        """Convert todo to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "constitutional_check": self.constitutional_check,
            "ai_metadata": self.ai_metadata,
        }
