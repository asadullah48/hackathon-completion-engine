'use client';

import { useState, useEffect } from 'react';
import { RecurrencePattern, RecurringTodo, Todo } from '@/lib/types';
import * as api from '@/lib/api';

interface RecurringPatternSelectorProps {
  todos: Todo[];
  onPatternCreated?: (recurring: RecurringTodo) => void;
}

const DAYS_OF_WEEK = [
  { value: 0, label: 'Mon' },
  { value: 1, label: 'Tue' },
  { value: 2, label: 'Wed' },
  { value: 3, label: 'Thu' },
  { value: 4, label: 'Fri' },
  { value: 5, label: 'Sat' },
  { value: 6, label: 'Sun' },
];

export default function RecurringPatternSelector({
  todos,
  onPatternCreated,
}: RecurringPatternSelectorProps) {
  const [pattern, setPattern] = useState<RecurrencePattern>('daily');
  const [interval, setInterval] = useState(1);
  const [daysOfWeek, setDaysOfWeek] = useState<number[]>([]);
  const [dayOfMonth, setDayOfMonth] = useState(1);
  const [endDate, setEndDate] = useState('');
  const [selectedTodoId, setSelectedTodoId] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [previewDates, setPreviewDates] = useState<string[]>([]);

  // Reset fields when pattern changes
  useEffect(() => {
    setDaysOfWeek([]);
    setDayOfMonth(1);
  }, [pattern]);

  // Fetch preview when pattern details change
  useEffect(() => {
    if (!selectedTodoId) {
      setPreviewDates([]);
      return;
    }

    // Simulate preview (since we need to create first to get preview)
    const dates: string[] = [];
    const now = new Date();

    for (let i = 1; i <= 5; i++) {
      const date = new Date(now);
      if (pattern === 'daily') {
        date.setDate(date.getDate() + i * interval);
      } else if (pattern === 'weekly') {
        date.setDate(date.getDate() + i * 7 * interval);
      } else if (pattern === 'monthly') {
        date.setMonth(date.getMonth() + i * interval);
        if (dayOfMonth) date.setDate(dayOfMonth);
      } else {
        date.setDate(date.getDate() + i * interval);
      }
      dates.push(date.toLocaleDateString('en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
      }));
    }
    setPreviewDates(dates);
  }, [pattern, interval, daysOfWeek, dayOfMonth, selectedTodoId]);

  const handleDayToggle = (day: number) => {
    setDaysOfWeek(prev =>
      prev.includes(day)
        ? prev.filter(d => d !== day)
        : [...prev, day].sort()
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!selectedTodoId) {
      setError('Please select a template todo');
      return;
    }

    setIsLoading(true);

    try {
      const recurring = await api.createRecurring({
        pattern,
        interval,
        days_of_week: pattern === 'weekly' ? daysOfWeek : undefined,
        day_of_month: pattern === 'monthly' ? dayOfMonth : undefined,
        end_date: endDate || undefined,
        template_todo_id: selectedTodoId,
      });

      onPatternCreated?.(recurring);

      // Reset form
      setSelectedTodoId('');
      setPattern('daily');
      setInterval(1);
      setDaysOfWeek([]);
      setDayOfMonth(1);
      setEndDate('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create pattern');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">Create Recurring Pattern</h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Template Todo Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Template Todo
          </label>
          <select
            value={selectedTodoId}
            onChange={(e) => setSelectedTodoId(e.target.value)}
            className="w-full border rounded-md p-2 focus:ring-2 focus:ring-blue-500"
            required
          >
            <option value="">Select a todo to repeat...</option>
            {todos.filter(t => t.status !== 'completed').map(todo => (
              <option key={todo.id} value={todo.id}>
                {todo.title}
              </option>
            ))}
          </select>
        </div>

        {/* Pattern Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Recurrence Pattern
          </label>
          <div className="flex gap-2">
            {(['daily', 'weekly', 'monthly', 'custom'] as RecurrencePattern[]).map(p => (
              <button
                key={p}
                type="button"
                onClick={() => setPattern(p)}
                className={`px-4 py-2 rounded-md capitalize ${
                  pattern === p
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 hover:bg-gray-200'
                }`}
              >
                {p}
              </button>
            ))}
          </div>
        </div>

        {/* Interval */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Every
          </label>
          <div className="flex items-center gap-2">
            <input
              type="number"
              min={1}
              max={365}
              value={interval}
              onChange={(e) => setInterval(parseInt(e.target.value) || 1)}
              className="w-20 border rounded-md p-2"
            />
            <span className="text-gray-600">
              {pattern === 'daily' && 'day(s)'}
              {pattern === 'weekly' && 'week(s)'}
              {pattern === 'monthly' && 'month(s)'}
              {pattern === 'custom' && 'day(s)'}
            </span>
          </div>
        </div>

        {/* Days of Week (for weekly) */}
        {pattern === 'weekly' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Days of Week
            </label>
            <div className="flex gap-2 flex-wrap">
              {DAYS_OF_WEEK.map(day => (
                <button
                  key={day.value}
                  type="button"
                  onClick={() => handleDayToggle(day.value)}
                  className={`px-3 py-1 rounded-full text-sm ${
                    daysOfWeek.includes(day.value)
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 hover:bg-gray-200'
                  }`}
                >
                  {day.label}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Day of Month (for monthly) */}
        {pattern === 'monthly' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Day of Month
            </label>
            <input
              type="number"
              min={1}
              max={31}
              value={dayOfMonth}
              onChange={(e) => setDayOfMonth(parseInt(e.target.value) || 1)}
              className="w-20 border rounded-md p-2"
            />
          </div>
        )}

        {/* End Date */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            End Date (Optional)
          </label>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            min={new Date().toISOString().split('T')[0]}
            className="border rounded-md p-2"
          />
        </div>

        {/* Preview */}
        {previewDates.length > 0 && (
          <div className="bg-gray-50 rounded-md p-4">
            <h3 className="text-sm font-medium text-gray-700 mb-2">
              Next 5 Occurrences Preview
            </h3>
            <div className="flex flex-wrap gap-2">
              {previewDates.map((date, i) => (
                <span
                  key={i}
                  className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm"
                >
                  {date}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-50 text-red-700 p-3 rounded-md">
            {error}
          </div>
        )}

        {/* Submit */}
        <button
          type="submit"
          disabled={isLoading || !selectedTodoId}
          className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Creating...' : 'Create Recurring Pattern'}
        </button>
      </form>
    </div>
  );
}
