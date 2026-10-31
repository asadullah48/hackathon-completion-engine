/**
 * Tests for AI Todo Parser.
 */
import { describe, it, expect } from 'vitest';
import {
  quickParse,
  extractDeadline,
  suggestImprovements,
  getParsingStatus,
} from '../lib/aiTodoParser';
import { getMockResponse } from '../lib/openaiClient';

describe('AI Todo Parser', () => {
  describe('getMockResponse', () => {
    it('should parse simple todo', () => {
      const result = getMockResponse('Buy milk');
      expect(result.title).toBe('Buy milk');
      expect(result.category).toBe('personal');
      expect(result.confidence).toBe(0.6);
    });

    it('should detect work category', () => {
      const result = getMockResponse('Prepare for client meeting');
      expect(result.category).toBe('work');
    });

    it('should detect study category', () => {
      const result = getMockResponse('Study chapter 5 for exam');
      expect(result.category).toBe('study');
    });

    it('should detect health category', () => {
      const result = getMockResponse('Exercise for 30 minutes');
      expect(result.category).toBe('health');
    });

    it('should detect high priority from urgent', () => {
      const result = getMockResponse('Urgent: fix the bug');
      expect(result.priority).toBe('high');
    });

    it('should detect low priority', () => {
      const result = getMockResponse('When possible clean the desk');
      expect(result.priority).toBe('low');
    });

    it('should extract tomorrow deadline', () => {
      const result = getMockResponse('Buy milk tomorrow');
      expect(result.deadline).toBeDefined();
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      expect(result.deadline?.toDateString()).toBe(tomorrow.toDateString());
    });

    it('should extract today deadline', () => {
      const result = getMockResponse('Finish report today');
      expect(result.deadline).toBeDefined();
      expect(result.deadline?.toDateString()).toBe(new Date().toDateString());
    });

    it('should clean title from keywords', () => {
      const result = getMockResponse('Urgent: buy milk tomorrow');
      expect(result.title).toBe('buy milk');
    });

    it('should include ai_metadata', () => {
      const result = getMockResponse('Test todo');
      expect(result.ai_metadata).toBeDefined();
      expect(result.ai_metadata.raw_input).toBe('Test todo');
      expect(result.ai_metadata.confidence).toBe(0.6);
    });
  });

  describe('quickParse', () => {
    it('should detect work category', () => {
      const result = quickParse('Meeting with client');
      expect(result.category).toBe('work');
    });

    it('should detect study category', () => {
      const result = quickParse('Study for exam');
      expect(result.category).toBe('study');
    });

    it('should detect health category', () => {
      const result = quickParse('Go to gym');
      expect(result.category).toBe('health');
    });

    it('should detect personal category', () => {
      const result = quickParse('Buy groceries');
      expect(result.category).toBe('personal');
    });

    it('should default to other category', () => {
      const result = quickParse('Random task');
      expect(result.category).toBe('other');
    });

    it('should detect high priority', () => {
      const result = quickParse('Urgent task');
      expect(result.priority).toBe('high');
    });

    it('should detect low priority', () => {
      const result = quickParse('Eventually do this');
      expect(result.priority).toBe('low');
    });

    it('should default to medium priority', () => {
      const result = quickParse('Normal task');
      expect(result.priority).toBe('medium');
    });

    it('should detect deadline keywords', () => {
      const result = quickParse('Do this tomorrow');
      expect(result.hasDeadline).toBe(true);
    });

    it('should not detect deadline when not present', () => {
      const result = quickParse('Normal task');
      expect(result.hasDeadline).toBe(false);
    });
  });

  describe('extractDeadline', () => {
    it('should extract today', () => {
      const result = extractDeadline('Finish this today');
      expect(result).toBeDefined();
      expect(result?.toDateString()).toBe(new Date().toDateString());
    });

    it('should extract tomorrow', () => {
      const result = extractDeadline('Do this tomorrow');
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      expect(result?.toDateString()).toBe(tomorrow.toDateString());
    });

    it('should extract next week', () => {
      const result = extractDeadline('Complete next week');
      const nextWeek = new Date();
      nextWeek.setDate(nextWeek.getDate() + 7);
      expect(result?.toDateString()).toBe(nextWeek.toDateString());
    });

    it('should extract "in X days"', () => {
      const result = extractDeadline('Finish in 3 days');
      const expected = new Date();
      expected.setDate(expected.getDate() + 3);
      expect(result?.toDateString()).toBe(expected.toDateString());
    });

    it('should return null when no deadline', () => {
      const result = extractDeadline('Random task');
      expect(result).toBeNull();
    });
  });

  describe('suggestImprovements', () => {
    it('should suggest specificity for vague words', () => {
      const suggestions = suggestImprovements('Do stuff');
      expect(suggestions).toContain('Be more specific about what needs to be done');
    });

    it('should suggest action verb', () => {
      const suggestions = suggestImprovements('The report');
      expect(suggestions.some((s) => s.includes('action verb'))).toBe(true);
    });

    it('should suggest more detail for short titles', () => {
      const suggestions = suggestImprovements('Hi');
      expect(suggestions).toContain('Add more detail to your task');
    });

    it('should suggest shortening for long titles', () => {
      const longTitle = 'A'.repeat(150);
      const suggestions = suggestImprovements(longTitle);
      expect(suggestions.some((s) => s.includes('shortening'))).toBe(true);
    });

    it('should return empty for good titles', () => {
      const suggestions = suggestImprovements('Complete the project report');
      expect(suggestions.length).toBe(0);
    });
  });

  describe('getParsingStatus', () => {
    it('should return parsing status info', () => {
      const status = getParsingStatus();
      expect(status).toHaveProperty('aiAvailable');
      expect(status).toHaveProperty('rateLimitRemaining');
      expect(status).toHaveProperty('mode');
      expect(['ai', 'mock']).toContain(status.mode);
    });
  });
});
