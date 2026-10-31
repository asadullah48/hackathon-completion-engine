/**
 * Zustand store for todo state management.
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import {
  Todo,
  TodoFilters,
  TodoStats,
  CreateTodoInput,
  UpdateTodoInput,
} from './types';
import * as api from './api';

interface TodoState {
  // Data
  todos: Todo[];
  stats: TodoStats | null;
  filters: TodoFilters;

  // UI State
  isLoading: boolean;
  error: string | null;
  selectedTodoId: string | null;

  // Actions
  fetchTodos: () => Promise<void>;
  fetchStats: () => Promise<void>;
  createTodo: (input: CreateTodoInput) => Promise<Todo | null>;
  updateTodo: (id: string, updates: UpdateTodoInput) => Promise<Todo | null>;
  deleteTodo: (id: string) => Promise<boolean>;
  setFilters: (filters: Partial<TodoFilters>) => void;
  clearFilters: () => void;
  selectTodo: (id: string | null) => void;
  completeTodo: (id: string) => Promise<void>;
  startTodo: (id: string) => Promise<void>;
  reopenTodo: (id: string) => Promise<void>;
  clearError: () => void;
}

export const useTodoStore = create<TodoState>()(
  devtools(
    (set, get) => ({
      // Initial state
      todos: [],
      stats: null,
      filters: {},
      isLoading: false,
      error: null,
      selectedTodoId: null,

      // Fetch todos from API
      fetchTodos: async () => {
        set({ isLoading: true, error: null });
        try {
          const todos = await api.getTodos(get().filters);
          set({ todos, isLoading: false });
        } catch (error) {
          const message = error instanceof api.ApiError
            ? error.message
            : 'Failed to fetch todos';
          set({ error: message, isLoading: false });
        }
      },

      // Fetch stats from API
      fetchStats: async () => {
        try {
          const stats = await api.getStats();
          set({ stats });
        } catch (error) {
          console.error('Failed to fetch stats:', error);
        }
      },

      // Create a new todo
      createTodo: async (input: CreateTodoInput) => {
        set({ isLoading: true, error: null });
        try {
          const todo = await api.createTodo(input);
          set((state) => ({
            todos: [todo, ...state.todos],
            isLoading: false,
          }));
          // Refresh stats
          get().fetchStats();
          return todo;
        } catch (error) {
          let message = 'Failed to create todo';
          if (error instanceof api.ApiError) {
            if (error.isConstitutionalViolation) {
              message = error.constitutionalMessage || 'Content policy violation';
            } else {
              message = error.message;
            }
          }
          set({ error: message, isLoading: false });
          return null;
        }
      },

      // Update a todo
      updateTodo: async (id: string, updates: UpdateTodoInput) => {
        set({ isLoading: true, error: null });
        try {
          const todo = await api.updateTodo(id, updates);
          set((state) => ({
            todos: state.todos.map((t) => (t.id === id ? todo : t)),
            isLoading: false,
          }));
          // Refresh stats if status changed
          if (updates.status) {
            get().fetchStats();
          }
          return todo;
        } catch (error) {
          let message = 'Failed to update todo';
          if (error instanceof api.ApiError) {
            if (error.isConstitutionalViolation) {
              message = error.constitutionalMessage || 'Content policy violation';
            } else {
              message = error.message;
            }
          }
          set({ error: message, isLoading: false });
          return null;
        }
      },

      // Delete a todo
      deleteTodo: async (id: string) => {
        set({ isLoading: true, error: null });
        try {
          await api.deleteTodo(id);
          set((state) => ({
            todos: state.todos.filter((t) => t.id !== id),
            isLoading: false,
            selectedTodoId: state.selectedTodoId === id ? null : state.selectedTodoId,
          }));
          // Refresh stats
          get().fetchStats();
          return true;
        } catch (error) {
          const message = error instanceof api.ApiError
            ? error.message
            : 'Failed to delete todo';
          set({ error: message, isLoading: false });
          return false;
        }
      },

      // Set filters and refetch
      setFilters: (newFilters: Partial<TodoFilters>) => {
        set((state) => ({
          filters: { ...state.filters, ...newFilters },
        }));
        get().fetchTodos();
      },

      // Clear all filters
      clearFilters: () => {
        set({ filters: {} });
        get().fetchTodos();
      },

      // Select a todo for editing
      selectTodo: (id: string | null) => {
        set({ selectedTodoId: id });
      },

      // Quick actions
      completeTodo: async (id: string) => {
        await get().updateTodo(id, { status: 'completed' });
      },

      startTodo: async (id: string) => {
        await get().updateTodo(id, { status: 'in_progress' });
      },

      reopenTodo: async (id: string) => {
        await get().updateTodo(id, { status: 'pending' });
      },

      // Clear error
      clearError: () => {
        set({ error: null });
      },
    }),
    { name: 'todo-store' }
  )
);

// Selectors
export const selectTodos = (state: TodoState) => state.todos;
export const selectStats = (state: TodoState) => state.stats;
export const selectFilters = (state: TodoState) => state.filters;
export const selectIsLoading = (state: TodoState) => state.isLoading;
export const selectError = (state: TodoState) => state.error;
export const selectSelectedTodo = (state: TodoState) =>
  state.todos.find((t) => t.id === state.selectedTodoId);

// Computed selectors
export const selectTodosByStatus = (status: string) => (state: TodoState) =>
  state.todos.filter((t) => t.status === status);

export const selectPendingTodos = selectTodosByStatus('pending');
export const selectCompletedTodos = selectTodosByStatus('completed');
export const selectFlaggedTodos = selectTodosByStatus('flagged');
