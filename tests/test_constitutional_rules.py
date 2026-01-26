import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from backend.middleware.constitutional_filter import ConstitutionalFilter


@pytest.fixture
def constitutional_filter():
    """Create a ConstitutionalFilter instance for testing"""
    return ConstitutionalFilter()


def test_homework_solution_blocked(constitutional_filter):
    """Test that homework solution requests are blocked"""
    query = "Can you solve this homework problem for me?"
    decision, reason, metadata = constitutional_filter.check_query(query)
    
    assert decision == "block"
    assert "prohibited pattern" in reason
    assert metadata["pattern_matched"] is not None


def test_code_writing_blocked(constitutional_filter):
    """Test that direct code writing requests are blocked"""
    query = "Write the code for me to complete this assignment"
    decision, reason, metadata = constitutional_filter.check_query(query)
    
    assert decision == "block"
    assert "prohibited pattern" in reason
    assert metadata["pattern_matched"] is not None


def test_direct_answer_blocked(constitutional_filter):
    """Test that direct answer requests are blocked"""
    query = "Give me the answer to this problem"
    decision, reason, metadata = constitutional_filter.check_query(query)
    
    assert decision == "block"
    assert "prohibited pattern" in reason
    assert metadata["pattern_matched"] is not None


def test_concept_question_allowed(constitutional_filter):
    """Test that concept questions are allowed"""
    query = "Can you explain how loops work in Python?"
    decision, reason, metadata = constitutional_filter.check_query(query)
    
    assert decision == "allow"
    assert "approved" in reason


def test_debugging_help_allowed(constitutional_filter):
    """Test that debugging help requests are allowed"""
    query = "Can you help me debug this code?"
    decision, reason, metadata = constitutional_filter.check_query(query)
    
    assert decision == "allow"
    assert "approved" in reason


def test_urgent_deadline_flagged(constitutional_filter):
    """Test that urgent deadline requests are flagged"""
    query = "I have an exam tomorrow and urgently need help"
    decision, reason, metadata = constitutional_filter.check_query(query)

    assert decision == "flag"
    assert "flagged" in reason
    assert metadata["requires_human_review"] is True


def test_time_pressure_flagged(constitutional_filter):
    """Test that time pressure requests are flagged"""
    query = "Due in 2 hours, need quick help"
    decision, reason, metadata = constitutional_filter.check_query(query)
    
    assert decision == "flag"
    assert "flagged" in reason
    assert metadata["requires_human_review"] is True