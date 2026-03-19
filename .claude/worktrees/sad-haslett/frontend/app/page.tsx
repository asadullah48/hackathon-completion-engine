'use client';

import { useState, useEffect, useCallback } from 'react';
import { BookOpen, MessageSquare, TrendingUp, Shield, Clock, Target } from 'lucide-react';
import ChatInterface from '@/components/ChatInterface';
import { getProgress, ProgressResponse, healthCheck } from '@/lib/api';
import { CONSTITUTIONAL_RULES } from '@/lib/constitutionalRules';

const STUDENT_ID = process.env.NEXT_PUBLIC_STUDENT_ID || 'demo_student';

export default function Home() {
  const [progress, setProgress] = useState<ProgressResponse | null>(null);
  const [isApiHealthy, setIsApiHealthy] = useState<boolean | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  // Check API health on mount
  useEffect(() => {
    healthCheck().then(setIsApiHealthy);
  }, []);

  // Fetch progress data
  const fetchProgress = useCallback(async () => {
    try {
      const data = await getProgress(STUDENT_ID);
      setProgress(data);
    } catch (error) {
      console.error('Failed to fetch progress:', error);
    }
  }, []);

  useEffect(() => {
    fetchProgress();
  }, [fetchProgress, refreshKey]);

  // Handle new message - refresh progress
  const handleNewMessage = () => {
    setRefreshKey((prev) => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* API Status Banner */}
      {isApiHealthy === false && (
        <div className="bg-red-500 text-white text-center py-2 text-sm">
          Backend API is not responding. Please ensure the server is running on port 8000.
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main Chat Area */}
          <div className="lg:col-span-3">
            <div className="h-[calc(100vh-8rem)]">
              <ChatInterface studentId={STUDENT_ID} onNewMessage={handleNewMessage} />
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Progress Summary Card */}
            <div className="bg-white rounded-lg shadow-lg p-4">
              <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-blue-600" />
                Your Progress
              </h2>

              {progress ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-gray-600">
                      <MessageSquare className="w-4 h-4" />
                      <span className="text-sm">Conversations</span>
                    </div>
                    <span className="font-semibold text-gray-800">
                      {progress.total_conversations}
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-gray-600">
                      <Clock className="w-4 h-4" />
                      <span className="text-sm">Time Learning</span>
                    </div>
                    <span className="font-semibold text-gray-800">
                      {progress.time_spent_minutes} min
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-gray-600">
                      <Target className="w-4 h-4" />
                      <span className="text-sm">Concepts</span>
                    </div>
                    <span className="font-semibold text-gray-800">
                      {progress.concepts_discussed.length}
                    </span>
                  </div>

                  {progress.last_active && (
                    <div className="pt-2 border-t">
                      <p className="text-xs text-gray-500">
                        Last active:{' '}
                        {new Date(progress.last_active).toLocaleDateString()}
                      </p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-4">
                  <p className="text-sm text-gray-500">Loading progress...</p>
                </div>
              )}
            </div>

            {/* Quick Links */}
            <div className="bg-white rounded-lg shadow-lg p-4">
              <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-green-600" />
                Quick Links
              </h2>

              <div className="space-y-2">
                <a
                  href="/progress"
                  className="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-50 transition-colors text-gray-700"
                >
                  <TrendingUp className="w-4 h-4" />
                  <span className="text-sm">View Full Progress</span>
                </a>
                <a
                  href="/materials"
                  className="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-50 transition-colors text-gray-700"
                >
                  <BookOpen className="w-4 h-4" />
                  <span className="text-sm">Course Materials</span>
                </a>
                <a
                  href="/rules"
                  className="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-50 transition-colors text-gray-700"
                >
                  <Shield className="w-4 h-4" />
                  <span className="text-sm">Constitutional Rules</span>
                </a>
              </div>
            </div>

            {/* Constitutional Rules Reminder */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg shadow-lg p-4">
              <h2 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
                <Shield className="w-5 h-5 text-indigo-600" />
                Learning Guidelines
              </h2>

              <div className="space-y-3">
                {CONSTITUTIONAL_RULES.slice(0, 3).map((rule, index) => (
                  <div key={index} className="flex items-start gap-2">
                    <div className="w-6 h-6 bg-indigo-100 rounded-full flex items-center justify-center flex-shrink-0">
                      <span className="text-xs font-medium text-indigo-600">{index + 1}</span>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-800">{rule.title}</p>
                      <p className="text-xs text-gray-600">{rule.description}</p>
                    </div>
                  </div>
                ))}
              </div>

              <a
                href="/rules"
                className="mt-3 inline-block text-sm text-indigo-600 hover:text-indigo-800"
              >
                View all rules →
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
