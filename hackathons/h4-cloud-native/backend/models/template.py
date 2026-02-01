"""Template model for todo templates."""
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, Text

from .todo import Base


class Template(Base):
    """
    Template model for creating multiple todos from a predefined template.

    Templates contain a list of todo items that can be instantiated
    with relative deadlines and pre-set categories/priorities.
    """
    __tablename__ = "templates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Template info
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)  # Default category for todos

    # Template todos stored as JSON array
    # Format: [{title, description, category, priority, relative_deadline_days}, ...]
    todos = Column(JSON, nullable=False)

    # Metadata
    created_by = Column(String(100), default="system")
    is_public = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)

    # Tags for search/filtering
    tags = Column(JSON, nullable=True)  # ["work", "project", ...]

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Template(id={self.id}, name='{self.name}', todos={len(self.todos or [])})>"

    def to_dict(self) -> dict:
        """Convert template to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "todos": self.todos,
            "created_by": self.created_by,
            "is_public": self.is_public,
            "usage_count": self.usage_count,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
