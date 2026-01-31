"""
Team and TeamMember models for collaboration.
"""

from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
import uuid

from .todo import Base


class MemberRole(str, PyEnum):
    """Role hierarchy for team members."""
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class TeamRole(str, PyEnum):
    """Role hierarchy for team members."""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class Team(Base):
    """Team model for grouping users and todos."""

    __tablename__ = "teams"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    owner_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    settings = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")

    def to_dict(self, include_members=False):
        """Convert team to dictionary."""
        result = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "owner_id": self.owner_id,
            "settings": self.settings or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        if include_members:
            result["members"] = [m.to_dict() for m in self.members]
        return result

    def __repr__(self):
        return f"<Team {self.name}>"


class TeamMember(Base):
    """Team membership with role."""

    __tablename__ = "team_members"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = Column(String(36), ForeignKey('teams.id'), nullable=False)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    role = Column(SQLEnum(MemberRole), default=MemberRole.VIEWER)
    added_by = Column(String(36), ForeignKey('users.id'), nullable=True)
    joined_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    team = relationship("Team", back_populates="members")
    user = relationship("User", foreign_keys=[user_id])
    inviter = relationship("User", foreign_keys=[added_by])

    def to_dict(self, include_user=False):
        """Convert membership to dictionary."""
        result = {
            "id": self.id,
            "team_id": self.team_id,
            "user_id": self.user_id,
            "role": self.role.value if self.role else None,
            "added_by": self.added_by,
            "joined_at": self.joined_at.isoformat() if self.joined_at else None
        }
        if include_user and self.user:
            result["user"] = self.user.to_dict()
        return result

    def __repr__(self):
        return f"<TeamMember {self.user_id} in {self.team_id}>"


class TeamTodo(Base):
    """Team-specific todo model."""

    __tablename__ = "team_todos"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = Column(String(36), ForeignKey('teams.id'), nullable=False)

    # Same fields as regular Todo
    title = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    category = Column(String(50), default="work")
    priority = Column(String(20), default="medium")
    status = Column(String(20), default="pending")
    deadline = Column(DateTime, nullable=True)

    # Team-specific fields
    assigned_to = Column(String(36), nullable=True)  # user_id
    assigned_to_name = Column(String(100), nullable=True)  # Cached
    created_by = Column(String(36), nullable=False)
    created_by_name = Column(String(100), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    team = relationship("Team")
    comments = relationship("TodoComment", back_populates="todo", cascade="all, delete-orphan")

    def to_dict(self, include_comments=False):
        """Convert team todo to dictionary."""
        result = {
            "id": self.id,
            "team_id": self.team_id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "priority": self.priority,
            "status": self.status,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "assigned_to": self.assigned_to,
            "assigned_to_name": self.assigned_to_name,
            "created_by": self.created_by,
            "created_by_name": self.created_by_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        if include_comments:
            result["comments"] = [c.to_dict() for c in self.comments]
        return result

    def __repr__(self):
        return f"<TeamTodo {self.title} in {self.team_id}>"


class TodoComment(Base):
    """Comment on a team todo."""

    __tablename__ = "todo_comments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    todo_id = Column(String(36), ForeignKey('team_todos.id'), nullable=False)
    user_id = Column(String(36), nullable=False)
    user_name = Column(String(100), nullable=False)
    content = Column(String(1000), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    todo = relationship("TeamTodo", back_populates="comments")

    def to_dict(self):
        """Convert comment to dictionary."""
        return {
            "id": self.id,
            "todo_id": self.todo_id,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<TodoComment by {self.user_name} on {self.todo_id}>"
