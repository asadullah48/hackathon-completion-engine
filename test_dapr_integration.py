"""
Test script to validate Dapr integration in the Course Companion API
"""

import asyncio
import json
import logging
from typing import Dict, Any

from backend.services.dapr_service import DaprService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_dapr_connection():
    """Test basic Dapr connection"""
    logger.info("Testing Dapr connection...")
    
    try:
        dapr_service = DaprService()
        dapr_service.initialize()
        logger.info("✓ Dapr connection successful")
        return True
    except Exception as e:
        logger.error(f"✗ Dapr connection failed: {str(e)}")
        return False


async def test_event_publishing():
    """Test Dapr event publishing functionality"""
    logger.info("Testing Dapr event publishing...")
    
    try:
        dapr_service = DaprService()
        dapr_service.initialize()
        
        # Test event data
        test_event = {
            "test_id": "integration_test_001",
            "message": "This is a test event for Dapr integration",
            "timestamp": "2026-02-06T10:00:00Z",
            "source": "test_script"
        }
        
        # Publish test event
        success = await dapr_service.publish_event(
            topic_name="test-topic",
            data=test_event
        )
        
        if success:
            logger.info("✓ Dapr event publishing successful")
            return True
        else:
            logger.error("✗ Dapr event publishing failed")
            return False
            
    except Exception as e:
        logger.error(f"✗ Dapr event publishing failed with exception: {str(e)}")
        return False


async def test_state_management():
    """Test Dapr state management functionality"""
    logger.info("Testing Dapr state management...")
    
    try:
        dapr_service = DaprService()
        dapr_service.initialize()
        
        # Test state data
        test_key = "test-state-key"
        test_value = {
            "test_id": "integration_test_001",
            "data": "This is test state data",
            "timestamp": "2026-02-06T10:00:00Z"
        }
        
        # Save state
        save_success = await dapr_service.save_state(
            store_name="statestore",
            key=test_key,
            value=test_value
        )
        
        if not save_success:
            logger.error("✗ Dapr state save failed")
            return False
        
        # Retrieve state
        retrieved_value = await dapr_service.get_state(
            store_name="statestore",
            key=test_key
        )
        
        if retrieved_value is not None and retrieved_value == test_value:
            logger.info("✓ Dapr state management successful")
            return True
        else:
            logger.error(f"✗ Dapr state retrieval failed. Expected: {test_value}, Got: {retrieved_value}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Dapr state management failed with exception: {str(e)}")
        return False


async def test_chat_event_publishing():
    """Test the specific chat event publishing functionality"""
    logger.info("Testing chat event publishing...")
    
    try:
        dapr_service = DaprService()
        dapr_service.initialize()
        
        # Simulate a chat event that would be published by the chat endpoint
        chat_event_data = {
            "type": "chat_completed",
            "student_id": "test_student_123",
            "conversation_id": "test_conv_456",
            "query": "What is the capital of France?",
            "response": "The capital of France is Paris.",
            "decision": "allow",
            "tokens_used": 15,
            "timestamp": 1707242400.0  # Unix timestamp
        }
        
        # Publish chat event
        success = await dapr_service.publish_event(
            topic_name="chat-events",
            data=chat_event_data
        )
        
        if success:
            logger.info("✓ Chat event publishing successful")
            return True
        else:
            logger.error("✗ Chat event publishing failed")
            return False
            
    except Exception as e:
        logger.error(f"✗ Chat event publishing failed with exception: {str(e)}")
        return False


async def run_all_tests():
    """Run all Dapr integration tests"""
    logger.info("Starting Dapr integration tests...\n")
    
    tests = [
        ("Dapr Connection", test_dapr_connection),
        ("Event Publishing", test_event_publishing),
        ("State Management", test_state_management),
        ("Chat Event Publishing", test_chat_event_publishing),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"Running {test_name} test...")
        result = await test_func()
        results.append((test_name, result))
        logger.info("")  # Empty line for readability
    
    # Summary
    logger.info("Test Results Summary:")
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        logger.info(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All Dapr integration tests passed!")
        return True
    else:
        logger.info("❌ Some Dapr integration tests failed.")
        return False


if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(run_all_tests())
    
    # Exit with appropriate code
    exit(0 if success else 1)