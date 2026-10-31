"""
Constitutional Filter Middleware
Enforces academic integrity rules by detecting prohibited queries
"""

import re
import logging
from typing import Dict, Tuple
from datetime import datetime
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class ConstitutionalFilter:
    """
    Multi-layer filter to enforce constitutional rules
    Prevents academic dishonesty while allowing legitimate learning
    """

    # Prohibited patterns - These MUST be blocked
    PROHIBITED_PATTERNS = [
        r"solve\s+(this|my|the)\s+(homework|assignment|problem)",
        r"write\s+(the|this|my)\s+code\s+for\s+me",
        r"give\s+me\s+the\s+answer",
        r"do\s+my\s+(homework|assignment|test|quiz)",
        r"complete\s+(this|my)\s+(assignment|homework)",
        r"(what|tell me)\s+(is|are)\s+the\s+answer",
        r"just\s+give\s+me\s+the\s+(answer|solution|code)",
    ]

    # Suspicious patterns - These should be FLAGGED for human review
    SUSPICIOUS_PATTERNS = [
        r"(exam|test|quiz)\s+(tomorrow|today|in\s+\d+\s+(hour|minute))",
        r"due\s+in\s+\d+\s+(hour|minute)",
        r"urgent(ly)?\s+(need|want)",
        r"deadline\s+(is\s+)?(tomorrow|today|tonight)",
        r"no\s+time",
    ]

    def __init__(self, vault_path: str = "../vault"):
        self.vault_path = Path(vault_path)
        self.pending_approval_dir = self.vault_path / "Pending_Approval"
        self.pending_approval_dir.mkdir(parents=True, exist_ok=True)

    def check_query(self, query: str, student_id: str = "unknown") -> Tuple[str, str, Dict]:
        """
        Check if query violates constitutional rules

        Returns:
            (decision, reason, metadata)
            decision: "allow", "block", or "flag"
            reason: explanation of decision
            metadata: additional context
        """

        query_lower = query.lower()

        # Check prohibited patterns
        for pattern in self.PROHIBITED_PATTERNS:
            if re.search(pattern, query_lower, re.IGNORECASE):
                reason = f"Query matches prohibited pattern: academic dishonesty detected"
                logger.warning(f"BLOCKED query from {student_id}: {query[:100]}")
                return ("block", reason, {
                    "pattern_matched": pattern,
                    "timestamp": datetime.now().isoformat()
                })

        # Check suspicious patterns
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, query_lower, re.IGNORECASE):
                reason = f"Query flagged as suspicious: time pressure or urgency detected"
                logger.warning(f"FLAGGED query from {student_id}: {query[:100]}")

                # Create approval request
                self._create_approval_request(query, student_id, pattern)

                return ("flag", reason, {
                    "pattern_matched": pattern,
                    "timestamp": datetime.now().isoformat(),
                    "requires_human_review": True
                })

        # Query is allowed
        return ("allow", "Query approved", {
            "timestamp": datetime.now().isoformat()
        })

    def _create_approval_request(self, query: str, student_id: str, pattern: str):
        """Create approval request file for HITL review"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"APPROVAL_QUERY_{student_id}_{timestamp}.md"
        filepath = self.pending_approval_dir / filename

        content = f"""---
type: query_approval
student_id: {student_id}
created: {datetime.now().isoformat()}
pattern_matched: {pattern}
status: pending
---

# QUERY APPROVAL REQUIRED

**Student ID:** {student_id}
**Timestamp:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Reason:** Suspicious pattern detected (time pressure/urgency)

---

## Query Content
```
{query}
```

---

## Review Options

- [ ] **APPROVE** - Allow AI to respond (legitimate learning need)
- [ ] **REJECT** - Block response (suspected cheating attempt)
- [ ] **ESCALATE** - Notify course instructor

---

## Reviewer Notes

_Add notes here after review_

---

**Reviewed by:** _________________
**Decision:** _________________
**Date:** _________________
"""

        try:
            filepath.write_text(content)
            logger.info(f"Created approval request: {filename}")
        except Exception as e:
            logger.error(f"Failed to create approval request: {e}")

    def get_socratic_response(self, blocked_reason: str) -> str:
        """
        Generate a Socratic response for blocked queries
        Redirects student toward learning instead of answers
        """

        responses = {
            "academic dishonesty detected": (
                "I'd love to help you learn! Instead of providing the answer directly, "
                "let's work through this together. What have you tried so far? "
                "What part of the problem is confusing you?"
            ),
            "time pressure": (
                "I understand you're feeling time pressure. While I can't provide "
                "direct answers, I can help you understand the concepts. "
                "What specific part of the material would you like me to explain?"
            ),
        }

        for key, response in responses.items():
            if key in blocked_reason.lower():
                return response

        return (
            "I'm here to help you learn! Let's approach this together. "
            "What do you already understand about this topic? "
            "Where are you getting stuck?"
        )

    def log_interaction(self, student_id: str, query: str, decision: str, response: str):
        """Log interaction for analytics and audit"""

        logs_dir = self.vault_path / "Conversation_Logs"
        logs_dir.mkdir(parents=True, exist_ok=True)

        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = logs_dir / f"interactions_{date_str}.jsonl"

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "student_id": student_id,
            "query": query[:500],  # Truncate for storage
            "decision": decision,
            "response_preview": response[:200] if response else None
        }

        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.error(f"Failed to log interaction: {e}")
