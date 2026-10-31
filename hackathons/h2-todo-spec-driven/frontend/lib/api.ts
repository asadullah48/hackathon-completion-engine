/**
 * API client for communicating with the FastAPI backend.
 * Handles CRUD operations for todos.
 */

import {
  Todo,
  CreateTodoInput,
  UpdateTodoInput,
  TodoFilters,
  TodoStats,
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Custom error class for API errors.
 */
export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public data?: any
  ) {
    super(`API Error: ${status} ${statusText}`);
    this.name = 'ApiError';
  }

  get isConstitutionalViolation(): boolean {
    return (
      this.status === 403 &&
      this.data?.detail?.error === 'constitutional_violation'
    );
  }

  get constitutionalMessage(): string | undefined {
    return this.data?.detail?.message;
  }
}

/**
 * Make an API request with error handling.
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw new ApiError(response.status, response.statusText, data);
  }

  return data as T;
}

/**
 * Create a new todo.
 */
export async function createTodo(todo: CreateTodoInput): Promise<Todo> {
  return apiRequest<Todo>('/api/todos', {
    method: 'POST',
    body: JSON.stringify(todo),
  });
}

/**
 * Get all todos with optional filters.
 */
export async function getTodos(filters?: TodoFilters): Promise<Todo[]> {
  const params = new URLSearchParams();

  // Handle array filters (category, status, priority)
  if (filters?.category?.length) {
    filters.category.forEach((c) => params.append('category', c));
  }
  if (filters?.status?.length) {
    filters.status.forEach((s) => params.append('status', s));
  }
  if (filters?.priority?.length) {
    filters.priority.forEach((p) => params.append('priority', p));
  }
  if (filters?.search) params.append('search', filters.search);
  if (filters?.deadline_before) params.append('deadline_before', filters.deadline_before);
  if (filters?.deadline_after) params.append('deadline_after', filters.deadline_after);

  const queryString = params.toString();
  const endpoint = queryString ? `/api/todos?${queryString}` : '/api/todos';

  return apiRequest<Todo[]>(endpoint);
}

/**
 * Get a single todo by ID.
 */
export async function getTodo(id: string): Promise<Todo> {
  return apiRequest<Todo>(`/api/todos/${id}`);
}

/**
 * Update a todo.
 */
export async function updateTodo(
  id: string,
  updates: UpdateTodoInput
): Promise<Todo> {
  return apiRequest<Todo>(`/api/todos/${id}`, {
    method: 'PUT',
    body: JSON.stringify(updates),
  });
}

/**
 * Delete a todo.
 */
export async function deleteTodo(id: string): Promise<{ deleted: boolean; id: string }> {
  return apiRequest<{ deleted: boolean; id: string }>(`/api/todos/${id}`, {
    method: 'DELETE',
  });
}

/**
 * Get todo statistics.
 */
export async function getStats(): Promise<TodoStats> {
  return apiRequest<TodoStats>('/api/stats');
}

/**
 * Check API health.
 */
export async function checkHealth(): Promise<{ status: string; service: string }> {
  return apiRequest<{ status: string; service: string }>('/health');
}

/**
 * Batch update multiple todos.
 */
export async function batchUpdateTodos(
  updates: Array<{ id: string; updates: UpdateTodoInput }>
): Promise<Todo[]> {
  return Promise.all(
    updates.map(({ id, updates }) => updateTodo(id, updates))
  );
}

/**
 * Batch delete multiple todos.
 */
export async function batchDeleteTodos(ids: string[]): Promise<void> {
  await Promise.all(ids.map((id) => deleteTodo(id)));
}

/**
 * Mark a todo as completed.
 */
export async function completeTodo(id: string): Promise<Todo> {
  return updateTodo(id, { status: 'completed' });
}

/**
 * Mark a todo as in progress.
 */
export async function startTodo(id: string): Promise<Todo> {
  return updateTodo(id, { status: 'in_progress' });
}

/**
 * Reopen a completed todo.
 */
export async function reopenTodo(id: string): Promise<Todo> {
  return updateTodo(id, { status: 'pending' });
}
