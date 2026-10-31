# CEO Briefing Generator Skill

**Purpose:** Generate weekly CEO briefings with progress summary and insights

**When to use:** Every Monday morning or on demand for executive reporting

---

## Core Functionality

### Briefing Structure

**File Location:** `vault/Briefings/[YYYY-MM-DD]-briefing.md`

**Standard Format:**
```markdown
# 📊 Monday CEO Briefing - [Date]

**Prepared:** [Current Date and Time]
**Reporting Period:** [Previous Week Dates]
**Prepared By:** Personal AI CTO

---

## 🎯 Executive Summary

[3-5 bullet points highlighting key achievements, challenges, and upcoming priorities]

---

## 📈 Progress by Hackathon

### H0: Personal AI CTO
- **Status:** [Current status and percentage]
- **Achievements:** [Key accomplishments from the week]
- **Blockers:** [Any challenges or impediments]
- **Next Steps:** [Planned activities for next week]

### H1: Course Companion
- **Status:** [Current status and percentage]
- **Achievements:** [Key accomplishments from the week]
- **Blockers:** [Any challenges or impediments]
- **Next Steps:** [Planned activities for next week]

### H2: Todo Spec-Driven
- **Status:** [Current status and percentage]
- **Achievements:** [Key accomplishments from the week]
- **Blockers:** [Any challenges or impediments]
- **Next Steps:** [Planned activities for next week]

### H3: Advanced Todo
- **Status:** [Current status and percentage]
- **Achievements:** [Key accomplishments from the week]
- **Blockers:** [Any challenges or impediments]
- **Next Steps:** [Planned activities for next week]

### H4: Cloud Deployment
- **Status:** [Current status and percentage]
- **Achievements:** [Key accomplishments from the week]
- **Blockers:** [Any challenges or impediments]
- **Next Steps:** [Planned activities for next week]

---

## 🏆 This Week's Wins

[Highlight significant achievements, milestones reached, or positive developments]

---

## ⚠️ Challenges & Blockers

[Detail any challenges faced, blockers encountered, or risks identified]

---

## 📅 Next Week Preview

[Outline planned activities, milestones, and priorities for the coming week]

---

## 💡 Strategic Recommendations

[Suggestions for improving efficiency, addressing challenges, or capitalizing on opportunities]

---

**Report Generated:** [Timestamp]
**Next Report:** [Next Monday Date]
```

---

## Data Sources

### 1. Dashboard Metrics
- Extract current progress percentages
- Pull status indicators
- Gather completion dates

### 2. Activity Logs
- Analyze recent activities
- Identify trends and patterns
- Highlight significant events

### 3. Hackathon Tracking Files
- Read individual hackathon status files
- Extract achievements and blockers
- Note milestone completions

### 4. System Health Reports
- Include component status
- Report on system performance
- Note any technical issues

---

## Generation Process

### Step 1: Data Collection
```python
def collect_weekly_data(start_date: datetime, end_date: datetime) -> dict:
    """Collect all relevant data for the briefing period."""
    data = {}
    
    # Collect dashboard metrics
    data['dashboard'] = get_dashboard_metrics()
    
    # Collect activity logs
    data['activities'] = get_activities_in_period(start_date, end_date)
    
    # Collect hackathon statuses
    data['hackathons'] = get_all_hackathon_statuses()
    
    # Collect system health
    data['health'] = get_system_health()
    
    return data
```

### Step 2: Analysis
```python
def analyze_data(data: dict) -> dict:
    """Analyze collected data to identify trends and highlights."""
    analysis = {}
    
    # Identify wins and achievements
    analysis['wins'] = identify_wins(data['activities'])
    
    # Identify challenges and blockers
    analysis['challenges'] = identify_challenges(data['activities'])
    
    # Identify trends
    analysis['trends'] = identify_trends(data)
    
    # Generate recommendations
    analysis['recommendations'] = generate_recommendations(analysis)
    
    return analysis
```

### Step 3: Report Generation
```python
def generate_briefing(data: dict, analysis: dict) -> str:
    """Generate the complete briefing document."""
    # Format the briefing using templates and collected data
    pass
```

### Step 4: Storage
```python
def save_briefing(briefing_content: str, date: datetime):
    """Save the briefing to the appropriate location."""
    filename = f"{date.strftime('%Y-%m-%d')}-briefing.md"
    filepath = Path("vault/Briefings") / filename
    
    with open(filepath, 'w') as f:
        f.write(briefing_content)
```

---

## Automation Schedule

### Weekly Generation
- **Day:** Every Monday
- **Time:** 9:00 AM
- **Trigger:** Automated scheduler
- **Fallback:** Manual generation option

### On-Demand Generation
- **Trigger:** Manual command
- **Use Case:** Executive request or special circumstances
- **Parameters:** Custom date range

---

## Quality Standards

### Executive Summary
- Maximum 5 bullet points
- Focus on outcomes, not activities
- Quantify achievements where possible
- Highlight risks and opportunities

### Progress Reporting
- Accurate percentage completion
- Clear status indicators
- Specific dates and milestones
- Actionable next steps

### Recommendations
- Specific and actionable
- Prioritized by impact
- Feasible within current constraints
- Aligned with business objectives

---

## Integration Points

### With Dashboard Updater
- Pull current metrics
- Ensure consistency in reporting
- Share data collection methods

### With Activity Logger
- Access historical data
- Identify patterns and trends
- Validate reported achievements

### With Hackathon Tracking
- Access detailed status updates
- Correlate with individual reports
- Maintain consistency across reports

---

## Error Handling

### Data Unavailability
- Graceful degradation when data missing
- Clear indication of incomplete information
- Fallback to previous period data if needed

### Generation Failures
- Log generation errors
- Attempt simplified report generation
- Notify system administrator

### File System Issues
- Handle disk space limitations
- Manage file write permissions
- Create backup reports if primary fails

---

_This skill enables automated executive reporting for the AI CTO system._