/**
 * Tests for Constitutional Todo Filter (frontend).
 */
import { describe, it, expect } from 'vitest';
import {
  checkTodoContent,
  validateTodo,
  hasWarningPatterns,
  getDecisionMessage,
} from '../lib/constitutionalTodoFilter';

describe('Constitutional Todo Filter', () => {
  describe('checkTodoContent', () => {
    describe('Blocked patterns', () => {
      it('should block "do my homework" requests', () => {
        const result = checkTodoContent('Do my homework assignment');
        expect(result.allowed).toBe(false);
        expect(result.decision).toBe('block');
        expect(result.reason).toContain('Academic dishonesty');
      });

      it('should block "write my essay" requests', () => {
        const result = checkTodoContent('Write my essay for class');
        expect(result.allowed).toBe(false);
        expect(result.decision).toBe('block');
      });

      it('should block hacking requests', () => {
        const result = checkTodoContent('Hack into the database');
        expect(result.allowed).toBe(false);
        expect(result.decision).toBe('block');
        expect(result.reason).toContain('Illegal activity');
      });

      it('should block fake documents requests', () => {
        const result = checkTodoContent('Create fake documents for visa');
        expect(result.allowed).toBe(false);
        expect(result.decision).toBe('block');
      });

      it('should block harassment requests', () => {
        const result = checkTodoContent('Harass the competitor');
        expect(result.allowed).toBe(false);
        expect(result.decision).toBe('block');
        expect(result.reason).toContain('Harmful action');
      });

      it('should block plagiarism requests', () => {
        const result = checkTodoContent('Plagiarize this paper');
        expect(result.allowed).toBe(false);
        expect(result.decision).toBe('block');
      });

      it('should block cheating requests', () => {
        const result = checkTodoContent('Cheat on the exam');
        expect(result.allowed).toBe(false);
        expect(result.decision).toBe('block');
      });
    });

    describe('Allowed patterns', () => {
      it('should allow study tasks', () => {
        const result = checkTodoContent('Study for exam tomorrow');
        expect(result.allowed).toBe(true);
        expect(result.decision).toBe('allow');
      });

      it('should allow work tasks', () => {
        const result = checkTodoContent('Complete work project proposal');
        expect(result.allowed).toBe(true);
        expect(result.decision).toBe('allow');
      });

      it('should allow exercise tasks', () => {
        const result = checkTodoContent('Exercise for 30 minutes');
        expect(result.allowed).toBe(true);
        expect(result.decision).toBe('allow');
      });

      it('should allow practice tasks', () => {
        const result = checkTodoContent('Practice coding exercises');
        expect(result.allowed).toBe(true);
        expect(result.decision).toBe('allow');
      });

      it('should allow research tasks', () => {
        const result = checkTodoContent('Research topic for paper');
        expect(result.allowed).toBe(true);
        expect(result.decision).toBe('allow');
      });

      it('should allow personal tasks', () => {
        const result = checkTodoContent('Buy groceries');
        expect(result.allowed).toBe(true);
        expect(result.decision).toBe('allow');
      });
    });

    describe('Flagged patterns', () => {
      it('should flag urgent assignment requests', () => {
        const result = checkTodoContent('Urgent: finish assignment in 1 hour');
        expect(result.allowed).toBe(true);
        expect(result.decision).toBe('flag');
        expect(result.reason).toContain('flagged for human review');
      });

      it('should flag urgent complete assignment', () => {
        const result = checkTodoContent('Urgent need to complete assignment tonight');
        expect(result.allowed).toBe(true);
        expect(result.decision).toBe('flag');
      });

      it('should flag deadline complete assignment', () => {
        const result = checkTodoContent('Deadline to complete assignment is tonight');
        expect(result.allowed).toBe(true);
        expect(result.decision).toBe('flag');
      });
    });

    describe('Edge cases', () => {
      it('should allow empty content', () => {
        const result = checkTodoContent('');
        expect(result.allowed).toBe(true);
        expect(result.decision).toBe('allow');
      });

      it('should be case-insensitive for blocking', () => {
        const result = checkTodoContent('DO MY HOMEWORK ASSIGNMENT');
        expect(result.allowed).toBe(false);
        expect(result.decision).toBe('block');
      });
    });
  });

  describe('validateTodo', () => {
    it('should validate both title and description', () => {
      const result = validateTodo('Study session', 'Review chapter 5');
      expect(result.allowed).toBe(true);
      expect(result.decision).toBe('allow');
    });

    it('should block if title is blocked', () => {
      const result = validateTodo('Do my homework', 'Please complete it');
      expect(result.allowed).toBe(false);
      expect(result.decision).toBe('block');
    });

    it('should block if description is blocked', () => {
      const result = validateTodo('Help needed', 'Hack into the system');
      expect(result.allowed).toBe(false);
      expect(result.decision).toBe('block');
    });

    it('should flag if title is flagged', () => {
      const result = validateTodo('Urgent need to finish assignment now', 'Help');
      expect(result.allowed).toBe(true);
      expect(result.decision).toBe('flag');
    });
  });

  describe('hasWarningPatterns', () => {
    it('should detect academic dishonesty patterns', () => {
      const result = hasWarningPatterns('do my homework');
      expect(result.hasWarning).toBe(true);
      expect(result.warningType).toBe('academic');
    });

    it('should detect illegal activity patterns', () => {
      const result = hasWarningPatterns('hack into server');
      expect(result.hasWarning).toBe(true);
      expect(result.warningType).toBe('illegal');
    });

    it('should detect harmful action patterns', () => {
      const result = hasWarningPatterns('harass them');
      expect(result.hasWarning).toBe(true);
      expect(result.warningType).toBe('harmful');
    });

    it('should detect flag patterns', () => {
      const result = hasWarningPatterns('urgent finish assignment');
      expect(result.hasWarning).toBe(true);
      expect(result.warningType).toBe('flag');
    });

    it('should not detect warnings in safe content', () => {
      const result = hasWarningPatterns('study for exam');
      expect(result.hasWarning).toBe(false);
    });
  });

  describe('getDecisionMessage', () => {
    it('should return correct message for allow', () => {
      const msg = getDecisionMessage('allow');
      expect(msg.icon).toBe('✅');
      expect(msg.title).toBe('Todo Allowed');
    });

    it('should return correct message for block', () => {
      const msg = getDecisionMessage('block');
      expect(msg.icon).toBe('🚫');
      expect(msg.title).toBe('Todo Blocked');
    });

    it('should return correct message for flag', () => {
      const msg = getDecisionMessage('flag');
      expect(msg.icon).toBe('🚩');
      expect(msg.title).toBe('Todo Flagged');
    });
  });
});
