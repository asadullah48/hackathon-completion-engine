/**
 * API Client for Course Companion Backend
 */

import axios, { AxiosError } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

// Types
export interface ChatResponse {
  response: string;
  conversation_id: string;
  constitutional_decision: 'allow' | 'block' | 'flag';
  logged: boolean;
}

export interface Conversation {
  timestamp: string;
  student_id: string;
  conversation_id: string;
  query: string;
  response: string;
  decision: string;
  metadata?: Record<string, unknown>;
}

export interface ConversationsResponse {
  student_id: string;
  conversations: Conversation[];
  total: number;
}

export interface ProgressResponse {
  student_id: string;
  total_conversations: number;
  concepts_discussed: string[];
  time_spent_minutes: number;
  last_active: string | null;
}

export interface FlagResponse {
  status: string;
  conversation_id: string;
  message: string;
}

export interface ApiError {
  message: string;
  status?: number;
}

/**
 * Send a chat message to the AI
 */
export async function sendMessage(
  message: string,
  studentId: string,
  conversationId?: string
): Promise<ChatResponse> {
  try {
    const response = await api.post<ChatResponse>('/api/chat', {
      message,
      student_id: studentId,
      conversation_id: conversationId,
    });
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError<{ detail?: string }>;
    throw {
      message: axiosError.response?.data?.detail || 'Failed to send message',
      status: axiosError.response?.status,
    } as ApiError;
  }
}

/**
 * Get conversation history for a student
 */
export async function getConversations(studentId: string): Promise<ConversationsResponse> {
  try {
    const response = await api.get<ConversationsResponse>(`/api/conversations/${studentId}`);
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError<{ detail?: string }>;
    throw {
      message: axiosError.response?.data?.detail || 'Failed to fetch conversations',
      status: axiosError.response?.status,
    } as ApiError;
  }
}

/**
 * Get progress statistics for a student
 */
export async function getProgress(studentId: string): Promise<ProgressResponse> {
  try {
    const response = await api.get<ProgressResponse>(`/api/progress/${studentId}`);
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError<{ detail?: string }>;
    throw {
      message: axiosError.response?.data?.detail || 'Failed to fetch progress',
      status: axiosError.response?.status,
    } as ApiError;
  }
}

/**
 * Flag a conversation for human review
 */
export async function flagConversation(
  conversationId: string,
  reason?: string
): Promise<FlagResponse> {
  try {
    const response = await api.post<FlagResponse>(`/api/flag/${conversationId}`, {
      reason,
    });
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError<{ detail?: string }>;
    throw {
      message: axiosError.response?.data?.detail || 'Failed to flag conversation',
      status: axiosError.response?.status,
    } as ApiError;
  }
}

/**
 * Health check for the API
 */
export async function healthCheck(): Promise<boolean> {
  try {
    const response = await api.get('/health');
    return response.data?.status === 'healthy';
  } catch {
    return false;
  }
}

export default api;
