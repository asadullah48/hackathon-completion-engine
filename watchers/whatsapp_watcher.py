"""
WhatsApp Watcher for Personal AI Employee
Monitors WhatsApp Web via Playwright for new messages containing business keywords.
Creates action items in the vault for messages that need attention.

Setup:
  1. pip install playwright
  2. playwright install chromium
  3. Run once to scan QR code: python watchers/whatsapp_watcher.py --vault ./vault
     (A browser window opens -- scan the QR code with your phone)
  4. Session is saved to .whatsapp_session/ for future headless runs

Usage:
  python watchers/whatsapp_watcher.py --vault ./vault
  python watchers/whatsapp_watcher.py --vault ./vault --headless
  python watchers/whatsapp_watcher.py --vault ./vault --dry-run
  python watchers/whatsapp_watcher.py --vault ./vault --interval 30

Note: Be aware of WhatsApp's Terms of Service regarding automation.
      This watcher is read-only (it does not send messages).
"""

import json
import time
import logging
import argparse
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("whatsapp_watcher")

# Playwright dependency
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning(
        "Playwright not installed. Run: pip install playwright && playwright install chromium"
    )


class WhatsAppWatcher:
    """Monitors WhatsApp Web for new messages with business keywords."""

    # Keywords that trigger action item creation
    BUSINESS_KEYWORDS = [
        "urgent", "asap", "invoice", "payment", "help",
        "deadline", "meeting", "proposal", "contract", "budget",
        "pricing", "quote", "order", "delivery", "project",
    ]

    def __init__(
        self,
        vault_path: Path,
        session_path: Path = Path(".whatsapp_session"),
        check_interval: int = 30,
        headless: bool = False,
        dry_run: bool = False,
    ):
        self.vault_path = Path(vault_path)
        self.session_path = Path(session_path)
        self.check_interval = check_interval
        self.headless = headless
        self.dry_run = dry_run

        # Vault directories
        self.needs_action = self.vault_path / "Needs_Action"
        self.logs_dir = self.vault_path / "Logs"
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # State tracking
        self.state_file = self.vault_path / ".whatsapp_watcher_state.json"
        self.processed_hashes: set = set()
        self._load_state()

    def _load_state(self) -> None:
        """Load previously processed message hashes."""
        if self.state_file.exists():
            with open(self.state_file) as f:
                state = json.load(f)
                self.processed_hashes = set(state.get("processed_hashes", []))
            logger.info(f"Loaded state: {len(self.processed_hashes)} processed messages")

    def _save_state(self) -> None:
        """Persist processed message hashes."""
        recent = list(self.processed_hashes)[-1000:]
        with open(self.state_file, "w") as f:
            json.dump(
                {"processed_hashes": recent, "last_updated": datetime.now().isoformat()},
                f,
                indent=2,
            )

    def _message_hash(self, contact: str, text: str) -> str:
        """Create a unique hash for a message to avoid duplicates."""
        return hashlib.md5(f"{contact}:{text}".encode()).hexdigest()

    def _has_business_keyword(self, text: str) -> Optional[str]:
        """Check if text contains a business keyword. Returns the keyword or None."""
        text_lower = text.lower()
        for kw in self.BUSINESS_KEYWORDS:
            if kw in text_lower:
                return kw
        return None

    def _determine_priority(self, text: str, keyword: str) -> str:
        """Determine message priority."""
        text_lower = text.lower()
        if any(w in text_lower for w in ["urgent", "asap", "deadline", "critical"]):
            return "high"
        if any(w in text_lower for w in ["invoice", "payment", "contract", "budget"]):
            return "high"
        return "medium"

    def check_for_updates(self) -> List[Dict]:
        """Open WhatsApp Web and check for unread messages with keywords."""
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("Playwright not available")
            return []

        new_messages = []

        with sync_playwright() as p:
            # Launch with persistent context to keep session
            context = p.chromium.launch_persistent_context(
                str(self.session_path),
                headless=self.headless,
                args=["--disable-blink-features=AutomationControlled"],
            )

            page = context.pages[0] if context.pages else context.new_page()
            page.goto("https://web.whatsapp.com")

            # Wait for WhatsApp to load (either chat list or QR code)
            try:
                logger.info("Waiting for WhatsApp Web to load...")
                # Wait for the main app to load
                page.wait_for_selector(
                    'div[aria-label="Chat list"], canvas[aria-label="Scan this QR code to link a device!"]',
                    timeout=60000,
                )

                # Check if QR code is showing (not logged in)
                qr = page.query_selector('canvas[aria-label="Scan this QR code to link a device!"]')
                if qr:
                    logger.info(
                        "QR code detected. Please scan with your phone to log in. "
                        "Waiting up to 120 seconds..."
                    )
                    page.wait_for_selector('div[aria-label="Chat list"]', timeout=120000)
                    logger.info("Logged in successfully!")

                # Wait a moment for messages to fully load
                time.sleep(3)

                # Find chats with unread messages
                unread_chats = page.query_selector_all(
                    'span[aria-label*="unread message"], span[data-icon="unread-count"]'
                )

                if not unread_chats:
                    # Alternative selector for unread badges
                    unread_chats = page.query_selector_all(
                        'div[class*="unread"] span[dir="auto"]'
                    )

                logger.info(f"Found {len(unread_chats)} chats with unread messages")

                # Try to get recent messages from visible chat panels
                # Click on each unread chat and read the latest messages
                chat_items = page.query_selector_all('div[role="listitem"]')

                for chat_item in chat_items[:10]:  # Limit to first 10 chats
                    try:
                        # Get contact name
                        name_el = chat_item.query_selector('span[title]')
                        if not name_el:
                            continue
                        contact_name = name_el.get_attribute("title") or "Unknown"

                        # Get last message preview
                        preview_el = chat_item.query_selector('span[dir="ltr"], span.ggj6brxn')
                        if not preview_el:
                            continue
                        preview_text = preview_el.inner_text()

                        # Check for unread indicator
                        unread_badge = chat_item.query_selector(
                            'span[aria-label*="unread"], span[data-icon="unread-count"]'
                        )

                        # Check for business keywords
                        keyword = self._has_business_keyword(preview_text)
                        if keyword and unread_badge:
                            msg_hash = self._message_hash(contact_name, preview_text)
                            if msg_hash not in self.processed_hashes:
                                priority = self._determine_priority(preview_text, keyword)
                                new_messages.append({
                                    "contact": contact_name,
                                    "text": preview_text,
                                    "keyword": keyword,
                                    "priority": priority,
                                    "hash": msg_hash,
                                    "timestamp": datetime.now().isoformat(),
                                })
                    except Exception as e:
                        logger.debug(f"Error reading chat item: {e}")
                        continue

            except PlaywrightTimeout:
                logger.warning("Timed out waiting for WhatsApp Web. Is the internet connected?")
            except Exception as e:
                logger.error(f"Error checking WhatsApp: {e}")
            finally:
                context.close()

        return new_messages

    def create_action_file(self, message: Dict) -> Optional[Path]:
        """Create an action item in vault/Needs_Action/ for a WhatsApp message."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_contact = "".join(c if c.isalnum() or c in " -_" else "" for c in message["contact"])[:30]
        filename = f"WHATSAPP_{timestamp}_{safe_contact.strip().replace(' ', '_')}.md"
        filepath = self.needs_action / filename

        content = f"""---
type: whatsapp
from: {message['contact']}
keyword_matched: {message['keyword']}
priority: {message['priority']}
detected: {message['timestamp']}
status: pending
---

## WhatsApp Message from {message['contact']}

**From:** {message['contact']}
**Detected:** {message['timestamp']}
**Priority:** {message['priority']}
**Keyword:** {message['keyword']}

### Message Preview

{message['text']}

### Suggested Actions

- [ ] Open WhatsApp and read full conversation
- [ ] Reply to {message['contact']}
- [ ] Forward to relevant team member
- [ ] Create follow-up task

### Status

- [x] Message detected by watcher
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
        """Main loop: periodically check WhatsApp for new messages."""
        logger.info("=" * 50)
        logger.info("WhatsApp Watcher Starting")
        logger.info(f"  Vault: {self.vault_path}")
        logger.info(f"  Session: {self.session_path}")
        logger.info(f"  Interval: {self.check_interval}s")
        logger.info(f"  Headless: {self.headless}")
        logger.info(f"  Dry run: {self.dry_run}")
        logger.info(f"  Keywords: {', '.join(self.BUSINESS_KEYWORDS)}")
        logger.info("=" * 50)

        try:
            while True:
                new_messages = self.check_for_updates()

                if new_messages:
                    logger.info(f"Found {len(new_messages)} new business message(s)")

                    for msg in new_messages:
                        logger.info(
                            f"  -> [{msg['priority'].upper()}] "
                            f"From: {msg['contact']} | "
                            f"Keyword: {msg['keyword']} | "
                            f"Preview: {msg['text'][:50]}..."
                        )

                        action_path = self.create_action_file(msg)
                        if action_path:
                            logger.info(f"     Created: {action_path.name}")

                        self._log_activity("whatsapp_detected", {
                            "contact": msg["contact"],
                            "keyword": msg["keyword"],
                            "priority": msg["priority"],
                            "preview": msg["text"][:100],
                            "action_item": str(action_path) if action_path else None,
                        })

                        self.processed_hashes.add(msg["hash"])

                    self._save_state()
                else:
                    logger.debug("No new business messages found")

                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            logger.info("\nWhatsApp Watcher Stopped")
            self._save_state()


def main():
    parser = argparse.ArgumentParser(description="WhatsApp Watcher for Personal AI Employee")
    parser.add_argument("--vault", type=str, default="./vault", help="Path to Obsidian vault")
    parser.add_argument("--session", type=str, default=".whatsapp_session", help="Path to browser session data")
    parser.add_argument("--interval", type=int, default=30, help="Check interval in seconds")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode (after first login)")
    parser.add_argument("--dry-run", action="store_true", help="Log only, no file writes")

    args = parser.parse_args()

    if not PLAYWRIGHT_AVAILABLE:
        logger.error(
            "Playwright not installed. Install with:\n"
            "  pip install playwright\n"
            "  playwright install chromium"
        )
        return

    watcher = WhatsAppWatcher(
        vault_path=Path(args.vault),
        session_path=Path(args.session),
        check_interval=args.interval,
        headless=args.headless,
        dry_run=args.dry_run,
    )
    watcher.run()


if __name__ == "__main__":
    main()
