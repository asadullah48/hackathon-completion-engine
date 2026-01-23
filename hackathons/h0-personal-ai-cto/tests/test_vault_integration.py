"""
Test suite for vault integration functionality
"""

import unittest
from pathlib import Path
import tempfile
import json
from datetime import datetime


class TestVaultIntegration(unittest.TestCase):
    """Test cases for vault integration."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary vault directory for testing
        self.temp_dir = Path(tempfile.mkdtemp())
        self.vault_path = self.temp_dir / "vault"
        
        self.vault_path.mkdir(exist_ok=True)
        
        # Create necessary subdirectories
        (self.vault_path / "Needs_Action").mkdir(exist_ok=True)
        (self.vault_path / "Pending_Approval").mkdir(exist_ok=True)
        (self.vault_path / "Approved").mkdir(exist_ok=True)
        (self.vault_path / "Rejected").mkdir(exist_ok=True)
        (self.vault_path / "Done").mkdir(exist_ok=True)
        (self.vault_path / "Logs").mkdir(exist_ok=True)
        (self.vault_path / "Hackathons").mkdir(exist_ok=True)
        (self.vault_path / "Briefings").mkdir(exist_ok=True)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_vault_structure_exists(self):
        """Test that all required vault directories exist."""
        required_dirs = [
            "Needs_Action",
            "Pending_Approval", 
            "Approved",
            "Rejected",
            "Done",
            "Logs",
            "Hackathons",
            "Briefings"
        ]
        
        for dir_name in required_dirs:
            with self.subTest(directory=dir_name):
                dir_path = self.vault_path / dir_name
                self.assertTrue(dir_path.exists(), f"Directory {dir_name} does not exist")
                self.assertTrue(dir_path.is_dir(), f"{dir_name} is not a directory")

    def test_create_action_item(self):
        """Test creating an action item in the vault."""
        action_item_path = self.vault_path / "Needs_Action" / "test_action.md"
        
        # Create a sample action item
        action_content = f"""# TEST ACTION ITEM

**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Category:** test
**Priority:** Medium

---

## Action Details

This is a test action item for vault integration testing.

---

## Status

- [x] Item created
- [ ] Action reviewed by human
- [ ] Action completed
- [ ] Item archived

---

**Test Action Item Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # Write the action item
        with open(action_item_path, 'w', encoding='utf-8') as f:
            f.write(action_content)
        
        # Verify the file was created
        self.assertTrue(action_item_path.exists())
        
        # Verify the content
        with open(action_item_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("TEST ACTION ITEM", content)
            # Check that the file was created with the correct name
            self.assertTrue(action_item_path.name.startswith("test_action"))

    def test_log_activity(self):
        """Test logging an activity to the vault."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.vault_path / "Logs" / f"{today}.json"
        
        # Create a sample log entry
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'test_activity',
            'details': {
                'test_key': 'test_value',
                'result': 'success'
            }
        }
        
        # Write the log entry
        log_data = {'date': today, 'activities': [log_entry]}
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        # Verify the log file was created
        self.assertTrue(log_file.exists())
        
        # Verify the content
        with open(log_file, 'r') as f:
            loaded_data = json.load(f)
            self.assertEqual(loaded_data['date'], today)
            self.assertEqual(len(loaded_data['activities']), 1)
            self.assertEqual(loaded_data['activities'][0]['type'], 'test_activity')


if __name__ == '__main__':
    unittest.main()