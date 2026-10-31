'use client';

/**
 * Create Todo Form Component.
 * AI-powered natural language todo creation with constitutional filtering.
 */

import { useState, useCallback } from 'react';
import {
  Sparkles,
  X,
  Calendar,
  AlertCircle,
  Check,
  Loader2,
} from 'lucide-react';
import { CreateTodoInput, TodoCategory, TodoPriority } from '@/lib/types';
import { parseTodoWithAI, ParseResult } from '@/lib/aiTodoParser';
import { useTodoStore } from '@/lib/store';
import {
  cn,
  CATEGORY_OPTIONS,
  PRIORITY_OPTIONS,
  getCategoryColor,
  getPriorityColor,
} from '@/lib/utils';
import { ConstitutionalAlert } from './ConstitutionalAlert';

interface CreateTodoFormProps {
  onSuccess?: () => void;
  className?: string;
}

export function CreateTodoForm({ onSuccess, className }: CreateTodoFormProps) {
  const { createTodo, isLoading: storeLoading } = useTodoStore();

  // Form state
  const [naturalInput, setNaturalInput] = useState('');
  const [isParsing, setIsParsing] = useState(false);
  const [parseResult, setParseResult] = useState<ParseResult | null>(null);

  // Editable fields after parsing
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState<TodoCategory>('other');
  const [priority, setPriority] = useState<TodoPriority>('medium');
  const [deadline, setDeadline] = useState('');

  // UI state
  const [showSuccess, setShowSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isBlocked = parseResult?.constitutionalCheck?.allowed === false &&
    parseResult?.constitutionalCheck?.decision === 'block';

  const isFlagged = parseResult?.constitutionalCheck?.decision === 'flag';

  const handleParse = useCallback(async () => {
    if (!naturalInput.trim()) return;

    setIsParsing(true);
    setError(null);
    setParseResult(null);

    try {
      const result = await parseTodoWithAI(naturalInput);
      setParseResult(result);

      if (result.success && result.data) {
        setTitle(result.data.title);
        setDescription(result.data.description || '');
        setCategory(result.data.category);
        setPriority(result.data.priority);
        // Convert Date to string for date input
        const deadlineStr = result.data.deadline
          ? result.data.deadline.toISOString().split('T')[0]
          : '';
        setDeadline(deadlineStr);
      } else if (result.error) {
        setError(result.error);
      }
    } catch (err) {
      setError('Failed to parse todo. Please try again.');
    } finally {
      setIsParsing(false);
    }
  }, [naturalInput]);

  const handleCreate = useCallback(async () => {
    if (!title.trim() || isBlocked) return;

    setError(null);

    const input: CreateTodoInput = {
      title: title.trim(),
      description: description.trim() || undefined,
      category,
      priority,
      deadline: deadline || undefined,
    };

    try {
      const result = await createTodo(input);
      if (result) {
        // Success
        setShowSuccess(true);
        setTimeout(() => setShowSuccess(false), 2000);

        // Reset form
        setNaturalInput('');
        setTitle('');
        setDescription('');
        setCategory('other');
        setPriority('medium');
        setDeadline('');
        setParseResult(null);

        onSuccess?.();
      }
    } catch (err) {
      setError('Failed to create todo. Please try again.');
    }
  }, [title, description, category, priority, deadline, isBlocked, createTodo, onSuccess]);

  const handleClear = useCallback(() => {
    setNaturalInput('');
    setTitle('');
    setDescription('');
    setCategory('other');
    setPriority('medium');
    setDeadline('');
    setParseResult(null);
    setError(null);
  }, []);

  const hasParsedData = parseResult?.success && parseResult.data;

  return (
    <div className={cn('bg-white rounded-lg shadow-sm border p-4', className)}>
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Create Todo</h2>

      {/* Natural Language Input */}
      <div className="space-y-3">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Describe your task in natural language
          </label>
          <textarea
            value={naturalInput}
            onChange={(e) => setNaturalInput(e.target.value)}
            placeholder="e.g., Buy groceries tomorrow morning, high priority..."
            className={cn(
              'w-full px-3 py-2 border rounded-lg resize-none transition-colors',
              'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
              'placeholder:text-gray-400'
            )}
            rows={3}
          />
        </div>

        {/* Parse Button */}
        <button
          onClick={handleParse}
          disabled={!naturalInput.trim() || isParsing}
          className={cn(
            'w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium',
            'transition-all duration-200',
            'bg-gradient-to-r from-purple-500 to-blue-500 text-white',
            'hover:from-purple-600 hover:to-blue-600',
            'disabled:opacity-50 disabled:cursor-not-allowed'
          )}
        >
          {isParsing ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Parsing...
            </>
          ) : (
            <>
              <Sparkles className="h-4 w-4" />
              Parse with AI
            </>
          )}
        </button>

        {/* Mock indicator */}
        {parseResult?.usedMock && (
          <p className="text-xs text-gray-500 text-center">
            Using mock AI (set OPENAI_API_KEY for real parsing)
          </p>
        )}
      </div>

      {/* Constitutional Alert */}
      {parseResult && !parseResult.constitutionalCheck.allowed && (
        <div className="mt-4">
          <ConstitutionalAlert
            decision={parseResult.constitutionalCheck.decision as any}
            reason={parseResult.constitutionalCheck.reason}
          />
        </div>
      )}

      {/* Error Alert */}
      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
          <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Parsed Result / Edit Fields */}
      {hasParsedData && !isBlocked && (
        <div className="mt-4 pt-4 border-t space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-700">
              Parsed Result
              {isFlagged && (
                <span className="ml-2 text-amber-600 text-xs">
                  (Will be flagged for review)
                </span>
              )}
            </h3>
            {parseResult.data && (
              <span className="text-xs text-gray-500">
                Confidence: {Math.round((parseResult.data.confidence || 0.8) * 100)}%
              </span>
            )}
          </div>

          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">
              Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className={cn(
                'w-full px-3 py-2 border rounded-lg transition-colors',
                'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
              )}
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">
              Description (optional)
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className={cn(
                'w-full px-3 py-2 border rounded-lg resize-none transition-colors',
                'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
              )}
              rows={2}
            />
          </div>

          {/* Category & Priority */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">
                Category
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value as TodoCategory)}
                className={cn(
                  'w-full px-3 py-2 border rounded-lg transition-colors',
                  'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                  getCategoryColor(category)
                )}
              >
                {CATEGORY_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">
                Priority
              </label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value as TodoPriority)}
                className={cn(
                  'w-full px-3 py-2 border rounded-lg transition-colors',
                  'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
                )}
              >
                {PRIORITY_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Deadline */}
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">
              Deadline (optional)
            </label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="date"
                value={deadline}
                onChange={(e) => setDeadline(e.target.value)}
                className={cn(
                  'w-full pl-10 pr-3 py-2 border rounded-lg transition-colors',
                  'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
                )}
              />
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-2">
            <button
              onClick={handleCreate}
              disabled={!title.trim() || storeLoading}
              className={cn(
                'flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium',
                'bg-green-500 text-white hover:bg-green-600',
                'disabled:opacity-50 disabled:cursor-not-allowed',
                'transition-colors'
              )}
            >
              {storeLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Creating...
                </>
              ) : (
                <>
                  <Check className="h-4 w-4" />
                  Create Todo
                </>
              )}
            </button>

            <button
              onClick={handleClear}
              className={cn(
                'px-4 py-2 rounded-lg font-medium',
                'border border-gray-300 text-gray-700 hover:bg-gray-50',
                'transition-colors'
              )}
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      {/* Success Toast */}
      {showSuccess && (
        <div className="fixed bottom-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg flex items-center gap-2 animate-fade-in">
          <Check className="h-4 w-4" />
          Todo created successfully!
        </div>
      )}
    </div>
  );
}

export default CreateTodoForm;
