"""
ChatGPT Service for Course Companion
Integrates with OpenAI API with constitutional rules embedded in system prompt
"""

import os
import time
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from collections import deque
from openai import OpenAI, OpenAIError

logger = logging.getLogger(__name__)

# Constitutional System Prompt - Embedded rules for Socratic teaching
SYSTEM_PROMPT = """You are a Course Companion AI tutor. Your role is to guide students to discover answers themselves through Socratic questioning.

CONSTITUTIONAL RULES (UNBREAKABLE):
1. NEVER provide complete homework solutions
2. NEVER write full code for assignments
3. NEVER give direct answers to graded work
4. ALWAYS use Socratic questioning
5. ALWAYS explain concepts, never just answers

When a student asks for help:
- Ask "What have you tried so far?"
- Guide with hints, not solutions
- Explain the concept behind the problem
- Encourage their thinking process
- Celebrate their attempts

Example:
Student: "What's the answer to this sorting problem?"
You: "Great question! Before we dive in, what sorting algorithms have you learned? What approach do you think might work here? Let's explore your thinking..."

If asked for direct solutions, politely redirect to learning.
"""


class RateLimiter:
    """Simple rate limiter using timestamp tracking"""

    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, deque] = {}

    def is_allowed(self, student_id: str) -> Tuple[bool, int]:
        """
        Check if request is allowed for student

        Returns:
            (is_allowed, seconds_until_reset)
        """
        current_time = time.time()

        if student_id not in self.requests:
            self.requests[student_id] = deque()

        # Remove expired timestamps
        while (self.requests[student_id] and
               current_time - self.requests[student_id][0] > self.window_seconds):
            self.requests[student_id].popleft()

        # Check if under limit
        if len(self.requests[student_id]) < self.max_requests:
            self.requests[student_id].append(current_time)
            return True, 0

        # Calculate wait time
        oldest_request = self.requests[student_id][0]
        wait_time = int(self.window_seconds - (current_time - oldest_request)) + 1
        return False, wait_time

    def get_remaining(self, student_id: str) -> int:
        """Get remaining requests for student"""
        current_time = time.time()

        if student_id not in self.requests:
            return self.max_requests

        # Remove expired timestamps
        while (self.requests[student_id] and
               current_time - self.requests[student_id][0] > self.window_seconds):
            self.requests[student_id].popleft()

        return self.max_requests - len(self.requests[student_id])


class ChatGPTService:
    """
    Service for interacting with OpenAI ChatGPT API
    Includes rate limiting and constitutional system prompt
    """

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "500"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))

        # Rate limiter: max 10 requests per minute per student
        max_rpm = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "10"))
        self.rate_limiter = RateLimiter(max_requests=max_rpm, window_seconds=60)

        self._client: Optional[OpenAI] = None

    @property
    def client(self) -> OpenAI:
        """Lazy-load OpenAI client"""
        if self._client is None:
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            self._client = OpenAI(api_key=self.api_key)
        return self._client

    @property
    def is_configured(self) -> bool:
        """Check if API key is configured"""
        return bool(self.api_key)

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text
        Rough estimation: ~4 characters per token for English
        """
        return len(text) // 4

    async def chat_completion(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        student_id: str = "anonymous"
    ) -> Dict:
        """
        Generate chat completion with constitutional system prompt

        Args:
            message: User message
            conversation_history: Previous messages in conversation
            student_id: Student identifier for rate limiting

        Returns:
            Dict with response, tokens_used, rate_limit_remaining
        """

        # Check rate limit
        is_allowed, wait_time = self.rate_limiter.is_allowed(student_id)
        if not is_allowed:
            logger.warning(f"Rate limit exceeded for student {student_id}")
            return {
                "success": False,
                "error": "rate_limit_exceeded",
                "message": f"Rate limit exceeded. Please wait {wait_time} seconds before trying again.",
                "wait_seconds": wait_time,
                "rate_limit_remaining": 0
            }

        # Build messages with system prompt
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

        # Add current message
        messages.append({"role": "user", "content": message})

        # Check if API key is configured
        if not self.is_configured:
            logger.info("No API key configured, returning mock response")
            mock_response = self._generate_mock_response(message)
            return {
                "success": True,
                "response": mock_response,
                "tokens_used": self.estimate_tokens(mock_response),
                "rate_limit_remaining": self.rate_limiter.get_remaining(student_id),
                "mock": True
            }

        try:
            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            ai_response = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0

            logger.info(f"ChatGPT response generated for student {student_id}, tokens: {tokens_used}")

            return {
                "success": True,
                "response": ai_response,
                "tokens_used": tokens_used,
                "rate_limit_remaining": self.rate_limiter.get_remaining(student_id),
                "mock": False
            }

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return {
                "success": False,
                "error": "api_error",
                "message": f"AI service error: {str(e)}",
                "rate_limit_remaining": self.rate_limiter.get_remaining(student_id)
            }
        except Exception as e:
            logger.error(f"Unexpected error in chat_completion: {str(e)}")
            return {
                "success": False,
                "error": "internal_error",
                "message": f"Internal error: {str(e)}",
                "rate_limit_remaining": self.rate_limiter.get_remaining(student_id)
            }

    def _generate_mock_response(self, message: str) -> str:
        """Generate a mock Socratic response when API key is not available"""
        return (
            f"Great question! Let me guide you through this.\n\n"
            f"Before I can help you understand this topic, I'd like to know:\n"
            f"1. What have you already tried?\n"
            f"2. What part of the concept is most confusing?\n"
            f"3. What do you think the first step might be?\n\n"
            f"Remember, the goal isn't just to get the answer - it's to truly "
            f"understand the concept so you can apply it in the future!\n\n"
            f"[Note: This is a mock response - configure OPENAI_API_KEY for full functionality]"
        )


# Singleton instance
_service_instance: Optional[ChatGPTService] = None


def get_chatgpt_service() -> ChatGPTService:
    """Get or create singleton ChatGPT service instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = ChatGPTService()
    return _service_instance
