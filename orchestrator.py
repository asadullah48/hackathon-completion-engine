"""
Orchestrator for Personal AI Employee
Coordinates file watcher, Claude Code vault checks, and scheduled briefings.

Usage:
    python orchestrator.py                    # Run with defaults
    python orchestrator.py --dry-run          # Log only, no actions
    python orchestrator.py --check-interval 30  # Check vault every 30s
    python orchestrator.py --no-claude        # Skip Claude Code triggers
"""

import subprocess
import sys
import time
import signal
import logging
import argparse
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

import yaml

try:
    import schedule
except ImportError:
    print("Missing 'schedule' package. Install with: pip install schedule")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("orchestrator")


class Orchestrator:
    """
    Master process that coordinates the Personal AI Employee components:
    - File watcher (subprocess)
    - Periodic vault checks via Claude Code CLI
    - Scheduled CEO briefing generation
    """

    def __init__(
        self,
        config_path: str = "config/config.yaml",
        check_interval: int = 60,
        dry_run: bool = False,
        enable_claude: bool = True,
        enable_gmail: bool = False,
        enable_whatsapp: bool = False,
    ):
        self.config = self._load_config(config_path)
        self.vault_path = Path(self.config.get("watcher", {}).get("vault_path", "./vault"))
        self.drop_folder = self.config.get("watcher", {}).get("drop_folder", "/mnt/d/AI-Employee-Inbox")
        self.watcher_interval = self.config.get("watcher", {}).get("default_interval", 10)
        self.check_interval = check_interval
        self.dry_run = dry_run
        self.enable_claude = enable_claude
        self.file_watcher_process = None
        self.gmail_watcher_process = None
        self.whatsapp_watcher_process = None
        self.enable_gmail = enable_gmail
        self.enable_whatsapp = enable_whatsapp
        self.running = True

        # Check if Claude CLI is available
        self.claude_available = shutil.which("claude") is not None
        if self.enable_claude and not self.claude_available:
            logger.warning("Claude Code CLI not found in PATH. Vault checks will be skipped.")

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        path = Path(config_path)
        if path.exists():
            with open(path) as f:
                return yaml.safe_load(f) or {}
        logger.warning(f"Config file not found: {config_path}. Using defaults.")
        return {}

    def _ensure_vault_dirs(self):
        """Ensure all vault directories exist."""
        dirs = ["Inbox", "Needs_Action", "Pending_Approval", "Approved",
                "Rejected", "Done", "Briefings", "Logs", "Conversation_Logs"]
        for d in dirs:
            (self.vault_path / d).mkdir(parents=True, exist_ok=True)

    def _start_watcher(self, name: str, script: str, extra_args: list = None) -> Optional[subprocess.Popen]:
        """Start a watcher subprocess."""
        watcher_script = Path(script)
        if not watcher_script.exists():
            logger.error(f"{name} script not found: {watcher_script}")
            return None

        cmd = [sys.executable, str(watcher_script), "--vault", str(self.vault_path)]
        if extra_args:
            cmd.extend(extra_args)
        if self.dry_run:
            cmd.append("--dry-run")

        logger.info(f"Starting {name}: {' '.join(cmd)}")
        if not self.dry_run:
            proc = subprocess.Popen(cmd)
            logger.info(f"{name} started (PID: {proc.pid})")
            return proc
        else:
            logger.info(f"[DRY RUN] Would start {name}")
            return None

    def start_file_watcher(self):
        """Start file watcher as a subprocess."""
        self.file_watcher_process = self._start_watcher(
            "File Watcher", "watchers/file_watcher.py",
            ["--drop-folder", self.drop_folder, "--interval", str(self.watcher_interval)],
        )

    def start_gmail_watcher(self):
        """Start Gmail watcher as a subprocess."""
        self.gmail_watcher_process = self._start_watcher(
            "Gmail Watcher", "watchers/gmail_watcher.py",
            ["--interval", "120"],
        )

    def start_whatsapp_watcher(self):
        """Start WhatsApp watcher as a subprocess."""
        self.whatsapp_watcher_process = self._start_watcher(
            "WhatsApp Watcher", "watchers/whatsapp_watcher.py",
            ["--interval", "30"],
        )

    def stop_file_watcher(self):
        """Stop the file watcher subprocess."""
        if self.file_watcher_process and self.file_watcher_process.poll() is None:
            logger.info("Stopping file watcher...")
            self.file_watcher_process.terminate()
            self.file_watcher_process.wait(timeout=5)
            logger.info("File watcher stopped")

    def _stop_all_watchers(self):
        """Stop all running watcher subprocesses."""
        for name, proc in [
            ("File Watcher", getattr(self, "file_watcher_process", None)),
            ("Gmail Watcher", getattr(self, "gmail_watcher_process", None)),
            ("WhatsApp Watcher", getattr(self, "whatsapp_watcher_process", None)),
        ]:
            if proc and proc.poll() is None:
                logger.info(f"Stopping {name}...")
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                logger.info(f"{name} stopped")

    def trigger_vault_check(self):
        """Ask Claude Code CLI to check vault and process items."""
        if not self.enable_claude or not self.claude_available:
            return

        prompt = (
            "Check vault/Inbox/ and vault/Needs_Action/ for new items. "
            "Process any new items following vault/Company_Handbook.md rules. "
            "Update vault/Dashboard.md with current counts."
        )

        logger.info("Triggering Claude Code vault check...")
        if self.dry_run:
            logger.info(f"[DRY RUN] Would run: claude --print '{prompt}'")
            return

        try:
            result = subprocess.run(
                ["claude", "--print", prompt],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(Path(__file__).parent),
            )
            if result.returncode == 0:
                logger.info("Claude Code vault check completed")
            else:
                logger.warning(f"Claude Code returned non-zero: {result.stderr[:200]}")
        except subprocess.TimeoutExpired:
            logger.warning("Claude Code vault check timed out (120s)")
        except FileNotFoundError:
            logger.warning("Claude Code CLI not found. Skipping vault check.")
            self.claude_available = False

    def trigger_ceo_briefing(self):
        """Generate CEO briefing using the briefing generator script."""
        logger.info("Generating CEO briefing...")
        if self.dry_run:
            logger.info("[DRY RUN] Would generate CEO briefing")
            return

        try:
            result = subprocess.run(
                [
                    sys.executable, "watchers/ceo_briefing_generator.py",
                    "--vault", str(self.vault_path),
                    "--output-dir", str(self.vault_path / "Briefings"),
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                logger.info(f"CEO briefing generated: {result.stdout.strip()}")
            else:
                logger.error(f"CEO briefing failed: {result.stderr[:200]}")
        except Exception as e:
            logger.error(f"Error generating CEO briefing: {e}")

    def _handle_signal(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}. Shutting down...")
        self.running = False

    def run(self):
        """Main orchestration loop."""
        # Register signal handlers
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

        logger.info("=" * 60)
        logger.info("Personal AI Employee - Orchestrator Starting")
        logger.info(f"  Vault: {self.vault_path}")
        logger.info(f"  Drop folder: {self.drop_folder}")
        logger.info(f"  Check interval: {self.check_interval}s")
        logger.info(f"  Dry run: {self.dry_run}")
        logger.info(f"  Claude CLI: {'available' if self.claude_available else 'not found'}")
        logger.info(f"  Gmail Watcher: {'enabled' if self.enable_gmail else 'disabled'}")
        logger.info(f"  WhatsApp Watcher: {'enabled' if self.enable_whatsapp else 'disabled'}")
        logger.info("=" * 60)

        # Ensure vault structure
        self._ensure_vault_dirs()

        # Start watchers
        self.start_file_watcher()
        if self.enable_gmail:
            self.start_gmail_watcher()
        if self.enable_whatsapp:
            self.start_whatsapp_watcher()

        # Schedule CEO briefing for Mondays at 9 AM
        schedule.every().monday.at("09:00").do(self.trigger_ceo_briefing)
        logger.info("Scheduled CEO briefing: every Monday at 09:00")

        # Main loop
        try:
            while self.running:
                # Run scheduled tasks
                schedule.run_pending()

                # Check vault
                self.trigger_vault_check()

                # Restart crashed watchers
                if self.file_watcher_process and self.file_watcher_process.poll() is not None:
                    logger.warning("File watcher died. Restarting...")
                    self.start_file_watcher()
                if self.enable_gmail and self.gmail_watcher_process and self.gmail_watcher_process.poll() is not None:
                    logger.warning("Gmail watcher died. Restarting...")
                    self.start_gmail_watcher()
                if self.enable_whatsapp and self.whatsapp_watcher_process and self.whatsapp_watcher_process.poll() is not None:
                    logger.warning("WhatsApp watcher died. Restarting...")
                    self.start_whatsapp_watcher()

                # Sleep
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            pass
        finally:
            logger.info("Shutting down orchestrator...")
            self._stop_all_watchers()
            logger.info("Orchestrator stopped.")


def main():
    parser = argparse.ArgumentParser(
        description="Personal AI Employee Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python orchestrator.py                     # Run normally
  python orchestrator.py --dry-run           # Preview mode
  python orchestrator.py --check-interval 30 # Check vault every 30s
  python orchestrator.py --no-claude         # Run without Claude Code
  python orchestrator.py --gmail             # Enable Gmail watcher
  python orchestrator.py --whatsapp          # Enable WhatsApp watcher
  python orchestrator.py --gmail --whatsapp  # Enable both
        """,
    )
    parser.add_argument("--config", default="config/config.yaml", help="Path to config file")
    parser.add_argument("--check-interval", type=int, default=60, help="Seconds between vault checks")
    parser.add_argument("--dry-run", action="store_true", help="Log actions without executing")
    parser.add_argument("--no-claude", action="store_true", help="Disable Claude Code vault checks")
    parser.add_argument("--gmail", action="store_true", help="Enable Gmail watcher")
    parser.add_argument("--whatsapp", action="store_true", help="Enable WhatsApp watcher")

    args = parser.parse_args()

    orchestrator = Orchestrator(
        config_path=args.config,
        check_interval=args.check_interval,
        dry_run=args.dry_run,
        enable_claude=not args.no_claude,
        enable_gmail=args.gmail,
        enable_whatsapp=args.whatsapp,
    )
    orchestrator.run()


if __name__ == "__main__":
    main()
