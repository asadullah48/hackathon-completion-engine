'use client';

/**
 * Main page - AI-Powered Todo Application.
 * Integrates all components with Zustand store.
 */

import { useEffect, useState, useCallback } from 'react';
import { useTodoStore } from '@/lib/store';
import { Todo, TodoStatus, UpdateTodoInput } from '@/lib/types';
import {
  CreateTodoForm,
  TodoList,
  TodoFilters,
  TodoStats,
  EditTodoModal,
} from '@/components';
import { AlertCircle, RefreshCw } from 'lucide-react';

export default function Home() {
  const {
    todos,
    stats,
    filters,
    isLoading,
    error,
    fetchTodos,
    fetchStats,
    updateTodo,
    deleteTodo,
    setFilters,
    clearError,
  } = useTodoStore();

  // Edit modal state
  const [editingTodo, setEditingTodo] = useState<Todo | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);

  // Fetch data on mount
  useEffect(() => {
    fetchTodos();
    fetchStats();
  }, [fetchTodos, fetchStats]);

  // Refetch when filters change
  useEffect(() => {
    fetchTodos();
  }, [filters, fetchTodos]);

  // Handlers
  const handleEdit = useCallback((todo: Todo) => {
    setEditingTodo(todo);
    setIsEditModalOpen(true);
  }, []);

  const handleDelete = useCallback(
    async (todo: Todo) => {
      await deleteTodo(todo.id);
      await fetchStats();
    },
    [deleteTodo, fetchStats]
  );

  const handleStatusChange = useCallback(
    async (todo: Todo, status: TodoStatus) => {
      await updateTodo(todo.id, { status });
      await fetchStats();
    },
    [updateTodo, fetchStats]
  );

  const handleSaveEdit = useCallback(
    async (id: string, updates: UpdateTodoInput) => {
      await updateTodo(id, updates);
      await fetchStats();
    },
    [updateTodo, fetchStats]
  );

  const handleDeleteFromModal = useCallback(
    async (todo: Todo) => {
      await deleteTodo(todo.id);
      await fetchStats();
    },
    [deleteTodo, fetchStats]
  );

  const handleCloseEditModal = useCallback(() => {
    setIsEditModalOpen(false);
    setEditingTodo(null);
  }, []);

  const handleCreateSuccess = useCallback(() => {
    fetchTodos();
    fetchStats();
  }, [fetchTodos, fetchStats]);

  const handleRefresh = useCallback(() => {
    fetchTodos();
    fetchStats();
  }, [fetchTodos, fetchStats]);

  return (
    <div className="space-y-6">
      {/* Error Banner */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0" />
            <p className="text-red-800">{error}</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleRefresh}
              className="text-red-600 hover:text-red-800 p-1"
              title="Retry"
            >
              <RefreshCw className="h-4 w-4" />
            </button>
            <button
              onClick={clearError}
              className="text-red-600 hover:text-red-800 text-sm font-medium"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      {/* Main Layout */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left Column - Create Form + Stats */}
        <div className="lg:col-span-1 space-y-6">
          <CreateTodoForm onSuccess={handleCreateSuccess} />
          <TodoStats stats={stats} isLoading={isLoading} />
        </div>

        {/* Right Column - Filters + List */}
        <div className="lg:col-span-2 space-y-4">
          <TodoFilters filters={filters} onFiltersChange={setFilters} />
          <TodoList
            todos={todos}
            isLoading={isLoading}
            onEdit={handleEdit}
            onDelete={handleDelete}
            onStatusChange={handleStatusChange}
          />
        </div>
      </div>

      {/* Edit Modal */}
      <EditTodoModal
        todo={editingTodo}
        isOpen={isEditModalOpen}
        onClose={handleCloseEditModal}
        onSave={handleSaveEdit}
        onDelete={handleDeleteFromModal}
      />
    </div>
  );
}
