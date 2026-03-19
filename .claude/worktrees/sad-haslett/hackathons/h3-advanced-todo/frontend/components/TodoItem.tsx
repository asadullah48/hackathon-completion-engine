'use client';

/**
 * Todo Item Component.
 * Displays a single todo with all its details and actions.
 */

import { useState } from 'react';
import {
  Calendar,
  Check,
  Edit2,
  MoreVertical,
  Trash2,
  Clock,
  Play,
  Pause,
} from 'lucide-react';
import { Todo, TodoStatus } from '@/lib/types';
import {
  cn,
  formatDate,
  formatRelativeTime,
  getDeadlineStatus,
  getDeadlineColor,
  getCategoryColor,
  getPriorityColor,
  getStatusColor,
  getPriorityIndicator,
} from '@/lib/utils';
import { ConstitutionalBadge } from './ConstitutionalAlert';

interface TodoItemProps {
  todo: Todo;
  onEdit?: (todo: Todo) => void;
  onDelete?: (todo: Todo) => void;
  onStatusChange?: (todo: Todo, status: TodoStatus) => void;
  className?: string;
}

export function TodoItem({
  todo,
  onEdit,
  onDelete,
  onStatusChange,
  className,
}: TodoItemProps) {
  const [showActions, setShowActions] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const deadlineStatus = getDeadlineStatus(todo.deadline);
  const isCompleted = todo.status === 'completed';
  const isFlagged = todo.status === 'flagged';

  const handleDelete = () => {
    if (isDeleting) {
      onDelete?.(todo);
      setIsDeleting(false);
    } else {
      setIsDeleting(true);
      setTimeout(() => setIsDeleting(false), 3000);
    }
  };

  const handleStatusToggle = () => {
    if (isCompleted) {
      onStatusChange?.(todo, 'pending');
    } else {
      onStatusChange?.(todo, 'completed');
    }
  };

  const handleStartProgress = () => {
    onStatusChange?.(todo, 'in_progress');
  };

  return (
    <div
      className={cn(
        'group relative bg-white border rounded-lg p-4 transition-all duration-200',
        'hover:shadow-md hover:border-gray-300',
        isCompleted && 'bg-gray-50 opacity-75',
        isFlagged && 'border-amber-300 bg-amber-50/30',
        className
      )}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => {
        setShowActions(false);
        setIsDeleting(false);
      }}
    >
      <div className="flex items-start gap-3">
        {/* Checkbox */}
        <button
          onClick={handleStatusToggle}
          className={cn(
            'flex-shrink-0 mt-0.5 w-5 h-5 rounded border-2 transition-colors',
            'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500',
            isCompleted
              ? 'bg-green-500 border-green-500 text-white'
              : 'border-gray-300 hover:border-gray-400'
          )}
          title={isCompleted ? 'Mark as pending' : 'Mark as complete'}
        >
          {isCompleted && <Check className="h-4 w-4" />}
        </button>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Title */}
          <div className="flex items-start gap-2">
            <h3
              className={cn(
                'text-base font-medium text-gray-900',
                isCompleted && 'line-through text-gray-500'
              )}
            >
              {todo.title}
            </h3>
            <ConstitutionalBadge decision={todo.constitutional_check.decision} />
          </div>

          {/* Description */}
          {todo.description && (
            <p
              className={cn(
                'mt-1 text-sm text-gray-600',
                isCompleted && 'line-through text-gray-400'
              )}
            >
              {todo.description}
            </p>
          )}

          {/* Badges */}
          <div className="flex flex-wrap items-center gap-2 mt-3">
            {/* Priority */}
            <span
              className={cn(
                'inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium border',
                getPriorityColor(todo.priority)
              )}
            >
              <span>{getPriorityIndicator(todo.priority)}</span>
              {todo.priority}
            </span>

            {/* Category */}
            <span
              className={cn(
                'px-2 py-0.5 rounded text-xs font-medium border',
                getCategoryColor(todo.category)
              )}
            >
              {todo.category}
            </span>

            {/* Status */}
            <span
              className={cn(
                'px-2 py-0.5 rounded text-xs font-medium border',
                getStatusColor(todo.status)
              )}
            >
              {todo.status.replace('_', ' ')}
            </span>

            {/* Deadline */}
            {todo.deadline && (
              <span
                className={cn(
                  'inline-flex items-center gap-1 text-xs',
                  getDeadlineColor(deadlineStatus)
                )}
              >
                <Calendar className="h-3 w-3" />
                {formatDate(todo.deadline)}
                {deadlineStatus === 'overdue' && ' (overdue)'}
              </span>
            )}
          </div>

          {/* AI Metadata (if available) */}
          {todo.ai_metadata && todo.ai_metadata.confidence < 0.8 && (
            <p className="mt-2 text-xs text-gray-400">
              AI confidence: {Math.round(todo.ai_metadata.confidence * 100)}%
            </p>
          )}

          {/* Created time */}
          <p className="mt-2 text-xs text-gray-400">
            Created {formatRelativeTime(todo.created_at)}
          </p>
        </div>

        {/* Actions */}
        <div
          className={cn(
            'flex-shrink-0 flex items-center gap-1 transition-opacity',
            showActions ? 'opacity-100' : 'opacity-0'
          )}
        >
          {/* Start/Pause Progress */}
          {!isCompleted && todo.status !== 'in_progress' && (
            <button
              onClick={handleStartProgress}
              className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded"
              title="Start progress"
            >
              <Play className="h-4 w-4" />
            </button>
          )}
          {todo.status === 'in_progress' && (
            <button
              onClick={() => onStatusChange?.(todo, 'pending')}
              className="p-1.5 text-blue-500 hover:text-blue-700 hover:bg-blue-50 rounded"
              title="Pause progress"
            >
              <Pause className="h-4 w-4" />
            </button>
          )}

          {/* Edit */}
          <button
            onClick={() => onEdit?.(todo)}
            className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded"
            title="Edit todo"
          >
            <Edit2 className="h-4 w-4" />
          </button>

          {/* Delete */}
          <button
            onClick={handleDelete}
            className={cn(
              'p-1.5 rounded transition-colors',
              isDeleting
                ? 'text-white bg-red-500 hover:bg-red-600'
                : 'text-gray-400 hover:text-red-600 hover:bg-red-50'
            )}
            title={isDeleting ? 'Click again to confirm' : 'Delete todo'}
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

export default TodoItem;
