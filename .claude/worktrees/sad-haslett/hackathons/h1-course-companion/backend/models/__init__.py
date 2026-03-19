"""
Data Models for Course Companion API
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"


class Student(BaseModel):
    student_id: str
    name: str
    email: str
    courses: List[str] = []
    created_at: datetime = datetime.now()
    last_active: Optional[datetime] = None


class Course(BaseModel):
    course_id: str
    title: str
    description: str
    instructor_id: str
    students_enrolled: List[str] = []
    created_at: datetime = datetime.now()


class Lesson(BaseModel):
    lesson_id: str
    course_id: str
    title: str
    content: str
    order: int
    created_at: datetime = datetime.now()


class ProgressRecord(BaseModel):
    student_id: str
    lesson_id: str
    course_id: str
    completed: bool = False
    score: Optional[float] = None
    time_spent: Optional[int] = None  # in seconds
    updated_at: datetime = datetime.now()


class ChatMessage(BaseModel):
    message_id: str
    student_id: str
    message: str
    response: str
    timestamp: datetime = datetime.now()
    decision: str  # "allow", "block", or "flag"
    blocked_reason: Optional[str] = None


class ConstitutionalRule(BaseModel):
    rule_id: str
    category: str  # "prohibited" or "suspicious"
    pattern: str
    description: str
    active: bool = True
    created_at: datetime = datetime.now()