"""
Gmail Watcher for Personal AI Employee
Monitors Gmail for new unread/important emails and creates action items in the vault.

Setup:
  1. Create a Google Cloud project at https://console.cloud.google.com/
  2. Enable the Gmail API
  3. Create OAuth 2.0 credentials (Desktop app type)
  4. Download credentials.json to this project root
  5. Run this script once to complete the OAuth flow (opens browser)
  6. After first run, token.json is saved for future use

Usage:
  python watchers/gmail_watcher.py --vault ./vault
  python watchers/gmail_watcher.py --vault ./vault --dry-run
  python watchers/gmail_watcher.py --vault ./vault --interval 120
"""

import os
import json
import time
import logging
import argparse
import base64
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from email.utils import parseaddr

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("gmail_watcher")

# Gmail API dependencies
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    logger.warning(
        "Gmail API packages not installed. Run: "
        "pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client"
    )

# OAuth scopes - read-only for safety
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class GmailWatcher:
    """Monitors Gmail for new unread/important emails and creates vault action items."""

    # Keywords that elevate an email to high priority
    URGENT_KEYWORDS = [
        "urgent", "asap", "invoice", "payment", "deadline",
        "overdue", "critical", "immediate", "action required",
    ]

    def __init__(
        self,
        vault_path: Path,
        credentials_path: Path = Path("credentials.json"),
        token_path: Path = Path("token.json"),
        check_interval: int = 120,
        dry_run: bool = False,
        max_results: int = 10,
    ):
        self.vault_path = Path(vault_path)
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self.check_interval = check_interval
        self.dry_run = dry_run
        self.max_results = max_results

        # Vault directories
        self.needs_action = self.vault_path / "Needs_Action"
        self.logs_dir = self.vault_path / "Logs"
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # State: track processed message IDs
        self.state_file = self.vault_path / ".gmail_watcher_state.json"
        self.processed_ids: set = set()
        self._load_state()

        # Gmail service (initialized lazily)
        self._service = None

    def _load_state(self) -> None:
        """Load previously processed message IDs."""
        if self.state_file.exists():
            with open(self.state_file) as f:
                state = json.load(f)
                self.processed_ids = set(state.get("processed_ids", []))
            logger.info(f"Loaded state: {len(self.processed_ids)} processed emails")

    def _save_state(self) -> None:
        """Persist processed message IDs."""
        # Keep only last 500 IDs to prevent unbounded growth
        recent_ids = list(self.processed_ids)[-500:]
        with open(self.state_file, "w") as f:
            json.dump(
                {"processed_ids": recent_ids, "last_updated": datetime.now().isoformat()},
                f,
                indent=2,
            )

    def _authenticate(self) -> None:
        """Authenticate with Gmail API using OAuth2."""
        if not GMAIL_AVAILABLE:
            raise RuntimeError(
                "Gmail API packages not installed. Run: "
                "pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client"
            )

        creds = None

        # Load existing token
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired Gmail token...")
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"Gmail credentials not found at {self.credentials_path}. "
                        "Download from Google Cloud Console > APIs > Credentials."
                    )
                logger.info("Starting OAuth flow (will open browser)...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save token for future runs
            with open(self.token_path, "w") as token_file:
                token_file.write(creds.to_json())
            logger.info(f"Token saved to {self.token_path}")

        self._service = build("gmail", "v1", credentials=creds)
        logger.info("Gmail API authenticated successfully")

    @property
    def service(self):
        """Lazy-initialize Gmail service."""
        if self._service is None:
            self._authenticate()
        return self._service

    def _get_header(self, headers: List[Dict], name: str) -> str:
        """Extract a header value from Gmail message headers."""
        for h in headers:
            if h["name"].lower() == name.lower():
                return h["value"]
        return ""

    def _determine_priority(self, subject: str, snippet: str, labels: List[str]) -> str:
        """Determine email priority based on content and labels."""
        text = (subject + " " + snippet).lower()

        if "IMPORTANT" in labels or any(kw in text for kw in self.URGENT_KEYWORDS):
            return "high"
        if "CATEGORY_UPDATES" in labels or "CATEGORY_SOCIAL" in labels:
            return "low"
        return "medium"

    def check_for_updates(self) -> List[Dict]:
        """Check Gmail for new unread emails."""
        try:
            results = self.service.users().messages().list(
                userId="me",
                q="is:unread",
                maxResults=self.max_results,
            ).execute()

            messages = results.get("messages", [])
            new_messages = []

            for msg_ref in messages:
                if msg_ref["id"] in self.processed_ids:
                    continue

                # Fetch full message
                msg = self.service.users().messages().get(
                    userId="me", id=msg_ref["id"], format="metadata",
                    metadataHeaders=["From", "Subject", "Date"],
                ).execute()

                headers = msg.get("payload", {}).get("headers", [])
                labels = msg.get("labelIds", [])

                sender = self._get_header(headers, "From")
                subject = self._get_header(headers, "Subject")
                date = self._get_header(headers, "Date")
                snippet = msg.get("snippet", "")

                new_messages.append({
                    "id": msg_ref["id"],
                    "from": sender,
                    "from_name": parseaddr(sender)[0] or parseaddr(sender)[1],
                    "from_email": parseaddr(sender)[1],
                    "subject": subject,
                    "date": date,
                    "snippet": snippet,
                    "labels": labels,
                    "priority": self._determine_priority(subject, snippet, labels),
                })

            return new_messages

        except Exception as e:
            logger.error(f"Error checking Gmail: {e}")
            return []

    def create_action_file(self, email: Dict) -> Optional[Path]:
        """Create an action item in vault/Needs_Action/ for a new email."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Sanitize subject for filename
        safe_subject = "".join(c if c.isalnum() or c in " -_" else "" for c in email["subject"])[:40]
        filename = f"EMAIL_{timestamp}_{safe_subject.strip().replace(' ', '_')}.md"
        filepath = self.needs_action / filename

        content = f"""---
type: email
from: {email['from_email']}
from_name: {email['from_name']}
subject: {email['subject']}
received: {email['date']}
priority: {email['priority']}
status: pending
gmail_id: {email['id']}
---

## Email: {email['subject']}

**From:** {email['from']}
**Date:** {email['date']}
**Priority:** {email['priority']}

### Preview

{email['snippet']}

### Suggested Actions

- [ ] Read full email in Gmail
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing

### Status

- [x] Email detected by watcher
- [ ] Reviewed by human
- [ ] Action taken
- [ ] Moved to Done/
"""

        if self.dry_run:
            logger.info(f"[DRY RUN] Would create: {filepath.name}")
            return None

        filepath.write_text(content, encoding="utf-8")
        return filepath

    def _log_activity(self, activity_type: str, details: Dict) -> None:
        """Log activity to daily JSON log."""
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.logs_dir / f"{today}.json"

        if log_file.exists():
            with open(log_file) as f:
                log_data = json.load(f)
        else:
            log_data = {"date": today, "activities": []}

        log_data["activities"].append({
            "timestamp": datetime.now().isoformat(),
            "type": activity_type,
            "details": details,
        })

        if not self.dry_run:
            with open(log_file, "w") as f:
                json.dump(log_data, f, indent=2)

    def run(self) -> None:
        """Main loop: continuously check Gmail for new emails."""
        logger.info("=" * 50)
        logger.info("Gmail Watcher Starting")
        logger.info(f"  Vault: {self.vault_path}")
        logger.info(f"  Interval: {self.check_interval}s")
        logger.info(f"  Dry run: {self.dry_run}")
        logger.info(f"  Max results per check: {self.max_results}")
        logger.info("=" * 50)

        try:
            while True:
                new_emails = self.check_for_updates()

                if new_emails:
                    logger.info(f"Found {len(new_emails)} new email(s)")

                    for email in new_emails:
                        logger.info(
                            f"  -> [{email['priority'].upper()}] "
                            f"From: {email['from_name']} | "
                            f"Subject: {email['subject'][:60]}"
                        )

                        action_path = self.create_action_file(email)
                        if action_path:
                            logger.info(f"     Created: {action_path.name}")

                        self._log_activity("email_detected", {
                            "gmail_id": email["id"],
                            "from": email["from_email"],
                            "subject": email["subject"],
                            "priority": email["priority"],
                            "action_item": str(action_path) if action_path else None,
                        })

                        self.processed_ids.add(email["id"])

                    self._save_state()

                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            logger.info("\nGmail Watcher Stopped")
            self._save_state()


def main():
    parser = argparse.ArgumentParser(description="Gmail Watcher for Personal AI Employee")
    parser.add_argument("--vault", type=str, default="./vault", help="Path to Obsidian vault")
    parser.add_argument("--credentials", type=str, default="credentials.json", help="Path to Google OAuth credentials")
    parser.add_argument("--token", type=str, default="token.json", help="Path to saved OAuth token")
    parser.add_argument("--interval", type=int, default=120, help="Check interval in seconds")
    parser.add_argument("--max-results", type=int, default=10, help="Max emails per check")
    parser.add_argument("--dry-run", action="store_true", help="Log only, no file writes")

    args = parser.parse_args()

    if not GMAIL_AVAILABLE:
        logger.error(
            "Gmail API packages not installed. Install with:\n"
            "  pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client"
        )
        return

    watcher = GmailWatcher(
        vault_path=Path(args.vault),
        credentials_path=Path(args.credentials),
        token_path=Path(args.token),
        check_interval=args.interval,
        dry_run=args.dry_run,
        max_results=args.max_results,
    )
    watcher.run()


if __name__ == "__main__":
    main()
