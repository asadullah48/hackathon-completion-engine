/**
 * OpenAI client for frontend (Zero-Backend-LLM architecture).
 * All AI logic runs client-side.
 */

import { ParsedTodoResult, TodoCategory, TodoPriority } from './types';

// Rate limiting configuration
const RATE_LIMIT_REQUESTS = 10;
const RATE_LIMIT_WINDOW_MS = 60000; // 1 minute

let requestTimestamps: number[] = [];

/**
 * Check if we're within rate limits.
 */
function checkRateLimit(): boolean {
  const now = Date.now();
  // Remove timestamps outside the window
  requestTimestamps = requestTimestamps.filter(
    (ts) => now - ts < RATE_LIMIT_WINDOW_MS
  );
  return requestTimestamps.length < RATE_LIMIT_REQUESTS;
}

/**
 * Record a request for rate limiting.
 */
function recordRequest(): void {
  requestTimestamps.push(Date.now());
}

/**
 * Get the OpenAI API key from environment.
 */
function getApiKey(): string | null {
  if (typeof window !== 'undefined') {
    // Client-side: check for exposed env var
    return process.env.NEXT_PUBLIC_OPENAI_API_KEY || null;
  }
  return null;
}

/**
 * Parse natural language todo using OpenAI API.
 * Returns mock response if no API key is available.
 */
export async function parseWithOpenAI(input: string): Promise<ParsedTodoResult> {
  const apiKey = getApiKey();

  // If no API key, use mock response
  if (!apiKey) {
    console.log('No OpenAI API key found, using mock response');
    return getMockResponse(input);
  }

  // Check rate limit
  if (!checkRateLimit()) {
    console.warn('Rate limit exceeded, using mock response');
    return getMockResponse(input);
  }

  try {
    recordRequest();

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: 'gpt-3.5-turbo',
        messages: [
          {
            role: 'system',
            content: `You are a todo parser. Extract structured data from natural language input.

Return a JSON object with these fields:
- title: The main task (clean, concise)
- description: Optional additional details
- category: One of: work, personal, study, health, other
- priority: One of: high, medium, low
- deadline: ISO date string if mentioned, otherwise null
- confidence: 0.0 to 1.0 indicating parsing confidence

Examples:
Input: "Buy milk tomorrow"
Output: {"title": "Buy milk", "category": "personal", "priority": "low", "deadline": "${getNextDay()}", "confidence": 0.9}

Input: "Urgent: client meeting prep"
Output: {"title": "Client meeting prep", "category": "work", "priority": "high", "deadline": null, "confidence": 0.85}

Input: "Study chapter 5 for Friday exam"
Output: {"title": "Study chapter 5 for exam", "category": "study", "priority": "medium", "deadline": "${getNextFriday()}", "confidence": 0.9}

Return ONLY valid JSON, no explanations.`,
          },
          {
            role: 'user',
            content: input,
          },
        ],
        temperature: 0.3,
        max_tokens: 200,
      }),
    });

    if (!response.ok) {
      console.error('OpenAI API error:', response.status);
      return getMockResponse(input);
    }

    const data = await response.json();
    const content = data.choices[0]?.message?.content;

    if (!content) {
      return getMockResponse(input);
    }

    const parsed = JSON.parse(content);
    return formatParsedResult(parsed, input);
  } catch (error) {
    console.error('Error calling OpenAI:', error);
    return getMockResponse(input);
  }
}

/**
 * Format the parsed result into our standard format.
 */
function formatParsedResult(parsed: any, rawInput: string): ParsedTodoResult {
  const category = validateCategory(parsed.category);
  const priority = validatePriority(parsed.priority);

  return {
    title: parsed.title || rawInput,
    description: parsed.description,
    category,
    priority,
    deadline: parsed.deadline ? new Date(parsed.deadline) : undefined,
    confidence: typeof parsed.confidence === 'number' ? parsed.confidence : 0.7,
    ai_metadata: {
      inferred_category: category,
      inferred_priority: priority,
      extracted_deadline: parsed.deadline,
      confidence: parsed.confidence || 0.7,
      raw_input: rawInput,
    },
  };
}

/**
 * Validate and normalize category.
 */
function validateCategory(category: string): TodoCategory {
  const valid: TodoCategory[] = ['work', 'personal', 'study', 'health', 'other'];
  const normalized = category?.toLowerCase();
  return valid.includes(normalized as TodoCategory)
    ? (normalized as TodoCategory)
    : 'other';
}

/**
 * Validate and normalize priority.
 */
function validatePriority(priority: string): TodoPriority {
  const valid: TodoPriority[] = ['high', 'medium', 'low'];
  const normalized = priority?.toLowerCase();
  return valid.includes(normalized as TodoPriority)
    ? (normalized as TodoPriority)
    : 'medium';
}

/**
 * Get mock response for when API is unavailable.
 * Uses simple heuristics to parse the input.
 */
export function getMockResponse(input: string): ParsedTodoResult {
  const lowerInput = input.toLowerCase();

  // Detect category
  let category: TodoCategory = 'other';
  if (
    lowerInput.includes('work') ||
    lowerInput.includes('meeting') ||
    lowerInput.includes('client') ||
    lowerInput.includes('project') ||
    lowerInput.includes('deadline')
  ) {
    category = 'work';
  } else if (
    lowerInput.includes('study') ||
    lowerInput.includes('exam') ||
    lowerInput.includes('chapter') ||
    lowerInput.includes('homework') ||
    lowerInput.includes('assignment')
  ) {
    category = 'study';
  } else if (
    lowerInput.includes('exercise') ||
    lowerInput.includes('gym') ||
    lowerInput.includes('run') ||
    lowerInput.includes('health') ||
    lowerInput.includes('doctor')
  ) {
    category = 'health';
  } else if (
    lowerInput.includes('buy') ||
    lowerInput.includes('groceries') ||
    lowerInput.includes('call') ||
    lowerInput.includes('home')
  ) {
    category = 'personal';
  }

  // Detect priority
  let priority: TodoPriority = 'medium';
  if (
    lowerInput.includes('urgent') ||
    lowerInput.includes('asap') ||
    lowerInput.includes('important') ||
    lowerInput.includes('critical')
  ) {
    priority = 'high';
  } else if (
    lowerInput.includes('when possible') ||
    lowerInput.includes('eventually') ||
    lowerInput.includes('low priority')
  ) {
    priority = 'low';
  }

  // Detect deadline
  let deadline: Date | undefined;
  if (lowerInput.includes('tomorrow')) {
    deadline = new Date();
    deadline.setDate(deadline.getDate() + 1);
  } else if (lowerInput.includes('today')) {
    deadline = new Date();
  } else if (lowerInput.includes('friday')) {
    deadline = getNextFridayDate();
  } else if (lowerInput.includes('monday')) {
    deadline = getNextDayOfWeek(1);
  } else if (lowerInput.includes('next week')) {
    deadline = new Date();
    deadline.setDate(deadline.getDate() + 7);
  }

  // Clean up title
  const title = input
    .replace(/^(urgent:?\s*|asap:?\s*|important:?\s*)/i, '')
    .replace(/\s*(tomorrow|today|by friday|next week)\s*/gi, '')
    .trim();

  return {
    title: title || input,
    category,
    priority,
    deadline,
    confidence: 0.6, // Lower confidence for mock
    ai_metadata: {
      inferred_category: category,
      inferred_priority: priority,
      extracted_deadline: deadline?.toISOString(),
      confidence: 0.6,
      raw_input: input,
    },
  };
}

// Helper functions for date calculations
function getNextDay(): string {
  const date = new Date();
  date.setDate(date.getDate() + 1);
  return date.toISOString().split('T')[0];
}

function getNextFriday(): string {
  return getNextFridayDate().toISOString().split('T')[0];
}

function getNextFridayDate(): Date {
  return getNextDayOfWeek(5);
}

function getNextDayOfWeek(dayOfWeek: number): Date {
  const date = new Date();
  const currentDay = date.getDay();
  const daysUntil = (dayOfWeek - currentDay + 7) % 7 || 7;
  date.setDate(date.getDate() + daysUntil);
  return date;
}

/**
 * Check if OpenAI API is available.
 */
export function isOpenAIAvailable(): boolean {
  return !!getApiKey();
}

/**
 * Get remaining rate limit.
 */
export function getRateLimitRemaining(): number {
  const now = Date.now();
  requestTimestamps = requestTimestamps.filter(
    (ts) => now - ts < RATE_LIMIT_WINDOW_MS
  );
  return Math.max(0, RATE_LIMIT_REQUESTS - requestTimestamps.length);
}
