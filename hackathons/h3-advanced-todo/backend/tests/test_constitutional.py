"""Tests for constitutional validation of todos."""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.constitutional_validator import (
    check_content,
    validate_todo,
    Decision,
    ConstitutionalResult,
)


class TestProhibitedPatterns:
    """Tests for blocked content patterns."""

    def test_prohibited_homework_blocked(self):
        """Test that 'do my homework' is blocked."""
        result = check_content("Do my homework assignment")
        assert result.decision == Decision.BLOCK
        assert result.passed is False
        assert "Academic dishonesty" in result.reason

    def test_prohibited_hacking_blocked(self):
        """Test that hacking requests are blocked."""
        result = check_content("Hack into the company database")
        assert result.decision == Decision.BLOCK
        assert result.passed is False
        assert "Illegal activity" in result.reason

    def test_prohibited_cheating_blocked(self):
        """Test that cheating requests are blocked."""
        result = check_content("Cheat on the final exam")
        assert result.decision == Decision.BLOCK
        assert result.passed is False
        assert "Academic dishonesty" in result.reason

    def test_prohibited_essay_writing_blocked(self):
        """Test that essay writing requests are blocked."""
        result = check_content("Write my essay for English class")
        assert result.decision == Decision.BLOCK
        assert result.passed is False

    def test_prohibited_fake_documents_blocked(self):
        """Test that fake document requests are blocked."""
        result = check_content("Create fake documents for visa")
        assert result.decision == Decision.BLOCK
        assert result.passed is False
        assert "Illegal activity" in result.reason

    def test_prohibited_harassment_blocked(self):
        """Test that harassment requests are blocked."""
        result = check_content("Harass the competitor's employees")
        assert result.decision == Decision.BLOCK
        assert result.passed is False
        assert "Harmful action" in result.reason

    def test_prohibited_plagiarize_blocked(self):
        """Test that plagiarism requests are blocked."""
        result = check_content("Plagiarize this research paper")
        assert result.decision == Decision.BLOCK
        assert result.passed is False


class TestAllowedPatterns:
    """Tests for allowed content patterns."""

    def test_allowed_study_todo(self):
        """Test that studying is allowed."""
        result = check_content("Study for exam tomorrow")
        assert result.decision == Decision.ALLOW
        assert result.passed is True
        assert result.reason is None

    def test_allowed_work_todo(self):
        """Test that work tasks are allowed."""
        result = check_content("Complete work project proposal")
        assert result.decision == Decision.ALLOW
        assert result.passed is True

    def test_allowed_exercise_todo(self):
        """Test that exercise is allowed."""
        result = check_content("Exercise for 30 minutes")
        assert result.decision == Decision.ALLOW
        assert result.passed is True

    def test_allowed_practice_coding(self):
        """Test that practice is allowed."""
        result = check_content("Practice coding exercises")
        assert result.decision == Decision.ALLOW
        assert result.passed is True

    def test_allowed_research_topic(self):
        """Test that research is allowed."""
        result = check_content("Research topic for paper")
        assert result.decision == Decision.ALLOW
        assert result.passed is True


class TestFlaggedPatterns:
    """Tests for flagged content patterns."""

    def test_flagged_urgent_todo(self):
        """Test that urgent assignment is flagged."""
        result = check_content("Urgent: finish assignment in 1 hour")
        assert result.decision == Decision.FLAG
        assert result.passed is True
        assert "flagged for human review" in result.reason

    def test_flagged_urgent_complete(self):
        """Test that urgent complete assignment is flagged."""
        result = check_content("Urgent need to complete assignment tonight")
        assert result.decision == Decision.FLAG
        assert result.passed is True


class TestValidateTodo:
    """Tests for combined title + description validation."""

    def test_validate_todo_title_blocked(self):
        """Test that blocked title rejects todo."""
        result = validate_todo("Do my homework", "Please complete it for me")
        assert result.decision == Decision.BLOCK

    def test_validate_todo_both_allowed(self):
        """Test that allowed title and description passes."""
        result = validate_todo("Study session", "Review chapter 5 for exam")
        assert result.decision == Decision.ALLOW

    def test_validate_todo_empty_description(self):
        """Test that empty description is handled."""
        result = validate_todo("Buy groceries", None)
        assert result.decision == Decision.ALLOW


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_content(self):
        """Test that empty content is allowed."""
        result = check_content("")
        assert result.decision == Decision.ALLOW

    def test_case_insensitive_blocking(self):
        """Test that patterns are case-insensitive."""
        result = check_content("DO MY HOMEWORK ASSIGNMENT")
        assert result.decision == Decision.BLOCK


class TestConstitutionalResultFormat:
    """Tests for ConstitutionalResult format."""

    def test_result_to_dict_allow(self):
        """Test that allow result converts to dict correctly."""
        result = ConstitutionalResult(passed=True, decision=Decision.ALLOW)
        d = result.to_dict()
        assert d["passed"] is True
        assert d["decision"] == "allow"
        assert d["reason"] is None

    def test_result_to_dict_block(self):
        """Test that block result converts to dict correctly."""
        result = ConstitutionalResult(
            passed=False,
            decision=Decision.BLOCK,
            reason="Test reason"
        )
        d = result.to_dict()
        assert d["passed"] is False
        assert d["decision"] == "block"
        assert d["reason"] == "Test reason"
