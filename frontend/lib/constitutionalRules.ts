/**
 * Constitutional Rules - Frontend Implementation
 * Mirrors backend patterns for client-side validation
 */

export interface CheckResult {
  allowed: boolean;
  decision: 'allow' | 'block' | 'flag';
  reason: string;
  pattern?: string;
}

// Prohibited patterns - These MUST be blocked (same as backend)
const PROHIBITED_PATTERNS: RegExp[] = [
  /solve\s+(this|my|the)\s+(homework|assignment|problem)/i,
  /write\s+(the|this|my)\s+code\s+for\s+me/i,
  /give\s+me\s+the\s+answer/i,
  /do\s+my\s+(homework|assignment|test|quiz)/i,
  /complete\s+(this|my)\s+(assignment|homework)/i,
  /(what|tell me)\s+(is|are)\s+the\s+answer/i,
  /just\s+give\s+me\s+the\s+(answer|solution|code)/i,
];

// Suspicious patterns - These should be FLAGGED for human review (same as backend)
const SUSPICIOUS_PATTERNS: RegExp[] = [
  /(exam|test|quiz)\s+(tomorrow|today|in\s+\d+\s+(hour|minute))/i,
  /due\s+in\s+\d+\s+(hour|minute)/i,
  /urgent(ly)?\s+(need|want)/i,
  /deadline\s+(is\s+)?(tomorrow|today|tonight)/i,
  /no\s+time/i,
];

// User-friendly warning messages
const WARNING_MESSAGES = {
  block: {
    homework: "It looks like you're asking for a direct homework solution. I'm here to help you learn, not to do your work for you. Try asking about the concepts instead!",
    code: "I can't write your code for you, but I can help you understand how to write it yourself. What specific concept are you struggling with?",
    answer: "I can't just give you the answer, but I can guide you through the problem-solving process. What have you tried so far?",
    default: "This request appears to be asking for direct academic work. Let's focus on learning the concepts instead!"
  },
  flag: {
    urgency: "I notice you're under time pressure. While I want to help, I need to ensure we're focusing on learning. A human instructor will review this request.",
    deadline: "Deadline pressure can be stressful! However, I can't compromise on academic integrity. Let me help you understand the material instead.",
    default: "Your request has been flagged for review. In the meantime, I can help you with general concept explanations."
  }
};

/**
 * Check if a query violates constitutional rules
 * @param query - The user's input query
 * @returns CheckResult with decision and reason
 */
export function checkQuery(query: string): CheckResult {
  const queryLower = query.toLowerCase();

  // Check prohibited patterns first
  for (const pattern of PROHIBITED_PATTERNS) {
    if (pattern.test(queryLower)) {
      let warningKey: keyof typeof WARNING_MESSAGES.block = 'default';

      if (/homework|assignment/.test(queryLower)) warningKey = 'homework';
      else if (/code/.test(queryLower)) warningKey = 'code';
      else if (/answer/.test(queryLower)) warningKey = 'answer';

      return {
        allowed: false,
        decision: 'block',
        reason: WARNING_MESSAGES.block[warningKey],
        pattern: pattern.source
      };
    }
  }

  // Check suspicious patterns
  for (const pattern of SUSPICIOUS_PATTERNS) {
    if (pattern.test(queryLower)) {
      let warningKey: keyof typeof WARNING_MESSAGES.flag = 'default';

      if (/urgent|no\s+time/.test(queryLower)) warningKey = 'urgency';
      else if (/deadline|due|tomorrow|today/.test(queryLower)) warningKey = 'deadline';

      return {
        allowed: true, // Allow to send but flag it
        decision: 'flag',
        reason: WARNING_MESSAGES.flag[warningKey],
        pattern: pattern.source
      };
    }
  }

  // Query is allowed
  return {
    allowed: true,
    decision: 'allow',
    reason: 'Query approved for submission'
  };
}

/**
 * Get a preview warning for the user while typing
 * @param query - The current input
 * @returns Warning message or null if no issues
 */
export function getTypingWarning(query: string): string | null {
  if (query.length < 10) return null;

  const result = checkQuery(query);

  if (result.decision === 'block') {
    return result.reason;
  }

  if (result.decision === 'flag') {
    return "This message may be flagged for review due to urgency indicators.";
  }

  return null;
}

/**
 * Constitutional rules summary for display
 */
export const CONSTITUTIONAL_RULES = [
  {
    title: "No Direct Solutions",
    description: "I cannot provide complete homework solutions or write code for assignments.",
    icon: "ban"
  },
  {
    title: "Socratic Learning",
    description: "I guide you through concepts using questions and explanations.",
    icon: "help-circle"
  },
  {
    title: "Concept Explanations",
    description: "I can explain any programming concept, algorithm, or theory.",
    icon: "book-open"
  },
  {
    title: "Debugging Help",
    description: "I can help you understand errors and guide you to fix them.",
    icon: "bug"
  },
  {
    title: "Human Review",
    description: "Urgent requests are flagged for instructor review.",
    icon: "eye"
  }
];
