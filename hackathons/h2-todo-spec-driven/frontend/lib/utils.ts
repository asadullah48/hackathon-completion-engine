/**
 * Utility functions for H2 Todo frontend.
 */

import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { format, formatDistanceToNow, isPast, isToday, isTomorrow, isThisWeek, parseISO } from 'date-fns';
import { TodoCategory, TodoPriority, TodoStatus } from './types';

/**
 * Merge Tailwind classes with clsx.
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format a date string for display.
 */
export function formatDate(dateString: string | undefined): string {
  if (!dateString) return '';

  try {
    const date = parseISO(dateString);

    if (isToday(date)) {
      return 'Today';
    }
    if (isTomorrow(date)) {
      return 'Tomorrow';
    }
    if (isThisWeek(date)) {
      return format(date, 'EEEE'); // Day name
    }
    return format(date, 'MMM d, yyyy');
  } catch {
    return dateString;
  }
}

/**
 * Format a date as relative time (e.g., "2 hours ago").
 */
export function formatRelativeTime(dateString: string): string {
  try {
    const date = parseISO(dateString);
    return formatDistanceToNow(date, { addSuffix: true });
  } catch {
    return dateString;
  }
}

/**
 * Get deadline status for styling.
 */
export type DeadlineStatus = 'overdue' | 'today' | 'tomorrow' | 'upcoming' | 'none';

export function getDeadlineStatus(deadline: string | undefined): DeadlineStatus {
  if (!deadline) return 'none';

  try {
    const date = parseISO(deadline);

    if (isPast(date) && !isToday(date)) {
      return 'overdue';
    }
    if (isToday(date)) {
      return 'today';
    }
    if (isTomorrow(date)) {
      return 'tomorrow';
    }
    return 'upcoming';
  } catch {
    return 'none';
  }
}

/**
 * Get color classes for category badges.
 */
export function getCategoryColor(category: TodoCategory): string {
  const colors: Record<TodoCategory, string> = {
    work: 'bg-blue-100 text-blue-800 border-blue-200',
    personal: 'bg-pink-100 text-pink-800 border-pink-200',
    study: 'bg-purple-100 text-purple-800 border-purple-200',
    health: 'bg-emerald-100 text-emerald-800 border-emerald-200',
    other: 'bg-gray-100 text-gray-800 border-gray-200',
  };
  return colors[category] || colors.other;
}

/**
 * Get color classes for priority badges.
 */
export function getPriorityColor(priority: TodoPriority): string {
  const colors: Record<TodoPriority, string> = {
    high: 'bg-red-100 text-red-800 border-red-200',
    medium: 'bg-amber-100 text-amber-800 border-amber-200',
    low: 'bg-green-100 text-green-800 border-green-200',
  };
  return colors[priority] || colors.medium;
}

/**
 * Get color classes for status badges.
 */
export function getStatusColor(status: TodoStatus): string {
  const colors: Record<TodoStatus, string> = {
    pending: 'bg-gray-100 text-gray-700 border-gray-200',
    in_progress: 'bg-blue-100 text-blue-700 border-blue-200',
    completed: 'bg-green-100 text-green-700 border-green-200',
    flagged: 'bg-orange-100 text-orange-700 border-orange-200',
  };
  return colors[status] || colors.pending;
}

/**
 * Get priority icon/indicator.
 */
export function getPriorityIndicator(priority: TodoPriority): string {
  const indicators: Record<TodoPriority, string> = {
    high: '↑',
    medium: '→',
    low: '↓',
  };
  return indicators[priority] || indicators.medium;
}

/**
 * Get deadline color based on status.
 */
export function getDeadlineColor(status: DeadlineStatus): string {
  const colors: Record<DeadlineStatus, string> = {
    overdue: 'text-red-600 font-medium',
    today: 'text-amber-600 font-medium',
    tomorrow: 'text-blue-600',
    upcoming: 'text-gray-600',
    none: 'text-gray-400',
  };
  return colors[status];
}

/**
 * Category options for dropdowns.
 */
export const CATEGORY_OPTIONS: { value: TodoCategory; label: string }[] = [
  { value: 'work', label: 'Work' },
  { value: 'personal', label: 'Personal' },
  { value: 'study', label: 'Study' },
  { value: 'health', label: 'Health' },
  { value: 'other', label: 'Other' },
];

/**
 * Priority options for dropdowns.
 */
export const PRIORITY_OPTIONS: { value: TodoPriority; label: string }[] = [
  { value: 'high', label: 'High' },
  { value: 'medium', label: 'Medium' },
  { value: 'low', label: 'Low' },
];

/**
 * Status options for dropdowns.
 */
export const STATUS_OPTIONS: { value: TodoStatus; label: string }[] = [
  { value: 'pending', label: 'Pending' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'completed', label: 'Completed' },
  { value: 'flagged', label: 'Flagged' },
];
