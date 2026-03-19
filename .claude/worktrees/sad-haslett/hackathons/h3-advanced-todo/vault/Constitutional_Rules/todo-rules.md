# Constitutional Rules for Todo Application

## Overview

This document defines the constitutional rules that govern what todos can be created in the H2 Todo application. These rules enforce ethical, legal, and academic integrity standards.

---

## 1. Prohibited Todo Types

### 1.1 Academic Dishonesty

The following patterns are **BLOCKED** as they violate academic integrity:

| Pattern | Example | Reason |
|---------|---------|--------|
| `do my homework` | "Do my homework assignment" | Delegating academic work |
| `write my essay` | "Write my essay for class" | Academic dishonesty |
| `complete my coding project` | "Complete my coding project for me" | Submitting others' work |
| `take my exam` | "Take my exam for me" | Exam fraud |
| `finish assignment for me` | "Finish my assignment for me" | Cheating |
| `plagiarize` | "Plagiarize this paper" | Academic fraud |
| `cheat on` | "Cheat on the test" | Academic dishonesty |

### 1.2 Illegal Activities

The following patterns are **BLOCKED** as they involve illegal activities:

| Pattern | Example | Reason |
|---------|---------|--------|
| `hack into` | "Hack into the database" | Unauthorized access |
| `create fake documents` | "Create fake ID documents" | Forgery |
| `bypass security` | "Bypass the security system" | Security violation |
| `steal data` | "Steal customer data" | Theft |
| `phishing` | "Set up phishing page" | Fraud |
| `malware` | "Create malware" | Cybercrime |

### 1.3 Harmful Actions

The following patterns are **BLOCKED** as they cause harm:

| Pattern | Example | Reason |
|---------|---------|--------|
| `harass` | "Harass the competitor" | Harassment |
| `spread misinformation` | "Spread misinformation about X" | Disinformation |
| `create harmful content` | "Create harmful content" | Harm |
| `bully` | "Bully the new employee" | Bullying |
| `threaten` | "Threaten the client" | Threats |
| `doxing` | "Dox the critic" | Privacy violation |

---

## 2. Flagged Todo Types (Requires Human Review)

The following patterns are **FLAGGED** for human-in-the-loop review:

| Pattern | Example | Concern |
|---------|---------|---------|
| `urgent.*assignment` | "Urgent: finish assignment in 1 hour" | Possible last-minute academic cheating |
| `exam tomorrow` | "Exam tomorrow, need help" | Time pressure may lead to cheating |
| `deadline.*assignment` | "Deadline for assignment tonight" | Urgency may indicate dishonest intent |
| `last minute.*homework` | "Last minute homework help" | May be seeking completion services |

**Flagged todos are:**
- Created with status = "flagged"
- Stored in `vault/Pending_Approval/`
- Require human approval before becoming active

---

## 3. Allowed Todo Types

The following types of todos are **ALLOWED**:

### 3.1 Legitimate Work
- "Study chapter 5 for exam"
- "Practice coding exercises"
- "Research topic for paper"
- "Prepare presentation outline"
- "Review lecture notes"
- "Complete work project" (legitimate work)
- "Debug production issue"

### 3.2 Personal Growth
- "Learn new programming language"
- "Exercise for 30 minutes"
- "Read chapter of book"
- "Meditate for 10 minutes"
- "Practice guitar"

### 3.3 Personal Tasks
- "Buy groceries"
- "Call mom"
- "Schedule dentist appointment"
- "Pay bills"
- "Clean apartment"

### 3.4 Health
- "Take medication"
- "Drink 8 glasses of water"
- "Go for a walk"
- "Schedule annual checkup"

---

## 4. Enforcement Mechanism

### 4.1 Validation Flow

```
User Input → Constitutional Validator → Decision
                    ↓
            ┌───────┴───────┐
            ↓               ↓
         BLOCK           ALLOW/FLAG
            ↓               ↓
    Return 403 Error    Create Todo
                            ↓
                    If FLAG: Create approval request
```

### 4.2 Decision Types

| Decision | HTTP Status | Action |
|----------|-------------|--------|
| ALLOW | 201 Created | Todo created normally |
| BLOCK | 403 Forbidden | Todo rejected with reason |
| FLAG | 201 Created | Todo created with status="flagged" |

### 4.3 Logging

All constitutional decisions are logged to:
- `vault/Logs/constitutional_log_YYYYMMDD.jsonl`

Log format:
```json
{
  "timestamp": "2026-01-25T10:30:00Z",
  "todo_id": "uuid",
  "content_preview": "Do my homework...",
  "decision": "block",
  "passed": false,
  "reason": "Academic dishonesty detected..."
}
```

---

## 5. Human-in-the-Loop (HITL) Workflow

### 5.1 Flagged Todo Approval

When a todo is flagged:
1. Approval request created in `vault/Pending_Approval/todo_{id}.md`
2. Human reviewer checks the request
3. Reviewer marks as Approved or Rejected
4. System updates todo status accordingly

### 5.2 Approval Request Format

```markdown
# Todo Approval Request

## Todo ID
{uuid}

## Title
{todo_title}

## Flag Reason
{reason_for_flag}

## Decision
- [ ] Approve
- [ ] Reject

## Reviewer Notes
{notes}
```

---

## 6. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-25 | Initial rules from SPEC-H2-CORE |

---

**Document Status:** Active
**Last Updated:** 2026-01-25
**Maintained By:** H2 Todo System
