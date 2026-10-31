'use client';

/**
 * Edit Todo Modal Component.
 * Slide-in panel for editing existing todos.
 */

import { useState, useEffect, useCallback } from 'react';
import {
  X,
  Save,
  Trash2,
  Calendar,
  Loader2,
  AlertCircle,
} from 'lucide-react';
import {
  Todo,
  UpdateTodoInput,
  TodoCategory,
  TodoPriority,
  TodoStatus,
} from '@/lib/types';
import { checkTodoContent } from '@/lib/constitutionalTodoFilter';
import {
  cn,
  CATEGORY_OPTIONS,
  PRIORITY_OPTIONS,
  STATUS_OPTIONS,
} from '@/lib/utils';
import { ConstitutionalAlert } from './ConstitutionalAlert';

interface EditTodoModalProps {
  todo: Todo | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (id: string, updates: UpdateTodoInput) => Promise<void>;
  onDelete: (todo: Todo) => Promise<void>;
}

export function EditTodoModal({
  todo,
  isOpen,
  onClose,
  onSave,
  onDelete,
}: EditTodoModalProps) {
  // Form state
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState<TodoCategory>('other');
  const [priority, setPriority] = useState<TodoPriority>('medium');
  const [status, setStatus] = useState<TodoStatus>('pending');
  const [deadline, setDeadline] = useState('');

  // UI state
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [constitutionalResult, setConstitutionalResult] = useState<ReturnType<typeof checkTodoContent> | null>(null);

  // Initialize form when todo changes
  useEffect(() => {
    if (todo) {
      setTitle(todo.title);
      setDescription(todo.description || '');
      setCategory(todo.category);
      setPriority(todo.priority);
      setStatus(todo.status);
      setDeadline(todo.deadline || '');
      setError(null);
      setConstitutionalResult(null);
      setConfirmDelete(false);
    }
  }, [todo]);

  // Check constitutional compliance when title/description changes
  useEffect(() => {
    if (todo && (title !== todo.title || description !== (todo.description || ''))) {
      // Combine title and description for constitutional check
      const combinedContent = `${title} ${description}`.trim();
      const result = checkTodoContent(combinedContent);
      setConstitutionalResult(result);
    } else {
      setConstitutionalResult(null);
    }
  }, [title, description, todo]);

  const handleSave = useCallback(async () => {
    if (!todo || !title.trim()) return;
    if (constitutionalResult && !constitutionalResult.allowed && constitutionalResult.decision === 'block') {
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      const updates: UpdateTodoInput = {
        title: title.trim(),
        description: description.trim() || undefined,
        category,
        priority,
        status,
        deadline: deadline || undefined,
      };
      await onSave(todo.id, updates);
      onClose();
    } catch (err) {
      setError('Failed to save changes. Please try again.');
    } finally {
      setIsSaving(false);
    }
  }, [todo, title, description, category, priority, status, deadline, constitutionalResult, onSave, onClose]);

  const handleDelete = useCallback(async () => {
    if (!todo) return;

    if (!confirmDelete) {
      setConfirmDelete(true);
      return;
    }

    setIsDeleting(true);
    try {
      await onDelete(todo);
      onClose();
    } catch (err) {
      setError('Failed to delete todo. Please try again.');
    } finally {
      setIsDeleting(false);
      setConfirmDelete(false);
    }
  }, [todo, confirmDelete, onDelete, onClose]);

  const handleClose = useCallback(() => {
    setConfirmDelete(false);
    onClose();
  }, [onClose]);

  const isBlocked = !!(constitutionalResult && !constitutionalResult.allowed && constitutionalResult.decision === 'block');

  if (!isOpen || !todo) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 z-40 transition-opacity"
        onClick={handleClose}
      />

      {/* Modal Panel */}
      <div
        className={cn(
          'fixed right-0 top-0 bottom-0 w-full max-w-md bg-white shadow-xl z-50',
          'transform transition-transform duration-300',
          isOpen ? 'translate-x-0' : 'translate-x-full'
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold">Edit Todo</h2>
          <button
            onClick={handleClose}
            className="p-2 hover:bg-gray-100 rounded-lg"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-4 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 180px)' }}>
          {/* Error Alert */}
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
              <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {/* Constitutional Alert */}
          {constitutionalResult && !constitutionalResult.allowed && (
            <ConstitutionalAlert
              decision={constitutionalResult.decision}
              reason={constitutionalResult.reason}
            />
          )}

          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className={cn(
                'w-full px-3 py-2 border rounded-lg transition-colors',
                'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                isBlocked && 'border-red-300 bg-red-50'
              )}
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className={cn(
                'w-full px-3 py-2 border rounded-lg resize-none transition-colors',
                'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
              )}
              rows={3}
            />
          </div>

          {/* Category */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Category
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value as TodoCategory)}
              className={cn(
                'w-full px-3 py-2 border rounded-lg transition-colors',
                'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
              )}
            >
              {CATEGORY_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Priority */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
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

          {/* Status */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value as TodoStatus)}
              className={cn(
                'w-full px-3 py-2 border rounded-lg transition-colors',
                'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
              )}
            >
              {STATUS_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Deadline */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Deadline
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

          {/* AI Metadata (read-only) */}
          {todo.ai_metadata && (
            <div className="p-3 bg-gray-50 rounded-lg text-xs text-gray-500">
              <p className="font-medium text-gray-700 mb-1">AI Metadata</p>
              <p>Original input: "{todo.ai_metadata.raw_input}"</p>
              <p>Confidence: {Math.round(todo.ai_metadata.confidence * 100)}%</p>
            </div>
          )}

          {/* Danger Zone */}
          <div className="pt-4 border-t border-red-200">
            <p className="text-sm font-medium text-red-700 mb-2">Danger Zone</p>
            <button
              onClick={handleDelete}
              disabled={isDeleting}
              className={cn(
                'w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium',
                'transition-colors',
                confirmDelete
                  ? 'bg-red-600 text-white hover:bg-red-700'
                  : 'border border-red-300 text-red-600 hover:bg-red-50'
              )}
            >
              {isDeleting ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Deleting...
                </>
              ) : confirmDelete ? (
                <>
                  <Trash2 className="h-4 w-4" />
                  Click again to confirm delete
                </>
              ) : (
                <>
                  <Trash2 className="h-4 w-4" />
                  Delete Todo
                </>
              )}
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t bg-white">
          <div className="flex gap-3">
            <button
              onClick={handleClose}
              className={cn(
                'flex-1 px-4 py-2 rounded-lg font-medium',
                'border border-gray-300 text-gray-700 hover:bg-gray-50',
                'transition-colors'
              )}
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={!title.trim() || isSaving || isBlocked}
              className={cn(
                'flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium',
                'bg-blue-500 text-white hover:bg-blue-600',
                'disabled:opacity-50 disabled:cursor-not-allowed',
                'transition-colors'
              )}
            >
              {isSaving ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4" />
                  Save Changes
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

export default EditTodoModal;
