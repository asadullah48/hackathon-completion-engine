'use client';

/**
 * Todo Filters Component.
 * Search and filter todos by category, status, priority, and deadline.
 */

import { useState, useCallback, useEffect } from 'react';
import {
  Search,
  Filter,
  X,
  Calendar,
  AlertTriangle,
} from 'lucide-react';
import { TodoFilters as TodoFiltersType, TodoCategory, TodoStatus, TodoPriority } from '@/lib/types';
import {
  cn,
  CATEGORY_OPTIONS,
  STATUS_OPTIONS,
  PRIORITY_OPTIONS,
  getCategoryColor,
  getPriorityColor,
  getStatusColor,
} from '@/lib/utils';

interface TodoFiltersProps {
  filters: TodoFiltersType;
  onFiltersChange: (filters: TodoFiltersType) => void;
  className?: string;
}

type DeadlineFilter = 'all' | 'overdue' | 'today' | 'this_week' | 'no_deadline';

export function TodoFilters({
  filters,
  onFiltersChange,
  className,
}: TodoFiltersProps) {
  const [searchInput, setSearchInput] = useState(filters.search || '');
  const [showFilters, setShowFilters] = useState(false);
  const [deadlineFilter, setDeadlineFilter] = useState<DeadlineFilter>('all');

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchInput !== filters.search) {
        onFiltersChange({ ...filters, search: searchInput || undefined });
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [searchInput, filters, onFiltersChange]);

  const updateFilters = useCallback(
    (updates: Partial<TodoFiltersType>) => {
      onFiltersChange({ ...filters, ...updates });
    },
    [filters, onFiltersChange]
  );

  const toggleCategory = (category: TodoCategory) => {
    const current = filters.category || [];
    const updated = current.includes(category)
      ? current.filter((c) => c !== category)
      : [...current, category];
    updateFilters({ category: updated.length > 0 ? updated : undefined });
  };

  const toggleStatus = (status: TodoStatus) => {
    const current = filters.status || [];
    const updated = current.includes(status)
      ? current.filter((s) => s !== status)
      : [...current, status];
    updateFilters({ status: updated.length > 0 ? updated : undefined });
  };

  const togglePriority = (priority: TodoPriority) => {
    const current = filters.priority || [];
    const updated = current.includes(priority)
      ? current.filter((p) => p !== priority)
      : [...current, priority];
    updateFilters({ priority: updated.length > 0 ? updated : undefined });
  };

  const handleDeadlineFilter = (value: DeadlineFilter) => {
    setDeadlineFilter(value);
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

    switch (value) {
      case 'overdue':
        updateFilters({ deadline_before: today.toISOString().split('T')[0] });
        break;
      case 'today':
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        updateFilters({
          deadline_after: today.toISOString().split('T')[0],
          deadline_before: tomorrow.toISOString().split('T')[0],
        });
        break;
      case 'this_week':
        const weekEnd = new Date(today);
        weekEnd.setDate(weekEnd.getDate() + 7);
        updateFilters({
          deadline_after: today.toISOString().split('T')[0],
          deadline_before: weekEnd.toISOString().split('T')[0],
        });
        break;
      default:
        updateFilters({
          deadline_after: undefined,
          deadline_before: undefined,
        });
    }
  };

  const clearFilters = () => {
    setSearchInput('');
    setDeadlineFilter('all');
    onFiltersChange({});
  };

  const activeFilterCount =
    (filters.category?.length || 0) +
    (filters.status?.length || 0) +
    (filters.priority?.length || 0) +
    (deadlineFilter !== 'all' ? 1 : 0);

  const hasActiveFilters = activeFilterCount > 0 || !!filters.search;

  return (
    <div className={cn('bg-white rounded-lg shadow-sm border p-4', className)}>
      {/* Search Bar */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search todos..."
            className={cn(
              'w-full pl-10 pr-10 py-2 border rounded-lg transition-colors',
              'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
              'placeholder:text-gray-400'
            )}
          />
          {searchInput && (
            <button
              onClick={() => setSearchInput('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>

        <button
          onClick={() => setShowFilters(!showFilters)}
          className={cn(
            'flex items-center gap-2 px-4 py-2 border rounded-lg transition-colors',
            showFilters || activeFilterCount > 0
              ? 'bg-blue-50 border-blue-300 text-blue-700'
              : 'hover:bg-gray-50'
          )}
        >
          <Filter className="h-4 w-4" />
          Filters
          {activeFilterCount > 0 && (
            <span className="bg-blue-500 text-white text-xs rounded-full px-1.5 py-0.5 min-w-[1.25rem]">
              {activeFilterCount}
            </span>
          )}
        </button>

        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="px-3 py-2 text-sm text-gray-500 hover:text-gray-700 hover:bg-gray-50 rounded-lg"
          >
            Clear all
          </button>
        )}
      </div>

      {/* Filter Panel */}
      {showFilters && (
        <div className="mt-4 pt-4 border-t space-y-4">
          {/* Category Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Category
            </label>
            <div className="flex flex-wrap gap-2">
              {CATEGORY_OPTIONS.map((opt) => {
                const isActive = filters.category?.includes(opt.value);
                return (
                  <button
                    key={opt.value}
                    onClick={() => toggleCategory(opt.value)}
                    className={cn(
                      'px-3 py-1.5 rounded-full text-sm font-medium border transition-all',
                      isActive
                        ? cn(getCategoryColor(opt.value), 'ring-2 ring-offset-1 ring-blue-500')
                        : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
                    )}
                  >
                    {opt.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Status Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Status
            </label>
            <div className="flex flex-wrap gap-2">
              {STATUS_OPTIONS.map((opt) => {
                const isActive = filters.status?.includes(opt.value);
                return (
                  <button
                    key={opt.value}
                    onClick={() => toggleStatus(opt.value)}
                    className={cn(
                      'px-3 py-1.5 rounded-full text-sm font-medium border transition-all',
                      isActive
                        ? cn(getStatusColor(opt.value), 'ring-2 ring-offset-1 ring-blue-500')
                        : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
                    )}
                  >
                    {opt.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Priority Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Priority
            </label>
            <div className="flex flex-wrap gap-2">
              {PRIORITY_OPTIONS.map((opt) => {
                const isActive = filters.priority?.includes(opt.value);
                return (
                  <button
                    key={opt.value}
                    onClick={() => togglePriority(opt.value)}
                    className={cn(
                      'px-3 py-1.5 rounded-full text-sm font-medium border transition-all',
                      isActive
                        ? cn(getPriorityColor(opt.value), 'ring-2 ring-offset-1 ring-blue-500')
                        : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
                    )}
                  >
                    {opt.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Deadline Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Deadline
            </label>
            <div className="flex flex-wrap gap-2">
              {[
                { value: 'all', label: 'All' },
                { value: 'overdue', label: 'Overdue' },
                { value: 'today', label: 'Today' },
                { value: 'this_week', label: 'This Week' },
                { value: 'no_deadline', label: 'No Deadline' },
              ].map((opt) => {
                const isActive = deadlineFilter === opt.value;
                return (
                  <button
                    key={opt.value}
                    onClick={() => handleDeadlineFilter(opt.value as DeadlineFilter)}
                    className={cn(
                      'px-3 py-1.5 rounded-full text-sm font-medium border transition-all',
                      isActive
                        ? 'bg-blue-100 text-blue-700 border-blue-300 ring-2 ring-offset-1 ring-blue-500'
                        : 'bg-gray-50 text-gray-600 hover:bg-gray-100',
                      opt.value === 'overdue' && isActive && 'bg-red-100 text-red-700 border-red-300'
                    )}
                  >
                    {opt.value === 'overdue' && <AlertTriangle className="inline h-3 w-3 mr-1" />}
                    {opt.label}
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Active Filter Badges */}
      {hasActiveFilters && !showFilters && (
        <div className="mt-3 flex flex-wrap gap-2">
          {filters.search && (
            <span className="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 rounded-full text-xs">
              Search: "{filters.search}"
              <button onClick={() => setSearchInput('')} className="hover:text-red-500">
                <X className="h-3 w-3" />
              </button>
            </span>
          )}
          {filters.category?.map((c) => (
            <span
              key={c}
              className={cn(
                'inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs',
                getCategoryColor(c)
              )}
            >
              {c}
              <button onClick={() => toggleCategory(c)} className="hover:text-red-500">
                <X className="h-3 w-3" />
              </button>
            </span>
          ))}
          {filters.status?.map((s) => (
            <span
              key={s}
              className={cn(
                'inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs',
                getStatusColor(s)
              )}
            >
              {s.replace('_', ' ')}
              <button onClick={() => toggleStatus(s)} className="hover:text-red-500">
                <X className="h-3 w-3" />
              </button>
            </span>
          ))}
          {filters.priority?.map((p) => (
            <span
              key={p}
              className={cn(
                'inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs',
                getPriorityColor(p)
              )}
            >
              {p}
              <button onClick={() => togglePriority(p)} className="hover:text-red-500">
                <X className="h-3 w-3" />
              </button>
            </span>
          ))}
          {deadlineFilter !== 'all' && (
            <span className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs">
              <Calendar className="h-3 w-3" />
              {deadlineFilter.replace('_', ' ')}
              <button onClick={() => handleDeadlineFilter('all')} className="hover:text-red-500">
                <X className="h-3 w-3" />
              </button>
            </span>
          )}
        </div>
      )}
    </div>
  );
}

export default TodoFilters;
