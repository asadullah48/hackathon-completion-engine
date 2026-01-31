'use client';

/**
 * Main page - H3 Advanced Todo Application.
 * Tabs: My Todos, Recurring, Templates, Teams
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
import RecurringPatternSelector from '@/components/RecurringPatternSelector';
import TemplateLibrary from '@/components/TemplateLibrary';
import TeamDashboard from '@/components/TeamDashboard';
import TeamDetail from '@/components/TeamDetail';
import AnalyticsDashboard from '@/components/AnalyticsDashboard';
import ExportImportPanel from '@/components/ExportImportPanel';
import NotificationBadge from '@/components/NotificationBadge';
import { AlertCircle, RefreshCw, ListTodo, Repeat, Layout, Users, BarChart3, Search, Settings } from 'lucide-react';

type TabType = 'todos' | 'recurring' | 'templates' | 'teams' | 'analytics';

export default function Home() {
  const {
    todos,
    stats,
    filters,
    isLoading,
    error,
    fetchTodos,
    fetchStats,
    fetchRecurring,
    fetchTemplates,
    updateTodo,
    deleteTodo,
    setFilters,
    clearError,
  } = useTodoStore();

  // Tab state
  const [activeTab, setActiveTab] = useState<TabType>('todos');

  // Team state
  const [selectedTeamId, setSelectedTeamId] = useState<string | null>(null);

  // Edit modal state
  const [editingTodo, setEditingTodo] = useState<Todo | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);

  // Fetch data on mount
  useEffect(() => {
    fetchTodos();
    fetchStats();
    fetchRecurring();
    fetchTemplates();
  }, [fetchTodos, fetchStats, fetchRecurring, fetchTemplates]);

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
    fetchRecurring();
    fetchTemplates();
  }, [fetchTodos, fetchStats, fetchRecurring, fetchTemplates]);

  const handleRecurringCreated = useCallback(() => {
    fetchRecurring();
  }, [fetchRecurring]);

  const handleTemplateUsed = useCallback(() => {
    fetchTodos();
    fetchStats();
    fetchTemplates();
  }, [fetchTodos, fetchStats, fetchTemplates]);

  const tabs = [
    { id: 'todos' as TabType, label: 'My Todos', icon: ListTodo },
    { id: 'recurring' as TabType, label: 'Recurring', icon: Repeat },
    { id: 'templates' as TabType, label: 'Templates', icon: Layout },
    { id: 'teams' as TabType, label: 'Teams', icon: Users },
    { id: 'analytics' as TabType, label: 'Analytics', icon: BarChart3 },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-4 md:p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <header className="mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">H3 Advanced Todo</h1>
              <p className="text-gray-600 mt-1">Manage your tasks efficiently with team collaboration</p>
            </div>
            <div className="flex items-center gap-3">
              <NotificationBadge />
              <button className="p-2 text-gray-600 hover:text-gray-900 rounded-full hover:bg-gray-200 transition-colors">
                <Settings className="w-5 h-5" />
              </button>
            </div>
          </div>
        </header>

        {/* Error Banner */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6 flex items-center justify-between shadow-sm">
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

        {/* Stats Summary Bar */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
              <p className="text-sm text-gray-600">Total Tasks</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
            </div>
            <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
              <p className="text-sm text-gray-600">Pending</p>
              <p className="text-2xl font-bold text-yellow-600">{stats.by_status.pending}</p>
            </div>
            <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
              <p className="text-sm text-gray-600">In Progress</p>
              <p className="text-2xl font-bold text-blue-600">{stats.by_status.in_progress}</p>
            </div>
            <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
              <p className="text-sm text-gray-600">Completed</p>
              <p className="text-2xl font-bold text-green-600">{stats.by_status.completed}</p>
            </div>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 mb-6 overflow-hidden">
          <nav className="flex flex-wrap" aria-label="Tabs">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => {
                    setActiveTab(tab.id);
                    setSelectedTeamId(null); // Reset team selection when switching tabs
                  }}
                  className={`
                    flex items-center gap-2 px-5 py-4 text-sm font-medium transition-colors
                    ${
                      activeTab === tab.id
                        ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    }
                  `}
                >
                    <Icon className="h-4 w-4" />
                    {tab.label}
                  </button>
              );
            })}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          {activeTab === 'todos' && (
            <div className="space-y-6">
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

              {/* Export/Import Panel */}
              <ExportImportPanel todos={todos} />
            </div>
          )}

          {activeTab === 'recurring' && (
            <div className="grid lg:grid-cols-2 gap-6">
              {/* Left Column - Create Recurring Pattern */}
              <div>
                <RecurringPatternSelector
                  todos={todos}
                  onPatternCreated={handleRecurringCreated}
                />
              </div>

              {/* Right Column - Active Patterns */}
              <div>
                <RecurringPatternsList />
              </div>
            </div>
          )}

          {activeTab === 'templates' && (
            <TemplateLibrary onTemplateUsed={handleTemplateUsed} />
          )}

          {activeTab === 'teams' && !selectedTeamId && (
            <TeamDashboard onTeamSelect={setSelectedTeamId} />
          )}

          {activeTab === 'teams' && selectedTeamId && (
            <TeamDetail teamId={selectedTeamId} onBack={() => setSelectedTeamId(null)} />
          )}

          {activeTab === 'analytics' && (
            <AnalyticsDashboard />
          )}
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
    </div>
  );
}

// Component to display active recurring patterns
function RecurringPatternsList() {
  const { recurring, fetchRecurring } = useTodoStore();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchRecurring().finally(() => setIsLoading(false));
  }, [fetchRecurring]);

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this recurring pattern?')) return;
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/recurring/${id}`,
        { method: 'DELETE' }
      );
      if (response.ok) {
        fetchRecurring();
      }
    } catch (error) {
      console.error('Failed to delete recurring pattern:', error);
    }
  };

  const handleGenerate = async (id: string) => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/recurring/${id}/generate`,
        { method: 'POST' }
      );
      if (response.ok) {
        alert('Todo generated successfully!');
      }
    } catch (error) {
      console.error('Failed to generate occurrence:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Active Patterns</h2>
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">Active Patterns</h2>

      {recurring.length === 0 ? (
        <p className="text-gray-500 text-center py-8">
          No recurring patterns yet. Create one to get started!
        </p>
      ) : (
        <div className="space-y-4">
          {recurring.map((pattern) => (
            <div
              key={pattern.id}
              className="border rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-medium">
                    {pattern.pattern.charAt(0).toUpperCase() + pattern.pattern.slice(1)} Pattern
                  </h3>
                  <p className="text-sm text-gray-600">
                    Every {pattern.interval} {pattern.pattern === 'daily' ? 'day' : pattern.pattern === 'weekly' ? 'week' : 'month'}
                    {pattern.interval > 1 ? 's' : ''}
                  </p>
                  {pattern.next_occurrence && (
                    <p className="text-sm text-blue-600 mt-1">
                      Next: {new Date(pattern.next_occurrence).toLocaleDateString()}
                    </p>
                  )}
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleGenerate(pattern.id)}
                    className="text-sm px-3 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200"
                  >
                    Generate
                  </button>
                  <button
                    onClick={() => handleDelete(pattern.id)}
                    className="text-sm px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
