# H0 VALIDATION CHECKLIST
**Quick Verification Guide for Personal AI CTO**

**Use this to verify each component after Claude Code implements it.**

---

## ✅ PHASE 1: FOUNDATION VALIDATION

### Directory Structure
```bash
# Run this command to verify structure
cd D:\Personal-AI-Employee\hackathons\h0-personal-ai-cto
tree /F /A
```

**Expected:**
- [ ] `vault/` directory exists
- [ ] `vault/Inbox/` exists
- [ ] `vault/Needs_Action/` exists
- [ ] `vault/Pending_Approval/` exists
- [ ] `vault/Approved/` exists
- [ ] `vault/Rejected/` exists
- [ ] `vault/Done/` exists
- [ ] `vault/Hackathons/` exists
- [ ] `vault/Logs/` exists
- [ ] `vault/Briefings/` exists
- [ ] `watchers/` directory exists
- [ ] `skills/` directory exists
- [ ] `config/` directory exists
- [ ] `tests/` directory exists

### Vault Files
**Check these files exist and have content:**
- [ ] `vault/Dashboard.md` (>100 lines)
- [ ] `vault/Handbook.md` (>200 lines)
- [ ] `vault/Business_Goals.md` (>150 lines)

**Quick Test:**
```bash
# Check file line counts
wc -l vault/Dashboard.md vault/Handbook.md vault/Business_Goals.md
```

### Configuration Files
- [ ] `requirements.txt` exists
- [ ] `.env.example` exists
- [ ] `.gitignore` exists
- [ ] `README.md` exists (if created)

**Quick Test:**
```bash
# Verify requirements.txt is valid
python -m pip install -r requirements.txt --dry-run
```

**✅ PHASE 1 PASS if all items checked**

---

## ✅ PHASE 2: FILE WATCHER VALIDATION

### Code Validation
```bash
# Check file exists and has correct class
cd D:\Personal-AI-Employee\hackathons\h0-personal-ai-cto
python -c "from watchers.file_watcher import FileWatcher; print('✅ Import successful')"
```

**Expected:** "✅ Import successful"

### Dry-Run Test
```bash
# Run watcher in dry-run mode for 30 seconds
python watchers/file_watcher.py --dry-run --interval 5
# Press Ctrl+C after 30 seconds
```

**Expected Output:**
```
🚀 File Watcher Starting...
   Monitoring: D:\AI-Employee-Inbox
   Vault: D:\Personal-AI-Employee\hackathons\h0-personal-ai-cto\vault
   Interval: 5s
   Dry Run: True
```

**Checklist:**
- [ ] Watcher starts without errors
- [ ] Shows correct paths
- [ ] Dry run mode indicated
- [ ] Can stop with Ctrl+C

### Real Mode Test
**Setup:**
```bash
# Create inbox if missing
mkdir D:\AI-Employee-Inbox

# Create test file
echo "Test content" > D:\AI-Employee-Inbox\test.txt
```

**Run:**
```bash
# Run watcher in real mode for 30 seconds
python watchers/file_watcher.py --interval 5
# Wait 10 seconds, then Ctrl+C
```

**Verification:**
```bash
# Check action item created
dir vault\Needs_Action\FILE_*.md

# Check log created
dir vault\Logs\*.json
```

**Checklist:**
- [ ] Action item file created in `vault/Needs_Action/`
- [ ] Action item has correct format (frontmatter, file info, actions)
- [ ] Log file created in `vault/Logs/`
- [ ] Log contains activity entry
- [ ] Test file detected correctly

**✅ PHASE 2 PASS if all items checked**

---

## ✅ PHASE 3: INTEGRATION VALIDATION

### Action Item Format
**Open:** `vault/Needs_Action/FILE_*.md`

**Verify contains:**
- [ ] Proper markdown frontmatter
- [ ] File information section
- [ ] Suggested actions checkboxes
- [ ] Status section
- [ ] Notes section
- [ ] File path reference

**Expected Format:**
```markdown
# FILE DETECTED: test.txt

**Detected:** 2026-01-20 09:00:00
**Category:** other
**Priority:** Medium

---

## File Information
...

## Suggested Actions
- [ ] Review file
...

## Status
- [x] File detected
- [ ] Action reviewed by human
...
```

### Activity Log Format
**Open:** `vault/Logs/[TODAY].json`

**Verify structure:**
```json
{
  "date": "2026-01-20",
  "activities": [
    {
      "timestamp": "2026-01-20T09:00:00",
      "type": "file_detected",
      "details": {
        "filename": "test.txt",
        "path": "...",
        "category": "other",
        "action_item": "..."
      }
    }
  ]
}
```

**Checklist:**
- [ ] Valid JSON format
- [ ] Contains date field
- [ ] Contains activities array
- [ ] Activity has timestamp
- [ ] Activity has type
- [ ] Activity has details

### HITL Workflow
**Check skill file:**
- [ ] `skills/hitl-approval-manager.md` exists
- [ ] Contains workflow documentation
- [ ] Has template for approval requests
- [ ] Includes usage examples

**Test approval request:**
```bash
# Check if sample approval created
dir vault\Pending_Approval\APPROVAL_*.md
```

**Checklist:**
- [ ] Sample approval file exists
- [ ] Has proper structure
- [ ] Contains decision checkboxes
- [ ] Has feedback section

**✅ PHASE 3 PASS if all items checked**

---

## ✅ PHASE 4: END-TO-END VALIDATION

### Complete Workflow Test

**Step 1: Drop new file**
```bash
echo "Important document" > D:\AI-Employee-Inbox\important.pdf
```

**Step 2: Wait 15 seconds**

**Step 3: Verify action created**
```bash
dir vault\Needs_Action\FILE_*important*.md
```

**Step 4: Check dashboard**
- Open `vault/Dashboard.md`
- Verify "Pending Actions" count updated
- Verify "Recent Activity" shows new file

**Step 5: Check log**
```bash
type vault\Logs\[TODAY].json
```

**Complete Workflow Checklist:**
- [ ] New file detected within 15 seconds
- [ ] Action item created with correct category
- [ ] Log entry added
- [ ] Dashboard reflects new action (if auto-update implemented)
- [ ] No errors in console

### Dashboard Validation
**Open:** `vault/Dashboard.md`

**Verify sections:**
- [ ] Quick Stats table
- [ ] Hackathon Status table
- [ ] Recent Activity section
- [ ] Urgent Items section
- [ ] This Week's Goals section
- [ ] System Health table

### Documentation Validation
**Open:** `README.md`

**Must contain:**
- [ ] Project description
- [ ] Installation instructions
- [ ] Usage guide
- [ ] Configuration guide
- [ ] Troubleshooting section

**✅ PHASE 4 PASS if all items checked**

---

## 🎯 TIER ASSESSMENT

### Bronze Tier Requirements
- [ ] File watcher monitors inbox ✓
- [ ] Action items created automatically ✓
- [ ] Vault structure complete ✓
- [ ] HITL workflow documented ✓
- [ ] Dashboard shows status ✓
- [ ] Basic logging functional ✓

**If all checked:** ✅ **BRONZE TIER ACHIEVED**

### Silver Tier Requirements (Stretch)
- [ ] CEO briefing generator implemented
- [ ] Email integration working
- [ ] Advanced dashboard with auto-refresh
- [ ] Multiple watcher types (file + email)

**If 2+ checked:** 🎯 **SILVER TIER ACHIEVED**

---

## 🚨 COMMON ISSUES & FIXES

### Issue: File watcher not detecting files
**Check:**
1. Inbox folder exists: `D:\AI-Employee-Inbox`
2. Watcher is running
3. Check interval isn't too long
4. File permissions allow reading

**Fix:**
```bash
# Verify inbox
mkdir D:\AI-Employee-Inbox

# Test with larger interval
python watchers/file_watcher.py --interval 1
```

### Issue: Action items not created
**Check:**
1. `vault/Needs_Action/` directory exists
2. Watcher has write permissions
3. Not in dry-run mode

**Fix:**
```bash
# Verify directory
mkdir vault\Needs_Action

# Run in verbose mode (add logging)
```

### Issue: Logs not writing
**Check:**
1. `vault/Logs/` directory exists
2. Valid JSON format
3. Disk space available

**Fix:**
```bash
# Verify directory
mkdir vault\Logs

# Check disk space
dir
```

---

## 📊 FINAL VALIDATION REPORT

**Complete this after all phases:**

```
H0 VALIDATION REPORT
Date: [TODAY]
Validated By: Asadullah

PHASE 1: Foundation          [✓/✗]
PHASE 2: File Watcher        [✓/✗]
PHASE 3: Integration         [✓/✗]
PHASE 4: End-to-End         [✓/✗]

TIER ACHIEVED: [Bronze/Silver/Gold]

CRITICAL ISSUES: [None/List]
MINOR ISSUES: [None/List]

READY FOR PRODUCTION: [YES/NO]

NEXT STEPS:
1. [Action item]
2. [Action item]
```

---

**END OF VALIDATION CHECKLIST**

_Use this to verify H0 is complete and functional._
