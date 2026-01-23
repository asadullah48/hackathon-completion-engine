#!/usr/bin/env python3
"""
Test script to verify H0 Personal AI CTO implementation
"""

import os
import sys
import time
from pathlib import Path
import tempfile

def test_file_watcher():
    """Test the file watcher functionality."""
    print("🔍 Testing File Watcher Implementation...")
    
    # Import the FileWatcher class
    try:
        from watchers.file_watcher import FileWatcher
        print("✅ Successfully imported FileWatcher")
    except ImportError as e:
        print(f"❌ Failed to import FileWatcher: {e}")
        return False
    
    # Create temporary directories for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        drop_folder = temp_path / "test_drop_folder"
        vault_path = temp_path / "test_vault"
        
        drop_folder.mkdir()
        vault_path.mkdir()
        
        # Create required subdirectories in vault
        (vault_path / "Needs_Action").mkdir()
        (vault_path / "Logs").mkdir()
        
        # Test FileWatcher initialization
        try:
            watcher = FileWatcher(
                drop_folder=drop_folder,
                vault_path=vault_path,
                check_interval=1,
                dry_run=True
            )
            print("✅ FileWatcher initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize FileWatcher: {e}")
            return False
        
        # Test file categorization
        test_file = drop_folder / "test.py"
        test_file.touch()
        
        category = watcher._categorize_file(test_file)
        if category == "code":
            print("✅ File categorization working correctly")
        else:
            print(f"❌ File categorization failed. Expected 'code', got '{category}'")
            return False
        
        # Test action item creation (dry run)
        action_path = watcher._create_action_item(test_file)
        if action_path is None:  # Because dry_run=True
            print("✅ Action item creation in dry-run mode working correctly")
        else:
            print(f"❌ Action item creation in dry-run mode failed. Expected None, got {action_path}")
            return False
        
        # Test logging
        try:
            watcher._log_activity('test_event', {'test': 'data'})
            print("✅ Logging functionality working")
        except Exception as e:
            print(f"❌ Logging functionality failed: {e}")
            return False
    
    return True

def test_directories():
    """Test that all required directories exist."""
    print("\n🔍 Testing Directory Structure...")
    
    base_path = Path("/mnt/d/Personal-AI-Employee/hackathons/h0-personal-ai-cto")
    
    required_dirs = [
        "vault",
        "vault/Inbox",
        "vault/Needs_Action",
        "vault/Pending_Approval",
        "vault/Approved",
        "vault/Rejected",
        "vault/Done",
        "vault/Hackathons",
        "vault/Logs",
        "vault/Briefings",
        "watchers",
        "skills",
        "config",
        "config/credentials",
        "tests"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        full_path = base_path / dir_path
        if full_path.exists() and full_path.is_dir():
            print(f"✅ {dir_path}/ exists")
        else:
            print(f"❌ {dir_path}/ missing")
            all_exist = False
    
    return all_exist

def test_files():
    """Test that all required files exist."""
    print("\n🔍 Testing Required Files...")
    
    base_path = Path("/mnt/d/Personal-AI-Employee/hackathons/h0-personal-ai-cto")
    
    required_files = [
        "README.md",
        "requirements.txt",
        ".env.example",
        ".gitignore",
        "watchers/file_watcher.py",
        "watchers/ceo_briefing_generator.py",
        "skills/hitl-approval-manager.md",
        "vault/Dashboard.md",
        "vault/Handbook.md",
        "vault/Business_Goals.md",
        "config/config.yaml",
        "tests/test_file_watcher.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists() and full_path.is_file():
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests."""
    print("🚀 Running H0 Personal AI CTO Implementation Tests...\n")
    
    # Change to the project directory
    project_dir = "/mnt/d/Personal-AI-Employee/hackathons/h0-personal-ai-cto"
    os.chdir(project_dir)
    
    # Run tests
    dir_success = test_directories()
    file_success = test_files()
    watcher_success = test_file_watcher()
    
    print(f"\n📋 Test Results:")
    print(f"Directory Structure: {'✅ PASS' if dir_success else '❌ FAIL'}")
    print(f"Required Files: {'✅ PASS' if file_success else '❌ FAIL'}")
    print(f"File Watcher: {'✅ PASS' if watcher_success else '❌ FAIL'}")
    
    overall_success = dir_success and file_success and watcher_success
    print(f"\n🎯 Overall Status: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n🎉 H0 Personal AI CTO implementation is complete and functional!")
        print("✨ Ready for Silver tier evaluation.")
    else:
        print("\n⚠️  Some components need attention before deployment.")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)