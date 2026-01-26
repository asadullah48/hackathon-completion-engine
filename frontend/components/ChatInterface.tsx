'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { Send, Loader2, AlertCircle, RefreshCw } from 'lucide-react';
import MessageBubble, { Message } from './MessageBubble';
import { checkQuery, getTypingWarning } from '@/lib/constitutionalRules';
import { sendMessage, flagConversation, ApiError } from '@/lib/api';

interface ChatInterfaceProps {
  studentId: string;
  onNewMessage?: () => void;
}

export default function ChatInterface({ studentId, onNewMessage }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [typingWarning, setTypingWarning] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Check input as user types
  useEffect(() => {
    const warning = getTypingWarning(input);
    setTypingWarning(warning);
  }, [input]);

  // Handle input change with auto-resize
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    setError(null);

    // Auto-resize textarea
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 150) + 'px';
  };

  // Handle message submission
  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();

    const trimmedInput = input.trim();
    if (!trimmedInput || isLoading) return;

    // Check constitutional rules on client side
    const checkResult = checkQuery(trimmedInput);

    // Add user message to chat
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      content: trimmedInput,
      role: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setError(null);

    // Reset textarea height
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
    }

    try {
      // Send to backend
      const response = await sendMessage(trimmedInput, studentId, conversationId || undefined);

      // Store conversation ID for future messages
      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      // Add assistant response
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        content: response.response,
        role: 'assistant',
        timestamp: new Date(),
        decision: response.constitutional_decision,
        conversationId: response.conversation_id,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Notify parent of new message
      onNewMessage?.();
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.message || 'Failed to send message. Please try again.');

      // Remove the user message on error
      setMessages((prev) => prev.slice(0, -1));
      setInput(trimmedInput); // Restore input
    } finally {
      setIsLoading(false);
    }
  };

  // Handle flagging a conversation
  const handleFlag = async (msgConversationId: string) => {
    try {
      await flagConversation(msgConversationId, 'Flagged by user for review');

      // Update the message to show it's flagged
      setMessages((prev) =>
        prev.map((msg) =>
          msg.conversationId === msgConversationId ? { ...msg, decision: 'flag' as const } : msg
        )
      );
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.message || 'Failed to flag conversation');
    }
  };

  // Handle Enter key (submit on Enter, new line on Shift+Enter)
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  // Check if send is allowed
  const checkResult = checkQuery(input);
  const canSend = input.trim().length > 0 && !isLoading;

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg">
      {/* Messages container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <div className="text-6xl mb-4">🎓</div>
            <h3 className="text-lg font-medium mb-2">Welcome to Course Companion!</h3>
            <p className="text-sm text-center max-w-md">
              I'm here to help you learn through Socratic questioning. Ask me about any concept,
              and I'll guide you to discover the answer yourself.
            </p>
          </div>
        ) : (
          messages.map((message) => (
            <MessageBubble key={message.id} message={message} onFlag={handleFlag} />
          ))
        )}

        {/* Loading indicator */}
        {isLoading && (
          <div className="flex items-center gap-2 text-gray-500">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span className="text-sm">Thinking...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Warning banner */}
      {typingWarning && (
        <div className="mx-4 mb-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg flex items-start gap-2">
          <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-yellow-800">{typingWarning}</p>
        </div>
      )}

      {/* Error banner */}
      {error && (
        <div className="mx-4 mb-2 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm text-red-800">{error}</p>
          </div>
          <button
            onClick={() => setError(null)}
            className="text-red-600 hover:text-red-800"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Input area */}
      <form onSubmit={handleSubmit} className="border-t p-4">
        <div className="flex items-end gap-2">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder="Ask me about any concept..."
              rows={1}
              className={`w-full resize-none rounded-lg border px-4 py-3 pr-12 text-sm focus:outline-none focus:ring-2 ${
                checkResult.decision === 'block'
                  ? 'border-red-300 focus:ring-red-500 bg-red-50'
                  : checkResult.decision === 'flag'
                  ? 'border-yellow-300 focus:ring-yellow-500 bg-yellow-50'
                  : 'border-gray-300 focus:ring-blue-500'
              }`}
              disabled={isLoading}
            />

            {/* Decision indicator */}
            {input.trim().length > 0 && checkResult.decision !== 'allow' && (
              <div className="absolute right-12 top-1/2 -translate-y-1/2">
                {checkResult.decision === 'block' ? (
                  <span className="text-red-500 text-xs font-medium">Blocked</span>
                ) : (
                  <span className="text-yellow-500 text-xs font-medium">Will Flag</span>
                )}
              </div>
            )}
          </div>

          <button
            type="submit"
            disabled={!canSend}
            className={`flex-shrink-0 p-3 rounded-lg transition-colors ${
              canSend
                ? 'bg-blue-600 hover:bg-blue-700 text-white'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            }`}
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>

        <p className="mt-2 text-xs text-gray-500">
          Press Enter to send, Shift+Enter for new line
        </p>
      </form>
    </div>
  );
}
