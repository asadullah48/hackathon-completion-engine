"""
Tests for Chat Endpoint
Tests the chat router with constitutional filtering
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os
import time

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

from backend.main import app

client = TestClient(app)


class TestChatAllowedQueries:
    """Test that legitimate learning queries are allowed"""

    def test_chat_allowed_query_concept(self):
        """Test that concept questions work"""
        response = client.post("/api/chat", json={
            "message": "Can you explain how sorting algorithms work?",
            "student_id": "test_student_001"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["constitutional_decision"] == "allow"
        assert "response" in data
        assert data["logged"] is True
        assert "conversation_id" in data

    def test_chat_allowed_debugging_help(self):
        """Test that debugging help is allowed"""
        response = client.post("/api/chat", json={
            "message": "Can you help me understand why my code isn't working?",
            "student_id": "test_student_002"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["constitutional_decision"] == "allow"

    def test_chat_allowed_general_learning(self):
        """Test general learning questions"""
        response = client.post("/api/chat", json={
            "message": "What is the difference between a list and a tuple in Python?",
            "student_id": "test_student_003"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["constitutional_decision"] == "allow"


class TestChatBlockedQueries:
    """Test that prohibited queries are blocked"""

    def test_chat_blocked_homework_request(self):
        """Test that homework solution requests are blocked"""
        response = client.post("/api/chat", json={
            "message": "Solve my homework problem for me",
            "student_id": "test_student_block_001"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["constitutional_decision"] == "block"
        assert "response" in data
        # Should contain Socratic guidance
        assert any(keyword in data["response"].lower() for keyword in
                   ["help you learn", "tried so far", "understand", "work through"])

    def test_chat_blocked_code_writing(self):
        """Test that code writing requests are blocked"""
        response = client.post("/api/chat", json={
            "message": "Write the code for me to complete this assignment",
            "student_id": "test_student_block_002"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["constitutional_decision"] == "block"

    def test_chat_blocked_direct_answer(self):
        """Test that direct answer requests are blocked"""
        response = client.post("/api/chat", json={
            "message": "Just give me the answer to this problem",
            "student_id": "test_student_block_003"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["constitutional_decision"] == "block"


class TestConversationLogging:
    """Test that conversations are properly logged"""

    def test_conversation_logged(self):
        """Verify that conversations are logged"""
        student_id = f"test_logger_{int(time.time())}"

        # Send a message
        response = client.post("/api/chat", json={
            "message": "Can you explain recursion?",
            "student_id": student_id
        })

        assert response.status_code == 200
        data = response.json()
        assert data["logged"] is True

        # Check that we can retrieve the conversation
        conv_response = client.get(f"/api/conversations/{student_id}")
        assert conv_response.status_code == 200
        conv_data = conv_response.json()
        assert conv_data["student_id"] == student_id
        # Should have at least 1 conversation
        assert conv_data["total"] >= 1

    def test_blocked_query_logged(self):
        """Verify blocked queries are also logged"""
        student_id = f"test_blocked_log_{int(time.time())}"

        response = client.post("/api/chat", json={
            "message": "Do my homework for me",
            "student_id": student_id
        })

        assert response.status_code == 200
        data = response.json()
        assert data["constitutional_decision"] == "block"
        assert data["logged"] is True


class TestSocraticResponse:
    """Test that responses follow Socratic style"""

    def test_socratic_response_style(self):
        """Check that blocked responses use Socratic questioning"""
        response = client.post("/api/chat", json={
            "message": "Give me the answer to this test question",
            "student_id": "test_socratic_001"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["constitutional_decision"] == "block"

        # Check for Socratic elements in response
        response_text = data["response"].lower()
        socratic_indicators = [
            "what have you tried",
            "understand",
            "help you learn",
            "work through",
            "concept",
            "confusing"
        ]
        assert any(indicator in response_text for indicator in socratic_indicators)


class TestRateLimiting:
    """Test rate limiting functionality"""

    def test_rate_limiting_enforced(self):
        """Test that rate limiting is enforced (max 10/min)"""
        student_id = f"test_rate_limit_{int(time.time())}"
        responses = []

        # Send 12 requests quickly
        for i in range(12):
            response = client.post("/api/chat", json={
                "message": f"Explain concept {i}",
                "student_id": student_id
            })
            responses.append(response)

        # Count successful vs rate-limited responses
        # First 10 should succeed, rest should be rate-limited
        success_count = sum(1 for r in responses if r.status_code == 200 and
                           r.json().get("constitutional_decision") != "block" or
                           "rate limit" not in r.json().get("response", "").lower())

        # After 10 requests, should start seeing rate limiting
        # Check if any response mentions rate limiting
        rate_limited = any(
            "rate limit" in r.json().get("response", "").lower()
            for r in responses
        )

        # We should see rate limiting kick in after 10 requests
        assert success_count <= 10 or rate_limited


class TestFlaggedQueries:
    """Test flagging functionality"""

    def test_flagged_query_suspicious(self):
        """Test that suspicious queries are flagged for HITL review"""
        response = client.post("/api/chat", json={
            "message": "I have an exam tomorrow and urgently need help",
            "student_id": "test_flag_001"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["constitutional_decision"] == "flag"
        assert "flagged" in data["response"].lower() or "review" in data["response"].lower()

    def test_manual_flag_endpoint(self):
        """Test manually flagging a conversation"""
        # First create a conversation
        chat_response = client.post("/api/chat", json={
            "message": "How do loops work?",
            "student_id": "test_manual_flag"
        })
        conv_id = chat_response.json()["conversation_id"]

        # Flag it manually
        flag_response = client.post(f"/api/flag/{conv_id}", json={
            "reason": "Testing manual flag"
        })

        assert flag_response.status_code == 200
        data = flag_response.json()
        assert data["status"] == "flagged"
        assert data["conversation_id"] == conv_id


class TestConversationRetrieval:
    """Test conversation history retrieval"""

    def test_get_student_conversations(self):
        """Test retrieving conversation history for a student"""
        student_id = f"test_history_{int(time.time())}"

        # Create a few conversations
        for i in range(3):
            client.post("/api/chat", json={
                "message": f"Question number {i}",
                "student_id": student_id
            })

        # Retrieve history
        response = client.get(f"/api/conversations/{student_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["student_id"] == student_id
        assert data["total"] >= 3

    def test_get_nonexistent_student(self):
        """Test retrieving history for non-existent student"""
        response = client.get("/api/conversations/nonexistent_student_xyz")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
