'use client';

import { useState, useEffect } from 'react';
import { X, UserPlus, Users, Calendar, FileText, Check, AlertCircle } from 'lucide-react';
import { Todo, TeamMember, TodoAssignment, User } from '@/lib/types';
import { getMembers, assignTodo, getTodoAssignments, deleteAssignment, getUsers } from '@/lib/api';

interface AssignTodoModalProps {
  isOpen: boolean;
  onClose: () => void;
  todo: Todo;
  teamId?: string;
  currentUserId: string;
  onAssignmentChange?: () => void;
}

export default function AssignTodoModal({
  isOpen,
  onClose,
  todo,
  teamId,
  currentUserId,
  onAssignmentChange,
}: AssignTodoModalProps) {
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([]);
  const [allUsers, setAllUsers] = useState<User[]>([]);
  const [existingAssignments, setExistingAssignments] = useState<TodoAssignment[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Form state
  const [selectedUserId, setSelectedUserId] = useState<string>('');
  const [dueDate, setDueDate] = useState<string>('');
  const [notes, setNotes] = useState<string>('');

  useEffect(() => {
    if (isOpen) {
      fetchData();
    }
  }, [isOpen, todo.id, teamId]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch existing assignments for this todo
      const assignments = await getTodoAssignments(todo.id);
      setExistingAssignments(Array.isArray(assignments) ? assignments : []);

      // Fetch users to assign to
      if (teamId) {
        // If todo belongs to a team, get team members
        const members = await getMembers(teamId);
        const memberList = Array.isArray(members) ? members : members.data || [];
        setTeamMembers(memberList);
        setAllUsers([]);
      } else {
        // If personal todo, get all users
        const users = await getUsers();
        setAllUsers(Array.isArray(users) ? users : []);
        setTeamMembers([]);
      }
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to load assignment data');
    } finally {
      setLoading(false);
    }
  };

  const handleAssign = async () => {
    if (!selectedUserId) {
      setError('Please select a user to assign');
      return;
    }

    try {
      setSubmitting(true);
      setError(null);

      await assignTodo(todo.id, currentUserId, {
        assignee_id: selectedUserId,
        team_id: teamId,
        due_date: dueDate || undefined,
        notes: notes || undefined,
      });

      setSuccess('Todo assigned successfully!');
      setSelectedUserId('');
      setDueDate('');
      setNotes('');

      // Refresh assignments
      await fetchData();
      onAssignmentChange?.();

      // Clear success message after 2 seconds
      setTimeout(() => setSuccess(null), 2000);
    } catch (err: any) {
      console.error('Error assigning todo:', err);
      setError(err.data?.detail || 'Failed to assign todo');
    } finally {
      setSubmitting(false);
    }
  };

  const handleRemoveAssignment = async (assignmentId: string) => {
    if (!confirm('Are you sure you want to remove this assignment?')) return;

    try {
      await deleteAssignment(assignmentId);
      await fetchData();
      onAssignmentChange?.();
    } catch (err) {
      console.error('Error removing assignment:', err);
      setError('Failed to remove assignment');
    }
  };

  const getAvailableUsers = () => {
    const assignedUserIds = new Set(existingAssignments.map((a) => a.assignee_id));

    if (teamId && teamMembers.length > 0) {
      return teamMembers
        .filter((m) => !assignedUserIds.has(m.user_id))
        .map((m) => ({
          id: m.user_id,
          display_name: m.user?.display_name || 'Unknown',
          email: m.user?.email || '',
        }));
    }

    return allUsers.filter((u) => !assignedUserIds.has(u.id));
  };

  if (!isOpen) return null;

  const availableUsers = getAvailableUsers();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-full max-w-lg max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <UserPlus className="w-5 h-5" />
            Assign Todo
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 overflow-y-auto max-h-[calc(90vh-120px)]">
          {/* Todo Info */}
          <div className="mb-4 p-3 bg-gray-50 rounded-lg">
            <h3 className="font-medium text-gray-900">{todo.title}</h3>
            {todo.description && (
              <p className="text-sm text-gray-600 mt-1">{todo.description}</p>
            )}
            <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
              <span className="capitalize">{todo.category}</span>
              <span className="capitalize">{todo.priority} priority</span>
            </div>
          </div>

          {loading ? (
            <div className="flex justify-center items-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <>
              {/* Error/Success Messages */}
              {error && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm flex items-center gap-2">
                  <AlertCircle className="w-4 h-4" />
                  {error}
                </div>
              )}
              {success && (
                <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm flex items-center gap-2">
                  <Check className="w-4 h-4" />
                  {success}
                </div>
              )}

              {/* Existing Assignments */}
              {existingAssignments.length > 0 && (
                <div className="mb-6">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">
                    Current Assignments ({existingAssignments.length})
                  </h4>
                  <div className="space-y-2">
                    {existingAssignments.map((assignment) => (
                      <div
                        key={assignment.id}
                        className="flex items-center justify-between p-2 bg-blue-50 border border-blue-200 rounded-lg"
                      >
                        <div className="flex items-center gap-2">
                          <Users className="w-4 h-4 text-blue-600" />
                          <span className="text-sm font-medium">
                            {assignment.assignee?.display_name || assignment.assignee_id}
                          </span>
                          <span className={`text-xs px-2 py-0.5 rounded-full ${
                            assignment.status === 'completed' ? 'bg-green-100 text-green-700' :
                            assignment.status === 'in_progress' ? 'bg-yellow-100 text-yellow-700' :
                            assignment.status === 'declined' ? 'bg-red-100 text-red-700' :
                            'bg-gray-100 text-gray-700'
                          }`}>
                            {assignment.status}
                          </span>
                        </div>
                        <button
                          onClick={() => handleRemoveAssignment(assignment.id)}
                          className="text-red-500 hover:text-red-700"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* New Assignment Form */}
              <div className="space-y-4">
                <h4 className="text-sm font-medium text-gray-700">Add New Assignment</h4>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Assign To *
                  </label>
                  <select
                    value={selectedUserId}
                    onChange={(e) => setSelectedUserId(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select a user...</option>
                    {availableUsers.map((user) => (
                      <option key={user.id} value={user.id}>
                        {user.display_name} {user.email && `(${user.email})`}
                      </option>
                    ))}
                  </select>
                  {availableUsers.length === 0 && (
                    <p className="mt-1 text-sm text-gray-500">
                      {teamId
                        ? 'All team members have been assigned.'
                        : 'No users available to assign.'}
                    </p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    <Calendar className="w-4 h-4 inline mr-1" />
                    Due Date (optional)
                  </label>
                  <input
                    type="datetime-local"
                    value={dueDate}
                    onChange={(e) => setDueDate(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    <FileText className="w-4 h-4 inline mr-1" />
                    Notes (optional)
                  </label>
                  <textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Add any instructions or context..."
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-3 p-4 border-t border-gray-200 bg-gray-50">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-100"
          >
            Close
          </button>
          <button
            onClick={handleAssign}
            disabled={!selectedUserId || submitting || loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {submitting ? (
              <>
                <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                Assigning...
              </>
            ) : (
              <>
                <UserPlus className="w-4 h-4" />
                Assign
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
