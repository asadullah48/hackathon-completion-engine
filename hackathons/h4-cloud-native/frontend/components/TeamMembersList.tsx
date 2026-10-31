'use client';

import { useState, useEffect } from 'react';
import { Users, UserPlus, Trash2, Crown, Shield, Edit2, Eye, X, Check } from 'lucide-react';
import { TeamMember, TeamRole, User } from '@/lib/types';
import { getMembers, getUsers, addMember, removeMember } from '@/lib/api';

interface TeamMembersListProps {
  teamId: string;
  ownerId: string;
  currentUserId: string;
  onMembersChange?: () => void;
}

const roleIcons: Record<TeamRole, React.ElementType> = {
  owner: Crown,
  admin: Shield,
  member: Users,
  viewer: Eye,
};

const roleColors: Record<TeamRole, string> = {
  owner: 'text-yellow-600 bg-yellow-50',
  admin: 'text-purple-600 bg-purple-50',
  member: 'text-blue-600 bg-blue-50',
  viewer: 'text-gray-600 bg-gray-50',
};

export default function TeamMembersList({
  teamId,
  ownerId,
  currentUserId,
  onMembersChange,
}: TeamMembersListProps) {
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [availableUsers, setAvailableUsers] = useState<User[]>([]);
  const [selectedUserId, setSelectedUserId] = useState<string>('');
  const [selectedRole, setSelectedRole] = useState<TeamRole>('member');
  const [addingMember, setAddingMember] = useState(false);

  const isOwner = currentUserId === ownerId;
  const currentMember = members.find((m) => m.user_id === currentUserId);
  const isAdmin = currentMember?.role === 'admin' || isOwner;

  useEffect(() => {
    fetchMembers();
  }, [teamId]);

  const fetchMembers = async () => {
    try {
      setLoading(true);
      const response = await getMembers(teamId);
      // Handle both array and { data: array } response formats
      const memberList = Array.isArray(response) ? response : response.data;
      setMembers(memberList || []);
      setError(null);
    } catch (err) {
      console.error('Error fetching members:', err);
      setError('Failed to load team members');
    } finally {
      setLoading(false);
    }
  };

  const fetchAvailableUsers = async () => {
    try {
      const users = await getUsers();
      // Filter out existing members
      const memberIds = new Set(members.map((m) => m.user_id));
      const available = (Array.isArray(users) ? users : []).filter(
        (u) => !memberIds.has(u.id)
      );
      setAvailableUsers(available);
    } catch (err) {
      console.error('Error fetching users:', err);
    }
  };

  const handleOpenAddModal = () => {
    fetchAvailableUsers();
    setShowAddModal(true);
  };

  const handleAddMember = async () => {
    if (!selectedUserId) return;

    try {
      setAddingMember(true);
      await addMember(teamId, {
        user_id: selectedUserId,
        role: selectedRole,
      });
      await fetchMembers();
      setShowAddModal(false);
      setSelectedUserId('');
      setSelectedRole('member');
      onMembersChange?.();
    } catch (err) {
      console.error('Error adding member:', err);
      setError('Failed to add member');
    } finally {
      setAddingMember(false);
    }
  };

  const handleRemoveMember = async (userId: string) => {
    if (!confirm('Are you sure you want to remove this member?')) return;

    try {
      await removeMember(teamId, userId);
      await fetchMembers();
      onMembersChange?.();
    } catch (err) {
      console.error('Error removing member:', err);
      setError('Failed to remove member');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-32">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <Users className="w-5 h-5" />
          Team Members ({members.length})
        </h3>
        {isAdmin && (
          <button
            onClick={handleOpenAddModal}
            className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800"
          >
            <UserPlus className="w-4 h-4" />
            Add Member
          </button>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">
          {error}
        </div>
      )}

      <div className="space-y-2">
        {members.map((member) => {
          const RoleIcon = roleIcons[member.role];
          const roleColor = roleColors[member.role];
          const canRemove = isAdmin && member.role !== 'owner' && member.user_id !== currentUserId;

          return (
            <div
              key={member.id}
              className="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg"
            >
              <div className="flex items-center gap-3">
                {member.user?.avatar_url ? (
                  <img
                    src={member.user.avatar_url}
                    alt={member.user?.display_name || 'User'}
                    className="w-10 h-10 rounded-full"
                  />
                ) : (
                  <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
                    <Users className="w-5 h-5 text-gray-500" />
                  </div>
                )}

                <div>
                  <div className="font-medium text-gray-900">
                    {member.user?.display_name || 'Unknown User'}
                    {member.user_id === currentUserId && (
                      <span className="ml-2 text-xs text-gray-500">(You)</span>
                    )}
                  </div>
                  <div className="text-sm text-gray-500">
                    {member.user?.email || member.user_id}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <span className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${roleColor}`}>
                  <RoleIcon className="w-3 h-3" />
                  {member.role.charAt(0).toUpperCase() + member.role.slice(1)}
                </span>

                {canRemove && (
                  <button
                    onClick={() => handleRemoveMember(member.user_id)}
                    className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                    title="Remove member"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Add Member Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">Add Team Member</h2>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Select User *
                </label>
                <select
                  value={selectedUserId}
                  onChange={(e) => setSelectedUserId(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Choose a user...</option>
                  {availableUsers.map((user) => (
                    <option key={user.id} value={user.id}>
                      {user.display_name} ({user.email})
                    </option>
                  ))}
                </select>
                {availableUsers.length === 0 && (
                  <p className="mt-1 text-sm text-gray-500">
                    No available users to add. All users are already members.
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Role
                </label>
                <select
                  value={selectedRole}
                  onChange={(e) => setSelectedRole(e.target.value as TeamRole)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="viewer">Viewer - Can view todos</option>
                  <option value="member">Member - Can create and edit todos</option>
                  <option value="admin">Admin - Can manage members</option>
                </select>
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={() => setShowAddModal(false)}
                className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleAddMember}
                disabled={!selectedUserId || addingMember}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {addingMember ? (
                  <>
                    <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                    Adding...
                  </>
                ) : (
                  <>
                    <UserPlus className="w-4 h-4" />
                    Add Member
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
