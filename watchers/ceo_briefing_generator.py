"""
CEO Briefing Generator for Personal AI Employee
Creates weekly executive summaries from real vault data: logs, folder counts, and goals.

Usage:
    python watchers/ceo_briefing_generator.py --vault ./vault
    python watchers/ceo_briefing_generator.py --vault ./vault --output-dir ./vault/Briefings
"""

import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple


def count_vault_items(vault_path: Path) -> Dict[str, int]:
    """Count real items in each vault folder, excluding .gitkeep."""
    folders = [
        "Inbox", "Needs_Action", "Pending_Approval",
        "Approved", "Rejected", "Done", "Briefings",
    ]
    counts = {}
    for folder in folders:
        folder_path = vault_path / folder
        if folder_path.exists():
            items = [f for f in folder_path.iterdir() if f.name != ".gitkeep" and f.is_file()]
            counts[folder] = len(items)
        else:
            counts[folder] = 0
    return counts


def load_week_activities(vault_path: Path, days: int = 7) -> List[Dict]:
    """Load all log activities from the past N days."""
    activities = []
    today = datetime.now()
    for i in range(days):
        date_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        log_path = vault_path / "Logs" / f"{date_str}.json"
        if log_path.exists():
            try:
                with open(log_path) as f:
                    data = json.load(f)
                    for act in data.get("activities", []):
                        act["_date"] = date_str
                        activities.append(act)
            except (json.JSONDecodeError, KeyError):
                continue
    return activities


def categorize_activities(activities: List[Dict]) -> Dict[str, List[Dict]]:
    """Group activities by type."""
    groups: Dict[str, List[Dict]] = {}
    for act in activities:
        act_type = act.get("type", "unknown")
        groups.setdefault(act_type, []).append(act)
    return groups


def identify_bottlenecks(vault_path: Path) -> List[str]:
    """Find items stuck in Needs_Action (older than 48 hours)."""
    bottlenecks = []
    needs_action = vault_path / "Needs_Action"
    if not needs_action.exists():
        return bottlenecks
    cutoff = datetime.now() - timedelta(hours=48)
    for item in needs_action.iterdir():
        if item.name == ".gitkeep" or not item.is_file():
            continue
        mtime = datetime.fromtimestamp(item.stat().st_mtime)
        if mtime < cutoff:
            bottlenecks.append(f"{item.name} (since {mtime.strftime('%Y-%m-%d')})")
    return bottlenecks


def check_watcher_health(vault_path: Path) -> List[Tuple[str, str, str]]:
    """Check watcher state files for health status."""
    watchers = []

    # File Watcher
    fw_state = vault_path / ".file_watcher_state.json"
    if fw_state.exists():
        try:
            data = json.load(open(fw_state))
            last = data.get("last_updated", "unknown")
            count = len(data.get("processed_files", []))
            watchers.append(("File Watcher", "Operational", f"{count} files processed, last: {last}"))
        except Exception:
            watchers.append(("File Watcher", "Error", "State file unreadable"))
    else:
        watchers.append(("File Watcher", "Not configured", "No state file"))

    # Gmail Watcher
    gw_state = vault_path / ".gmail_watcher_state.json"
    if gw_state.exists():
        try:
            data = json.load(open(gw_state))
            last = data.get("last_updated", "unknown")
            count = len(data.get("processed_ids", []))
            watchers.append(("Gmail Watcher", "Operational", f"{count} emails processed, last: {last}"))
        except Exception:
            watchers.append(("Gmail Watcher", "Error", "State file unreadable"))
    else:
        watchers.append(("Gmail Watcher", "Not configured", "No state file"))

    # WhatsApp Watcher
    wa_state = vault_path / ".whatsapp_watcher_state.json"
    if wa_state.exists():
        try:
            data = json.load(open(wa_state))
            last = data.get("last_updated", "unknown")
            count = len(data.get("processed_hashes", []))
            watchers.append(("WhatsApp Watcher", "Operational", f"{count} messages processed, last: {last}"))
        except Exception:
            watchers.append(("WhatsApp Watcher", "Error", "State file unreadable"))
    else:
        watchers.append(("WhatsApp Watcher", "Standby", "No messages matched keywords yet"))

    return watchers


def generate_ceo_briefing(vault_path: Path) -> str:
    """Generate a data-driven CEO briefing from real vault contents."""
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())

    # Collect real data
    counts = count_vault_items(vault_path)
    activities = load_week_activities(vault_path)
    grouped = categorize_activities(activities)
    bottlenecks = identify_bottlenecks(vault_path)
    watcher_health = check_watcher_health(vault_path)

    # Activity stats
    emails_detected = len(grouped.get("email_detected", []))
    files_detected = len(grouped.get("file_detected", []))
    whatsapp_detected = len(grouped.get("whatsapp_detected", []))
    total_activities = len(activities)

    # Build briefing
    briefing = f"""# CEO Briefing - Week of {start_of_week.strftime('%B %d, %Y')}

**Generated:** {today.strftime('%Y-%m-%d %H:%M:%S')}
**Period:** {start_of_week.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}
**Prepared by:** Personal AI Employee

---

## Executive Summary

- **{total_activities}** activities logged this week across all watchers
- **{emails_detected}** emails detected and triaged from Gmail
- **{files_detected}** files detected from inbox folder
- **{whatsapp_detected}** WhatsApp messages matched business keywords
- **{counts['Needs_Action']}** items currently awaiting action
- **{counts['Pending_Approval']}** items awaiting human approval

---

## Vault Status

| Folder | Item Count | Status |
|--------|-----------|--------|
| Inbox | {counts['Inbox']} | {'Empty - all triaged' if counts['Inbox'] == 0 else 'Items pending triage'} |
| Needs_Action | {counts['Needs_Action']} | {'Attention needed' if counts['Needs_Action'] > 5 else 'Manageable'} |
| Pending_Approval | {counts['Pending_Approval']} | {'Review needed' if counts['Pending_Approval'] > 0 else 'Clear'} |
| Approved | {counts['Approved']} | {'Ready to execute' if counts['Approved'] > 0 else 'No approved actions'} |
| Rejected | {counts['Rejected']} | {f'{counts["Rejected"]} rejected' if counts['Rejected'] > 0 else 'None'} |
| Done | {counts['Done']} | {f'{counts["Done"]} completed' if counts['Done'] > 0 else 'No completions yet'} |

---

## Recent Activities

"""

    # List recent activities (up to 15)
    for act in activities[:15]:
        ts = act.get("timestamp", "unknown")
        atype = act.get("type", "unknown")
        details = act.get("details", {})
        subject = details.get("subject", details.get("filename", ""))
        sender = details.get("from", details.get("contact", ""))
        priority = details.get("priority", "")
        if ts != "unknown":
            ts = ts.split("T")[1][:8] if "T" in ts else ts
        briefing += f"| {ts} | {atype} | {subject[:50]} | {sender} | {priority} |\n"

    if not activities:
        briefing += "*No activities logged this week.*\n"

    briefing += f"""
---

## Bottlenecks

"""
    if bottlenecks:
        for b in bottlenecks:
            briefing += f"- {b}\n"
    else:
        briefing += "*No bottlenecks identified (all items < 48 hours old).*\n"

    briefing += f"""
---

## System Health

| Component | Status | Details |
|-----------|--------|---------|
"""
    for name, status, detail in watcher_health:
        briefing += f"| {name} | {status} | {detail} |\n"

    briefing += f"""
---

## Recommendations

"""
    if counts["Pending_Approval"] > 0:
        briefing += f"1. **Review {counts['Pending_Approval']} pending approvals** in vault/Pending_Approval/\n"
    if counts["Needs_Action"] > 10:
        briefing += f"2. **Triage backlog**: {counts['Needs_Action']} items in Needs_Action need processing\n"
    if counts["Done"] == 0:
        briefing += f"3. **Complete first items**: Move processed items to Done/ to track progress\n"
    if emails_detected > 0:
        briefing += f"4. **Email review**: {emails_detected} emails detected - review for actionable items\n"

    briefing += f"""
---

**Next Briefing:** {(today + timedelta(days=7)).strftime('%A, %B %d, %Y')}

---

_Report generated from real vault data by Personal AI Employee system._
"""

    return briefing


def main():
    parser = argparse.ArgumentParser(description="Generate CEO Briefing for Personal AI Employee")
    parser.add_argument("--vault", type=str, default="./vault", help="Path to Obsidian vault")
    parser.add_argument("--output-dir", type=str, default="./vault/Briefings", help="Directory to save briefing")

    args = parser.parse_args()
    vault_path = Path(args.vault)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    briefing_content = generate_ceo_briefing(vault_path)

    today = datetime.now().strftime("%Y-%m-%d")
    output_file = output_dir / f"{today}-ceo-briefing.md"
    output_file.write_text(briefing_content, encoding="utf-8")

    print(f"CEO Briefing generated: {output_file}")


if __name__ == "__main__":
    main()
