/**
 * Constitutional Todo Filter - Frontend validation.
 * Mirrors backend validation for immediate feedback.
 *
 * Enforces rules against:
 * - Academic dishonesty
 * - Illegal activities
 * - Harmful actions
 */

import { ConstitutionalFilterResult, ConstitutionalDecision } from './types';

// Prohibited patterns for academic dishonesty
const ACADEMIC_DISHONESTY_PATTERNS: RegExp[] = [
  /\bdo\s+(my|the)\s+homework\b/i,
  /\bwrite\s+(my|the)\s+essay\b/i,
  /\bcomplete\s+(my|the)\s+coding\s+project\b/i,
  /\btake\s+(my|the)\s+exam\b/i,
  /\bfinish\s+(my|the)\s+assignment\s+for\s+me\b/i,
  /\bdo\s+(my|the)\s+project\s+for\s+me\b/i,
  /\bwrite\s+(my|the)\s+paper\s+for\s+me\b/i,
  /\bsubmit\s+(my|the)\s+work\s+for\s+me\b/i,
  /\bcopy\s+someone('s|s)\s+work\b/i,
  /\bplagiarize\b/i,
  /\bcheat\s+on\b/i,
];

// Prohibited patterns for illegal activities
const ILLEGAL_ACTIVITY_PATTERNS: RegExp[] = [
  /\bhack\s+into\b/i,
  /\bcreate\s+fake\s+documents?\b/i,
  /\bbypass\s+security\b/i,
  /\bsteal\s+(data|information|credentials)\b/i,
  /\bbreak\s+into\b/i,
  /\billegal\s+access\b/i,
  /\bcrack\s+password\b/i,
  /\bforge\s+(documents?|signatures?)\b/i,
  /\bphishing\b/i,
  /\bmalware\b/i,
  /\bransomware\b/i,
];

// Prohibited patterns for harmful actions
const HARMFUL_ACTION_PATTERNS: RegExp[] = [
  /\bharass\b/i,
  /\bspread\s+misinformation\b/i,
  /\bcreate\s+harmful\s+content\b/i,
  /\bbully\b/i,
  /\bthreaten\b/i,
  /\bstalk\b/i,
  /\bdoxing\b/i,
  /\bdefame\b/i,
  /\bslander\b/i,
  /\bhate\s+speech\b/i,
  /\bviolent\s+content\b/i,
];

// Patterns that need human review (flagged)
const FLAG_PATTERNS: RegExp[] = [
  /\burgent.*finish.*assignment\b/i,
  /\burgent.*complete.*assignment\b/i,
  /\bneed.*done.*exam\s+tomorrow\b/i,
  /\bdeadline.*complete.*assignment\b/i,
  /\blast\s+minute.*finish.*homework\b/i,
  /\bsubmit.*someone\s+else\b/i,
  /\bhelp.*finish.*assignment.*urgent\b/i,
];

/**
 * Check todo content against constitutional rules.
 */
export function checkTodoContent(content: string): ConstitutionalFilterResult {
  if (!content || content.trim() === '') {
    return { allowed: true, decision: 'allow' };
  }

  // Check academic dishonesty
  for (const pattern of ACADEMIC_DISHONESTY_PATTERNS) {
    if (pattern.test(content)) {
      return {
        allowed: false,
        decision: 'block',
        reason:
          'Academic dishonesty detected. Todos that request completing academic work for you are not allowed.',
      };
    }
  }

  // Check illegal activities
  for (const pattern of ILLEGAL_ACTIVITY_PATTERNS) {
    if (pattern.test(content)) {
      return {
        allowed: false,
        decision: 'block',
        reason:
          'Illegal activity detected. Todos involving hacking, fraud, or other illegal actions are not allowed.',
      };
    }
  }

  // Check harmful actions
  for (const pattern of HARMFUL_ACTION_PATTERNS) {
    if (pattern.test(content)) {
      return {
        allowed: false,
        decision: 'block',
        reason:
          'Harmful action detected. Todos involving harassment or harmful content are not allowed.',
      };
    }
  }

  // Check for flagged patterns (need human review)
  for (const pattern of FLAG_PATTERNS) {
    if (pattern.test(content)) {
      return {
        allowed: true, // Allowed but flagged
        decision: 'flag',
        reason:
          'This todo has been flagged for human review due to potential academic integrity concerns.',
      };
    }
  }

  // All checks passed
  return { allowed: true, decision: 'allow' };
}

/**
 * Validate both title and description.
 */
export function validateTodo(
  title: string,
  description?: string
): ConstitutionalFilterResult {
  // Check title first
  const titleResult = checkTodoContent(title);
  if (titleResult.decision === 'block') {
    return titleResult;
  }

  // Check description if provided
  if (description) {
    const descResult = checkTodoContent(description);
    if (descResult.decision === 'block') {
      return descResult;
    }
    // If description is flagged, flag the whole todo
    if (descResult.decision === 'flag') {
      return descResult;
    }
  }

  // Return title result (could be ALLOW or FLAG)
  return titleResult;
}

/**
 * Get a user-friendly message for a decision.
 */
export function getDecisionMessage(
  decision: ConstitutionalDecision
): { icon: string; title: string; description: string } {
  switch (decision) {
    case 'allow':
      return {
        icon: '✅',
        title: 'Todo Allowed',
        description: 'This todo meets our content guidelines.',
      };
    case 'block':
      return {
        icon: '🚫',
        title: 'Todo Blocked',
        description:
          'This todo violates our content guidelines and cannot be created.',
      };
    case 'flag':
      return {
        icon: '🚩',
        title: 'Todo Flagged',
        description:
          'This todo has been flagged for review and may require approval.',
      };
  }
}

/**
 * Check if content contains any concerning patterns (for real-time feedback).
 */
export function hasWarningPatterns(content: string): {
  hasWarning: boolean;
  warningType?: 'academic' | 'illegal' | 'harmful' | 'flag';
} {
  if (!content) return { hasWarning: false };

  // Check each pattern category
  for (const pattern of ACADEMIC_DISHONESTY_PATTERNS) {
    if (pattern.test(content)) {
      return { hasWarning: true, warningType: 'academic' };
    }
  }

  for (const pattern of ILLEGAL_ACTIVITY_PATTERNS) {
    if (pattern.test(content)) {
      return { hasWarning: true, warningType: 'illegal' };
    }
  }

  for (const pattern of HARMFUL_ACTION_PATTERNS) {
    if (pattern.test(content)) {
      return { hasWarning: true, warningType: 'harmful' };
    }
  }

  for (const pattern of FLAG_PATTERNS) {
    if (pattern.test(content)) {
      return { hasWarning: true, warningType: 'flag' };
    }
  }

  return { hasWarning: false };
}

/**
 * Get examples of allowed vs blocked content.
 */
export function getContentGuidelines(): {
  allowed: string[];
  blocked: string[];
  flagged: string[];
} {
  return {
    allowed: [
      'Study for exam tomorrow',
      'Practice coding exercises',
      'Research topic for paper',
      'Complete work project',
      'Buy groceries',
      'Exercise for 30 minutes',
    ],
    blocked: [
      'Do my homework assignment',
      'Write my essay for me',
      'Hack into database',
      'Create fake documents',
      'Harass competitor',
    ],
    flagged: [
      'Urgent: finish assignment in 1 hour',
      'Need this done before exam tomorrow',
    ],
  };
}
