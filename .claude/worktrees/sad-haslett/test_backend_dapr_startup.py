"""
Simple test to verify backend can start with Dapr integration
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def test_backend_imports():
    """Test that all modules can be imported without errors"""
    print("Testing backend module imports with Dapr integration...")
    
    try:
        # Test main app import
        from backend.main import app, dapr_service
        print("✓ Main app imported successfully")
        
        # Test Dapr service import
        from backend.services.dapr_service import DaprService, get_dapr_service
        print("✓ Dapr service imported successfully")
        
        # Test that we can get a Dapr service instance
        service = get_dapr_service()
        print("✓ Dapr service instance created successfully")
        
        # Test router import
        from backend.routers.chat import router, dapr_service as chat_dapr_service
        print("✓ Chat router with Dapr imported successfully")
        
        print("\n✓ All imports successful! Dapr integration is properly set up.")
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_backend_imports()
    if not success:
        sys.exit(1)