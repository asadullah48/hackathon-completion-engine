'use client';

/**
 * Todo Stats Component.
 * Dashboard showing todo statistics and completion rates.
 */

import {
  CheckCircle2,
  Clock,
  AlertTriangle,
  ListTodo,
  TrendingUp,
  Calendar,
  Target,
  Flame,
} from 'lucide-react';
import { TodoStats as TodoStatsType } from '@/lib/types';
import { cn, getCategoryColor, getPriorityColor } from '@/lib/utils';

interface TodoStatsProps {
  stats: TodoStatsType | null;
  isLoading?: boolean;
  className?: string;
}

export function TodoStats({ stats, isLoading, className }: TodoStatsProps) {
  if (isLoading) {
    return (
      <div className={cn('bg-white rounded-lg shadow-sm border p-4', className)}>
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/3"></div>
          <div className="grid grid-cols-2 gap-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-20 bg-gray-100 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className={cn('bg-white rounded-lg shadow-sm border p-4', className)}>
        <p className="text-gray-500 text-center">No statistics available</p>
      </div>
    );
  }

  const completionPercent = Math.round(stats.completion_rate * 100);
  const overdueCount = stats.by_status.flagged || 0;
  const inProgressCount = stats.by_status.in_progress || 0;
  const pendingCount = stats.by_status.pending || 0;
  const completedCount = stats.by_status.completed || 0;

  return (
    <div className={cn('bg-white rounded-lg shadow-sm border p-4 space-y-4', className)}>
      <h2 className="text-lg font-semibold text-gray-900">Statistics</h2>

      {/* Completion Rate */}
      <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-4 border border-green-100">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-green-800">Completion Rate</span>
          <span className="text-2xl font-bold text-green-600">{completionPercent}%</span>
        </div>
        <div className="h-2 bg-green-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-green-400 to-emerald-500 transition-all duration-500"
            style={{ width: `${completionPercent}%` }}
          />
        </div>
        <p className="text-xs text-green-700 mt-2">
          {completedCount} of {stats.total} todos completed
        </p>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-2 gap-3">
        <StatCard
          icon={<ListTodo className="h-5 w-5" />}
          label="Total"
          value={stats.total}
          color="gray"
        />
        <StatCard
          icon={<Clock className="h-5 w-5" />}
          label="In Progress"
          value={inProgressCount}
          color="blue"
        />
        <StatCard
          icon={<Target className="h-5 w-5" />}
          label="Pending"
          value={pendingCount}
          color="amber"
        />
        <StatCard
          icon={<CheckCircle2 className="h-5 w-5" />}
          label="Completed"
          value={completedCount}
          color="green"
        />
      </div>

      {/* Flagged Alert */}
      {overdueCount > 0 && (
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-3 flex items-center gap-3">
          <AlertTriangle className="h-5 w-5 text-orange-500" />
          <div>
            <p className="text-sm font-medium text-orange-800">
              {overdueCount} flagged {overdueCount === 1 ? 'todo' : 'todos'}
            </p>
            <p className="text-xs text-orange-600">Requires human review</p>
          </div>
        </div>
      )}

      {/* By Category */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-2">By Category</h3>
        <div className="space-y-2">
          {Object.entries(stats.by_category).map(([category, count]) => {
            if (count === 0) return null;
            const percent = stats.total > 0 ? (count / stats.total) * 100 : 0;
            return (
              <div key={category} className="flex items-center gap-2">
                <span
                  className={cn(
                    'w-20 text-xs font-medium px-2 py-0.5 rounded',
                    getCategoryColor(category as any)
                  )}
                >
                  {category}
                </span>
                <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gray-400 rounded-full transition-all"
                    style={{ width: `${percent}%` }}
                  />
                </div>
                <span className="text-xs text-gray-500 w-8 text-right">{count}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* By Priority */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-2">By Priority</h3>
        <div className="flex gap-2">
          {(['high', 'medium', 'low'] as const).map((priority) => {
            const count = stats.by_priority[priority] || 0;
            return (
              <div
                key={priority}
                className={cn(
                  'flex-1 text-center p-2 rounded-lg border',
                  getPriorityColor(priority)
                )}
              >
                <p className="text-lg font-bold">{count}</p>
                <p className="text-xs capitalize">{priority}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Today's Focus */}
      <div className="bg-blue-50 border border-blue-100 rounded-lg p-3">
        <div className="flex items-center gap-2 mb-2">
          <Flame className="h-4 w-4 text-blue-600" />
          <h3 className="text-sm font-medium text-blue-800">Today's Focus</h3>
        </div>
        <p className="text-xs text-blue-700">
          {inProgressCount > 0
            ? `${inProgressCount} task${inProgressCount > 1 ? 's' : ''} in progress`
            : 'No tasks in progress. Start one!'}
        </p>
        {stats.by_priority.high > 0 && (
          <p className="text-xs text-red-600 mt-1">
            {stats.by_priority.high} high priority pending
          </p>
        )}
      </div>
    </div>
  );
}

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: number;
  color: 'gray' | 'blue' | 'green' | 'amber' | 'red';
}

function StatCard({ icon, label, value, color }: StatCardProps) {
  const colors = {
    gray: 'bg-gray-50 text-gray-600 border-gray-200',
    blue: 'bg-blue-50 text-blue-600 border-blue-200',
    green: 'bg-green-50 text-green-600 border-green-200',
    amber: 'bg-amber-50 text-amber-600 border-amber-200',
    red: 'bg-red-50 text-red-600 border-red-200',
  };

  return (
    <div className={cn('rounded-lg border p-3', colors[color])}>
      <div className="flex items-center gap-2 mb-1">
        {icon}
        <span className="text-xs font-medium">{label}</span>
      </div>
      <p className="text-2xl font-bold">{value}</p>
    </div>
  );
}

export default TodoStats;
