"""Recurring Todo model for scheduled task generation."""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, List

from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship

from .todo import Base


class RecurrencePattern(str, PyEnum):
    """Recurrence pattern types."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class RecurringTodo(Base):
    """
    Recurring Todo model for automatic todo generation.

    Supports daily, weekly, monthly, and custom patterns.
    Links to a template todo that gets cloned on each occurrence.
    """
    __tablename__ = "recurring_todos"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Recurrence pattern settings
    pattern = Column(String(20), nullable=False)  # daily, weekly, monthly, custom
    interval = Column(Integer, default=1)  # Every N days/weeks/months

    # Weekly-specific: days of week [0=Mon, 1=Tue, ..., 6=Sun]
    days_of_week = Column(JSON, nullable=True)

    # Monthly-specific: day of month (1-31)
    day_of_month = Column(Integer, nullable=True)

    # Date range
    start_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_date = Column(DateTime, nullable=True)  # None = no end

    # Generation tracking
    last_generated = Column(DateTime, nullable=True)
    next_occurrence = Column(DateTime, nullable=True)

    # Options
    skip_holidays = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # Template todo to clone
    template_todo_id = Column(String(36), ForeignKey('todos.id'), nullable=False)
    template_todo = relationship("Todo", foreign_keys=[template_todo_id])

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Additional metadata
    metadata_json = Column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<RecurringTodo(id={self.id}, pattern='{self.pattern}', interval={self.interval})>"

    def to_dict(self) -> dict:
        """Convert recurring todo to dictionary."""
        return {
            "id": self.id,
            "pattern": self.pattern,
            "interval": self.interval,
            "days_of_week": self.days_of_week,
            "day_of_month": self.day_of_month,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "last_generated": self.last_generated.isoformat() if self.last_generated else None,
            "next_occurrence": self.next_occurrence.isoformat() if self.next_occurrence else None,
            "skip_holidays": self.skip_holidays,
            "is_active": self.is_active,
            "template_todo_id": self.template_todo_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
