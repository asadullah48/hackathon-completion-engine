# Dashboard Updater Skill

**Purpose:** Automatically update the dashboard with current system status

**When to use:** When system status changes, metrics update, or new information is available

---

## Core Functionality

### Update Dashboard Elements

**Dashboard File:** `vault/Dashboard.md`

**Elements Updated:**
1. **Quick Stats** - Current metrics and counts
2. **Hackathon Status** - Progress of all 5 hackathons
3. **Recent Activity** - Latest 10 system activities
4. **Urgent Items** - High-priority tasks requiring attention
5. **System Health** - Status of all components
6. **AI Assistant Notes** - Current system state

### Update Triggers

**Automatic Updates:**
- File detection → Update Quick Stats
- Action completed → Update Recent Activity
- Approval needed → Update Urgent Items
- Component status change → Update System Health
- Daily schedule → Update all metrics

**Manual Updates:**
- Periodic refresh (every 5 minutes)
- System events (start/stop, errors, warnings)

---

## Implementation Approach

### 1. Read Current Dashboard
```python
def read_current_dashboard(dashboard_path: str) -> str:
    """Read the current dashboard content."""
    with open(dashboard_path, 'r') as f:
        return f.read()
```

### 2. Extract Sections
```python
def extract_section(content: str, section_header: str) -> tuple:
    """Extract a section from markdown content."""
    # Find section boundaries and return content
    pass
```

### 3. Update Metrics
```python
def calculate_metrics() -> dict:
    """Calculate current system metrics."""
    # Calculate all metrics needed for dashboard
    return {
        'active_hackathons': 5,
        'pending_actions': count_pending_actions(),
        'pending_approvals': count_pending_approvals(),
        'files_monitored': count_monitored_files(),
        'total_progress': calculate_total_progress()
    }
```

### 4. Update Dashboard
```python
def update_dashboard(dashboard_path: str, new_metrics: dict):
    """Update dashboard with new metrics."""
    # Update the dashboard file with new values
    pass
```

---

## Section Templates

### Quick Stats Section
```markdown
## 📊 Quick Stats

| Metric | Value | Status |
|--------|-------|--------|
| Active Hackathons | {active_hackathons} | {hackathons_status} |
| Pending Actions | {pending_actions} | {actions_status} |
| Pending Approvals | {pending_approvals} | {approvals_status} |
| Files Monitored | {files_monitored} | {files_status} |
| Total Progress | {total_progress}% | {progress_status} |
```

### Hackathon Status Section
```markdown
## 🎯 Hackathon Status

| ID | Hackathon | Progress | Status | Target Date |
|----|-----------|----------|--------|-------------|
| H0 | Personal AI CTO | {h0_progress}% | {h0_status} | {h0_target_date} |
| H1 | Course Companion | {h1_progress}% | {h1_status} | {h1_target_date} |
| H2 | Todo Spec-Driven | {h2_progress}% | {h2_status} | {h2_target_date} |
| H3 | Advanced Todo | {h3_progress}% | {h3_status} | {h3_target_date} |
| H4 | Cloud Deployment | {h4_progress}% | {h4_status} | {h4_target_date} |
```

### Recent Activity Section
```markdown
## ⚡ Recent Activity

{recent_activities}
```

### System Health Section
```markdown
## 🔧 System Health

| Component | Status | Last Check |
|-----------|--------|------------|
| File Watcher | {file_watcher_status} | {file_watcher_last_check} |
| Gmail Watcher | {gmail_watcher_status} | {gmail_watcher_last_check} |
| Dashboard | {dashboard_status} | {dashboard_last_check} |
| HITL System | {hitl_status} | {hitl_last_check} |
```

---

## Best Practices

### 1. Preserve Manual Content
- Only update templated sections
- Leave custom content untouched
- Backup before major updates

### 2. Timestamp Consistency
- Use consistent timestamp format: `YYYY-MM-DD HH:MM:SS`
- Update "Last Updated" field with each change
- Include timestamps in all activity logs

### 3. Status Indicators
- Use consistent emoji indicators:
  - 🟢 Running/Active/Good
  - 🟡 Warning/In Progress
  - 🔴 Error/Stopped
  - ⚪ Not Configured
  - ✅ Complete
  - ❌ Failed

### 4. Error Handling
- Handle file read/write errors gracefully
- Log dashboard update failures
- Fallback to backup if primary dashboard corrupt

---

## Integration Points

### With File Watcher
- Update when new files detected
- Increment file counter
- Add to recent activity

### With HITL System
- Update when approval requested
- Update when approval received
- Modify urgent items section

### With Activity Logger
- Pull recent activities for dashboard
- Show last 10 activities
- Highlight important events

---

_This skill enables automatic dashboard maintenance for the AI CTO system._