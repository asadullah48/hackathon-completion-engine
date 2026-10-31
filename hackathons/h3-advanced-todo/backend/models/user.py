"""
User model for team collaboration.
"""

from sqlalchemy import Column, String, DateTime, Boolean
from datetime import datetime
import uuid

from .todo import Base


class User(Base):
    """User model for authentication and team membership."""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert user to dictionary."""
        return {
            "id": self.id,
            "email": self.email,
            "display_name": self.display_name,
            "avatar_url": self.avatar_url,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<User {self.email}>"
