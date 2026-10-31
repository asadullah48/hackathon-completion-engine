'use client';

import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Calendar, TrendingUp, Users, CheckCircle, Clock, AlertTriangle } from 'lucide-react';
import { useTodoStore } from '@/lib/store';
import { Todo, TodoStatus, TodoCategory, TodoPriority } from '@/lib/types';

// Define types for analytics data
interface StatusData {
  name: string;
  value: number;
  color: string;
}

interface CategoryData {
  name: string;
  value: number;
  color: string;
}

interface PriorityData {
  name: string;
  value: number;
  color: string;
}

interface TimelineData {
  date: string;
  completed: number;
  pending: number;
}

export default function AnalyticsDashboard() {
  const { todos, stats } = useTodoStore();
  const [timeRange, setTimeRange] = useState<'week' | 'month' | 'quarter'>('month');
  const [statusData, setStatusData] = useState<StatusData[]>([]);
  const [categoryData, setCategoryData] = useState<CategoryData[]>([]);
  const [priorityData, setPriorityData] = useState<PriorityData[]>([]);
  const [timelineData, setTimelineData] = useState<TimelineData[]>([]);

  // Colors for charts
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];
  const STATUS_COLORS: Record<TodoStatus, string> = {
    pending: '#FFBB28',
    in_progress: '#0088FE',
    completed: '#00C49F',
    flagged: '#FF8042'
  };
  const CATEGORY_COLORS: Record<TodoCategory, string> = {
    work: '#3b82f6',
    personal: '#ec4899',
    study: '#a855f7',
    health: '#22c55e',
    other: '#6b7280'
  };
  const PRIORITY_COLORS: Record<TodoPriority, string> = {
    low: '#10b981',
    medium: '#f59e0b',
    high: '#ef4444'
  };

  // Process data for charts
  useEffect(() => {
    if (!todos.length) return;

    // Status distribution
    const statusCounts: Record<TodoStatus, number> = {
      pending: 0,
      in_progress: 0,
      completed: 0,
      flagged: 0
    };
    todos.forEach(todo => {
      statusCounts[todo.status]++;
    });
    const statusChartData: StatusData[] = Object.entries(statusCounts).map(([key, value]) => ({
      name: key.replace('_', ' '),
      value,
      color: STATUS_COLORS[key as TodoStatus]
    })).filter(item => item.value > 0);
    setStatusData(statusChartData);

    // Category distribution
    const categoryCounts: Record<TodoCategory, number> = {
      work: 0,
      personal: 0,
      study: 0,
      health: 0,
      other: 0
    };
    todos.forEach(todo => {
      if (todo.category in categoryCounts) {
        categoryCounts[todo.category as TodoCategory]++;
      }
    });
    const categoryChartData: CategoryData[] = Object.entries(categoryCounts).map(([key, value]) => ({
      name: key,
      value,
      color: CATEGORY_COLORS[key as TodoCategory]
    })).filter(item => item.value > 0);
    setCategoryData(categoryChartData);

    // Priority distribution
    const priorityCounts: Record<TodoPriority, number> = {
      low: 0,
      medium: 0,
      high: 0
    };
    todos.forEach(todo => {
      if (todo.priority in priorityCounts) {
        priorityCounts[todo.priority as TodoPriority]++;
      }
    });
    const priorityChartData: PriorityData[] = Object.entries(priorityCounts).map(([key, value]) => ({
      name: key,
      value,
      color: PRIORITY_COLORS[key as TodoPriority]
    })).filter(item => item.value > 0);
    setPriorityData(priorityChartData);

    // Timeline data (last 30 days)
    const today = new Date();
    const thirtyDaysAgo = new Date(today);
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

    const timelineMap: Record<string, { completed: number; pending: number }> = {};
    
    // Initialize the map with dates
    for (let d = new Date(thirtyDaysAgo); d <= today; d.setDate(d.getDate() + 1)) {
      const dateStr = d.toISOString().split('T')[0];
      timelineMap[dateStr] = { completed: 0, pending: 0 };
    }

    // Count todos by date
    todos.forEach(todo => {
      if (todo.created_at) {
        const dateStr = new Date(todo.created_at).toISOString().split('T')[0];
        if (timelineMap[dateStr]) {
          if (todo.status === 'completed') {
            timelineMap[dateStr].completed++;
          } else {
            timelineMap[dateStr].pending++;
          }
        }
      }
    });

    const timelineArray: TimelineData[] = Object.entries(timelineMap).map(([date, counts]) => ({
      date,
      completed: counts.completed,
      pending: counts.pending
    }));
    
    setTimelineData(timelineArray);
  }, [todos]);

  // Calculate metrics
  const totalTodos = todos.length;
  const completedTodos = todos.filter(todo => todo.status === 'completed').length;
  const inProgressTodos = todos.filter(todo => todo.status === 'in_progress').length;
  const pendingTodos = todos.filter(todo => todo.status === 'pending').length;
  const flaggedTodos = todos.filter(todo => todo.status === 'flagged').length;
  const completionRate = totalTodos > 0 ? Math.round((completedTodos / totalTodos) * 100) : 0;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="text-gray-600 mt-1">Track your productivity and team performance</p>
        </div>
        <div className="flex gap-2">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value as 'week' | 'month' | 'quarter')}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="week">Last Week</option>
            <option value="month">Last Month</option>
            <option value="quarter">Last Quarter</option>
          </select>
        </div>
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-200">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <TrendingUp className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Tasks</p>
              <p className="text-xl font-bold text-gray-900">{totalTodos}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-200">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Completed</p>
              <p className="text-xl font-bold text-gray-900">{completedTodos}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-200">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <Clock className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Pending</p>
              <p className="text-xl font-bold text-gray-900">{pendingTodos}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-200">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <AlertTriangle className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Completion Rate</p>
              <p className="text-xl font-bold text-gray-900">{completionRate}%</p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Status Distribution */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Tasks by Status</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={statusData}
                  cx="50%"
                  cy="50%"
                  labelLine={true}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }: { name?: string; percent?: number }) => `${name || ''}: ${((percent || 0) * 100).toFixed(0)}%`}
                >
                  {statusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => [`${value} tasks`, 'Count']} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Category Distribution */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Tasks by Category</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={categoryData}
                margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" name="Task Count">
                  {categoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Priority Distribution */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 lg:col-span-2">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Tasks by Priority</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={priorityData}
                  cx="50%"
                  cy="50%"
                  labelLine={true}
                  innerRadius={60}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }: { name?: string; percent?: number }) => `${name || ''}: ${((percent || 0) * 100).toFixed(0)}%`}
                >
                  {priorityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => [`${value} tasks`, 'Count']} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Timeline */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 lg:col-span-2">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Task Activity Over Time</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={timelineData}
                margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="completed" name="Completed" fill="#00C49F" />
                <Bar dataKey="pending" name="Pending" fill="#FFBB28" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}