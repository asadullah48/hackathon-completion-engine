"""AI Suggestion model for intelligent todo recommendations."""
import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Boolean, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship
from .todo import Base


class SuggestionType(str, enum.Enum):
    """Types of AI suggestions."""
    PRIORITY = "priority"        # Suggest priority adjustments
    BREAKDOWN = "breakdown"      # Break down complex tasks
    RECURRING = "recurring"      # Suggest recurring patterns
    INSIGHT = "insight"          # General productivity insights
    DEADLINE = "deadline"        # Deadline recommendations
    CATEGORY = "category"        # Category suggestions


class SuggestionStatus(str, enum.Enum):
    """Status of a suggestion."""
    PENDING = "pending"          # Awaiting user action
    ACCEPTED = "accepted"        # User accepted suggestion
    DISMISSED = "dismissed"      # User dismissed suggestion
    EXPIRED = "expired"          # Suggestion no longer relevant


class Suggestion(Base):
    """AI-generated suggestion for todo improvements."""
    __tablename__ = "suggestions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    todo_id = Column(String(36), ForeignKey("todos.id"), nullable=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)

    suggestion_type = Column(Enum(SuggestionType), nullable=False)
    status = Column(Enum(SuggestionStatus), default=SuggestionStatus.PENDING)

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Suggested changes (JSON format for flexibility)
    suggested_changes = Column(JSON, default={})

    # AI confidence score (0.0 - 1.0)
    confidence = Column(String(10), default="0.8")

    # Reasoning provided by AI
    reasoning = Column(Text, nullable=True)

    # For breakdown suggestions - list of subtask suggestions
    subtasks = Column(JSON, default=[])

    # Metadata
    is_actionable = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    actioned_at = Column(DateTime, nullable=True)

    # Relationships
    todo = relationship("Todo", foreign_keys=[todo_id])
    user = relationship("User", foreign_keys=[user_id])

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "todo_id": self.todo_id,
            "user_id": self.user_id,
            "suggestion_type": self.suggestion_type.value if self.suggestion_type else None,
            "status": self.status.value if self.status else None,
            "title": self.title,
            "description": self.description,
            "suggested_changes": self.suggested_changes,
            "confidence": float(self.confidence) if self.confidence else 0.8,
            "reasoning": self.reasoning,
            "subtasks": self.subtasks,
            "is_actionable": self.is_actionable,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "actioned_at": self.actioned_at.isoformat() if self.actioned_at else None,
        }
