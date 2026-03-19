'use client';

import { useState, useEffect } from 'react';
import { Template, CreateTemplateInput, TemplateTodoItem, UseTemplateResult } from '@/lib/types';
import * as api from '@/lib/api';

interface TemplateLibraryProps {
  onTemplateUsed?: (result: UseTemplateResult) => void;
}

const CATEGORY_COLORS: Record<string, string> = {
  work: 'bg-blue-100 text-blue-800',
  personal: 'bg-green-100 text-green-800',
  study: 'bg-purple-100 text-purple-800',
  health: 'bg-red-100 text-red-800',
  other: 'bg-gray-100 text-gray-800',
};

export default function TemplateLibrary({ onTemplateUsed }: TemplateLibraryProps) {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [previewTemplate, setPreviewTemplate] = useState<Template | null>(null);
  const [usingTemplateId, setUsingTemplateId] = useState<string | null>(null);

  // Fetch templates
  useEffect(() => {
    fetchTemplates();
  }, [searchQuery, selectedCategory]);

  const fetchTemplates = async () => {
    setIsLoading(true);
    try {
      const data = await api.getTemplates({
        search: searchQuery || undefined,
        category: selectedCategory || undefined,
      });
      setTemplates(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch templates');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUseTemplate = async (templateId: string) => {
    setUsingTemplateId(templateId);
    setError('');

    try {
      const result = await api.useTemplate(templateId);
      onTemplateUsed?.(result);

      // Refresh templates to update usage count
      fetchTemplates();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to use template');
    } finally {
      setUsingTemplateId(null);
    }
  };

  const categories = Array.from(new Set(templates.map(t => t.category).filter(Boolean)));

  return (
    <div className="space-y-6">
      {/* Search and Filter */}
      <div className="flex gap-4 flex-wrap">
        <div className="flex-1 min-w-[200px]">
          <input
            type="text"
            placeholder="Search templates..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full border rounded-md p-2 focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="border rounded-md p-2"
        >
          <option value="">All Categories</option>
          {categories.map(cat => (
            <option key={cat} value={cat}>{cat}</option>
          ))}
        </select>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
        >
          Create Template
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 text-red-700 p-3 rounded-md">
          {error}
        </div>
      )}

      {/* Loading */}
      {isLoading ? (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        /* Template Grid */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {templates.map(template => (
            <div
              key={template.id}
              className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-4 relative"
              onMouseEnter={() => setPreviewTemplate(template)}
              onMouseLeave={() => setPreviewTemplate(null)}
            >
              {/* Header */}
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-semibold text-lg">{template.name}</h3>
                <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                  {template.usage_count} uses
                </span>
              </div>

              {/* Description */}
              {template.description && (
                <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                  {template.description}
                </p>
              )}

              {/* Category & Tags */}
              <div className="flex flex-wrap gap-2 mb-3">
                {template.category && (
                  <span className={`text-xs px-2 py-1 rounded ${CATEGORY_COLORS[template.category] || CATEGORY_COLORS.other}`}>
                    {template.category}
                  </span>
                )}
                {template.tags?.slice(0, 3).map(tag => (
                  <span key={tag} className="text-xs bg-gray-100 px-2 py-1 rounded">
                    #{tag}
                  </span>
                ))}
              </div>

              {/* Todo Count */}
              <p className="text-sm text-gray-500 mb-3">
                {template.todos.length} todo{template.todos.length !== 1 ? 's' : ''}
              </p>

              {/* Actions */}
              <div className="flex gap-2">
                <button
                  onClick={() => handleUseTemplate(template.id)}
                  disabled={usingTemplateId === template.id}
                  className="flex-1 bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  {usingTemplateId === template.id ? 'Creating...' : 'Use Template'}
                </button>
                {template.created_by !== 'system' && (
                  <button
                    onClick={async () => {
                      if (confirm('Delete this template?')) {
                        await api.deleteTemplate(template.id);
                        fetchTemplates();
                      }
                    }}
                    className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-md"
                  >
                    Delete
                  </button>
                )}
              </div>

              {/* Preview Tooltip */}
              {previewTemplate?.id === template.id && (
                <div className="absolute z-10 top-full left-0 right-0 mt-2 bg-white border rounded-lg shadow-lg p-4 max-h-60 overflow-y-auto">
                  <h4 className="font-medium mb-2">Todos in this template:</h4>
                  <ul className="space-y-1">
                    {template.todos.map((todo, i) => (
                      <li key={i} className="text-sm flex items-center gap-2">
                        <span className="w-1 h-1 bg-blue-600 rounded-full"></span>
                        <span>{todo.title}</span>
                        {todo.relative_deadline_days && (
                          <span className="text-gray-400">
                            (+{todo.relative_deadline_days}d)
                          </span>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Empty State */}
      {!isLoading && templates.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No templates found. Create one to get started!
        </div>
      )}

      {/* Create Template Modal */}
      {showCreateModal && (
        <CreateTemplateModal
          onClose={() => setShowCreateModal(false)}
          onCreated={() => {
            setShowCreateModal(false);
            fetchTemplates();
          }}
        />
      )}
    </div>
  );
}

// Create Template Modal Component
function CreateTemplateModal({
  onClose,
  onCreated,
}: {
  onClose: () => void;
  onCreated: () => void;
}) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('');
  const [tags, setTags] = useState('');
  const [todos, setTodos] = useState<TemplateTodoItem[]>([
    { title: '', priority: 'medium' },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const addTodo = () => {
    setTodos([...todos, { title: '', priority: 'medium' }]);
  };

  const removeTodo = (index: number) => {
    setTodos(todos.filter((_, i) => i !== index));
  };

  const updateTodo = (index: number, updates: Partial<TemplateTodoItem>) => {
    setTodos(todos.map((todo, i) => (i === index ? { ...todo, ...updates } : todo)));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const validTodos = todos.filter(t => t.title.trim());
    if (validTodos.length === 0) {
      setError('Add at least one todo');
      return;
    }

    setIsLoading(true);

    try {
      await api.createTemplate({
        name,
        description: description || undefined,
        category: category || undefined,
        todos: validTodos,
        tags: tags ? tags.split(',').map(t => t.trim()) : undefined,
      });
      onCreated();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create template');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Create Template</h2>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              &times;
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Template Name *
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className="w-full border rounded-md p-2"
                placeholder="My Template"
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
                className="w-full border rounded-md p-2"
                rows={2}
                placeholder="What is this template for?"
              />
            </div>

            {/* Category & Tags */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category
                </label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full border rounded-md p-2"
                >
                  <option value="">None</option>
                  <option value="work">Work</option>
                  <option value="personal">Personal</option>
                  <option value="study">Study</option>
                  <option value="health">Health</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tags (comma-separated)
                </label>
                <input
                  type="text"
                  value={tags}
                  onChange={(e) => setTags(e.target.value)}
                  className="w-full border rounded-md p-2"
                  placeholder="project, planning"
                />
              </div>
            </div>

            {/* Todos */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Template Todos *
              </label>
              <div className="space-y-2">
                {todos.map((todo, index) => (
                  <div key={index} className="flex gap-2 items-start">
                    <input
                      type="text"
                      value={todo.title}
                      onChange={(e) => updateTodo(index, { title: e.target.value })}
                      className="flex-1 border rounded-md p-2"
                      placeholder="Todo title"
                    />
                    <select
                      value={todo.priority || 'medium'}
                      onChange={(e) => updateTodo(index, { priority: e.target.value })}
                      className="border rounded-md p-2"
                    >
                      <option value="high">High</option>
                      <option value="medium">Medium</option>
                      <option value="low">Low</option>
                    </select>
                    <input
                      type="number"
                      value={todo.relative_deadline_days || ''}
                      onChange={(e) => updateTodo(index, {
                        relative_deadline_days: e.target.value ? parseInt(e.target.value) : undefined
                      })}
                      className="w-20 border rounded-md p-2"
                      placeholder="Days"
                      title="Days from now"
                    />
                    <button
                      type="button"
                      onClick={() => removeTodo(index)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded"
                      disabled={todos.length === 1}
                    >
                      &times;
                    </button>
                  </div>
                ))}
              </div>
              <button
                type="button"
                onClick={addTodo}
                className="mt-2 text-blue-600 hover:text-blue-700 text-sm"
              >
                + Add Todo
              </button>
            </div>

            {/* Error */}
            {error && (
              <div className="bg-red-50 text-red-700 p-3 rounded-md">
                {error}
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 border border-gray-300 py-2 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isLoading}
                className="flex-1 bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {isLoading ? 'Creating...' : 'Create Template'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
