/**
 * TypeScript types for H2 Todo application.
 */

export type TodoCategory = 'work' | 'personal' | 'study' | 'health' | 'other';
export type TodoPriority = 'high' | 'medium' | 'low';
export type TodoStatus = 'pending' | 'in_progress' | 'completed' | 'flagged';
export type ConstitutionalDecision = 'allow' | 'block' | 'flag';

export interface ConstitutionalCheck {
  passed: boolean;
  decision: ConstitutionalDecision;
  reason?: string;
}

export interface AIMetadata {
  inferred_category: TodoCategory;
  inferred_priority: TodoPriority;
  extracted_deadline?: string;
  confidence: number;
  raw_input: string;
}

export interface Todo {
  id: string;
  title: string;
  description?: string;
  category: TodoCategory;
  priority: TodoPriority;
  status: TodoStatus;
  deadline?: string;
  created_at: string;
  updated_at: string;
  constitutional_check: ConstitutionalCheck;
  ai_metadata?: AIMetadata;
}

export interface CreateTodoInput {
  title: string;
  description?: string;
  category?: TodoCategory;
  priority?: TodoPriority;
  deadline?: string;
  ai_metadata?: AIMetadata;
}

export interface UpdateTodoInput {
  title?: string;
  description?: string;
  category?: TodoCategory;
  priority?: TodoPriority;
  status?: TodoStatus;
  deadline?: string;
}

export interface TodoFilters {
  category?: TodoCategory[];
  status?: TodoStatus[];
  priority?: TodoPriority[];
  search?: string;
  deadline_before?: string;
  deadline_after?: string;
}

export interface TodoStats {
  total: number;
  by_status: Record<TodoStatus, number>;
  by_category: Record<TodoCategory, number>;
  by_priority: Record<TodoPriority, number>;
  completion_rate: number;
}

export interface ParsedTodoResult {
  title: string;
  description?: string;
  category: TodoCategory;
  priority: TodoPriority;
  deadline?: Date;
  confidence: number;
  ai_metadata: AIMetadata;
}

export interface ConstitutionalFilterResult {
  allowed: boolean;
  decision: ConstitutionalDecision;
  reason?: string;
}
