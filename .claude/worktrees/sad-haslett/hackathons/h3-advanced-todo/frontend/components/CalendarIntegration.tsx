'use client';

/**
 * Calendar Integration Component.
 * Manages calendar connections and syncs todos to external calendars.
 */

import { useState, useEffect } from 'react';
import {
  Calendar,
  Link2,
  Unlink,
  RefreshCw,
  Check,
  AlertCircle,
  Settings,
  ChevronRight,
  Clock,
  ExternalLink,
} from 'lucide-react';
import {
  CalendarConnection,
  CalendarEvent,
  CalendarProvider,
  ConnectionStatus,
  SyncDirection,
} from '@/lib/types';
import {
  getCalendarConnections,
  initiateCalendarConnection,
  completeCalendarConnection,
  disconnectCalendar,
  updateCalendarSyncSettings,
  getCalendarEvents,
  syncTodosToCalendar,
} from '@/lib/api';
import { cn } from '@/lib/utils';

interface CalendarIntegrationProps {
  userId: string;
  className?: string;
}

const providerInfo: Record<CalendarProvider, { name: string; icon: string; color: string }> = {
  google: { name: 'Google Calendar', icon: 'G', color: 'bg-red-500' },
  outlook: { name: 'Outlook Calendar', icon: 'O', color: 'bg-blue-600' },
  apple: { name: 'Apple Calendar', icon: 'A', color: 'bg-gray-800' },
};

const statusColors: Record<ConnectionStatus, string> = {
  pending: 'text-yellow-600 bg-yellow-50',
  connected: 'text-green-600 bg-green-50',
  disconnected: 'text-gray-500 bg-gray-50',
  error: 'text-red-600 bg-red-50',
};

export function CalendarIntegration({ userId, className }: CalendarIntegrationProps) {
  const [connections, setConnections] = useState<CalendarConnection[]>([]);
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState<string | null>(null);
  const [connecting, setConnecting] = useState<CalendarProvider | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState<string | null>(null);
  const [selectedConnection, setSelectedConnection] = useState<string | null>(null);

  useEffect(() => {
    if (userId) {
      loadConnections();
    }
  }, [userId]);

  useEffect(() => {
    if (selectedConnection) {
      loadEvents(selectedConnection);
    }
  }, [selectedConnection]);

  const loadConnections = async () => {
    if (!userId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getCalendarConnections(userId);
      setConnections(data);
      // Auto-select first connected calendar
      const connected = data.find((c) => c.status === 'connected');
      if (connected) {
        setSelectedConnection(connected.id);
      }
    } catch (err) {
      setError('Failed to load calendar connections');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadEvents = async (connectionId: string) => {
    try {
      const data = await getCalendarEvents(connectionId);
      setEvents(data);
    } catch (err) {
      console.error('Failed to load events:', err);
    }
  };

  const handleConnect = async (provider: CalendarProvider) => {
    if (!userId) return;
    setConnecting(provider);
    setError(null);
    try {
      // Initiate connection
      const response = await initiateCalendarConnection(userId, { provider });

      if (response.status === 'already_connected') {
        setError(`Already connected to ${providerInfo[provider].name}`);
        setConnecting(null);
        return;
      }

      // In a real app, we'd redirect to OAuth URL
      // For demo, we'll simulate OAuth completion
      setTimeout(async () => {
        try {
          const connection = await completeCalendarConnection(response.connection_id);
          setConnections((prev) => [...prev, connection]);
          setSelectedConnection(connection.id);
        } catch (err) {
          setError('Failed to complete connection');
        } finally {
          setConnecting(null);
        }
      }, 1500);
    } catch (err) {
      setError('Failed to initiate connection');
      setConnecting(null);
    }
  };

  const handleDisconnect = async (connectionId: string) => {
    try {
      await disconnectCalendar(connectionId);
      setConnections((prev) => prev.filter((c) => c.id !== connectionId));
      if (selectedConnection === connectionId) {
        setSelectedConnection(null);
        setEvents([]);
      }
    } catch (err) {
      setError('Failed to disconnect');
    }
  };

  const handleSync = async (connectionId: string) => {
    if (!userId) return;
    setSyncing(connectionId);
    try {
      const result = await syncTodosToCalendar(connectionId, userId);
      // Reload events after sync
      await loadEvents(connectionId);
      // Update last sync time
      setConnections((prev) =>
        prev.map((c) =>
          c.id === connectionId ? { ...c, last_sync_at: result.last_sync_at } : c
        )
      );
    } catch (err) {
      setError('Failed to sync todos');
    } finally {
      setSyncing(null);
    }
  };

  const handleUpdateSettings = async (
    connectionId: string,
    settings: { sync_enabled?: boolean; sync_direction?: SyncDirection }
  ) => {
    try {
      const updated = await updateCalendarSyncSettings(connectionId, settings);
      setConnections((prev) => prev.map((c) => (c.id === connectionId ? updated : c)));
    } catch (err) {
      setError('Failed to update settings');
    }
  };

  const formatLastSync = (date?: string) => {
    if (!date) return 'Never';
    const d = new Date(date);
    return d.toLocaleString();
  };

  if (loading) {
    return (
      <div className={cn('bg-white rounded-lg border p-6', className)}>
        <div className="flex items-center justify-center py-8">
          <RefreshCw className="h-6 w-6 animate-spin text-gray-400" />
          <span className="ml-2 text-gray-500">Loading calendars...</span>
        </div>
      </div>
    );
  }

  return (
    <div className={cn('bg-white rounded-lg border', className)}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center gap-2">
          <Calendar className="h-5 w-5 text-blue-500" />
          <h2 className="text-lg font-semibold text-gray-900">Calendar Integration</h2>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="p-4 bg-red-50 border-b border-red-100 flex items-center gap-2">
          <AlertCircle className="h-4 w-4 text-red-500" />
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* Available Providers */}
      <div className="p-4 border-b">
        <h3 className="text-sm font-medium text-gray-700 mb-3">Connect a Calendar</h3>
        <div className="flex flex-wrap gap-2">
          {(Object.keys(providerInfo) as CalendarProvider[]).map((provider) => {
            const info = providerInfo[provider];
            const isConnected = connections.some(
              (c) => c.provider === provider && c.status === 'connected'
            );
            const isConnecting = connecting === provider;

            return (
              <button
                key={provider}
                onClick={() => !isConnected && !isConnecting && handleConnect(provider)}
                disabled={isConnected || isConnecting}
                className={cn(
                  'flex items-center gap-2 px-4 py-2 rounded-lg border transition-all',
                  isConnected
                    ? 'bg-green-50 border-green-200 text-green-700 cursor-default'
                    : isConnecting
                    ? 'bg-gray-100 border-gray-200 text-gray-400 cursor-wait'
                    : 'bg-white border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                )}
              >
                <span
                  className={cn(
                    'w-6 h-6 rounded flex items-center justify-center text-white text-xs font-bold',
                    info.color
                  )}
                >
                  {info.icon}
                </span>
                <span className="text-sm font-medium">{info.name}</span>
                {isConnected && <Check className="h-4 w-4" />}
                {isConnecting && <RefreshCw className="h-4 w-4 animate-spin" />}
              </button>
            );
          })}
        </div>
      </div>

      {/* Connected Calendars */}
      {connections.filter((c) => c.status === 'connected').length > 0 && (
        <div className="divide-y">
          {connections
            .filter((c) => c.status === 'connected')
            .map((connection) => {
              const info = providerInfo[connection.provider];
              const isSelected = selectedConnection === connection.id;
              const isSyncing = syncing === connection.id;
              const isSettingsOpen = showSettings === connection.id;

              return (
                <div key={connection.id} className="p-4">
                  <div className="flex items-center justify-between">
                    <div
                      className="flex items-center gap-3 cursor-pointer"
                      onClick={() => setSelectedConnection(connection.id)}
                    >
                      <span
                        className={cn(
                          'w-8 h-8 rounded-lg flex items-center justify-center text-white text-sm font-bold',
                          info.color
                        )}
                      >
                        {info.icon}
                      </span>
                      <div>
                        <p className="font-medium text-gray-900">
                          {connection.calendar_name || info.name}
                        </p>
                        <p className="text-xs text-gray-500">
                          Last synced: {formatLastSync(connection.last_sync_at)}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      {/* Sync Button */}
                      <button
                        onClick={() => handleSync(connection.id)}
                        disabled={isSyncing}
                        className={cn(
                          'flex items-center gap-1 px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
                          isSyncing
                            ? 'bg-gray-100 text-gray-400'
                            : 'bg-blue-50 text-blue-600 hover:bg-blue-100'
                        )}
                      >
                        <RefreshCw className={cn('h-4 w-4', isSyncing && 'animate-spin')} />
                        {isSyncing ? 'Syncing...' : 'Sync'}
                      </button>

                      {/* Settings Toggle */}
                      <button
                        onClick={() => setShowSettings(isSettingsOpen ? null : connection.id)}
                        className={cn(
                          'p-1.5 rounded-md transition-colors',
                          isSettingsOpen
                            ? 'bg-gray-200 text-gray-700'
                            : 'text-gray-400 hover:bg-gray-100'
                        )}
                      >
                        <Settings className="h-4 w-4" />
                      </button>

                      {/* Disconnect */}
                      <button
                        onClick={() => handleDisconnect(connection.id)}
                        className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors"
                        title="Disconnect"
                      >
                        <Unlink className="h-4 w-4" />
                      </button>
                    </div>
                  </div>

                  {/* Settings Panel */}
                  {isSettingsOpen && (
                    <div className="mt-4 p-3 bg-gray-50 rounded-lg space-y-3">
                      <div className="flex items-center justify-between">
                        <label className="text-sm text-gray-700">Sync Enabled</label>
                        <button
                          onClick={() =>
                            handleUpdateSettings(connection.id, {
                              sync_enabled: !connection.sync_enabled,
                            })
                          }
                          className={cn(
                            'w-10 h-5 rounded-full transition-colors relative',
                            connection.sync_enabled ? 'bg-blue-500' : 'bg-gray-300'
                          )}
                        >
                          <span
                            className={cn(
                              'absolute top-0.5 w-4 h-4 bg-white rounded-full transition-transform',
                              connection.sync_enabled ? 'left-5' : 'left-0.5'
                            )}
                          />
                        </button>
                      </div>

                      <div>
                        <label className="text-sm text-gray-700 block mb-1">Sync Direction</label>
                        <select
                          value={connection.sync_direction}
                          onChange={(e) =>
                            handleUpdateSettings(connection.id, {
                              sync_direction: e.target.value as SyncDirection,
                            })
                          }
                          className="w-full text-sm border rounded-md px-2 py-1.5"
                        >
                          <option value="todo_to_calendar">Todos to Calendar</option>
                          <option value="calendar_to_todo">Calendar to Todos</option>
                          <option value="bidirectional">Bidirectional</option>
                        </select>
                      </div>
                    </div>
                  )}

                  {/* Events List (when selected) */}
                  {isSelected && events.length > 0 && (
                    <div className="mt-4 space-y-2">
                      <p className="text-xs font-medium text-gray-500 uppercase">
                        Synced Events ({events.length})
                      </p>
                      <div className="space-y-1 max-h-48 overflow-y-auto">
                        {events.slice(0, 5).map((event) => (
                          <div
                            key={event.id}
                            className="flex items-center gap-2 p-2 bg-gray-50 rounded text-sm"
                          >
                            <Clock className="h-3.5 w-3.5 text-gray-400" />
                            <span className="flex-1 truncate">{event.title}</span>
                            <span className="text-xs text-gray-400">
                              {new Date(event.start_time).toLocaleDateString()}
                            </span>
                          </div>
                        ))}
                        {events.length > 5 && (
                          <p className="text-xs text-gray-400 text-center py-1">
                            +{events.length - 5} more events
                          </p>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
        </div>
      )}

      {/* Empty State */}
      {connections.filter((c) => c.status === 'connected').length === 0 && (
        <div className="p-8 text-center">
          <Calendar className="h-12 w-12 mx-auto text-gray-300 mb-3" />
          <p className="text-gray-500 mb-2">No calendars connected</p>
          <p className="text-sm text-gray-400">
            Connect a calendar above to sync your todos with your schedule.
          </p>
        </div>
      )}
    </div>
  );
}

export default CalendarIntegration;
