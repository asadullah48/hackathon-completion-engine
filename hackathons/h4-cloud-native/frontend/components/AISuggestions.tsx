'use client';

/**
 * AI Suggestions Component.
 * Displays AI-powered suggestions and productivity insights.
 */

import { useState, useEffect } from 'react';
import {
  Lightbulb,
  TrendingUp,
  CheckCircle,
  X,
  ChevronRight,
  RefreshCw,
  Zap,
  AlertTriangle,
  Calendar,
  Tag,
  LayoutList,
} from 'lucide-react';
import { Suggestion, SuggestionType, SuggestionStatus } from '@/lib/types';
import {
  getSuggestions,
  generateInsights,
  updateSuggestion,
  applySuggestion,
  deleteSuggestion,
} from '@/lib/api';
import { cn } from '@/lib/utils';

interface AISuggestionsProps {
  userId: string;
  onRefreshTodos?: () => void;
  className?: string;
}

const suggestionTypeIcons: Record<SuggestionType, React.ElementType> = {
  priority: AlertTriangle,
  breakdown: LayoutList,
  recurring: RefreshCw,
  insight: TrendingUp,
  deadline: Calendar,
  category: Tag,
};

const suggestionTypeColors: Record<SuggestionType, string> = {
  priority: 'text-orange-600 bg-orange-50 border-orange-200',
  breakdown: 'text-purple-600 bg-purple-50 border-purple-200',
  recurring: 'text-blue-600 bg-blue-50 border-blue-200',
  insight: 'text-green-600 bg-green-50 border-green-200',
  deadline: 'text-red-600 bg-red-50 border-red-200',
  category: 'text-teal-600 bg-teal-50 border-teal-200',
};

export function AISuggestions({ userId, onRefreshTodos, className }: AISuggestionsProps) {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    if (userId) {
      loadSuggestions();
    }
  }, [userId]);

  const loadSuggestions = async () => {
    if (!userId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getSuggestions({ user_id: userId, status: 'pending' });
      setSuggestions(data);
    } catch (err) {
      setError('Failed to load suggestions');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateInsights = async () => {
    if (!userId) return;
    setGenerating(true);
    setError(null);
    try {
      const newInsights = await generateInsights(userId);
      setSuggestions((prev) => [...newInsights, ...prev]);
    } catch (err) {
      setError('Failed to generate insights');
      console.error(err);
    } finally {
      setGenerating(false);
    }
  };

  const handleAccept = async (suggestion: Suggestion) => {
    try {
      if (suggestion.is_actionable && suggestion.todo_id) {
        await applySuggestion(suggestion.id);
        onRefreshTodos?.();
      } else {
        await updateSuggestion(suggestion.id, { status: 'accepted' });
      }
      setSuggestions((prev) => prev.filter((s) => s.id !== suggestion.id));
    } catch (err) {
      console.error('Failed to accept suggestion:', err);
    }
  };

  const handleDismiss = async (suggestion: Suggestion) => {
    try {
      await updateSuggestion(suggestion.id, { status: 'dismissed' });
      setSuggestions((prev) => prev.filter((s) => s.id !== suggestion.id));
    } catch (err) {
      console.error('Failed to dismiss suggestion:', err);
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-gray-500';
  };

  if (loading) {
    return (
      <div className={cn('bg-white rounded-lg border p-6', className)}>
        <div className="flex items-center justify-center py-8">
          <RefreshCw className="h-6 w-6 animate-spin text-gray-400" />
          <span className="ml-2 text-gray-500">Loading suggestions...</span>
        </div>
      </div>
    );
  }

  return (
    <div className={cn('bg-white rounded-lg border', className)}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center gap-2">
          <Lightbulb className="h-5 w-5 text-yellow-500" />
          <h2 className="text-lg font-semibold text-gray-900">AI Suggestions</h2>
          {suggestions.length > 0 && (
            <span className="px-2 py-0.5 text-xs font-medium bg-blue-100 text-blue-700 rounded-full">
              {suggestions.length}
            </span>
          )}
        </div>
        <button
          onClick={handleGenerateInsights}
          disabled={generating}
          className={cn(
            'flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
            generating
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-blue-50 text-blue-600 hover:bg-blue-100'
          )}
        >
          {generating ? (
            <RefreshCw className="h-4 w-4 animate-spin" />
          ) : (
            <Zap className="h-4 w-4" />
          )}
          {generating ? 'Analyzing...' : 'Get Insights'}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="p-4 bg-red-50 border-b border-red-100">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* Suggestions List */}
      <div className="divide-y">
        {suggestions.length === 0 ? (
          <div className="p-8 text-center">
            <Lightbulb className="h-12 w-12 mx-auto text-gray-300 mb-3" />
            <p className="text-gray-500 mb-2">No suggestions yet</p>
            <p className="text-sm text-gray-400">
              Click &quot;Get Insights&quot; to analyze your todos and get personalized recommendations.
            </p>
          </div>
        ) : (
          suggestions.map((suggestion) => {
            const Icon = suggestionTypeIcons[suggestion.suggestion_type];
            const colorClass = suggestionTypeColors[suggestion.suggestion_type];
            const isExpanded = expandedId === suggestion.id;

            return (
              <div key={suggestion.id} className="p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-start gap-3">
                  {/* Type Icon */}
                  <div className={cn('p-2 rounded-lg border', colorClass)}>
                    <Icon className="h-4 w-4" />
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <h3 className="font-medium text-gray-900">{suggestion.title}</h3>
                        <p className="text-sm text-gray-500 mt-0.5">{suggestion.description}</p>
                      </div>
                      <span className={cn('text-xs font-medium', getConfidenceColor(suggestion.confidence))}>
                        {Math.round(suggestion.confidence * 100)}% confident
                      </span>
                    </div>

                    {/* Reasoning (expandable) */}
                    {suggestion.reasoning && (
                      <button
                        onClick={() => setExpandedId(isExpanded ? null : suggestion.id)}
                        className="flex items-center gap-1 mt-2 text-xs text-gray-400 hover:text-gray-600"
                      >
                        <ChevronRight
                          className={cn('h-3 w-3 transition-transform', isExpanded && 'rotate-90')}
                        />
                        {isExpanded ? 'Hide reasoning' : 'Show reasoning'}
                      </button>
                    )}
                    {isExpanded && suggestion.reasoning && (
                      <p className="mt-2 text-sm text-gray-600 bg-gray-50 p-2 rounded">
                        {suggestion.reasoning}
                      </p>
                    )}

                    {/* Subtasks for breakdown suggestions */}
                    {suggestion.suggestion_type === 'breakdown' && suggestion.subtasks.length > 0 && (
                      <div className="mt-3 space-y-1">
                        <p className="text-xs font-medium text-gray-500 uppercase">Suggested subtasks:</p>
                        {suggestion.subtasks.map((subtask, idx) => (
                          <div key={idx} className="flex items-center gap-2 text-sm text-gray-600">
                            <span className="w-5 h-5 flex items-center justify-center bg-gray-100 rounded text-xs">
                              {idx + 1}
                            </span>
                            {subtask.title}
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Actions */}
                    <div className="flex items-center gap-2 mt-3">
                      {suggestion.is_actionable && (
                        <button
                          onClick={() => handleAccept(suggestion)}
                          className="flex items-center gap-1 px-3 py-1 text-sm font-medium text-green-700 bg-green-50 hover:bg-green-100 rounded-md transition-colors"
                        >
                          <CheckCircle className="h-3.5 w-3.5" />
                          Apply
                        </button>
                      )}
                      <button
                        onClick={() => handleDismiss(suggestion)}
                        className="flex items-center gap-1 px-3 py-1 text-sm font-medium text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
                      >
                        <X className="h-3.5 w-3.5" />
                        Dismiss
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Footer with stats */}
      {suggestions.length > 0 && (
        <div className="p-3 bg-gray-50 border-t text-center">
          <p className="text-xs text-gray-500">
            {suggestions.filter((s) => s.is_actionable).length} actionable suggestions
          </p>
        </div>
      )}
    </div>
  );
}

export default AISuggestions;
