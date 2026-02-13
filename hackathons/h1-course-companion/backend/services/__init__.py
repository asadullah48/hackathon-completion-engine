"""
Services for Course Companion API
Contains business logic for various operations
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from pathlib import Path

# Import the main services
from .chatgpt_service import ChatGPTService, get_chatgpt_service
from .logger_service import ConversationLogger, get_conversation_logger

try:
    from models import Student, Course, Lesson, ProgressRecord, ChatMessage
except ImportError:
    # Models may not be available in all contexts
    pass

logger = logging.getLogger(__name__)

__all__ = [
    "ChatGPTService",
    "get_chatgpt_service",
    "ConversationLogger",
    "get_conversation_logger",
    "StudentService",
    "CourseService",
    "ProgressService",
    "ConversationService",
]


class StudentService:
    """Service for managing student-related operations"""
    
    def __init__(self, vault_path: str = "../vault"):
        self.vault_path = Path(vault_path)
        self.students_dir = self.vault_path / "Students"
        self.students_dir.mkdir(parents=True, exist_ok=True)
    
    async def create_student(self, student: Student) -> bool:
        """Create a new student record"""
        try:
            student_file = self.students_dir / f"{student.student_id}.json"
            with open(student_file, 'w') as f:
                json.dump(student.dict(), f, indent=2, default=str)
            return True
        except Exception as e:
            logger.error(f"Error creating student: {e}")
            return False
    
    async def get_student(self, student_id: str) -> Optional[Student]:
        """Retrieve a student by ID"""
        try:
            student_file = self.students_dir / f"{student_id}.json"
            if student_file.exists():
                with open(student_file, 'r') as f:
                    data = json.load(f)
                return Student(**data)
            return None
        except Exception as e:
            logger.error(f"Error retrieving student: {e}")
            return None
    
    async def update_student(self, student: Student) -> bool:
        """Update an existing student record"""
        try:
            student_file = self.students_dir / f"{student.student_id}.json"
            with open(student_file, 'w') as f:
                json.dump(student.dict(), f, indent=2, default=str)
            return True
        except Exception as e:
            logger.error(f"Error updating student: {e}")
            return False


class CourseService:
    """Service for managing course-related operations"""
    
    def __init__(self, vault_path: str = "../vault"):
        self.vault_path = Path(vault_path)
        self.courses_dir = self.vault_path / "Courses"
        self.courses_dir.mkdir(parents=True, exist_ok=True)
    
    async def create_course(self, course: Course) -> bool:
        """Create a new course"""
        try:
            course_file = self.courses_dir / f"{course.course_id}.json"
            with open(course_file, 'w') as f:
                json.dump(course.dict(), f, indent=2, default=str)
            return True
        except Exception as e:
            logger.error(f"Error creating course: {e}")
            return False
    
    async def get_course(self, course_id: str) -> Optional[Course]:
        """Retrieve a course by ID"""
        try:
            course_file = self.courses_dir / f"{course_id}.json"
            if course_file.exists():
                with open(course_file, 'r') as f:
                    data = json.load(f)
                return Course(**data)
            return None
        except Exception as e:
            logger.error(f"Error retrieving course: {e}")
            return None
    
    async def enroll_student(self, course_id: str, student_id: str) -> bool:
        """Enroll a student in a course"""
        try:
            course = await self.get_course(course_id)
            if not course:
                return False
            
            if student_id not in course.students_enrolled:
                course.students_enrolled.append(student_id)
                course.updated_at = datetime.now()
                return await self.update_course(course)
            
            return True
        except Exception as e:
            logger.error(f"Error enrolling student: {e}")
            return False
    
    async def update_course(self, course: Course) -> bool:
        """Update an existing course"""
        try:
            course_file = self.courses_dir / f"{course.course_id}.json"
            with open(course_file, 'w') as f:
                json.dump(course.dict(), f, indent=2, default=str)
            return True
        except Exception as e:
            logger.error(f"Error updating course: {e}")
            return False


class ProgressService:
    """Service for managing student progress"""
    
    def __init__(self, vault_path: str = "../vault"):
        self.vault_path = Path(vault_path)
        self.progress_dir = self.vault_path / "Student_Progress"
        self.progress_dir.mkdir(parents=True, exist_ok=True)
    
    async def save_progress(self, progress: ProgressRecord) -> bool:
        """Save progress record for a student"""
        try:
            student_file = self.progress_dir / f"{progress.student_id}_progress.json"
            
            # Load existing progress or create new
            if student_file.exists():
                with open(student_file, 'r') as f:
                    progress_data = json.load(f)
            else:
                progress_data = {}
            
            # Add/update progress record
            key = f"{progress.course_id}:{progress.lesson_id}"
            progress_data[key] = progress.dict()
            
            # Save updated progress
            with open(student_file, 'w') as f:
                json.dump(progress_data, f, indent=2, default=str)
            
            return True
        except Exception as e:
            logger.error(f"Error saving progress: {e}")
            return False
    
    async def get_progress(self, student_id: str, course_id: Optional[str] = None) -> List[ProgressRecord]:
        """Get progress records for a student"""
        try:
            student_file = self.progress_dir / f"{student_id}_progress.json"
            if not student_file.exists():
                return []
            
            with open(student_file, 'r') as f:
                progress_data = json.load(f)
            
            # Filter by course if specified
            if course_id:
                progress_data = {k: v for k, v in progress_data.items() if k.startswith(course_id)}
            
            records = []
            for key, data in progress_data.items():
                records.append(ProgressRecord(**data))
            
            return records
        except Exception as e:
            logger.error(f"Error retrieving progress: {e}")
            return []


class ConversationService:
    """Service for managing conversations"""
    
    def __init__(self, vault_path: str = "../vault"):
        self.vault_path = Path(vault_path)
        self.logs_dir = self.vault_path / "Conversation_Logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    async def log_conversation(self, message: ChatMessage) -> bool:
        """Log a conversation message"""
        try:
            date_str = datetime.now().strftime("%Y-%m-%d")
            log_file = self.logs_dir / f"conversations_{date_str}.jsonl"
            
            log_entry = {
                "timestamp": message.timestamp.isoformat(),
                "student_id": message.student_id,
                "message": message.message,
                "response": message.response,
                "decision": message.decision,
                "blocked_reason": message.blocked_reason
            }
            
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
            
            return True
        except Exception as e:
            logger.error(f"Error logging conversation: {e}")
            return False
    
    async def get_conversations(self, student_id: str, limit: int = 50) -> List[ChatMessage]:
        """Get recent conversations for a student"""
        try:
            conversations = []
            # Look through recent days' logs
            for i in range(7):  # Check last 7 days
                date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - \
                       datetime.timedelta(days=i)
                date_str = date.strftime("%Y-%m-%d")
                log_file = self.logs_dir / f"conversations_{date_str}.jsonl"
                
                if log_file.exists():
                    with open(log_file, 'r') as f:
                        for line in f:
                            entry = json.loads(line.strip())
                            if entry.get('student_id') == student_id:
                                # Create a simplified ChatMessage object
                                conv = ChatMessage(
                                    message_id=entry.get('timestamp', ''),  # Using timestamp as ID
                                    student_id=entry['student_id'],
                                    message=entry['message'],
                                    response=entry['response'],
                                    decision=entry['decision'],
                                    blocked_reason=entry.get('blocked_reason'),
                                    timestamp=datetime.fromisoformat(entry['timestamp'])
                                )
                                conversations.append(conv)
                                
                                if len(conversations) >= limit:
                                    return conversations
            
            return conversations
        except Exception as e:
            logger.error(f"Error retrieving conversations: {e}")
            return []