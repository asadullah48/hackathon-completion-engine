'use client';

import { useState, useEffect } from 'react';
import { ChevronLeft, Plus, UserPlus, MessageSquare, Calendar, Clock, UserCheck } from 'lucide-react';
import { Team, TeamMember, TeamTodo, Comment } from '@/lib/types';
import {
  getTeam,
  getMembers,
  addMember,
  removeMember,
  getTeamTodos,
  createTeamTodo,
  updateTeamTodo,
  deleteTeamTodo,
  addComment,
  getComments
} from '@/lib/api';
import { useNotifications } from '@/components/NotificationProvider';

// Helper to get member display name
const getMemberName = (member: TeamMember) => member.user?.display_name || member.user_id;

interface TeamDetailProps {
  teamId: string;
  onBack: () => void;
}

export default function TeamDetail({ teamId, onBack }: TeamDetailProps) {
  const [team, setTeam] = useState<Team | null>(null);
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [todos, setTodos] = useState<TeamTodo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // State for adding members
  const [showAddMember, setShowAddMember] = useState(false);
  const [newMemberEmail, setNewMemberEmail] = useState('');
  const [newMemberRole, setNewMemberRole] = useState('member');

  // State for creating team todos
  const [showCreateTodo, setShowCreateTodo] = useState(false);
  const [newTodoTitle, setNewTodoTitle] = useState('');
  const [newTodoDescription, setNewTodoDescription] = useState('');
  const [newTodoCategory, setNewTodoCategory] = useState('work');
  const [newTodoPriority, setNewTodoPriority] = useState('medium');
  const [newTodoDeadline, setNewTodoDeadline] = useState('');
  const [newTodoAssignedTo, setNewTodoAssignedTo] = useState('');

  // State for comments
  const [comments, setComments] = useState<Record<string, Comment[]>>({});
  const [newComment, setNewComment] = useState<Record<string, string>>({});

  const { addNotification } = useNotifications();

  useEffect(() => {
    if (teamId) {
      fetchTeamData();
    }
  }, [teamId]);

  const fetchTeamData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch team details
      const teamResponse = await getTeam(teamId);
      setTeam(teamResponse.data);

      // Fetch members
      const membersResponse = await getMembers(teamId);
      setMembers(membersResponse.data);

      // Fetch team todos
      const todosResponse = await getTeamTodos(teamId);
      setTodos(todosResponse.data);
    } catch (err) {
      console.error('Error fetching team data:', err);
      setError('Failed to load team data');
    } finally {
      setLoading(false);
    }
  };

  const handleAddMember = async () => {
    if (!newMemberEmail.trim()) {
      setError('Email is required');
      return;
    }

    try {
      // In a real app, we would look up the user by email
      // For now, we'll use a placeholder user ID
      const response = await addMember(teamId, {
        user_id: `user_${Date.now()}`, // Placeholder
        role: newMemberRole as any
      });

      setMembers([...members, response.data]);
      setNewMemberEmail('');
      setNewMemberRole('member');
      setShowAddMember(false);

      // Show notification
      addNotification({
        type: 'success',
        title: 'Member Added',
        message: `Successfully added ${response.data?.user?.display_name || 'member'} to the team`,
        teamId: teamId
      });
    } catch (err) {
      console.error('Error adding member:', err);
      setError('Failed to add member');

      // Show error notification
      addNotification({
        type: 'error',
        title: 'Failed to Add Member',
        message: 'Could not add member to the team',
        teamId: teamId
      });
    }
  };

  const handleCreateTodo = async () => {
    if (!newTodoTitle.trim()) {
      setError('Todo title is required');
      return;
    }

    try {
      const response = await createTeamTodo(teamId, {
        title: newTodoTitle,
        description: newTodoDescription,
        category: newTodoCategory,
        priority: newTodoPriority,
        deadline: newTodoDeadline ? new Date(newTodoDeadline) : null,
        assigned_to: newTodoAssignedTo || null,
        assigned_to_name: newTodoAssignedTo ? members.find(m => m.user_id === newTodoAssignedTo)?.user?.display_name || null : null,
        created_by_name: 'Current User' // TODO: Get from auth
      });

      setTodos([...todos, response.data]);
      resetTodoForm();
      setShowCreateTodo(false);

      // Show notification
      addNotification({
        type: 'success',
        title: 'Todo Created',
        message: `Successfully created "${response.data.title}"`,
        teamId: teamId
      });
    } catch (err) {
      console.error('Error creating todo:', err);
      setError('Failed to create todo');

      // Show error notification
      addNotification({
        type: 'error',
        title: 'Failed to Create Todo',
        message: 'Could not create the team todo',
        teamId: teamId
      });
    }
  };

  const resetTodoForm = () => {
    setNewTodoTitle('');
    setNewTodoDescription('');
    setNewTodoCategory('work');
    setNewTodoPriority('medium');
    setNewTodoDeadline('');
    setNewTodoAssignedTo('');
  };

  const handleAssignTodo = async (todoId: string, userId: string) => {
    try {
      const member = members.find(m => m.user_id === userId);
      const todo = todos.find(t => t.id === todoId);

      if (!todo || !member) return;

      const updatedTodo = await updateTeamTodo(teamId, todoId, {
        ...todo,
        assigned_to: userId,
        assigned_to_name: getMemberName(member)
      });

      setTodos(todos.map(t => t.id === todoId ? updatedTodo.data : t));

      // Show notification
      const todoTitle = updatedTodo.data.title.substring(0, 30) + (updatedTodo.data.title.length > 30 ? '...' : '');
      addNotification({
        type: 'info',
        title: 'Todo Assigned',
        message: `Assigned "${todoTitle}" to ${getMemberName(member)}`,
        teamId: teamId
      });
    } catch (err) {
      console.error('Error assigning todo:', err);
      setError('Failed to assign todo');

      // Show error notification
      addNotification({
        type: 'error',
        title: 'Failed to Assign Todo',
        message: 'Could not assign the todo to the member',
        teamId: teamId
      });
    }
  };

  const handleAddComment = async (todoId: string) => {
    const commentText = newComment[todoId];
    if (!commentText?.trim()) {
      setError('Comment cannot be empty');
      return;
    }

    try {
      const response = await addComment(teamId, todoId, {
        content: commentText,
        user_id: 'current_user_id', // TODO: Get from auth
        user_name: 'Current User' // TODO: Get from auth
      });

      // Update comments state
      setComments(prev => ({
        ...prev,
        [todoId]: [...(prev[todoId] || []), response.data]
      }));

      // Clear the comment input
      setNewComment(prev => ({ ...prev, [todoId]: '' }));

      // Show notification
      const todoTitle = todos.find(t => t.id === todoId)?.title.substring(0, 20) + '...';
      addNotification({
        type: 'info',
        title: 'Comment Added',
        message: `Added a comment to "${todoTitle}"`,
        teamId: teamId
      });
    } catch (err) {
      console.error('Error adding comment:', err);
      setError('Failed to add comment');

      // Show error notification
      addNotification({
        type: 'error',
        title: 'Failed to Add Comment',
        message: 'Could not add your comment',
        teamId: teamId
      });
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        {error}
      </div>
    );
  }

  if (!team) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">Team not found</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-blue-600 hover:text-blue-800"
        >
          <ChevronLeft className="w-4 h-4" />
          Back to Teams
        </button>
        <h1 className="text-2xl font-bold text-gray-900">{team.name}</h1>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          {error}
        </div>
      )}

      {/* Team Info */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">{team.name}</h2>
            {team.description && (
              <p className="mt-2 text-gray-600">{team.description}</p>
            )}
          </div>
          <div className="text-sm text-gray-500">
            Created: {new Date(team.created_at).toLocaleDateString()}
          </div>
        </div>
        
        <div className="mt-4 flex items-center gap-6">
          <div className="flex items-center text-sm text-gray-500">
            <UserCheck className="w-4 h-4 mr-1" />
            <span>{members.length} members</span>
          </div>
          <div className="flex items-center text-sm text-gray-500">
            <Calendar className="w-4 h-4 mr-1" />
            <span>{todos.length} todos</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Members and Create Todo */}
        <div className="lg:col-span-1 space-y-6">
          {/* Members Section */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-4 border-b border-gray-200 flex justify-between items-center">
              <h3 className="font-medium text-gray-900">Members</h3>
              <button
                onClick={() => setShowAddMember(true)}
                className="flex items-center gap-1 text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
              >
                <UserPlus className="w-4 h-4" />
                Add
              </button>
            </div>
            
            <div className="p-4">
              {members.length === 0 ? (
                <p className="text-gray-500 text-center py-4">No members yet</p>
              ) : (
                <ul className="space-y-3">
                  {members.map((member) => (
                    <li key={member.id} className="flex justify-between items-center py-2 border-b border-gray-100 last:border-0">
                      <div>
                        <p className="font-medium text-gray-900">{getMemberName(member) || member.user_id}</p>
                        <p className="text-xs text-gray-500 capitalize">{member.role}</p>
                      </div>
                      <button
                        onClick={() => {
                          if (confirm(`Remove ${getMemberName(member) || member.user_id} from team?`)) {
                            removeMember(teamId, member.user_id).then(() => {
                              setMembers(members.filter(m => m.user_id !== member.user_id));
                            }).catch(err => {
                              console.error('Error removing member:', err);
                              setError('Failed to remove member');
                            });
                          }
                        }}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        Remove
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          {/* Create Todo Button */}
          <button
            onClick={() => setShowCreateTodo(true)}
            className="w-full flex items-center justify-center gap-2 bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Create Team Todo
          </button>
        </div>

        {/* Right Column - Team Todos */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow">
            <div className="p-4 border-b border-gray-200">
              <h3 className="font-medium text-gray-900">Team Todos</h3>
            </div>
            
            <div className="p-4">
              {todos.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No todos yet. Create your first team todo!</p>
              ) : (
                <div className="space-y-4">
                  {todos.map((todo) => (
                    <div key={todo.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between">
                        <h4 className={`font-medium ${todo.status === 'completed' ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                          {todo.title}
                        </h4>
                        <div className="flex gap-2">
                          <select
                            value={todo.assigned_to || ''}
                            onChange={(e) => handleAssignTodo(todo.id, e.target.value)}
                            className="text-sm border border-gray-300 rounded px-2 py-1"
                          >
                            <option value="">Unassigned</option>
                            {members.map(member => (
                              <option key={member.user_id} value={member.user_id}>
                                {getMemberName(member) || member.user_id}
                              </option>
                            ))}
                          </select>
                        </div>
                      </div>
                      
                      {todo.description && (
                        <p className="mt-2 text-sm text-gray-600">{todo.description}</p>
                      )}
                      
                      <div className="mt-3 flex flex-wrap gap-4 text-xs text-gray-500">
                        <span className="flex items-center">
                          <Clock className="w-3 h-3 mr-1" />
                          {todo.deadline ? new Date(todo.deadline).toLocaleDateString() : 'No deadline'}
                        </span>
                        <span className="capitalize">{todo.priority}</span>
                        <span className="capitalize">{todo.category}</span>
                        <span className="capitalize">{todo.status}</span>
                        {todo.assigned_to_name && (
                          <span>Assigned to: {todo.assigned_to_name}</span>
                        )}
                      </div>
                      
                      {/* Comments Section */}
                      <div className="mt-4 pt-4 border-t border-gray-100">
                        <div className="flex items-center gap-2 mb-2">
                          <MessageSquare className="w-4 h-4 text-gray-500" />
                          <span className="text-sm font-medium text-gray-700">Comments ({todo.comment_count})</span>
                        </div>
                        
                        <div className="space-y-2">
                          {(comments[todo.id] || []).map((comment) => (
                            <div key={comment.id} className="bg-gray-50 rounded p-3">
                              <div className="flex justify-between">
                                <span className="font-medium text-sm">{comment.user_name}</span>
                                <span className="text-xs text-gray-500">
                                  {new Date(comment.created_at).toLocaleString()}
                                </span>
                              </div>
                              <p className="mt-1 text-sm text-gray-700">{comment.content}</p>
                            </div>
                          ))}
                          
                          <div className="flex gap-2 mt-3">
                            <input
                              type="text"
                              value={newComment[todo.id] || ''}
                              onChange={(e) => setNewComment(prev => ({ ...prev, [todo.id]: e.target.value }))}
                              placeholder="Add a comment..."
                              className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm"
                            />
                            <button
                              onClick={() => handleAddComment(todo.id)}
                              className="px-3 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700"
                            >
                              Post
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Add Member Modal */}
      {showAddMember && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Add Member</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  User Email
                </label>
                <input
                  type="email"
                  value={newMemberEmail}
                  onChange={(e) => setNewMemberEmail(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter user email"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Role
                </label>
                <select
                  value={newMemberRole}
                  onChange={(e) => setNewMemberRole(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="viewer">Viewer</option>
                  <option value="member">Member</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
            </div>
            
            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowAddMember(false);
                  setNewMemberEmail('');
                  setError(null);
                }}
                className="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleAddMember}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Add Member
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Todo Modal */}
      {showCreateTodo && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Create Team Todo</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Title *
                </label>
                <input
                  type="text"
                  value={newTodoTitle}
                  onChange={(e) => setNewTodoTitle(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter todo title"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={newTodoDescription}
                  onChange={(e) => setNewTodoDescription(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter description"
                  rows={3}
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Category
                  </label>
                  <select
                    value={newTodoCategory}
                    onChange={(e) => setNewTodoCategory(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="work">Work</option>
                    <option value="personal">Personal</option>
                    <option value="shopping">Shopping</option>
                    <option value="health">Health</option>
                    <option value="education">Education</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Priority
                  </label>
                  <select
                    value={newTodoPriority}
                    onChange={(e) => setNewTodoPriority(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                  </select>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Deadline
                </label>
                <input
                  type="date"
                  value={newTodoDeadline}
                  onChange={(e) => setNewTodoDeadline(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Assign To
                </label>
                <select
                  value={newTodoAssignedTo}
                  onChange={(e) => setNewTodoAssignedTo(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Unassigned</option>
                  {members.map(member => (
                    <option key={member.user_id} value={member.user_id}>
                      {getMemberName(member) || member.user_id}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowCreateTodo(false);
                  resetTodoForm();
                  setError(null);
                }}
                className="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateTodo}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Create Todo
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}