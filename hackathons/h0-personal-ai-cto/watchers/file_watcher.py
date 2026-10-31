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
import argparse


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
        default='./vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--drop-folder',
        type=str,
        default='/mnt/d/AI-Employee-Inbox',
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