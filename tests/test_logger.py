"""
Tests for Logger Service
Tests the conversation logging functionality
"""

import pytest
import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

from backend.services.logger_service import ConversationLogger, get_conversation_logger


@pytest.fixture
def logger():
    """Create a ConversationLogger instance for testing"""
    # Use test vault path
    test_vault = Path(__file__).parent.parent / "vault"
    return ConversationLogger(vault_path=str(test_vault))


@pytest.fixture
def unique_student_id():
    """Generate a unique student ID for testing"""
    return f"test_student_{int(time.time() * 1000)}"


class TestLogConversation:
    """Test conversation logging"""

    def test_log_conversation(self, logger, unique_student_id):
        """Test that conversations are logged correctly"""
        student_id = unique_student_id
        query = "How does recursion work?"
        response = "Great question! What do you already know about functions calling themselves?"
        decision = "allow"

        # Log the conversation
        log_entry = logger.log_conversation(
            student_id=student_id,
            query=query,
            response=response,
            decision=decision
        )

        # Verify log entry structure
        assert log_entry["student_id"] == student_id
        assert log_entry["query"] == query
        assert log_entry["response"] == response
        assert log_entry["decision"] == decision
        assert "timestamp" in log_entry

    def test_log_with_conversation_id(self, logger, unique_student_id):
        """Test logging with explicit conversation ID"""
        conv_id = f"conv_{int(time.time())}"

        log_entry = logger.log_conversation(
            student_id=unique_student_id,
            query="Test query",
            response="Test response",
            decision="allow",
            conversation_id=conv_id
        )

        assert log_entry["conversation_id"] == conv_id

    def test_log_with_metadata(self, logger, unique_student_id):
        """Test logging with additional metadata"""
        metadata = {
            "tokens_used": 150,
            "mock": False,
            "concepts": ["recursion", "functions"]
        }

        log_entry = logger.log_conversation(
            student_id=unique_student_id,
            query="Explain recursion",
            response="Recursion is...",
            decision="allow",
            metadata=metadata
        )

        assert log_entry["metadata"] == metadata


class TestGetStudentHistory:
    """Test retrieving student conversation history"""

    def test_get_student_history(self, logger, unique_student_id):
        """Test retrieving history for a specific student"""
        student_id = unique_student_id

        # Create multiple conversations
        for i in range(3):
            logger.log_conversation(
                student_id=student_id,
                query=f"Question {i}",
                response=f"Answer {i}",
                decision="allow"
            )

        # Retrieve history
        history = logger.get_student_conversations(student_id)

        assert len(history) >= 3
        # Verify all entries belong to the student
        assert all(entry["student_id"] == student_id for entry in history)

    def test_get_empty_history(self, logger):
        """Test retrieving history for non-existent student"""
        history = logger.get_student_conversations("nonexistent_student_12345")
        assert history == []


class TestDailyLogCreated:
    """Test daily log file creation"""

    def test_daily_log_created(self, logger, unique_student_id):
        """Test that daily log file is created"""
        # Log a conversation
        logger.log_conversation(
            student_id=unique_student_id,
            query="Test query",
            response="Test response",
            decision="allow"
        )

        # Check that today's log file exists
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = logger.logs_dir / f"{today}.json"

        assert log_file.exists()

        # Verify it's valid JSON
        with open(log_file, "r") as f:
            data = json.load(f)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_multiple_logs_same_day(self, logger, unique_student_id):
        """Test multiple logs on the same day"""
        # Log multiple conversations
        for i in range(5):
            logger.log_conversation(
                student_id=unique_student_id,
                query=f"Query {i}",
                response=f"Response {i}",
                decision="allow"
            )

        # Get today's file
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = logger.logs_dir / f"{today}.json"

        with open(log_file, "r") as f:
            data = json.load(f)

        # Should have at least 5 entries
        assert len(data) >= 5


class TestStudentStats:
    """Test student statistics calculation"""

    def test_get_student_stats(self, logger, unique_student_id):
        """Test retrieving student statistics"""
        student_id = unique_student_id

        # Create conversations with metadata
        for i in range(3):
            logger.log_conversation(
                student_id=student_id,
                query=f"Question {i}",
                response=f"Answer {i}",
                decision="allow",
                metadata={"concepts": [f"concept_{i}"]}
            )

        # Get stats
        stats = logger.get_student_stats(student_id)

        assert stats["total_conversations"] >= 3
        assert "concepts_discussed" in stats
        assert "time_spent" in stats
        assert "last_active" in stats

    def test_stats_empty_student(self, logger):
        """Test stats for non-existent student"""
        stats = logger.get_student_stats("nonexistent_student_xyz")

        assert stats["total_conversations"] == 0
        assert stats["concepts_discussed"] == []


class TestFlaggedConversations:
    """Test flagged conversation retrieval"""

    def test_get_flagged_conversations(self, logger, unique_student_id):
        """Test retrieving flagged conversations"""
        # Log a flagged conversation
        logger.log_conversation(
            student_id=unique_student_id,
            query="Urgent help needed for exam tomorrow",
            response="Flagged for review",
            decision="flag",
            metadata={"requires_human_review": True}
        )

        # Get flagged conversations
        flagged = logger.get_flagged_conversations()

        # Should have at least one flagged
        assert len(flagged) >= 1
        assert all(conv["decision"] == "flag" for conv in flagged)


class TestSingletonLogger:
    """Test singleton pattern"""

    def test_singleton_instance(self):
        """Test that get_conversation_logger returns singleton"""
        logger1 = get_conversation_logger()
        logger2 = get_conversation_logger()

        assert logger1 is logger2
