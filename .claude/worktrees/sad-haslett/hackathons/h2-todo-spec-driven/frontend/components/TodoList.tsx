'use client';

/**
 * Todo List Component.
 * Displays todos with sorting and grouping options.
 */

import { useState, useMemo } from 'react';
import {
  List,
  Grid3X3,
  SortAsc,
  SortDesc,
  Inbox,
  Loader2,
} from 'lucide-react';
import { Todo, TodoStatus, TodoCategory } from '@/lib/types';
import { cn } from '@/lib/utils';
import { TodoItem } from './TodoItem';

type SortField = 'created_at' | 'priority' | 'deadline' | 'category';
type SortDirection = 'asc' | 'desc';
type ViewMode = 'list' | 'grid';
type GroupBy = 'none' | 'category' | 'status';

interface TodoListProps {
  todos: Todo[];
  isLoading?: boolean;
  onEdit?: (todo: Todo) => void;
  onDelete?: (todo: Todo) => void;
  onStatusChange?: (todo: Todo, status: TodoStatus) => void;
  className?: string;
}

const PRIORITY_ORDER: Record<string, number> = {
  high: 0,
  medium: 1,
  low: 2,
};

const STATUS_ORDER: Record<string, number> = {
  in_progress: 0,
  pending: 1,
  flagged: 2,
  completed: 3,
};

export function TodoList({
  todos,
  isLoading = false,
  onEdit,
  onDelete,
  onStatusChange,
  className,
}: TodoListProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const [sortField, setSortField] = useState<SortField>('created_at');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [groupBy, setGroupBy] = useState<GroupBy>('none');

  // Sort todos
  const sortedTodos = useMemo(() => {
    const sorted = [...todos].sort((a, b) => {
      let comparison = 0;

      switch (sortField) {
        case 'priority':
          comparison = PRIORITY_ORDER[a.priority] - PRIORITY_ORDER[b.priority];
          break;
        case 'deadline':
          if (!a.deadline && !b.deadline) comparison = 0;
          else if (!a.deadline) comparison = 1;
          else if (!b.deadline) comparison = -1;
          else comparison = new Date(a.deadline).getTime() - new Date(b.deadline).getTime();
          break;
        case 'category':
          comparison = a.category.localeCompare(b.category);
          break;
        case 'created_at':
        default:
          comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
      }

      return sortDirection === 'asc' ? comparison : -comparison;
    });

    return sorted;
  }, [todos, sortField, sortDirection]);

  // Group todos
  const groupedTodos = useMemo(() => {
    if (groupBy === 'none') {
      return { ungrouped: sortedTodos };
    }

    const groups: Record<string, Todo[]> = {};

    sortedTodos.forEach((todo) => {
      const key = groupBy === 'category' ? todo.category : todo.status;
      if (!groups[key]) {
        groups[key] = [];
      }
      groups[key].push(todo);
    });

    // Sort groups
    const sortedGroups: Record<string, Todo[]> = {};
    const keys = Object.keys(groups);

    if (groupBy === 'status') {
      keys.sort((a, b) => STATUS_ORDER[a] - STATUS_ORDER[b]);
    } else {
      keys.sort();
    }

    keys.forEach((key) => {
      sortedGroups[key] = groups[key];
    });

    return sortedGroups;
  }, [sortedTodos, groupBy]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const SortIcon = sortDirection === 'asc' ? SortAsc : SortDesc;

  // Loading state
  if (isLoading) {
    return (
      <div className={cn('bg-white rounded-lg shadow-sm border p-8', className)}>
        <div className="flex flex-col items-center justify-center text-gray-500">
          <Loader2 className="h-8 w-8 animate-spin mb-2" />
          <p>Loading todos...</p>
        </div>
      </div>
    );
  }

  // Empty state
  if (todos.length === 0) {
    return (
      <div className={cn('bg-white rounded-lg shadow-sm border p-8', className)}>
        <div className="flex flex-col items-center justify-center text-gray-500">
          <Inbox className="h-12 w-12 mb-3 text-gray-300" />
          <p className="text-lg font-medium">No todos yet</p>
          <p className="text-sm mt-1">Create your first todo to get started!</p>
        </div>
      </div>
    );
  }

  return (
    <div className={cn('bg-white rounded-lg shadow-sm border', className)}>
      {/* Header / Controls */}
      <div className="flex items-center justify-between p-4 border-b">
        <h2 className="text-lg font-semibold text-gray-900">
          Todos
          <span className="ml-2 text-sm font-normal text-gray-500">
            ({todos.length})
          </span>
        </h2>

        <div className="flex items-center gap-4">
          {/* Group By */}
          <select
            value={groupBy}
            onChange={(e) => setGroupBy(e.target.value as GroupBy)}
            className="text-sm border rounded-lg px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="none">No grouping</option>
            <option value="category">Group by category</option>
            <option value="status">Group by status</option>
          </select>

          {/* Sort */}
          <div className="flex items-center gap-1">
            <select
              value={sortField}
              onChange={(e) => handleSort(e.target.value as SortField)}
              className="text-sm border rounded-lg px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="created_at">Created</option>
              <option value="priority">Priority</option>
              <option value="deadline">Deadline</option>
              <option value="category">Category</option>
            </select>
            <button
              onClick={() => setSortDirection((d) => (d === 'asc' ? 'desc' : 'asc'))}
              className="p-1 hover:bg-gray-100 rounded"
              title={`Sort ${sortDirection === 'asc' ? 'descending' : 'ascending'}`}
            >
              <SortIcon className="h-4 w-4 text-gray-500" />
            </button>
          </div>

          {/* View Mode */}
          <div className="flex border rounded-lg overflow-hidden">
            <button
              onClick={() => setViewMode('list')}
              className={cn(
                'p-1.5',
                viewMode === 'list'
                  ? 'bg-blue-500 text-white'
                  : 'bg-white text-gray-500 hover:bg-gray-50'
              )}
              title="List view"
            >
              <List className="h-4 w-4" />
            </button>
            <button
              onClick={() => setViewMode('grid')}
              className={cn(
                'p-1.5',
                viewMode === 'grid'
                  ? 'bg-blue-500 text-white'
                  : 'bg-white text-gray-500 hover:bg-gray-50'
              )}
              title="Grid view"
            >
              <Grid3X3 className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Todo Items */}
      <div className="p-4">
        {Object.entries(groupedTodos).map(([group, groupTodos]) => (
          <div key={group} className="mb-4 last:mb-0">
            {group !== 'ungrouped' && (
              <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-2">
                {group.replace('_', ' ')}
                <span className="ml-2 text-gray-400">({groupTodos.length})</span>
              </h3>
            )}
            <div
              className={cn(
                viewMode === 'grid'
                  ? 'grid grid-cols-1 md:grid-cols-2 gap-3'
                  : 'space-y-3'
              )}
            >
              {groupTodos.map((todo) => (
                <TodoItem
                  key={todo.id}
                  todo={todo}
                  onEdit={onEdit}
                  onDelete={onDelete}
                  onStatusChange={onStatusChange}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default TodoList;
