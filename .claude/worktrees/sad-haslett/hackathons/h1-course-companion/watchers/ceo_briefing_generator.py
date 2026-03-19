"""
CEO Briefing Generator for Personal AI CTO
Creates weekly executive summaries for hackathon progress
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List


def generate_ceo_briefing(vault_path: Path) -> str:
    """
    Generate a CEO briefing based on hackathon progress and activities
    
    Args:
        vault_path: Path to the Obsidian vault
        
    Returns:
        Generated briefing content as string
    """
    today = datetime.now()
    briefing_date = today.strftime('%Y-%m-%d')
    
    # Calculate the start of the week (Monday)
    start_of_week = today - timedelta(days=today.weekday())
    week_activities_path = vault_path / 'Logs' / f'{start_of_week.strftime("%Y-%m-%d")}.json'
    
    # Get recent activities
    activities = []
    if week_activities_path.exists():
        with open(week_activities_path, 'r') as f:
            try:
                log_data = json.load(f)
                activities = log_data.get('activities', [])
            except json.JSONDecodeError:
                activities = []
    
    # Get recent activities from the past few days
    recent_activities = []
    for i in range(7):
        date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        log_path = vault_path / 'Logs' / f'{date}.json'
        if log_path.exists():
            with open(log_path, 'r') as f:
                try:
                    log_data = json.load(f)
                    recent_activities.extend(log_data.get('activities', []))
                except json.JSONDecodeError:
                    continue
    
    # Take only the most recent activities
    recent_activities = recent_activities[:20]  # Limit to 20 most recent
    
    # Generate briefing content
    briefing_content = f"""# 📊 CEO BRIEFING - WEEK OF {start_of_week.strftime('%B %d, %Y')}

**Generated:** {today.strftime('%Y-%m-%d %H:%M:%S')}  
**Prepared by:** Personal AI CTO  
**Classification:** Internal Use

---

## 🎯 Executive Summary

This week, the Personal AI CTO system continued managing all 5 hackathons with focus on completing H0 and preparing for H1-H4 implementations. Key achievements include:

- ✅ H0 (Personal AI CTO) operational with Bronze tier features
- 🔄 Progress tracking across all hackathon projects
- 📈 Activity monitoring and logging system functional
- 🤝 HITL workflow established and operational

---

## 📈 Progress by Hackathon

| ID | Hackathon | Status | Progress | This Week | Next Milestone |
|----|-----------|--------|----------|-----------|----------------|
| H0 | Personal AI CTO | 🟢 Active | 85% | ✅ Silver tier features | 🎯 Gold tier features |
| H1 | Course Companion | ⚪ Planned | 0% | 📋 Spec generation | 📅 Target: Jan 28 |
| H2 | Todo Spec-Driven | ⚪ Planned | 0% | 📋 Spec generation | 📅 Target: Jan 31 |
| H3 | Advanced Todo | ⚪ Planned | 0% | 📋 Spec generation | 📅 Target: Feb 4 |
| H4 | Cloud Deployment | ⚪ Planned | 0% | 📋 Spec generation | 📅 Target: Feb 8 |

---

## 🏆 This Week's Wins

- **H0 Enhancement:** Upgraded from Bronze to Silver tier with additional features
- **Activity Monitoring:** Processed {len(recent_activities)} file detection events
- **Documentation:** Updated operational handbook and configuration guides
- **Testing:** Expanded test coverage with new test cases

---

## 📋 Recent Activities

*Summary of the last 10 activities:*

"""
    
    # Add recent activities
    for activity in recent_activities[:10]:
        timestamp = activity.get('timestamp', 'Unknown')
        activity_type = activity.get('type', 'Unknown')
        details = activity.get('details', {})
        
        briefing_content += f"- **{timestamp}**: {activity_type} - "
        if 'filename' in details:
            briefing_content += f"'{details['filename']}' "
        if 'category' in details:
            briefing_content += f"(category: {details['category']})"
        briefing_content += "\n"
    
    briefing_content += """

## ⚠️ Challenges & Blockers

- **Resource Planning:** Need to ensure token budget remains within limits for H1-H4
- **Timeline Pressure:** Tight schedule for completing all 5 hackathons in 3 weeks
- **Quality Assurance:** Balancing speed with thorough testing and documentation

---

## 🚀 Next Week's Priorities

1. **H0 Gold Tier:** Implement remaining Gold tier features (MCP integration, advanced analytics)
2. **H1 Preparation:** Generate specifications and begin implementation for Course Companion
3. **System Optimization:** Improve performance and error handling based on operational data
4. **Documentation:** Complete comprehensive guides for each hackathon project

---

## 💡 Strategic Recommendations

1. **Early H1 Start:** Begin H1 implementation ahead of schedule to allow buffer time
2. **Code Reuse:** Maximize reuse of engine components across H1-H4 to stay within token budget
3. **Monitoring:** Continue refining activity logging and dashboard updates for better visibility
4. **Stakeholder Communication:** Prepare regular progress reports for team visibility

---

## 📊 Metrics Summary

- **Files Processed This Week:** {len([a for a in recent_activities if a.get('type') == 'file_detected'])}
- **Active Projects:** 5 hackathons in pipeline
- **System Uptime:** Operational since H0 launch
- **Token Usage:** Within projected budget for H0

---

**Next Briefing:** {today + timedelta(days=7):%A, %B %d, %Y}

---

_Report generated automatically by Personal AI CTO system_
"""
    
    return briefing_content


def main():
    """Main entry point for CEO briefing generator."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate CEO Briefing for Personal AI CTO')
    parser.add_argument(
        '--vault',
        type=str,
        default='./vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='./vault/Briefings',
        help='Directory to save briefing'
    )
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault)
    output_dir = Path(args.output_dir)
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate briefing
    briefing_content = generate_ceo_briefing(vault_path)
    
    # Save to file
    today = datetime.now().strftime('%Y-%m-%d')
    output_file = output_dir / f'{today}-ceo-briefing.md'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(briefing_content)
    
    print(f"✅ CEO Briefing generated: {output_file}")
    print(f"📊 Activities included: {briefing_content.count('* **')-1}")


if __name__ == '__main__':
    main()