'use client';

import {
  Shield,
  ArrowLeft,
  Ban,
  HelpCircle,
  BookOpen,
  Bug,
  Eye,
  CheckCircle,
  XCircle,
  AlertTriangle,
} from 'lucide-react';
import { CONSTITUTIONAL_RULES } from '@/lib/constitutionalRules';

const ICON_MAP: Record<string, React.ElementType> = {
  ban: Ban,
  'help-circle': HelpCircle,
  'book-open': BookOpen,
  bug: Bug,
  eye: Eye,
};

const EXAMPLE_QUERIES = {
  allowed: [
    "Can you explain how recursion works?",
    "What's the difference between a stack and a queue?",
    "Help me understand why my code isn't working",
    "What are the time complexities of different sorting algorithms?",
    "Can you explain object-oriented programming concepts?",
  ],
  blocked: [
    "Solve this homework problem for me",
    "Write the code for my assignment",
    "Give me the answer to this test question",
    "Do my homework",
    "Complete this assignment for me",
  ],
  flagged: [
    "I have an exam tomorrow and urgently need help",
    "Due in 2 hours, need quick solution",
    "Deadline is tonight, please help fast",
    "No time to learn, just need the answer",
    "Urgently need help with this quiz",
  ],
};

export default function RulesPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <a
            href="/"
            className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-800 mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Chat
          </a>
          <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-3">
            <Shield className="w-8 h-8 text-indigo-600" />
            Constitutional Rules
          </h1>
          <p className="text-gray-600 mt-2">
            Understanding how Course Companion helps you learn while maintaining academic integrity
          </p>
        </div>

        {/* Introduction */}
        <div className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-xl p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-3">Why These Rules?</h2>
          <p className="text-gray-700 leading-relaxed">
            Course Companion is designed to be your learning partner, not a homework machine. These
            constitutional rules ensure that every interaction helps you truly understand concepts
            rather than just getting answers. Research shows that active learning through questioning
            leads to better retention and understanding.
          </p>
        </div>

        {/* Core Rules */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-6">Core Guidelines</h2>
          <div className="space-y-6">
            {CONSTITUTIONAL_RULES.map((rule, index) => {
              const Icon = ICON_MAP[rule.icon] || Shield;
              return (
                <div key={index} className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-indigo-100 rounded-xl flex items-center justify-center flex-shrink-0">
                    <Icon className="w-6 h-6 text-indigo-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-gray-800">{rule.title}</h3>
                    <p className="text-gray-600 mt-1">{rule.description}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Example Queries */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Allowed */}
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <div className="bg-green-50 p-4 border-b border-green-100">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <h3 className="font-semibold text-green-800">Allowed</h3>
              </div>
            </div>
            <div className="p-4">
              <ul className="space-y-3">
                {EXAMPLE_QUERIES.allowed.map((query, index) => (
                  <li key={index} className="text-sm text-gray-700 flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
                    <span>"{query}"</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Blocked */}
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <div className="bg-red-50 p-4 border-b border-red-100">
              <div className="flex items-center gap-2">
                <XCircle className="w-5 h-5 text-red-600" />
                <h3 className="font-semibold text-red-800">Blocked</h3>
              </div>
            </div>
            <div className="p-4">
              <ul className="space-y-3">
                {EXAMPLE_QUERIES.blocked.map((query, index) => (
                  <li key={index} className="text-sm text-gray-700 flex items-start gap-2">
                    <XCircle className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" />
                    <span>"{query}"</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Flagged */}
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <div className="bg-yellow-50 p-4 border-b border-yellow-100">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-yellow-600" />
                <h3 className="font-semibold text-yellow-800">Flagged for Review</h3>
              </div>
            </div>
            <div className="p-4">
              <ul className="space-y-3">
                {EXAMPLE_QUERIES.flagged.map((query, index) => (
                  <li key={index} className="text-sm text-gray-700 flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 text-yellow-500 flex-shrink-0 mt-0.5" />
                    <span>"{query}"</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* How It Works */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-6">How It Works</h2>
          <div className="space-y-6">
            <div className="flex items-start gap-4">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-blue-600 font-semibold">1</span>
              </div>
              <div>
                <h3 className="font-medium text-gray-800">You Ask a Question</h3>
                <p className="text-gray-600 mt-1">
                  Submit any question about programming, concepts, or your coursework.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-blue-600 font-semibold">2</span>
              </div>
              <div>
                <h3 className="font-medium text-gray-800">Constitutional Filter Checks</h3>
                <p className="text-gray-600 mt-1">
                  Your query is analyzed to determine if it's a learning request or an attempt to
                  bypass academic integrity.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-blue-600 font-semibold">3</span>
              </div>
              <div>
                <h3 className="font-medium text-gray-800">Socratic Response</h3>
                <p className="text-gray-600 mt-1">
                  The AI responds with guiding questions and explanations to help you discover the
                  answer yourself.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-blue-600 font-semibold">4</span>
              </div>
              <div>
                <h3 className="font-medium text-gray-800">Human-in-the-Loop</h3>
                <p className="text-gray-600 mt-1">
                  Flagged conversations are reviewed by instructors to ensure appropriate handling
                  of edge cases.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Tips for Best Results */}
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Tips for Best Results</h2>
          <ul className="space-y-3">
            <li className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <span className="text-gray-700">
                <strong>Be specific</strong> about what concept you're struggling with
              </span>
            </li>
            <li className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <span className="text-gray-700">
                <strong>Share what you've tried</strong> so the AI can identify where you're stuck
              </span>
            </li>
            <li className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <span className="text-gray-700">
                <strong>Ask for explanations</strong> rather than solutions
              </span>
            </li>
            <li className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <span className="text-gray-700">
                <strong>Follow up</strong> with more questions if you need deeper understanding
              </span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
