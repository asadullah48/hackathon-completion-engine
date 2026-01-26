"""
Conversation Logger Service for Course Companion
Logs all conversations to vault/Conversation_Logs/
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class ConversationLogger:
    """
    Logs conversations to the Obsidian vault for review and analytics
    Stores logs in vault/Conversation_Logs/YYYY-MM-DD.json format
    """

    def __init__(self, vault_path: str = "../vault"):
        self.vault_path = Path(vault_path)
        self.logs_dir = self.vault_path / "Conversation_Logs"
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Ensure required directories exist"""
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def _get_today_log_file(self) -> Path:
        """Get path to today's log file"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.logs_dir / f"{today}.json"

    def _load_daily_logs(self) -> List[Dict[str, Any]]:
        """Load existing logs for today"""
        log_file = self._get_today_log_file()
        if log_file.exists():
            try:
                with open(log_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load daily logs: {e}")
                return []
        return []

    def _save_daily_logs(self, logs: List[Dict[str, Any]]) -> None:
        """Save logs to today's file"""
        log_file = self._get_today_log_file()
        try:
            with open(log_file, "w") as f:
                json.dump(logs, f, indent=2, default=str)
        except IOError as e:
            logger.error(f"Failed to save daily logs: {e}")

    def log_conversation(
        self,
        student_id: str,
        query: str,
        response: str,
        decision: str,
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log a conversation interaction

        Args:
            student_id: Identifier for the student
            query: The student's question/message
            response: The AI's response
            decision: Filter decision (allow/block/flag)
            conversation_id: Optional conversation thread ID
            metadata: Optional additional metadata

        Returns:
            The logged entry with timestamp
        """
        timestamp = datetime.now().isoformat()

        log_entry = {
            "timestamp": timestamp,
            "student_id": student_id,
            "conversation_id": conversation_id,
            "query": query,
            "response": response,
            "decision": decision,
            "metadata": metadata or {}
        }

        # Add to daily logs
        daily_logs = self._load_daily_logs()
        daily_logs.append(log_entry)
        self._save_daily_logs(daily_logs)

        logger.info(
            f"Logged conversation for student {student_id}, "
            f"decision: {decision}, conv_id: {conversation_id}"
        )

        return log_entry

    def get_student_conversations(
        self,
        student_id: str,
        date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all conversations for a student

        Args:
            student_id: Student identifier
            date: Optional date in YYYY-MM-DD format (defaults to today)

        Returns:
            List of conversation entries for the student
        """
        if date:
            log_file = self.logs_dir / f"{date}.json"
        else:
            log_file = self._get_today_log_file()

        if not log_file.exists():
            return []

        try:
            with open(log_file, "r") as f:
                all_logs = json.load(f)
            return [log for log in all_logs if log.get("student_id") == student_id]
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load student conversations: {e}")
            return []

    def get_student_stats(self, student_id: str) -> Dict[str, Any]:
        """
        Get statistics for a student across all logged conversations

        Args:
            student_id: Student identifier

        Returns:
            Dict with total_conversations, concepts_discussed, time_spent, last_active
        """
        total_conversations = 0
        concepts = set()
        last_active = None

        # Scan all log files
        for log_file in sorted(self.logs_dir.glob("*.json"), reverse=True):
            try:
                with open(log_file, "r") as f:
                    daily_logs = json.load(f)

                for log in daily_logs:
                    if log.get("student_id") == student_id:
                        total_conversations += 1

                        # Track last active timestamp
                        if last_active is None:
                            last_active = log.get("timestamp")

                        # Extract concepts from metadata if available
                        metadata = log.get("metadata", {})
                        if "concepts" in metadata:
                            concepts.update(metadata["concepts"])

            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to read log file {log_file}: {e}")
                continue

        return {
            "total_conversations": total_conversations,
            "concepts_discussed": list(concepts),
            "time_spent": total_conversations * 2,  # Estimate 2 minutes per conversation
            "last_active": last_active
        }

    def get_flagged_conversations(
        self,
        date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all flagged conversations for review

        Args:
            date: Optional date filter in YYYY-MM-DD format

        Returns:
            List of flagged conversation entries
        """
        if date:
            log_files = [self.logs_dir / f"{date}.json"]
        else:
            log_files = list(self.logs_dir.glob("*.json"))

        flagged = []
        for log_file in log_files:
            if not log_file.exists():
                continue
            try:
                with open(log_file, "r") as f:
                    daily_logs = json.load(f)
                flagged.extend([
                    log for log in daily_logs
                    if log.get("decision") == "flag"
                ])
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to read log file {log_file}: {e}")

        return flagged


# Singleton instance
_logger_instance: Optional[ConversationLogger] = None


def get_conversation_logger(vault_path: str = "../vault") -> ConversationLogger:
    """Get or create singleton ConversationLogger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = ConversationLogger(vault_path=vault_path)
    return _logger_instance
