'use client';

import { format } from 'date-fns';
import { Flag, Bot, User, AlertTriangle, XCircle } from 'lucide-react';

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  decision?: 'allow' | 'block' | 'flag';
  conversationId?: string;
}

interface MessageBubbleProps {
  message: Message;
  onFlag?: (messageId: string) => void;
}

export default function MessageBubble({ message, onFlag }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const isBlocked = message.decision === 'block';
  const isFlagged = message.decision === 'flag';

  // Determine bubble styling based on role and decision
  const getBubbleStyles = () => {
    if (isUser) {
      return 'bg-blue-600 text-white ml-auto';
    }

    if (isBlocked) {
      return 'bg-red-50 border-2 border-red-200 text-gray-800';
    }

    if (isFlagged) {
      return 'bg-yellow-50 border-2 border-yellow-300 text-gray-800';
    }

    return 'bg-gray-100 text-gray-800';
  };

  // Get decision indicator
  const getDecisionIndicator = () => {
    if (isUser) return null;

    if (isBlocked) {
      return (
        <div className="flex items-center gap-1 text-red-600 text-xs mb-1">
          <XCircle className="w-3 h-3" />
          <span>Blocked - Academic Integrity</span>
        </div>
      );
    }

    if (isFlagged) {
      return (
        <div className="flex items-center gap-1 text-yellow-600 text-xs mb-1">
          <AlertTriangle className="w-3 h-3" />
          <span>Flagged for Review</span>
        </div>
      );
    }

    return null;
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`flex items-start gap-2 max-w-[80%] ${isUser ? 'flex-row-reverse' : ''}`}>
        {/* Avatar */}
        <div
          className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
            isUser ? 'bg-blue-600' : 'bg-gray-600'
          }`}
        >
          {isUser ? (
            <User className="w-4 h-4 text-white" />
          ) : (
            <Bot className="w-4 h-4 text-white" />
          )}
        </div>

        {/* Message content */}
        <div className="flex flex-col">
          {getDecisionIndicator()}

          <div className={`rounded-2xl px-4 py-2 ${getBubbleStyles()}`}>
            <p className="whitespace-pre-wrap text-sm">{message.content}</p>
          </div>

          {/* Timestamp and actions */}
          <div
            className={`flex items-center gap-2 mt-1 text-xs text-gray-500 ${
              isUser ? 'justify-end' : 'justify-start'
            }`}
          >
            <span>{format(message.timestamp, 'h:mm a')}</span>

            {/* Flag button for assistant messages */}
            {!isUser && !isFlagged && onFlag && (
              <button
                onClick={() => onFlag(message.conversationId || message.id)}
                className="flex items-center gap-1 text-gray-400 hover:text-yellow-600 transition-colors"
                title="Flag for review"
              >
                <Flag className="w-3 h-3" />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
