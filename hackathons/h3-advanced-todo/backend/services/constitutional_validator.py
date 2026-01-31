"""Constitutional validator service for todo content.

Enforces constitutional rules to prevent:
- Academic dishonesty
- Illegal activities
- Harmful actions
"""
import re
import os
import json
from datetime import datetime
from typing import Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class Decision(str, Enum):
    """Constitutional decision types."""
    ALLOW = "allow"
    BLOCK = "block"
    FLAG = "flag"


@dataclass
class ConstitutionalResult:
    """Result of constitutional validation."""
    passed: bool
    decision: Decision
    reason: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "decision": self.decision.value,
            "reason": self.reason,
        }


# Prohibited patterns for academic dishonesty
ACADEMIC_DISHONESTY_PATTERNS = [
    r"\bdo\s+(my|the)\s+homework\b",
    r"\bwrite\s+(my|the)\s+essay\b",
    r"\bcomplete\s+(my|the)\s+coding\s+project\b",
    r"\btake\s+(my|the)\s+exam\b",
    r"\bfinish\s+(my|the)\s+assignment\s+for\s+me\b",
    r"\bdo\s+(my|the)\s+project\s+for\s+me\b",
    r"\bwrite\s+(my|the)\s+paper\s+for\s+me\b",
    r"\bsubmit\s+(my|the)\s+work\s+for\s+me\b",
    r"\bcopy\s+someone('s|s)\s+work\b",
    r"\bplagiarize\b",
    r"\bcheat\s+on\b",
]

# Prohibited patterns for illegal activities
ILLEGAL_ACTIVITY_PATTERNS = [
    r"\bhack\s+into\b",
    r"\bcreate\s+fake\s+documents?\b",
    r"\bbypass\s+security\b",
    r"\bsteal\s+(data|information|credentials)\b",
    r"\bbreak\s+into\b",
    r"\billegal\s+access\b",
    r"\bcrack\s+password\b",
    r"\bforge\s+(documents?|signatures?)\b",
    r"\bphishing\b",
    r"\bmalware\b",
    r"\bransomware\b",
]

# Prohibited patterns for harmful actions
HARMFUL_ACTION_PATTERNS = [
    r"\bharass\b",
    r"\bspread\s+misinformation\b",
    r"\bcreate\s+harmful\s+content\b",
    r"\bbully\b",
    r"\bthreaten\b",
    r"\bstalk\b",
    r"\bdoxing\b",
    r"\bdefame\b",
    r"\bslander\b",
    r"\bhate\s+speech\b",
    r"\bviolent\s+content\b",
]

# Patterns that need human review (flagged)
# These are more specific to catch suspicious urgency about completing work
# but not flag legitimate study activities
FLAG_PATTERNS = [
    r"\burgent.*finish.*assignment\b",
    r"\burgent.*complete.*assignment\b",
    r"\bneed.*done.*exam\s+tomorrow\b",
    r"\bdeadline.*complete.*assignment\b",
    r"\blast\s+minute.*finish.*homework\b",
    r"\bsubmit.*someone\s+else\b",
    r"\bhelp.*finish.*assignment.*urgent\b",
]

# Compile all patterns for efficiency
_compiled_academic = [re.compile(p, re.IGNORECASE) for p in ACADEMIC_DISHONESTY_PATTERNS]
_compiled_illegal = [re.compile(p, re.IGNORECASE) for p in ILLEGAL_ACTIVITY_PATTERNS]
_compiled_harmful = [re.compile(p, re.IGNORECASE) for p in HARMFUL_ACTION_PATTERNS]
_compiled_flag = [re.compile(p, re.IGNORECASE) for p in FLAG_PATTERNS]


def check_content(content: str) -> ConstitutionalResult:
    """
    Check todo content against constitutional rules.

    Args:
        content: The todo title or description to validate

    Returns:
        ConstitutionalResult with decision and reason
    """
    if not content:
        return ConstitutionalResult(passed=True, decision=Decision.ALLOW)

    # Check academic dishonesty
    for pattern in _compiled_academic:
        if pattern.search(content):
            return ConstitutionalResult(
                passed=False,
                decision=Decision.BLOCK,
                reason="Academic dishonesty detected. Todos that request completing academic work for the user are not allowed."
            )

    # Check illegal activities
    for pattern in _compiled_illegal:
        if pattern.search(content):
            return ConstitutionalResult(
                passed=False,
                decision=Decision.BLOCK,
                reason="Illegal activity detected. Todos involving hacking, fraud, or other illegal actions are not allowed."
            )

    # Check harmful actions
    for pattern in _compiled_harmful:
        if pattern.search(content):
            return ConstitutionalResult(
                passed=False,
                decision=Decision.BLOCK,
                reason="Harmful action detected. Todos involving harassment or harmful content are not allowed."
            )

    # Check for flagged patterns (need human review)
    for pattern in _compiled_flag:
        if pattern.search(content):
            return ConstitutionalResult(
                passed=True,  # Allow but flag for review
                decision=Decision.FLAG,
                reason="This todo has been flagged for human review due to potential academic integrity concerns."
            )

    # All checks passed
    return ConstitutionalResult(passed=True, decision=Decision.ALLOW)


def validate_todo(title: str, description: str | None = None) -> ConstitutionalResult:
    """
    Validate both title and description of a todo.

    Args:
        title: The todo title
        description: Optional todo description

    Returns:
        ConstitutionalResult with combined validation result
    """
    # Check title first
    title_result = check_content(title)
    if title_result.decision == Decision.BLOCK:
        return title_result

    # Check description if provided
    if description:
        desc_result = check_content(description)
        if desc_result.decision == Decision.BLOCK:
            return desc_result
        # If either is flagged, flag the whole todo
        if desc_result.decision == Decision.FLAG:
            return desc_result

    # Return title result (could be ALLOW or FLAG)
    return title_result


def log_decision(
    todo_id: str,
    content: str,
    result: ConstitutionalResult,
    vault_path: str | None = None
) -> None:
    """
    Log constitutional decision to vault.

    Args:
        todo_id: The todo ID
        content: The content that was checked
        result: The constitutional decision result
        vault_path: Path to vault directory
    """
    if vault_path is None:
        vault_path = os.getenv("VAULT_PATH", "../vault")

    log_dir = os.path.join(vault_path, "Logs")
    os.makedirs(log_dir, exist_ok=True)

    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "todo_id": todo_id,
        "content_preview": content[:100] if len(content) > 100 else content,
        "decision": result.decision.value,
        "passed": result.passed,
        "reason": result.reason,
    }

    log_file = os.path.join(log_dir, f"constitutional_log_{datetime.utcnow().strftime('%Y%m%d')}.jsonl")

    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def create_approval_request(
    todo_id: str,
    title: str,
    description: str | None,
    result: ConstitutionalResult,
    vault_path: str | None = None
) -> str:
    """
    Create a HITL approval request for flagged todos.

    Args:
        todo_id: The todo ID
        title: The todo title
        description: Optional description
        result: The constitutional result
        vault_path: Path to vault directory

    Returns:
        Path to the created approval file
    """
    if vault_path is None:
        vault_path = os.getenv("VAULT_PATH", "../vault")

    approval_dir = os.path.join(vault_path, "Pending_Approval")
    os.makedirs(approval_dir, exist_ok=True)

    approval_file = os.path.join(approval_dir, f"todo_{todo_id}.md")

    content = f"""# Todo Approval Request

## Todo ID
{todo_id}

## Title
{title}

## Description
{description or "N/A"}

## Flag Reason
{result.reason}

## Requested At
{datetime.utcnow().isoformat()}

---

## Decision (fill in)
- [ ] Approve
- [ ] Reject

## Reviewer Notes


"""

    with open(approval_file, "w") as f:
        f.write(content)

    return approval_file
