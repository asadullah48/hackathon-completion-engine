/**
 * AI Todo Parser - Zero-Backend-LLM implementation.
 * All AI parsing runs client-side.
 */

import {
  ParsedTodoResult,
  TodoCategory,
  TodoPriority,
  CreateTodoInput,
} from './types';
import {
  parseWithOpenAI,
  getMockResponse,
  isOpenAIAvailable,
  getRateLimitRemaining,
} from './openaiClient';
import { checkTodoContent } from './constitutionalTodoFilter';

export interface ParseResult {
  success: boolean;
  data?: ParsedTodoResult;
  error?: string;
  usedMock: boolean;
  constitutionalCheck: {
    allowed: boolean;
    decision: string;
    reason?: string;
  };
}

/**
 * Parse natural language input into a structured todo.
 * Includes constitutional validation.
 */
export async function parseTodoWithAI(
  naturalLanguageInput: string
): Promise<ParseResult> {
  if (!naturalLanguageInput.trim()) {
    return {
      success: false,
      error: 'Input cannot be empty',
      usedMock: false,
      constitutionalCheck: { allowed: false, decision: 'block', reason: 'Empty input' },
    };
  }

  // First, check constitutional compliance
  const constitutionalResult = checkTodoContent(naturalLanguageInput);

  if (constitutionalResult.decision === 'block') {
    return {
      success: false,
      error: constitutionalResult.reason,
      usedMock: false,
      constitutionalCheck: constitutionalResult,
    };
  }

  // Parse with AI
  const usedMock = !isOpenAIAvailable() || getRateLimitRemaining() === 0;
  let parsed: ParsedTodoResult;

  try {
    parsed = await parseWithOpenAI(naturalLanguageInput);
  } catch (error) {
    // Fallback to mock on any error
    parsed = getMockResponse(naturalLanguageInput);
  }

  return {
    success: true,
    data: parsed,
    usedMock,
    constitutionalCheck: constitutionalResult,
  };
}

/**
 * Convert parsed result to CreateTodoInput for API submission.
 */
export function toCreateTodoInput(parsed: ParsedTodoResult): CreateTodoInput {
  return {
    title: parsed.title,
    description: parsed.description,
    category: parsed.category,
    priority: parsed.priority,
    deadline: parsed.deadline?.toISOString(),
    ai_metadata: parsed.ai_metadata,
  };
}

/**
 * Quick parse without AI - uses heuristics only.
 * Useful for instant feedback while typing.
 */
export function quickParse(input: string): {
  category: TodoCategory;
  priority: TodoPriority;
  hasDeadline: boolean;
} {
  const lowerInput = input.toLowerCase();

  // Category detection
  let category: TodoCategory = 'other';
  if (/\b(work|meeting|client|project|office|boss)\b/.test(lowerInput)) {
    category = 'work';
  } else if (/\b(study|exam|homework|assignment|class|lecture)\b/.test(lowerInput)) {
    category = 'study';
  } else if (/\b(exercise|gym|health|doctor|medicine|workout)\b/.test(lowerInput)) {
    category = 'health';
  } else if (/\b(buy|groceries|home|call|family|personal)\b/.test(lowerInput)) {
    category = 'personal';
  }

  // Priority detection
  let priority: TodoPriority = 'medium';
  if (/\b(urgent|asap|critical|important|immediately)\b/.test(lowerInput)) {
    priority = 'high';
  } else if (/\b(whenever|eventually|low\s*priority|not\s*urgent)\b/.test(lowerInput)) {
    priority = 'low';
  }

  // Deadline detection
  const hasDeadline = /\b(today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday|next\s*week|by\s*\w+)\b/.test(
    lowerInput
  );

  return { category, priority, hasDeadline };
}

/**
 * Suggest improvements for a todo title.
 */
export function suggestImprovements(title: string): string[] {
  const suggestions: string[] = [];
  const lowerTitle = title.toLowerCase();

  // Check for vague language
  if (/\b(stuff|things|something)\b/.test(lowerTitle)) {
    suggestions.push('Be more specific about what needs to be done');
  }

  // Check for missing action verb
  if (!/^(do|make|create|write|read|study|buy|call|send|prepare|finish|complete|review|update|fix)/i.test(title)) {
    suggestions.push('Start with an action verb (e.g., "Buy", "Review", "Complete")');
  }

  // Check length
  if (title.length < 5) {
    suggestions.push('Add more detail to your task');
  }

  if (title.length > 100) {
    suggestions.push('Consider shortening your title and adding details to description');
  }

  return suggestions;
}

/**
 * Extract deadline from natural language.
 */
export function extractDeadline(input: string): Date | null {
  const lowerInput = input.toLowerCase();
  const now = new Date();

  // Today
  if (/\btoday\b/.test(lowerInput)) {
    return now;
  }

  // Tomorrow
  if (/\btomorrow\b/.test(lowerInput)) {
    const date = new Date(now);
    date.setDate(date.getDate() + 1);
    return date;
  }

  // Days of week
  const days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
  for (let i = 0; i < days.length; i++) {
    if (new RegExp(`\\b${days[i]}\\b`).test(lowerInput)) {
      const date = new Date(now);
      const currentDay = date.getDay();
      const daysUntil = (i - currentDay + 7) % 7 || 7;
      date.setDate(date.getDate() + daysUntil);
      return date;
    }
  }

  // Next week
  if (/\bnext\s*week\b/.test(lowerInput)) {
    const date = new Date(now);
    date.setDate(date.getDate() + 7);
    return date;
  }

  // In X days
  const daysMatch = lowerInput.match(/\bin\s*(\d+)\s*days?\b/);
  if (daysMatch) {
    const date = new Date(now);
    date.setDate(date.getDate() + parseInt(daysMatch[1], 10));
    return date;
  }

  return null;
}

/**
 * Get parsing status info.
 */
export function getParsingStatus(): {
  aiAvailable: boolean;
  rateLimitRemaining: number;
  mode: 'ai' | 'mock';
} {
  const aiAvailable = isOpenAIAvailable();
  const rateLimitRemaining = getRateLimitRemaining();

  return {
    aiAvailable,
    rateLimitRemaining,
    mode: aiAvailable && rateLimitRemaining > 0 ? 'ai' : 'mock',
  };
}
