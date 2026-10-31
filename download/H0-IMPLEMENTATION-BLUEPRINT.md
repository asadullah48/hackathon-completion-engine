# H0 IMPLEMENTATION BLUEPRINT
**Personal AI CTO - Complete Implementation Guide**

**Version:** 1.0.0  
**Created:** 2026-01-19  
**For Execution:** 2026-01-20 (After 3am rate limit reset)  
**Estimated Time:** 4-6 hours  
**Claude Code Ready:** ✅

---

## 🎯 EXECUTIVE SUMMARY

**What We're Building:**
An autonomous AI CTO system that manages 4 concurrent hackathons (H1-H4) with human oversight.

**Core Components:**
1. **Obsidian Vault** - Knowledge base and dashboard
2. **File Watcher** - Monitors D:\AI-Employee-Inbox
3. **HITL Workflow** - Human approval for critical decisions
4. **Progress Tracker** - Dashboard for all 5 hackathons
5. **CEO Briefing** - Monday morning insights (stretch goal)

**Success Criteria:**
- ✅ Bronze tier minimum (basic monitoring + vault + HITL)
- 🎯 Silver tier stretch (add email integration + CEO briefing)
- ⏱️ Complete in single day
- 💰 Token usage < 50K

---

## 📁 COMPLETE DIRECTORY STRUCTURE

```
D:\Personal-AI-Employee\hackathons\h0-personal-ai-cto\
│
├── README.md                           # Quick start guide
├── CONSTITUTION-H0.md                  # H0-specific rules
├── requirements.txt                    # Python dependencies
├── .env.example                        # Environment template
├── .gitignore                          # Git ignore rules
│
├── vault/                              # Obsidian vault (core knowledge base)
│   ├── Dashboard.md                    # Real-time system status
│   ├── Handbook.md                     # AI behavior rules
│   ├── Business_Goals.md               # Hackathon objectives
│   │
│   ├── Inbox/                          # New items needing action
│   ├── Needs_Action/                   # Requires human decision
│   ├── Pending_Approval/               # Awaiting HITL approval
│   ├── Approved/                       # Approved actions
│   ├── Rejected/                       # Rejected actions
│   ├── Done/                           # Completed items
│   │
│   ├── Hackathons/                     # Hackathon tracking
│   │   ├── H0-Personal-AI-CTO.md
│   │   ├── H1-Course-Companion.md
│   │   ├── H2-Todo-Spec.md
│   │   ├── H3-Advanced-Todo.md
│   │   └── H4-Cloud-Deployment.md
│   │
│   ├── Logs/                           # Activity logs
│   │   └── [YYYY-MM-DD].json          # Daily activity log
│   │
│   └── Briefings/                      # CEO briefings
│       └── [YYYY-MM-DD]-briefing.md   # Weekly briefing
│
├── watchers/                           # Perception layer
│   ├── base_watcher.py                # Abstract base class
│   ├── file_watcher.py                # File system monitor
│   └── gmail_watcher.py               # Email monitor (optional)
│
├── skills/                             # H0-specific skills
│   ├── hitl-approval-manager.md       # HITL workflow skill
│   ├── dashboard-updater.md           # Dashboard management
│   └── ceo-briefing-generator.md      # Briefing creation
│
├── config/                             # Configuration
│   ├── config.yaml                    # Main configuration
│   └── credentials/                   # API credentials (gitignored)
│       └── .gitkeep
│
└── tests/                              # Validation tests
    ├── test_file_watcher.py
    ├── test_vault_integration.py
    └── test_hitl_workflow.py
```

---

## 🏗️ COMPONENT SPECIFICATIONS

### Component 1: Obsidian Vault

**Purpose:** Central knowledge base for all hackathon data

**Files to Create:**

#### Dashboard.md
```markdown
# 🎯 Personal AI CTO - Dashboard

**Last Updated:** {{TIMESTAMP}}  
**Status:** 🟢 Active

---

## 📊 Quick Stats

| Metric | Value | Status |
|--------|-------|--------|
| Active Hackathons | 5 | 🟢 On Track |
| Pending Actions | 0 | ✅ Clear |
| Pending Approvals | 0 | ✅ Clear |
| Files Monitored | 0 | 🟢 Active |
| Total Progress | 15% | 🟡 Early Stage |

---

## 🎯 Hackathon Status

| ID | Hackathon | Progress | Status | Target Date |
|----|-----------|----------|--------|-------------|
| H0 | Personal AI CTO | 50% | 🟡 In Progress | Jan 20, 2026 |
| H1 | Course Companion | 0% | ⚪ Not Started | Jan 28, 2026 |
| H2 | Todo Spec-Driven | 0% | ⚪ Not Started | Jan 31, 2026 |
| H3 | Advanced Todo | 0% | ⚪ Not Started | Feb 4, 2026 |
| H4 | Cloud Deployment | 0% | ⚪ Not Started | Feb 8, 2026 |

**Overall Progress:** 10% (1 of 5 hackathons in progress)

---

## ⚡ Recent Activity

*No activity yet - watchers starting...*

---

## 🚨 Urgent Items

*No urgent items*

---

## 📅 This Week's Goals

**Week of Jan 19-25, 2026:**
- ✅ Complete Engine foundation
- 🟡 Complete H0 implementation (50% done)
- ⚪ Generate H1-H4 specs
- ⚪ Start H1 development

---

## 🔧 System Health

| Component | Status | Last Check |
|-----------|--------|------------|
| File Watcher | 🟢 Running | {{TIMESTAMP}} |
| Gmail Watcher | ⚪ Not Configured | N/A |
| Dashboard | 🟢 Active | {{TIMESTAMP}} |
| HITL System | 🟢 Ready | {{TIMESTAMP}} |

---

## 💡 AI Assistant Notes

*System initialized. Monitoring active. Awaiting first tasks...*

---

_This dashboard updates automatically as the AI CTO processes tasks._
```

#### Handbook.md
```markdown
# 🤖 Personal AI CTO - Operational Handbook

**Version:** 1.0.0  
**Last Updated:** {{DATE}}

---

## 🎯 Mission

Autonomously manage 4 concurrent hackathons (H1-H4) while building H0 as the management system itself.

---

## 📐 Core Principles

### Principle 1: Human-in-the-Loop for Critical Decisions

**Rule:** NEVER execute high-impact actions without human approval.

**High-Impact Actions:**
- Creating/deleting hackathon projects
- Deploying to production
- Modifying specifications
- Spending money
- External communications

**Low-Impact Actions (Auto-Execute):**
- Organizing files in vault
- Updating dashboard
- Logging activities
- Creating action items for review

### Principle 2: Spec-Driven Everything

**Rule:** No code without a spec first.

**Process:**
1. Detect need for new feature
2. Create specification in `specs/`
3. Request human approval
4. Claude Code implements from spec
5. Validate and deploy

### Principle 3: Transparent Operations

**Rule:** Log everything, hide nothing.

**Logging Requirements:**
- All file detections logged
- All decisions documented
- All approvals recorded
- Daily JSON activity log

---

## 🚦 Decision Framework

### Auto-Execute (No Approval Needed)
- Organizing files into correct folders
- Creating action items in Needs_Action/
- Updating dashboard metrics
- Logging activities
- Reading emails/files

### Request Approval (HITL Required)
- Creating new hackathon specs
- Deploying applications
- Modifying existing code
- Sending external communications
- Spending resources (time/money)

### Escalate Immediately
- Security issues detected
- Data loss risk
- Deadline risk
- Resource constraint risk

---

## 📧 Email Management (Future)

**Not implemented in Bronze tier.**

When implemented:
- Check Gmail every 15 minutes
- Categorize: Urgent, Important, FYI, Spam
- Create action items for Urgent/Important
- Auto-archive FYI emails after 7 days

---

## 📁 File Management

**Active Now:**

**Monitored Location:** `D:\AI-Employee-Inbox`

**Check Interval:** 10 seconds

**Process:**
1. New file detected
2. Categorize by type (document, code, data, etc.)
3. Create action item in `vault/Needs_Action/`
4. Log activity
5. Wait for human to process action item

**File Categories:**
- **Document:** .pdf, .docx, .txt, .md
- **Code:** .py, .js, .ts, .tsx, .json
- **Data:** .csv, .xlsx, .json, .sql
- **Image:** .png, .jpg, .gif, .svg
- **Video:** .mp4, .mov, .avi
- **Other:** Everything else

---

## ✅ Approval Workflow

**Location:** `vault/Pending_Approval/`

**Format:**
```markdown
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
```

---

## 📊 Dashboard Updates

**Frequency:** Real-time (after each action)

**What Gets Updated:**
- Quick Stats (pending actions, approvals)
- Recent Activity (last 10 actions)
- Urgent Items (high-priority tasks)
- System Health (component status)

**Update Trigger:**
- File detected → Update Quick Stats
- Action completed → Update Recent Activity
- Approval needed → Update Urgent Items
- Component status change → Update System Health

---

## 🎯 Hackathon Tracking

**Per Hackathon File:** `vault/Hackathons/H{N}-{Name}.md`

**Contents:**
- Current status and progress
- Key milestones and dates
- Blockers and risks
- Recent updates
- Next actions

**Update Frequency:** Daily or on significant events

---

## 📅 Monday CEO Briefing (Stretch Goal)

**Generation:** Every Monday 9 AM

**Location:** `vault/Briefings/[DATE]-briefing.md`

**Contents:**
1. Executive Summary (3-5 bullets)
2. Progress by Hackathon
3. Wins and Achievements
4. Challenges and Blockers
5. Week Ahead Preview
6. Strategic Recommendations

---

## 🔒 Security Rules

**Credentials:**
- Never log passwords or API keys
- Store in .env file (gitignored)
- Use environment variables

**Data Privacy:**
- No user data in logs
- Sanitize sensitive info in action items
- Respect file permissions

**Access Control:**
- Read-only access to email (initially)
- No delete operations without approval
- Audit trail for all actions

---

## 🚨 Error Handling

**When Something Fails:**
1. Log the error with full details
2. Create action item in Needs_Action/
3. Update dashboard with error status
4. Continue monitoring (don't crash)
5. Retry with exponential backoff (max 3 attempts)

**Graceful Degradation:**
- If Gmail fails → Continue file monitoring
- If vault unavailable → Log to temp file
- If approval system down → Queue for later

---

## 📈 Success Metrics

**Bronze Tier:**
- File watcher operational ✓
- Vault structure complete ✓
- HITL workflow functional ✓
- Dashboard updating ✓

**Silver Tier (Stretch):**
- Email integration working
- CEO briefing generated weekly
- Multi-hackathon tracking active

**Gold Tier (Future):**
- Full automation for low-risk tasks
- Proactive recommendations
- Business intelligence insights

---

_This handbook guides all AI CTO operations. When in doubt, ask for human guidance._
```

#### Business_Goals.md
```markdown
# 🎯 Personal AI CTO - Business Goals

**Period:** January - February 2026  
**Mission:** Complete all 5 Panaversity hackathons systematically

---

## 🏆 Primary Objectives

### Objective 1: Complete All 5 Hackathons
**Target:** February 8, 2026  
**Status:** 🟡 In Progress

**Breakdown:**
- H0: Personal AI CTO → Jan 20 ✓ (Target)
- H1: Course Companion → Jan 28
- H2: Todo Spec-Driven → Jan 31
- H3: Advanced Todo → Feb 4
- H4: Cloud Deployment → Feb 8

**Success Metric:** All 5 hackathons scoring Gold tier minimum

### Objective 2: Demonstrate Business Readiness
**Target:** Ongoing  
**Status:** 🟡 Building Evidence

**Proof Points:**
- ✅ Built meta-system (engine) for systematic approach
- 🟡 Completing defined problems (hackathons)
- ⏳ Documenting undefined → defined transformation
- ⏳ Showing leadership thinking (CTO vs Employee)

**Success Metric:** Invitation to join business product teams

### Objective 3: Maintain Quality Standards
**Target:** All deliverables  
**Status:** 🟢 On Track

**Standards:**
- Spec-driven development for all features
- 80%+ code coverage
- Complete documentation
- Production-ready deployments

**Success Metric:** Zero critical bugs, positive peer reviews

---

## 📊 Key Performance Indicators

### Execution KPIs

| KPI | Target | Current | Status |
|-----|--------|---------|--------|
| Hackathons Complete | 5 | 0.5 | 🟡 10% |
| Gold Tier Achievements | 5 | 0 | 🟡 Early |
| Avg Time per Hackathon | <7 days | TBD | ⏳ Measuring |
| Token Usage Efficiency | <250K total | 50K | 🟢 20% |
| Code Reusability | >60% | TBD | ⏳ Measuring |

### Quality KPIs

| KPI | Target | Current | Status |
|-----|--------|---------|--------|
| Test Coverage | >80% | 0% | 🟡 H0 pending |
| Documentation Complete | 100% | 70% | 🟢 Good |
| Security Vulnerabilities | 0 critical | 0 | 🟢 Clean |
| Deployment Success Rate | >95% | N/A | ⏳ Not started |

---

## 🎯 Weekly Goals

### Week 1: Jan 19-25, 2026

**Primary Focus:** Engine + H0

- [x] Create project constitution
- [x] Build spec generator
- [x] Generate H0 specification
- [ ] Complete H0 implementation
- [ ] Test H0 end-to-end
- [ ] Generate specs for H1-H4

**Success:** H0 complete and operational

### Week 2: Jan 26-Feb 1, 2026

**Primary Focus:** H1 + H2

- [ ] Implement H1 (Course Companion)
- [ ] Deploy H1 to Railway/Vercel
- [ ] Implement H2 (Todo Spec-Driven)
- [ ] Deploy H2 to Vercel
- [ ] Document learnings

**Success:** 2 more hackathons complete (60% total progress)

### Week 3: Feb 2-8, 2026

**Primary Focus:** H3 + H4 + Portfolio

- [ ] Implement H3 (Advanced Todo)
- [ ] Deploy H3 (Kubernetes + Cloud)
- [ ] Implement H4 (Multi-cloud Deployment)
- [ ] Create portfolio/completion report
- [ ] Submit all hackathons

**Success:** All 5 hackathons complete, business readiness demonstrated

---

## 💰 Resource Budget

### Time Budget

**Total Available:** 21 days (3 weeks)

**Allocation:**
- Engine development: 1 day ✅
- H0: 1 day (today)
- H1: 2 days
- H2: 2 days
- H3: 2 days
- H4: 2 days
- Buffer/Polish: 2 days

**Efficiency Target:** Complete 1-2 days early

### Token Budget

**Total Available:** 300K tokens (estimated)

**Allocation:**
- Engine: 50K ✅ (actual: ~45K)
- H0: 50K (today)
- H1: 40K (reuse engine)
- H2: 35K (reuse patterns)
- H3: 35K (reuse patterns)
- H4: 30K (reuse patterns)
- Buffer: 60K

**Efficiency Target:** Stay under 250K total

---

## 🚀 Strategic Initiatives

### Initiative 1: Skill Reusability

**Goal:** Leverage 39+ existing Agent Skills across all hackathons

**Approach:**
- Map skills to hackathon requirements
- Identify gaps early
- Create minimal new skills only when necessary
- Document skill usage patterns

**Success Metric:** 60%+ skill reuse across H1-H4

### Initiative 2: Framework Thinking

**Goal:** Build reusable patterns, not one-off solutions

**Approach:**
- Template-based project generation
- Standardized directory structures
- Common configuration patterns
- Shared deployment scripts

**Success Metric:** H4 completes in <2 days due to reuse

### Initiative 3: Documentation Excellence

**Goal:** Every project fully documented for business review

**Approach:**
- Comprehensive READMEs
- Architecture decision records
- Deployment guides
- Lessons learned logs

**Success Metric:** Any teammate can understand and deploy projects

---

## 📈 Progress Tracking

**Method:** This AI CTO system tracks itself!

**Daily:**
- Dashboard updates with current status
- Activity logs record all actions
- Metrics calculated automatically

**Weekly:**
- Monday CEO Briefing summarizes progress
- KPIs reviewed and updated
- Next week's goals set

**Milestone:**
- After each hackathon completion
- Lessons learned documented
- Celebrate wins! 🎉

---

## 🎓 Learning Objectives

**Beyond Just Completing Hackathons:**

1. **Master Spec-Driven Development**
   - Undefined → defined problem transformation
   - Systematic requirement gathering
   - Validation-first development

2. **Build Production Mindset**
   - Quality over speed
   - Documentation as code
   - Security by design
   - Monitoring and observability

3. **Demonstrate Leadership**
   - Strategic thinking
   - Resource optimization
   - Risk management
   - Team readiness

**Success:** Not just completion, but demonstrating business-ready capabilities

---

_These goals guide the AI CTO's autonomous operations and provide clear success criteria._
```

---

## Component 2: File Watcher

**File:** `watchers/file_watcher.py`

**Responsibilities:**
- Monitor `D:\AI-Employee-Inbox` for new files
- Categorize files by type
- Create action items in `vault/Needs_Action/`
- Log all activities

**Implementation:**
```python
"""
File System Watcher for Personal AI CTO
Monitors D:\AI-Employee-Inbox for new files
"""

import os
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import hashlib


class FileWatcher:
    """Monitors file system for new files and creates action items."""
    
    SUPPORTED_CATEGORIES = {
        'document': ['.pdf', '.docx', '.doc', '.txt', '.md', '.rtf'],
        'code': ['.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.cpp', '.c', '.h'],
        'data': ['.csv', '.xlsx', '.xls', '.json', '.xml', '.sql', '.db'],
        'image': ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp'],
        'video': ['.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv'],
        'archive': ['.zip', '.rar', '.7z', '.tar', '.gz'],
        'other': []
    }
    
    def __init__(
        self,
        drop_folder: Path,
        vault_path: Path,
        check_interval: int = 10,
        dry_run: bool = False
    ):
        """
        Initialize File Watcher
        
        Args:
            drop_folder: Path to monitor for new files
            vault_path: Path to Obsidian vault
            check_interval: Seconds between checks
            dry_run: If True, log actions without executing
        """
        self.drop_folder = Path(drop_folder)
        self.vault_path = Path(vault_path)
        self.check_interval = check_interval
        self.dry_run = dry_run
        
        # Directories
        self.needs_action = vault_path / 'Needs_Action'
        self.logs_dir = vault_path / 'Logs'
        
        # State tracking
        self.processed_files = set()
        self.state_file = vault_path / '.file_watcher_state.json'
        
        # Create directories
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Load previous state
        self._load_state()
    
    def _load_state(self) -> None:
        """Load previously processed files from state file."""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                self.processed_files = set(state.get('processed_files', []))
    
    def _save_state(self) -> None:
        """Save processed files to state file."""
        with open(self.state_file, 'w') as f:
            json.dump({
                'processed_files': list(self.processed_files),
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)
    
    def _categorize_file(self, filepath: Path) -> str:
        """
        Categorize file by extension
        
        Args:
            filepath: Path to file
            
        Returns:
            Category name
        """
        ext = filepath.suffix.lower()
        
        for category, extensions in self.SUPPORTED_CATEGORIES.items():
            if ext in extensions:
                return category
        
        return 'other'
    
    def _create_action_item(self, filepath: Path) -> Optional[Path]:
        """
        Create action item in Needs_Action folder
        
        Args:
            filepath: Path to detected file
            
        Returns:
            Path to created action item, or None if dry run
        """
        category = self._categorize_file(filepath)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        action_filename = f'FILE_{timestamp}_{filepath.stem}.md'
        action_path = self.needs_action / action_filename
        
        # Get file info
        stats = filepath.stat()
        file_size = stats.st_size
        created_time = datetime.fromtimestamp(stats.st_ctime)
        
        # Create action item content
        content = f"""# FILE DETECTED: {filepath.name}

**Detected:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Category:** {category}  
**Priority:** Medium

---

## File Information

- **Name:** {filepath.name}
- **Size:** {file_size:,} bytes ({file_size / 1024:.2f} KB)
- **Type:** {filepath.suffix}
- **Location:** `{filepath}`
- **Created:** {created_time.strftime('%Y-%m-%d %H:%M:%S')}

---

## Suggested Actions

Based on file type **{category}**, here are suggested actions:

"""
        
        # Add category-specific suggestions
        if category == 'document':
            content += """- [ ] Review document content
- [ ] Extract key information
- [ ] File in appropriate project folder
- [ ] Update relevant hackathon notes
"""
        elif category == 'code':
            content += """- [ ] Review code for quality
- [ ] Determine which hackathon this belongs to
- [ ] Run linting/type checking
- [ ] Integrate into project
"""
        elif category == 'data':
            content += """- [ ] Validate data format
- [ ] Analyze data contents
- [ ] Determine use case
- [ ] Import into appropriate system
"""
        else:
            content += """- [ ] Review file
- [ ] Categorize properly
- [ ] File in appropriate location
- [ ] Update tracking systems
"""
        
        content += f"""
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
**Action Item Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        if self.dry_run:
            print(f"[DRY RUN] Would create: {action_path}")
            return None
        
        # Write action item
        with open(action_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return action_path
    
    def _log_activity(self, activity_type: str, details: Dict) -> None:
        """
        Log activity to daily JSON log
        
        Args:
            activity_type: Type of activity
            details: Activity details
        """
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs_dir / f'{today}.json'
        
        # Load existing log
        if log_file.exists():
            with open(log_file, 'r') as f:
                log_data = json.load(f)
        else:
            log_data = {'date': today, 'activities': []}
        
        # Add new activity
        log_data['activities'].append({
            'timestamp': datetime.now().isoformat(),
            'type': activity_type,
            'details': details
        })
        
        # Save log
        if not self.dry_run:
            with open(log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
    
    def check_for_new_files(self) -> List[Path]:
        """
        Check for new files in drop folder
        
        Returns:
            List of new file paths
        """
        if not self.drop_folder.exists():
            print(f"Drop folder does not exist: {self.drop_folder}")
            return []
        
        new_files = []
        
        for filepath in self.drop_folder.iterdir():
            if filepath.is_file():
                # Create file ID (hash of path)
                file_id = hashlib.md5(str(filepath).encode()).hexdigest()
                
                if file_id not in self.processed_files:
                    new_files.append(filepath)
                    self.processed_files.add(file_id)
        
        return new_files
    
    def run(self) -> None:
        """
        Main run loop - continuously monitors for new files
        """
        print(f"🚀 File Watcher Starting...")
        print(f"   Monitoring: {self.drop_folder}")
        print(f"   Vault: {self.vault_path}")
        print(f"   Interval: {self.check_interval}s")
        print(f"   Dry Run: {self.dry_run}")
        print()
        
        try:
            while True:
                # Check for new files
                new_files = self.check_for_new_files()
                
                if new_files:
                    print(f"📁 Found {len(new_files)} new file(s)")
                    
                    for filepath in new_files:
                        print(f"   → {filepath.name}")
                        
                        # Create action item
                        action_path = self._create_action_item(filepath)
                        
                        if action_path:
                            print(f"   ✅ Created: {action_path.name}")
                        
                        # Log activity
                        self._log_activity('file_detected', {
                            'filename': filepath.name,
                            'path': str(filepath),
                            'category': self._categorize_file(filepath),
                            'action_item': str(action_path) if action_path else None
                        })
                    
                    # Save state
                    self._save_state()
                    print()
                
                # Wait before next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\n🛑 File Watcher Stopped")
            self._save_state()


def main():
    """Main entry point for file watcher."""
    import argparse
    
    parser = argparse.ArgumentParser(description='File System Watcher for AI CTO')
    parser.add_argument(
        '--vault',
        type=str,
        default=r'D:\Personal-AI-Employee\hackathons\h0-personal-ai-cto\vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--drop-folder',
        type=str,
        default=r'D:\AI-Employee-Inbox',
        help='Path to monitored drop folder'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=10,
        help='Check interval in seconds'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run mode (log only, no changes)'
    )
    
    args = parser.parse_args()
    
    watcher = FileWatcher(
        drop_folder=Path(args.drop_folder),
        vault_path=Path(args.vault),
        check_interval=args.interval,
        dry_run=args.dry_run
    )
    
    watcher.run()


if __name__ == '__main__':
    main()
```

---

## Component 3: HITL Workflow

**Location:** `skills/hitl-approval-manager.md`

**Content:**
```markdown
# HITL Approval Manager Skill

**Purpose:** Manage Human-in-the-Loop approval workflow for critical AI CTO decisions

**When to use:** When the AI needs human approval before executing actions

---

## Core Workflow

### Step 1: Create Approval Request

**Location:** `vault/Pending_Approval/APPROVAL_{timestamp}_{action}.md`

**Template:**
````markdown
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
````

### Step 2: Monitor for Decision

**Check:** Every 30 seconds

**Look For:**
- Checkbox marked (APPROVE/REJECT/MODIFY)
- Feedback provided

### Step 3: Execute Based on Decision

**If APPROVED:**
1. Move file to `Approved/`
2. Execute the action
3. Log result
4. Update dashboard

**If REJECTED:**
1. Move file to `Rejected/`
2. Log rejection
3. Update dashboard
4. Do NOT execute action

**If MODIFIED:**
1. Read feedback
2. Adjust proposal
3. Create new approval request
4. Repeat workflow

---

## Usage Examples

### Example 1: Deploy Hackathon

````markdown
# APPROVAL REQUEST: Deploy H1 to Production

**Created:** 2026-01-28 14:30:00  
**Priority:** High  
**Estimated Impact:** H1 will be publicly accessible

## Proposed Action
Deploy Course Companion FTE (H1) to Railway production environment

## Rationale
- All tests passing (100% coverage)
- Spec requirements met
- Ready for submission

## Risks
- Potential production bugs
- Railway usage costs
- Public exposure

## Alternatives Considered
1. Deploy to staging first (slower)
2. Wait for more testing (delays submission)

---

**Human Decision:**
- [x] ✅ APPROVE - Proceed with action
- [ ] ❌ REJECT - Do not proceed
- [ ] 🔄 MODIFY - Adjust and resubmit

**Feedback:**
Looks good! Deploy to production.
````

### Example 2: Create New Spec

````markdown
# APPROVAL REQUEST: Generate H3 Specification

**Created:** 2026-02-01 10:00:00  
**Priority:** Medium  
**Estimated Impact:** New spec for Advanced Todo hackathon

## Proposed Action
Use Spec Generator to create SPEC-H3-ADVANCED-TODO.md

## Rationale
- H2 completed successfully
- Ready to start H3
- Spec needed for implementation

## Risks
- May miss requirements
- Token usage (~8K tokens)

## Alternatives Considered
1. Manual spec writing (slower, less consistent)
2. Reuse H2 spec (inappropriate, different requirements)

---

**Human Decision:**
- [x] ✅ APPROVE - Proceed with action
- [ ] ❌ REJECT - Do not proceed
- [ ] 🔄 MODIFY - Adjust and resubmit

**Feedback:**
Approved. Generate the spec.
````

---

## Implementation Notes

**File Naming:**
`APPROVAL_{YYYYMMDD}_{HHMMSS}_{action_type}.md`

**Priority Levels:**
- **High:** Production deployments, external communications, spending money
- **Medium:** Creating specs, modifying code, data operations
- **Low:** Documentation updates, dashboard changes

**Response Time Expectations:**
- High priority: Review within 1 hour
- Medium priority: Review within 4 hours
- Low priority: Review within 24 hours

---

_This workflow ensures human oversight while maintaining AI autonomy for routine tasks._
```

---

## ⏱️ ESTIMATED TIMINGS (Tomorrow's Execution)

**Session 1: Foundation (1 hour)**
- Create directory structure (15 min)
- Generate Obsidian vault files (30 min)
- Initialize configuration (15 min)

**Session 2: File Watcher (1 hour)**
- Implement file_watcher.py (45 min)
- Test with sample files (15 min)

**Session 3: Integration (1 hour)**
- Connect watcher → vault (20 min)
- Implement HITL workflow (30 min)
- End-to-end testing (10 min)

**Session 4: Polish & Validation (1 hour)**
- Documentation (20 min)
- Final testing (20 min)
- Deployment preparation (20 min)

**Total: 4 hours** (Buffer: 2 hours for issues)

---

## ✅ VALIDATION CHECKLIST

### Phase 1: Foundation
- [ ] All directories created
- [ ] Vault files generated (Dashboard, Handbook, Goals)
- [ ] Configuration files present
- [ ] Git repository initialized

### Phase 2: File Watcher
- [ ] file_watcher.py implemented
- [ ] Can detect new files in drop folder
- [ ] Creates action items correctly
- [ ] Logs activities to JSON

### Phase 3: Integration
- [ ] Watcher writes to vault/Needs_Action/
- [ ] Dashboard updates automatically
- [ ] HITL workflow functional
- [ ] End-to-end flow works

### Phase 4: Quality
- [ ] Documentation complete
- [ ] All tests pass
- [ ] No critical bugs
- [ ] Ready for Bronze tier submission

---

**END OF BLUEPRINT**

_This blueprint contains everything Claude Code needs to implement H0 tomorrow._
