"""
Progress Router for Course Companion API
Tracks student learning progress and analytics
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
from datetime import datetime
from pathlib import Path
import os

from services.logger_service import get_conversation_logger

router = APIRouter()

# Initialize conversation logger for stats
conversation_logger = get_conversation_logger(vault_path="../vault")

class ProgressUpdate(BaseModel):
    student_id: str
    course_id: str
    lesson_id: str
    completed: bool = False
    score: Optional[float] = None
    time_spent: Optional[int] = None  # in seconds

class ProgressQuery(BaseModel):
    student_id: str
    course_id: Optional[str] = None


@router.get("/progress/{student_id}")
async def get_student_progress(student_id: str):
    """
    Get progress for a specific student

    Returns:
        student_id: str
        total_conversations: int
        concepts_discussed: list[str]
        time_spent_minutes: int
        last_active: str (ISO timestamp)
    """
    # Get stats from conversation logger
    stats = conversation_logger.get_student_stats(student_id)

    return {
        "student_id": student_id,
        "total_conversations": stats.get("total_conversations", 0),
        "concepts_discussed": stats.get("concepts_discussed", []),
        "time_spent_minutes": stats.get("time_spent", 0),
        "last_active": stats.get("last_active")
    }


@router.post("/progress/update")
async def update_progress(data: ProgressUpdate):
    """Update student progress for a specific lesson"""

    # Create progress directory if it doesn't exist
    vault_path = Path("../vault")
    progress_dir = vault_path / "Student_Progress"
    progress_dir.mkdir(parents=True, exist_ok=True)

    # Create student-specific file
    student_file = progress_dir / f"{data.student_id}_progress.json"

    # Load existing progress or create new
    if student_file.exists():
        with open(student_file, 'r') as f:
            progress_data = json.load(f)
    else:
        progress_data = {}

    # Update progress record
    key = f"{data.course_id}:{data.lesson_id}"
    progress_data[key] = {
        "course_id": data.course_id,
        "lesson_id": data.lesson_id,
        "completed": data.completed,
        "score": data.score,
        "time_spent": data.time_spent,
        "updated_at": datetime.now().isoformat()
    }

    # Save updated progress
    with open(student_file, 'w') as f:
        json.dump(progress_data, f, indent=2)

    return {
        "status": "success",
        "message": f"Progress updated for student {data.student_id}",
        "record": progress_data[key]
    }

@router.get("/progress/details/{student_id}")
async def get_progress_details(student_id: str, course_id: Optional[str] = None):
    """Get detailed progress for a specific student"""

    vault_path = Path("../vault")
    progress_dir = vault_path / "Student_Progress"
    student_file = progress_dir / f"{student_id}_progress.json"

    if not student_file.exists():
        return {
            "student_id": student_id,
            "courses": [],
            "total_completed": 0,
            "overall_score": None
        }

    with open(student_file, 'r') as f:
        progress_data = json.load(f)

    # Filter by course if specified
    if course_id:
        filtered_data = {k: v for k, v in progress_data.items() if k.startswith(course_id)}
    else:
        filtered_data = progress_data

    # Calculate statistics
    total_lessons = len(filtered_data)
    completed_lessons = sum(1 for v in filtered_data.values() if v.get('completed', False))
    scores = [v['score'] for v in filtered_data.values() if v.get('score') is not None]
    avg_score = sum(scores) / len(scores) if scores else None

    return {
        "student_id": student_id,
        "course_id": course_id,
        "progress_records": filtered_data,
        "total_lessons": total_lessons,
        "completed_lessons": completed_lessons,
        "completion_percentage": (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0,
        "average_score": avg_score
    }


@router.get("/progress/analytics/{student_id}")
async def get_student_analytics(student_id: str):
    """Get detailed analytics for a student"""

    vault_path = Path("../vault")
    progress_dir = vault_path / "Student_Progress"
    student_file = progress_dir / f"{student_id}_progress.json"

    if not student_file.exists():
        return {
            "student_id": student_id,
            "analytics": {},
            "message": "No progress data found for this student"
        }

    with open(student_file, 'r') as f:
        progress_data = json.load(f)

    # Calculate analytics
    total_lessons = len(progress_data)
    completed_lessons = sum(1 for v in progress_data.values() if v.get('completed', False))
    scores = [v['score'] for v in progress_data.values() if v.get('score') is not None]

    analytics = {
        "total_lessons": total_lessons,
        "completed_lessons": completed_lessons,
        "completion_rate": (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0,
        "average_score": sum(scores) / len(scores) if scores else None,
        "highest_score": max(scores) if scores else None,
        "lowest_score": min(scores) if scores else None,
        "total_time_spent": sum(v.get('time_spent', 0) for v in progress_data.values()),
        "last_updated": max(
            v.get('updated_at', '') for v in progress_data.values()
        ) if progress_data else None
    }

    return {
        "student_id": student_id,
        "analytics": analytics
    }