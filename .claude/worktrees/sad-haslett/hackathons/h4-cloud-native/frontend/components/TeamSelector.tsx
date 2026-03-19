'use client';

import { useState, useEffect } from 'react';
import { Users, ChevronDown, Check, X } from 'lucide-react';
import { Team } from '@/lib/types';
import { getTeams } from '@/lib/api';

interface TeamSelectorProps {
  selectedTeamId?: string;
  onSelect: (teamId: string | undefined) => void;
  placeholder?: string;
  allowNone?: boolean;
  className?: string;
}

export default function TeamSelector({
  selectedTeamId,
  onSelect,
  placeholder = 'Select a team',
  allowNone = true,
  className = '',
}: TeamSelectorProps) {
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [isOpen, setIsOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTeams();
  }, []);

  const fetchTeams = async () => {
    try {
      setLoading(true);
      const response = await getTeams();
      // Handle both array and { data: array } response formats
      const teamList = Array.isArray(response) ? response : response.data;
      setTeams(teamList || []);
      setError(null);
    } catch (err) {
      console.error('Error fetching teams:', err);
      setError('Failed to load teams');
      setTeams([]);
    } finally {
      setLoading(false);
    }
  };

  const selectedTeam = teams.find((t) => t.id === selectedTeamId);

  const handleSelect = (teamId: string | undefined) => {
    onSelect(teamId);
    setIsOpen(false);
  };

  if (loading) {
    return (
      <div className={`flex items-center gap-2 px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 ${className}`}>
        <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
        <span className="text-gray-500 text-sm">Loading teams...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`flex items-center gap-2 px-3 py-2 border border-red-300 rounded-lg bg-red-50 ${className}`}>
        <X className="w-4 h-4 text-red-500" />
        <span className="text-red-600 text-sm">{error}</span>
      </div>
    );
  }

  return (
    <div className={`relative ${className}`}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-3 py-2 border border-gray-300 rounded-lg bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <div className="flex items-center gap-2">
          <Users className="w-4 h-4 text-gray-500" />
          <span className={selectedTeam ? 'text-gray-900' : 'text-gray-500'}>
            {selectedTeam ? selectedTeam.name : placeholder}
          </span>
        </div>
        <ChevronDown
          className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'transform rotate-180' : ''}`}
        />
      </button>

      {isOpen && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-auto">
          {allowNone && (
            <button
              type="button"
              onClick={() => handleSelect(undefined)}
              className="w-full flex items-center justify-between px-3 py-2 hover:bg-gray-50 text-left"
            >
              <span className="text-gray-500">No team (personal)</span>
              {!selectedTeamId && <Check className="w-4 h-4 text-blue-500" />}
            </button>
          )}

          {teams.length === 0 ? (
            <div className="px-3 py-4 text-center text-gray-500 text-sm">
              No teams available. Create a team first.
            </div>
          ) : (
            teams.map((team) => (
              <button
                key={team.id}
                type="button"
                onClick={() => handleSelect(team.id)}
                className="w-full flex items-center justify-between px-3 py-2 hover:bg-gray-50 text-left"
              >
                <div>
                  <div className="font-medium text-gray-900">{team.name}</div>
                  {team.description && (
                    <div className="text-xs text-gray-500 truncate">{team.description}</div>
                  )}
                </div>
                {selectedTeamId === team.id && <Check className="w-4 h-4 text-blue-500" />}
              </button>
            ))
          )}
        </div>
      )}
    </div>
  );
}
