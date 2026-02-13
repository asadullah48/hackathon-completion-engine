'use client';

import { useState, useEffect } from 'react';
import { format } from 'date-fns';
import {
  TrendingUp,
  MessageSquare,
  Clock,
  Target,
  Calendar,
  ArrowLeft,
  CheckCircle,
  XCircle,
  AlertTriangle,
  RefreshCw,
} from 'lucide-react';
import { getProgress, getConversations, ProgressResponse, Conversation } from '@/lib/api';

const STUDENT_ID = process.env.NEXT_PUBLIC_STUDENT_ID || 'demo_student';

export default function ProgressPage() {
  const [progress, setProgress] = useState<ProgressResponse | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError(null);
      try {
        const [progressData, conversationsData] = await Promise.all([
          getProgress(STUDENT_ID),
          getConversations(STUDENT_ID),
        ]);
        setProgress(progressData);
        setConversations(conversationsData.conversations);
      } catch (err) {
        setError('Failed to load progress data. Please ensure the backend is running.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const getDecisionIcon = (decision: string) => {
    switch (decision) {
      case 'allow':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'block':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'flag':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      default:
        return <CheckCircle className="w-4 h-4 text-gray-400" />;
    }
  };

  const getDecisionLabel = (decision: string) => {
    switch (decision) {
      case 'allow':
        return 'Allowed';
      case 'block':
        return 'Blocked';
      case 'flag':
        return 'Flagged';
      default:
        return 'Unknown';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="flex items-center gap-2 text-gray-600">
          <RefreshCw className="w-5 h-5 animate-spin" />
          <span>Loading progress...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md text-center">
          <XCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-lg font-semibold text-red-800 mb-2">Error Loading Data</h2>
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <a
            href="/"
            className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-800 mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Chat
          </a>
          <h1 className="text-3xl font-bold text-gray-800">Learning Progress</h1>
          <p className="text-gray-600 mt-2">Track your learning journey with Course Companion</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                <MessageSquare className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-800">
                  {progress?.total_conversations || 0}
                </p>
                <p className="text-sm text-gray-600">Total Conversations</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                <Clock className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-800">
                  {progress?.time_spent_minutes || 0}
                </p>
                <p className="text-sm text-gray-600">Minutes Learning</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
                <Target className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-800">
                  {progress?.concepts_discussed.length || 0}
                </p>
                <p className="text-sm text-gray-600">Concepts Explored</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center">
                <Calendar className="w-6 h-6 text-orange-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-800">
                  {progress?.last_active
                    ? format(new Date(progress.last_active), 'MMM d')
                    : 'N/A'}
                </p>
                <p className="text-sm text-gray-600">Last Active</p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Concepts Discussed */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-purple-600" />
                Concepts Discussed
              </h2>

              {progress?.concepts_discussed && progress.concepts_discussed.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {progress.concepts_discussed.map((concept, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-purple-50 text-purple-700 rounded-full text-sm"
                    >
                      {concept}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-sm">
                  No concepts tracked yet. Start asking questions!
                </p>
              )}
            </div>
          </div>

          {/* Recent Activity */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <MessageSquare className="w-5 h-5 text-blue-600" />
                Recent Activity
              </h2>

              {conversations.length > 0 ? (
                <div className="space-y-4 max-h-[500px] overflow-y-auto">
                  {conversations.slice(0, 10).map((conv, index) => (
                    <div
                      key={index}
                      className="border-l-4 border-gray-200 pl-4 py-2 hover:border-blue-400 transition-colors"
                    >
                      <div className="flex items-center gap-2 mb-1">
                        {getDecisionIcon(conv.decision)}
                        <span
                          className={`text-xs font-medium ${
                            conv.decision === 'allow'
                              ? 'text-green-600'
                              : conv.decision === 'block'
                              ? 'text-red-600'
                              : 'text-yellow-600'
                          }`}
                        >
                          {getDecisionLabel(conv.decision)}
                        </span>
                        <span className="text-xs text-gray-400">
                          {format(new Date(conv.timestamp), 'MMM d, h:mm a')}
                        </span>
                      </div>
                      <p className="text-sm text-gray-800 font-medium truncate">{conv.query}</p>
                      <p className="text-sm text-gray-600 truncate mt-1">{conv.response}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-sm">
                  No conversations yet. Start chatting to see your activity!
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Decision Distribution */}
        <div className="mt-8">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Decision Distribution</h2>

            {conversations.length > 0 ? (
              <div className="grid grid-cols-3 gap-4">
                {['allow', 'block', 'flag'].map((decision) => {
                  const count = conversations.filter((c) => c.decision === decision).length;
                  const percentage =
                    conversations.length > 0
                      ? Math.round((count / conversations.length) * 100)
                      : 0;

                  return (
                    <div
                      key={decision}
                      className={`p-4 rounded-lg ${
                        decision === 'allow'
                          ? 'bg-green-50'
                          : decision === 'block'
                          ? 'bg-red-50'
                          : 'bg-yellow-50'
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-2">
                        {getDecisionIcon(decision)}
                        <span
                          className={`font-medium ${
                            decision === 'allow'
                              ? 'text-green-700'
                              : decision === 'block'
                              ? 'text-red-700'
                              : 'text-yellow-700'
                          }`}
                        >
                          {getDecisionLabel(decision)}
                        </span>
                      </div>
                      <p className="text-2xl font-bold text-gray-800">{count}</p>
                      <p className="text-sm text-gray-600">{percentage}% of total</p>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">No data available yet.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
