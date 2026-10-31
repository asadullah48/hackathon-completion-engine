"""Tests for Todo model and enums."""
import pytest
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from models import (
    Base,
    Todo,
    TodoCategory,
    TodoPriority,
    TodoStatus,
    ConstitutionalDecision,
)


# Test database setup
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_database():
    """Set up fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Get a database session."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


class TestTodoEnums:
    """Tests for todo enums."""

    def test_todo_category_values(self):
        """Test that category enum has expected values."""
        assert TodoCategory.WORK.value == "work"
        assert TodoCategory.PERSONAL.value == "personal"
        assert TodoCategory.STUDY.value == "study"
        assert TodoCategory.HEALTH.value == "health"
        assert TodoCategory.OTHER.value == "other"

    def test_todo_priority_values(self):
        """Test that priority enum has expected values."""
        assert TodoPriority.HIGH.value == "high"
        assert TodoPriority.MEDIUM.value == "medium"
        assert TodoPriority.LOW.value == "low"

    def test_todo_status_values(self):
        """Test that status enum has expected values."""
        assert TodoStatus.PENDING.value == "pending"
        assert TodoStatus.IN_PROGRESS.value == "in_progress"
        assert TodoStatus.COMPLETED.value == "completed"
        assert TodoStatus.FLAGGED.value == "flagged"

    def test_constitutional_decision_values(self):
        """Test that constitutional decision enum has expected values."""
        assert ConstitutionalDecision.ALLOW.value == "allow"
        assert ConstitutionalDecision.BLOCK.value == "block"
        assert ConstitutionalDecision.FLAG.value == "flag"


class TestTodoModelCreation:
    """Tests for Todo model creation."""

    def test_todo_model_creation(self, db_session):
        """Test creating a todo model."""
        todo = Todo(
            title="Test todo",
            description="Test description",
            category=TodoCategory.WORK,
            priority=TodoPriority.HIGH,
        )
        db_session.add(todo)
        db_session.commit()

        # Verify
        assert todo.id is not None
        assert todo.title == "Test todo"
        assert todo.description == "Test description"
        assert todo.category == TodoCategory.WORK
        assert todo.priority == TodoPriority.HIGH
        assert todo.status == TodoStatus.PENDING

    def test_todo_defaults(self, db_session):
        """Test that defaults are applied correctly."""
        todo = Todo(title="Minimal todo")
        db_session.add(todo)
        db_session.commit()

        assert todo.category == TodoCategory.OTHER
        assert todo.priority == TodoPriority.MEDIUM
        assert todo.status == TodoStatus.PENDING
        assert todo.description is None
        assert todo.deadline is None
        assert todo.ai_metadata is None

    def test_todo_constitutional_check_default(self, db_session):
        """Test that constitutional_check has correct default."""
        todo = Todo(title="Test todo")
        db_session.add(todo)
        db_session.commit()

        assert todo.constitutional_check is not None
        assert todo.constitutional_check["passed"] is True
        assert todo.constitutional_check["decision"] == "allow"

    def test_todo_timestamps(self, db_session):
        """Test that timestamps are set correctly."""
        todo = Todo(title="Timestamp test")
        db_session.add(todo)
        db_session.commit()

        assert todo.created_at is not None
        assert todo.updated_at is not None
        assert isinstance(todo.created_at, datetime)
        assert isinstance(todo.updated_at, datetime)

    def test_todo_with_deadline(self, db_session):
        """Test creating todo with deadline."""
        deadline = datetime(2026, 2, 1, 12, 0, 0)
        todo = Todo(title="Deadline test", deadline=deadline)
        db_session.add(todo)
        db_session.commit()

        assert todo.deadline == deadline

    def test_todo_with_ai_metadata(self, db_session):
        """Test creating todo with AI metadata."""
        ai_metadata = {
            "inferred_category": "work",
            "inferred_priority": "high",
            "extracted_deadline": "2026-02-01",
            "confidence": 0.95,
        }
        todo = Todo(title="AI parsed todo", ai_metadata=ai_metadata)
        db_session.add(todo)
        db_session.commit()

        assert todo.ai_metadata == ai_metadata
        assert todo.ai_metadata["confidence"] == 0.95


class TestTodoToDict:
    """Tests for Todo.to_dict() method."""

    def test_to_dict_basic(self, db_session):
        """Test converting todo to dictionary."""
        todo = Todo(
            title="Test todo",
            description="Description",
            category=TodoCategory.WORK,
            priority=TodoPriority.HIGH,
        )
        db_session.add(todo)
        db_session.commit()

        d = todo.to_dict()

        assert d["id"] == todo.id
        assert d["title"] == "Test todo"
        assert d["description"] == "Description"
        assert d["category"] == "work"
        assert d["priority"] == "high"
        assert d["status"] == "pending"
        assert d["deadline"] is None
        assert "created_at" in d
        assert "updated_at" in d
        assert d["constitutional_check"] is not None

    def test_to_dict_with_deadline(self, db_session):
        """Test that deadline is formatted as ISO string."""
        deadline = datetime(2026, 2, 1, 12, 0, 0)
        todo = Todo(title="Test", deadline=deadline)
        db_session.add(todo)
        db_session.commit()

        d = todo.to_dict()
        assert d["deadline"] == "2026-02-01T12:00:00"


class TestTodoRepr:
    """Tests for Todo.__repr__() method."""

    def test_repr_short_title(self, db_session):
        """Test repr with short title."""
        todo = Todo(title="Short")
        db_session.add(todo)
        db_session.commit()

        repr_str = repr(todo)
        assert "Short" in repr_str
        assert todo.id in repr_str

    def test_repr_long_title(self, db_session):
        """Test repr with long title (truncated)."""
        long_title = "A" * 100
        todo = Todo(title=long_title)
        db_session.add(todo)
        db_session.commit()

        repr_str = repr(todo)
        assert "..." in repr_str  # Title should be truncated


class TestTodoQueries:
    """Tests for querying todos."""

    def test_query_by_category(self, db_session):
        """Test querying by category."""
        todo1 = Todo(title="Work 1", category=TodoCategory.WORK)
        todo2 = Todo(title="Personal 1", category=TodoCategory.PERSONAL)
        db_session.add_all([todo1, todo2])
        db_session.commit()

        work_todos = db_session.query(Todo).filter(
            Todo.category == TodoCategory.WORK
        ).all()

        assert len(work_todos) == 1
        assert work_todos[0].title == "Work 1"

    def test_query_by_status(self, db_session):
        """Test querying by status."""
        todo1 = Todo(title="Pending", status=TodoStatus.PENDING)
        todo2 = Todo(title="Completed", status=TodoStatus.COMPLETED)
        db_session.add_all([todo1, todo2])
        db_session.commit()

        completed = db_session.query(Todo).filter(
            Todo.status == TodoStatus.COMPLETED
        ).all()

        assert len(completed) == 1
        assert completed[0].title == "Completed"

    def test_query_by_priority(self, db_session):
        """Test querying by priority."""
        todo1 = Todo(title="High", priority=TodoPriority.HIGH)
        todo2 = Todo(title="Low", priority=TodoPriority.LOW)
        db_session.add_all([todo1, todo2])
        db_session.commit()

        high_priority = db_session.query(Todo).filter(
            Todo.priority == TodoPriority.HIGH
        ).all()

        assert len(high_priority) == 1
        assert high_priority[0].title == "High"
