"""
Test suite for HITL (Human-in-the-Loop) workflow functionality
"""

import unittest
from pathlib import Path
import tempfile
import json
from datetime import datetime


class TestHITLWorkflow(unittest.TestCase):
    """Test cases for HITL workflow."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary vault directory for testing
        self.temp_dir = Path(tempfile.mkdtemp())
        self.vault_path = self.temp_dir / "vault"
        
        self.vault_path.mkdir(exist_ok=True)
        
        # Create necessary subdirectories
        (self.vault_path / "Pending_Approval").mkdir(exist_ok=True)
        (self.vault_path / "Approved").mkdir(exist_ok=True)
        (self.vault_path / "Rejected").mkdir(exist_ok=True)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_approval_request_creation(self):
        """Test creating an approval request."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        approval_filename = f"APPROVAL_{timestamp}_test_action.md"
        approval_path = self.vault_path / "Pending_Approval" / approval_filename
        
        # Create a sample approval request
        approval_content = f"""# APPROVAL REQUEST: Test Action

**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Priority:** Medium
**Estimated Impact:** Testing approval workflow

## Proposed Action
Test action for HITL workflow validation

## Rationale
Testing the approval workflow functionality

## Risks
No real risks - this is a test

## Alternatives Considered
None - this is for testing purposes only

---

**Human Decision:**
- [ ] ✅ APPROVE - Proceed with action
- [ ] ❌ REJECT - Do not proceed
- [ ] 🔄 MODIFY - Adjust and resubmit

**Feedback:**
[Test feedback for approval request]
"""
        
        # Write the approval request
        with open(approval_path, 'w', encoding='utf-8') as f:
            f.write(approval_content)
        
        # Verify the file was created
        self.assertTrue(approval_path.exists())
        
        # Verify the content
        with open(approval_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("APPROVAL REQUEST: Test Action", content)
            self.assertIn("Human Decision:", content)
            self.assertIn("✅ APPROVE", content)
            self.assertIn("❌ REJECT", content)

    def test_approval_process_approve(self):
        """Test approving an action request."""
        # First create an approval request
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        approval_filename = f"APPROVAL_{timestamp}_approve_test.md"
        approval_path = self.vault_path / "Pending_Approval" / approval_filename
        
        approval_content = f"""# APPROVAL REQUEST: Approve Test

**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Priority:** Medium

## Proposed Action
Test action for approval

---

**Human Decision:**
- [x] ✅ APPROVE - Proceed with action
- [ ] ❌ REJECT - Do not proceed
- [ ] 🔄 MODIFY - Adjust and resubmit

**Feedback:**
Approved for testing purposes.
"""
        
        with open(approval_path, 'w', encoding='utf-8') as f:
            f.write(approval_content)
        
        # Verify the approval request was created
        self.assertTrue(approval_path.exists())
        
        # Simulate moving to approved folder (this would normally be done by the HITL processor)
        approved_path = self.vault_path / "Approved" / approval_filename
        approval_path.rename(approved_path)
        
        # Verify the file moved to approved folder
        self.assertFalse(approval_path.exists())
        self.assertTrue(approved_path.exists())

    def test_approval_process_reject(self):
        """Test rejecting an action request."""
        # First create an approval request
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        approval_filename = f"APPROVAL_{timestamp}_reject_test.md"
        approval_path = self.vault_path / "Pending_Approval" / approval_filename
        
        approval_content = f"""# APPROVAL REQUEST: Reject Test

**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Priority:** Medium

## Proposed Action
Test action for rejection

---

**Human Decision:**
- [ ] ✅ APPROVE - Proceed with action
- [x] ❌ REJECT - Do not proceed
- [ ] 🔄 MODIFY - Adjust and resubmit

**Feedback:**
Rejected for testing purposes.
"""
        
        with open(approval_path, 'w', encoding='utf-8') as f:
            f.write(approval_content)
        
        # Verify the approval request was created
        self.assertTrue(approval_path.exists())
        
        # Simulate moving to rejected folder (this would normally be done by the HITL processor)
        rejected_path = self.vault_path / "Rejected" / approval_filename
        approval_path.rename(rejected_path)
        
        # Verify the file moved to rejected folder
        self.assertFalse(approval_path.exists())
        self.assertTrue(rejected_path.exists())


if __name__ == '__main__':
    unittest.main()