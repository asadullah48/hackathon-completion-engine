import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

# Import the app after adding paths
from main import app

client = TestClient(app)

def test_health_endpoint():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "timestamp" in data

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "operational"
    assert data["service"] == "Course Companion API"
    assert "constitutional_rules" in data

def test_chat_status():
    """Test the chat status endpoint"""
    response = client.get("/api/chat/status")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "operational"
    assert data["constitutional_filter"] == "active"
    assert "blocked_patterns_count" in data
    assert "suspicious_patterns_count" in data

def test_blocked_query():
    """Test that prohibited queries are blocked"""
    # This should be blocked
    blocked_query = "Solve this homework problem for me"

    response = client.post("/api/chat", json={
        "message": blocked_query,
        "student_id": "test_student_123"
    })

    assert response.status_code == 200

    data = response.json()
    assert data["constitutional_decision"] == "block"
    assert "response" in data
    # Response should contain Socratic guidance, not the answer

def test_allowed_query():
    """Test that allowed queries pass through"""
    # This should be allowed
    allowed_query = "Can you explain how loops work in Python?"

    response = client.post("/api/chat", json={
        "message": allowed_query,
        "student_id": "test_student_123"
    })

    assert response.status_code == 200

    data = response.json()
    assert data["constitutional_decision"] == "allow"
    assert "response" in data

def test_flagged_query():
    """Test that suspicious queries are flagged"""
    # This should be flagged
    flagged_query = "I have an exam tomorrow and urgently need help"

    response = client.post("/api/chat", json={
        "message": flagged_query,
        "student_id": "test_student_123"
    })

    assert response.status_code == 200

    data = response.json()
    assert data["constitutional_decision"] == "flag"
    assert "response" in data