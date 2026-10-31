"""
Chat Router for Course Companion API
Handles chat interactions with constitutional filtering
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import uuid
import os
from pathlib import Path

from middleware.constitutional_filter import ConstitutionalFilter
from services.chatgpt_service import get_chatgpt_service
from services.logger_service import get_conversation_logger

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
constitutional_filter = ConstitutionalFilter(vault_path="../vault")
chatgpt_service = get_chatgpt_service()
conversation_logger = get_conversation_logger(vault_path="../vault")


class ChatRequest(BaseModel):
    message: str
    student_id: str = "anonymous"
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    constitutional_decision: str  # "allow", "block", or "flag"
    logged: bool = True


class FlagRequest(BaseModel):
    reason: Optional[str] = None


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message through constitutional filtering

    Flow:
    1. Receive message
    2. Check constitutional filter
    3. If blocked → return error with explanation
    4. If flagged → log for HITL, return waiting message
    5. If allowed → send to ChatGPT → log → return response
    """
    # Generate conversation_id if not provided
    conv_id = request.conversation_id or str(uuid.uuid4())

    # Apply constitutional filter
    decision, reason, metadata = constitutional_filter.check_query(
        request.message,
        request.student_id
    )

    if decision == "block":
        # Return Socratic response instead of direct answer
        socratic_response = constitutional_filter.get_socratic_response(reason)

        # Log the blocked interaction
        conversation_logger.log_conversation(
            student_id=request.student_id,
            query=request.message,
            response=socratic_response,
            decision=decision,
            conversation_id=conv_id,
            metadata={"reason": reason, "pattern_matched": metadata.get("pattern_matched")}
        )

        return ChatResponse(
            response=socratic_response,
            conversation_id=conv_id,
            constitutional_decision=decision,
            logged=True
        )

    elif decision == "flag":
        # Return notice that human review is required
        flagged_response = (
            "Your request has been flagged for review. "
            "A human instructor will review your question shortly. "
            "In the meantime, I can help with general learning concepts."
        )

        # Log the flagged interaction
        conversation_logger.log_conversation(
            student_id=request.student_id,
            query=request.message,
            response=flagged_response,
            decision=decision,
            conversation_id=conv_id,
            metadata={"reason": reason, "requires_human_review": True}
        )

        return ChatResponse(
            response=flagged_response,
            conversation_id=conv_id,
            constitutional_decision=decision,
            logged=True
        )

    else:  # decision == "allow"
        # Process with ChatGPT service
        result = await chatgpt_service.chat_completion(
            message=request.message,
            student_id=request.student_id
        )

        if not result.get("success"):
            # Handle rate limiting or API errors
            error_response = result.get("message", "Service temporarily unavailable")

            conversation_logger.log_conversation(
                student_id=request.student_id,
                query=request.message,
                response=error_response,
                decision="error",
                conversation_id=conv_id,
                metadata={"error": result.get("error")}
            )

            if result.get("error") == "rate_limit_exceeded":
                return ChatResponse(
                    response=error_response,
                    conversation_id=conv_id,
                    constitutional_decision="block",
                    logged=True
                )

            raise HTTPException(status_code=500, detail=error_response)

        ai_response = result.get("response", "")

        # Log the allowed interaction
        conversation_logger.log_conversation(
            student_id=request.student_id,
            query=request.message,
            response=ai_response,
            decision=decision,
            conversation_id=conv_id,
            metadata={
                "tokens_used": result.get("tokens_used"),
                "mock": result.get("mock", False)
            }
        )

        return ChatResponse(
            response=ai_response,
            conversation_id=conv_id,
            constitutional_decision=decision,
            logged=True
        )


@router.get("/conversations/{student_id}")
async def get_conversations(student_id: str):
    """
    Get conversation history for a student from logs
    """
    conversations = conversation_logger.get_student_conversations(student_id)
    return {
        "student_id": student_id,
        "conversations": conversations,
        "total": len(conversations)
    }


@router.post("/flag/{conversation_id}")
async def flag_conversation(conversation_id: str, request: FlagRequest):
    """
    Manually flag a conversation for review
    Creates an approval request in Pending_Approval folder
    """
    # Create flag file in Pending_Approval
    vault_path = Path("../vault")
    pending_dir = vault_path / "Pending_Approval"
    pending_dir.mkdir(parents=True, exist_ok=True)

    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"MANUAL_FLAG_{conversation_id}_{timestamp}.md"
    filepath = pending_dir / filename

    content = f"""---
type: manual_flag
conversation_id: {conversation_id}
created: {datetime.now().isoformat()}
status: pending
---

# MANUALLY FLAGGED CONVERSATION

**Conversation ID:** {conversation_id}
**Timestamp:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Reason:** {request.reason or "Manual review requested"}

---

## Review Options

- [ ] **REVIEWED** - Mark as reviewed
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
        logger.info(f"Created manual flag: {filename}")
        return {
            "status": "flagged",
            "conversation_id": conversation_id,
            "message": "Conversation flagged for review"
        }
    except Exception as e:
        logger.error(f"Failed to create flag: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to flag conversation: {str(e)}")


@router.get("/chat/status")
async def chat_status():
    """Get status of the chat service"""
    return {
        "status": "operational",
        "constitutional_filter": "active",
        "openai_api_configured": bool(os.getenv("OPENAI_API_KEY")),
        "blocked_patterns_count": len(constitutional_filter.PROHIBITED_PATTERNS),
        "suspicious_patterns_count": len(constitutional_filter.SUSPICIOUS_PATTERNS)
    }