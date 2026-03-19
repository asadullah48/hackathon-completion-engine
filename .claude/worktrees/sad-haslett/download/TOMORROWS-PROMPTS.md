# TOMORROW'S READY-TO-USE PROMPTS
**Copy-Paste These Directly into Claude Code**

**Date:** 2026-01-20 (After 3am reset)  
**Goal:** Complete H0 implementation in 4 sessions

---

## 🚀 SESSION 1 PROMPT (Foundation - 1 hour)

### **COPY THIS →**

```
IMPLEMENTATION: H0 Personal AI CTO - Session 1 (Foundation)

CONTEXT:
Building autonomous AI CTO system to manage 4 concurrent hackathons.
Rate limits reset at 3am - fresh start with clear blueprint.

CRITICAL DOCUMENTS:
1. D:\Personal-AI-Employee\CONSTITUTION.md
2. D:\Personal-AI-Employee\specs\SPEC-H0-CORE.md

BLUEPRINT (Read carefully):
I have a detailed implementation blueprint that specifies:
- Complete directory structure
- All vault markdown files (Dashboard, Handbook, Business Goals)
- File watcher implementation
- HITL workflow
- Validation criteria

TASK 1.1: Create Directory Structure
Create this exact structure:

D:\Personal-AI-Employee\hackathons\h0-personal-ai-cto\
├── vault/
│   ├── Inbox/
│   ├── Needs_Action/
│   ├── Pending_Approval/
│   ├── Approved/
│   ├── Rejected/
│   ├── Done/
│   ├── Hackathons/
│   ├── Logs/
│   └── Briefings/
├── watchers/
├── skills/
├── config/
│   └── credentials/
└── tests/

TASK 1.2: Generate Vault Files
Create these files with COMPLETE content:

1. vault/Dashboard.md - Real-time system status dashboard
   Must include:
   - Quick Stats table
   - Hackathon Status table (H0-H4)
   - Recent Activity section
   - Urgent Items section
   - This Week's Goals
   - System Health table

2. vault/Handbook.md - AI operational rules
   Must include:
   - Mission statement
   - Core principles (HITL, Spec-Driven, Transparency)
   - Decision framework (Auto-Execute vs Approval vs Escalate)
   - File management process
   - Approval workflow specification
   - Dashboard update rules
   - Security rules
   - Error handling

3. vault/Business_Goals.md - Hackathon objectives
   Must include:
   - Primary objectives (complete 5 hackathons)
   - KPI tables
   - Weekly goals breakdown
   - Resource budgets (time, tokens)
   - Success metrics

TASK 1.3: Create Configuration Files
1. requirements.txt with:
   - watchdog==4.0.0
   - python-dotenv==1.0.0
   - pyyaml==6.0.1
   - requests==2.31.0
   - click==8.1.7
   - rich==13.7.0

2. .env.example with:
   - VAULT_PATH=D:\Personal-AI-Employee\hackathons\h0-personal-ai-cto\vault
   - DROP_FOLDER=D:\AI-Employee-Inbox
   - CHECK_INTERVAL=10
   - DRY_RUN=false

3. .gitignore with:
   - .env
   - *.pyc
   - __pycache__/
   - .venv/
   - vault/Logs/*.json
   - config/credentials/*
   - !config/credentials/.gitkeep

4. README.md with quick start guide

VALIDATION:
After completion, show me:
1. Complete directory tree (use tree command or dir)
2. Line count for each vault file (wc -l or measure)
3. Contents of requirements.txt
4. Confirmation all files created

Then STOP and wait for my approval before Session 2.

CONSTRAINTS:
- Use exact paths specified
- Generate COMPLETE file contents (not stubs)
- Follow markdown formatting strictly
- All dates use format: YYYY-MM-DD
- All timestamps use format: YYYY-MM-DD HH:MM:SS

START NOW. Create foundation files.
```

---

## 🚀 SESSION 2 PROMPT (File Watcher - 1 hour)

### **COPY THIS →**

```
IMPLEMENTATION: H0 Personal AI CTO - Session 2 (File Watcher)

PREREQUISITE: Session 1 foundation complete ✅

TASK 2.1: Implement FileWatcher Class
Create: D:\Personal-AI-Employee\hackathons\h0-personal-ai-cto\watchers\file_watcher.py

REQUIREMENTS:
1. FileWatcher class with these methods:
   - __init__(drop_folder, vault_path, check_interval, dry_run)
   - _load_state() - Load processed files from JSON
   - _save_state() - Save processed files to JSON
   - _categorize_file(filepath) - Categorize by extension
   - _create_action_item(filepath) - Create markdown action file
   - _log_activity(type, details) - Log to daily JSON
   - check_for_new_files() - Scan for new files
   - run() - Main monitoring loop

2. File Categories:
   - document: .pdf, .docx, .doc, .txt, .md, .rtf
   - code: .py, .js, .ts, .tsx, .jsx, .java, .cpp, .c, .h
   - data: .csv, .xlsx, .xls, .json, .xml, .sql, .db
   - image: .png, .jpg, .jpeg, .gif, .svg, .webp, .bmp
   - video: .mp4, .mov, .avi, .mkv, .wmv, .flv
   - archive: .zip, .rar, .7z, .tar, .gz
   - other: everything else

3. Action Item Format:
```markdown
# FILE DETECTED: {filename}

**Detected:** {timestamp}
**Category:** {category}
**Priority:** Medium

---

## File Information

- **Name:** {name}
- **Size:** {size} bytes ({KB} KB)
- **Type:** {extension}
- **Location:** `{path}`
- **Created:** {created_time}

---

## Suggested Actions

Based on file type **{category}**, here are suggested actions:

[Category-specific action items with checkboxes]

---

## Status

- [x] File detected
- [ ] Action reviewed by human
- [ ] Action completed
- [ ] File archived

---

## Notes

*Add any notes about this file here...*

---

**File Path:** `{filepath}`
**Action Item Created:** {timestamp}
```

4. Activity Log Format (JSON):
```json
{
  "date": "YYYY-MM-DD",
  "activities": [
    {
      "timestamp": "YYYY-MM-DDTHH:MM:SS",
      "type": "file_detected",
      "details": {
        "filename": "...",
        "path": "...",
        "category": "...",
        "action_item": "..."
      }
    }
  ]
}
```

5. CLI with argparse:
   - --vault (default: vault path)
   - --drop-folder (default: D:\AI-Employee-Inbox)
   - --interval (default: 10)
   - --dry-run (flag)

6. State Persistence:
   - Save processed file IDs to .file_watcher_state.json
   - Use MD5 hash of filepath as ID
   - Load state on startup

TASK 2.2: Test Implementation

Step 1: Dry-run test
```bash
python watchers/file_watcher.py --dry-run --interval 5
```
Expected: Starts without errors, shows monitoring message

Step 2: Real test (if D:\AI-Employee-Inbox exists)
```bash
# Create test file
echo "Test content" > D:\AI-Employee-Inbox\test.txt

# Run watcher for 30 seconds
python watchers/file_watcher.py --interval 5
```
Expected: Detects file, creates action item, logs activity

VALIDATION:
Show me:
1. file_watcher.py line count and class structure
2. Dry-run test output
3. Real test results (if inbox exists):
   - Created action item path
   - Action item content preview
   - Log file content
4. Any errors encountered

Then STOP and wait for approval before Session 3.

QUALITY REQUIREMENTS:
- Type hints for all methods
- Docstrings for class and methods
- Proper error handling (try/except)
- Graceful shutdown on Ctrl+C
- Rich/colored output for better UX

START NOW. Implement file watcher.
```

---

## 🚀 SESSION 3 PROMPT (Integration & HITL - 1.5 hours)

### **COPY THIS →**

```
IMPLEMENTATION: H0 Personal AI CTO - Session 3 (Integration & HITL)

PREREQUISITES:
✅ Session 1 foundation complete
✅ Session 2 file watcher implemented

TASK 3.1: Integration Testing

Step 1: Verify Environment
```bash
# Check directories exist
dir D:\Personal-AI-Employee\hackathons\h0-personal-ai-cto\vault\Needs_Action
dir D:\Personal-AI-Employee\hackathons\h0-personal-ai-cto\vault\Logs

# Create inbox if missing
mkdir D:\AI-Employee-Inbox
```

Step 2: End-to-End Test
```bash
# Create diverse test files
echo "Project specification document" > D:\AI-Employee-Inbox\project-spec.pdf
echo "def hello(): pass" > D:\AI-Employee-Inbox\test_code.py
echo "name,age\nJohn,30" > D:\AI-Employee-Inbox\data.csv

# Run watcher
python watchers/file_watcher.py --interval 5
# Wait 30 seconds, press Ctrl+C
```

Step 3: Verify Results
Check:
- 3 action items created in vault/Needs_Action/
- Each categorized correctly (document, code, data)
- Activity log has 3 entries
- No errors in console

TASK 3.2: Implement HITL Approval Manager Skill

Create: skills/hitl-approval-manager.md

CONTENT:
```markdown
# HITL Approval Manager Skill

**Purpose:** Manage Human-in-the-Loop approval workflow

---

## Core Workflow

### Step 1: Create Approval Request
Location: vault/Pending_Approval/APPROVAL_{timestamp}_{action}.md

Template:
---
# APPROVAL REQUEST: [Action Type]

**Created:** [Timestamp]
**Priority:** [High/Medium/Low]
**Estimated Impact:** [Description]

## Proposed Action
[What the AI wants to do]

## Rationale
[Why this action is needed]

## Risks
[Potential downsides]

## Alternatives Considered
[Other options]

---

**Human Decision:**
- [ ] ✅ APPROVE - Proceed with action
- [ ] ❌ REJECT - Do not proceed
- [ ] 🔄 MODIFY - Adjust and resubmit

**Feedback:**
[Human comments here]
---

### Step 2: Monitor for Decision
Check every 30 seconds for marked checkbox

### Step 3: Execute Based on Decision
- APPROVED → Move to Approved/, execute action
- REJECTED → Move to Rejected/, log rejection
- MODIFIED → Read feedback, adjust, resubmit

---

## Usage Examples

[Include 2-3 concrete examples]

---

## Implementation Notes
- File naming: APPROVAL_{YYYYMMDD}_{HHMMSS}_{action}.md
- Priority levels: High (1h), Medium (4h), Low (24h)
- Always log approval decisions
```

TASK 3.3: Create Sample Approval Request

Create: vault/Pending_Approval/APPROVAL_20260120_090000_test.md

Content: Sample approval for deploying H1 to production
- Follow template exactly
- Use realistic content
- Leave checkboxes unchecked

TASK 3.4: Dashboard Integration Check

Open vault/Dashboard.md and verify:
- Quick Stats section exists
- Hackathon Status table shows H0 at 50%
- Recent Activity section present
- System Health table ready

Update if needed to reflect:
- Pending Actions: 3 (from test files)
- Files Monitored: 3
- File Watcher status: 🟢 Running

VALIDATION:
Show me:
1. List of created action items (with categories)
2. Content of activity log (JSON)
3. HITL skill file preview
4. Sample approval request content
5. Updated dashboard Quick Stats

Then STOP and wait for approval before Session 4.

INTEGRATION QUALITY:
- All components work together seamlessly
- No manual intervention needed after drop
- Clear logging throughout
- Dashboard reflects real state

START NOW. Test integration and implement HITL.
```

---

## 🚀 SESSION 4 PROMPT (Validation & Polish - 1 hour)

### **COPY THIS →**

```
IMPLEMENTATION: H0 Personal AI CTO - Session 4 (Validation & Polish)

PREREQUISITES:
✅ Session 1 foundation complete
✅ Session 2 file watcher implemented
✅ Session 3 integration tested

TASK 4.1: Comprehensive Validation

RUN VALIDATION CHECKLIST:

Phase 1: Foundation
- [ ] Verify all 14 directories exist
- [ ] Check vault files have content (Dashboard >100 lines, Handbook >200 lines, Goals >150 lines)
- [ ] Validate requirements.txt format
- [ ] Test Python environment

Phase 2: File Watcher
- [ ] Import test: `from watchers.file_watcher import FileWatcher`
- [ ] Dry-run test passes
- [ ] Real mode detects files
- [ ] Action items created correctly
- [ ] Logs written properly

Phase 3: Integration
- [ ] End-to-end workflow completes
- [ ] Action items have correct format
- [ ] Activity logs valid JSON
- [ ] HITL skill documented
- [ ] Sample approval exists

Phase 4: Documentation
- [ ] README.md comprehensive
- [ ] Setup instructions clear
- [ ] Usage examples included
- [ ] Troubleshooting guide present

TASK 4.2: Create/Update Documentation

1. Comprehensive README.md
Include:
```markdown
# H0: Personal AI CTO

## Overview
Autonomous AI system managing 4 concurrent hackathons (H1-H4).

## Features
- ✅ File monitoring (D:\AI-Employee-Inbox)
- ✅ Automatic action item creation
- ✅ Obsidian vault knowledge base
- ✅ HITL approval workflow
- ✅ Real-time dashboard
- ✅ Activity logging

## Installation
[Step-by-step setup]

## Usage
[How to run file watcher]
[How to process action items]
[How to approve/reject actions]

## Architecture
[Component diagram]

## Configuration
[Environment variables]
[Config file options]

## Troubleshooting
[Common issues and fixes]

## Tier Achievement
✅ Bronze Tier Complete
- File monitoring functional
- Vault structure complete
- HITL workflow ready
- Dashboard operational

## Next Steps
[Optional Silver tier features]
```

2. CHANGELOG.md
```markdown
# Changelog

## [1.0.0] - 2026-01-20

### Added
- File system watcher with category detection
- Obsidian vault with dashboard, handbook, goals
- HITL approval workflow
- Activity logging system
- Bronze tier completion

### Achieved
- ✅ Bronze Tier Requirements Met
```

TASK 4.3: Final Testing

Complete Workflow Test:
1. Delete all previous test files
2. Clear vault/Needs_Action/
3. Clear vault/Logs/
4. Drop 3 new diverse files
5. Run watcher for 1 minute
6. Verify:
   - All files detected
   - Action items created
   - Logs written
   - No errors

TASK 4.4: Git Commit

```bash
git add .
git commit -m "[H0] feat: Complete Bronze tier - file monitoring, vault, HITL workflow"
```

TASK 4.5: Token Usage Report

Calculate total token usage:
- Session 1: [X]K tokens
- Session 2: [X]K tokens
- Session 3: [X]K tokens
- Session 4: [X]K tokens
- **Total: [X]K / 50K**

TASK 4.6: Tier Assessment

Evaluate achievement:

**Bronze Tier Checklist:**
- [ ] File watcher monitors inbox ✓
- [ ] Action items created automatically ✓
- [ ] Vault structure complete ✓
- [ ] HITL workflow functional ✓
- [ ] Dashboard shows status ✓
- [ ] Documentation complete ✓

**If all checked:** ✅ BRONZE TIER ACHIEVED

**Silver Tier Analysis:**
Remaining features for Silver:
- CEO briefing generator (est. 2 hours, 8K tokens)
- Email integration (est. 3 hours, 12K tokens)

**Recommendation:**
- If tokens < 35K used: Consider adding CEO briefing
- If tokens > 35K used: Stop at Bronze, proceed to H1

FINAL REPORT:
Generate completion summary:
```
H0 IMPLEMENTATION COMPLETE 🎉

ACHIEVEMENT: [Bronze/Silver] Tier
TOTAL TIME: [X] hours
TOTAL TOKENS: [X]K / 50K
EFFICIENCY: [X]% of budget

COMPONENTS DELIVERED:
✅ File system watcher (250 lines)
✅ Obsidian vault (3 core files)
✅ HITL workflow skill
✅ Activity logging
✅ Comprehensive documentation

VALIDATION STATUS:
✅ All tests passing
✅ End-to-end workflow functional
✅ Documentation complete
✅ Git committed

NEXT STEPS:
1. Review H0 functionality
2. Generate specs for H1-H4 using Spec Generator
3. Begin H1 implementation (Course Companion)

READY FOR PRODUCTION: YES ✅
```

Show me this final report and await final approval.

START NOW. Run validation and polish.
```

---

## 📊 QUICK REFERENCE TABLE

| Session | Focus | Time | Tokens | Key Deliverable |
|---------|-------|------|--------|-----------------|
| 1 | Foundation | 1h | 5-8K | Directory + Vault Files |
| 2 | File Watcher | 1h | 8-12K | file_watcher.py working |
| 3 | Integration | 1.5h | 10-15K | End-to-end workflow |
| 4 | Validation | 1h | 7-10K | Documentation + Report |
| **Total** | **H0 Complete** | **4-6h** | **30-45K** | **Bronze Tier ✅** |

---

## 🎯 SUCCESS CRITERIA QUICK CHECK

After each session, verify:
- **Session 1:** Can navigate directory tree, read vault files
- **Session 2:** Can run `python watchers/file_watcher.py --help`
- **Session 3:** Drop file → See action item created
- **Session 4:** All validation tests pass

If any fail, debug immediately before continuing.

---

**END OF READY-TO-USE PROMPTS**

_These prompts are optimized for Claude Code execution. Copy-paste exactly as shown._
